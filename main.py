import time
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.register import HackerRank
from utils.getchallenge import Reciever
from utils.submit import HackerRankSubmit
from utils.fetch import HackerRankFetch
from utils.ai import HackerRankAI
from utils.solutions import SolutionManager
import structlog
from utils.parse import extract_challenge_info
log = structlog.get_logger(__name__)

test_mode = False


def solve_challenge(challenge, session, csrf_token, contest, ai, solutions , domain_type):
    challenge_slug = challenge['slug']
    log.info("Processing challenge", slug=challenge_slug)
    
    rec = Reciever(session, csrf_token, contest, is_domain_type=domain_type)
    _ = rec.get_challenge(challenge_slug)
    challenge_info = extract_challenge_info(_)
    language = challenge_info['languages']
    
    existing_solution = solutions.get_solution(challenge_slug, language)
    if existing_solution:
        #log.info("Found existing solution", slug=challenge_slug)
        solution_code = existing_solution
        if test_mode:
            return True, "Reused existing solution"
    else:
        solution_code = None
    
    submitter = HackerRankSubmit(session, csrf_token, contest, is_domain_type=domain_type)
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        if not solution_code:
            solution_code = ai.generate_solution(challenge_info, language)
            if not solution_code:
                return False, "Failed to generate solution"
        
        success, reason = submitter.submit(challenge_slug, solution_code, language)
        
        if success:
            log.info("✅ Solution accepted", slug=challenge_slug)
            solutions.save_solution(challenge_slug, language, solution_code)
            return True, "Accepted"

        if isinstance(reason, dict):
            error_info = {
                'status': reason.get('status', 'Unknown Error'),
                'testcase_messages': reason.get('testcase_messages', []),
                'testcase_status': reason.get('testcase_status', []),
                'compile_message': reason.get('compile_message', ''),
                'code': reason.get('code', ''),
                'stderr': reason.get('stderr', '')
            }
            
            if reason.get('status') in ['Wrong Answer', 'Runtime Error']:
                retry_count += 1
                if retry_count < max_retries:
                    log.info(f"Retrying ({retry_count}/{max_retries})", error=error_info)
                    solution_code = ai.generate_solution(
                        challenge_info, 
                        language, 
                        retried=True, 
                        old_code=solution_code, 
                        error_reason=error_info
                    )
                    if not solution_code:
                        return False, "Failed to generate solution on retry"
                    time.sleep(2)
                else:
                    return False, f"Failed after {max_retries} retries: {error_info}"
            elif "Compilation error" in str(reason) or "Terminated due to timeout" in str(reason):
                retry_count += 1
                if retry_count < max_retries:
                    log.info(f"Retrying ({retry_count}/{max_retries})", error=error_info)
                    solution_code = ai.generate_solution(
                        challenge_info, 
                        language, 
                        retried=True, 
                        old_code=solution_code, 
                        error_reason=error_info
                    )
                    if not solution_code:
                        return False, "Failed to generate solution on retry"
                    time.sleep(2)
                else:
                    return False, f"Failed after {max_retries} retries: {error_info}"
            else:
                return False, error_info
        else:
            return False, reason
        
        time.sleep(2)
    
    return False, "Max retries reached"

def process_contest(contest, user, session, csrf_token):
    log.info("Processing contest", contest=contest)
    fetch = HackerRankFetch(session, csrf_token, contest)
    ai = HackerRankAI()
    solutions = SolutionManager()
    try:
        challenges = fetch.fetch_challenges()
        domain_type = fetch.is_domain_type
    except Exception as e:
        log.error(f"Error fetching challenges: {str(e)}")
        return
    
    if len(challenges) == 0:
        log.error("No challenges found or expired cookies or something else.. which only pro can find lel bro")
        return
    
    solved = 0
    failed = 0
    reused = 0
    
    for challenge in challenges:
        try:
            success, reason = solve_challenge(challenge, session, csrf_token, contest, ai, solutions, domain_type)
            if success:
                if "Reused" in reason:
                    reused += 1
                else:
                    solved += 1
            else:
                failed += 1
                log.error(f"Failed to solve {challenge['slug']}: {reason}")
        except Exception as e:
            failed += 1
            log.error(f"Error solving {challenge['slug']}: {str(e)}")
    
    log.info("Challenge summary", 
             contest=contest,
             solved=solved, 
             failed=failed, 
             reused=reused,
             total=len(challenges))

def main():
    contests = ["100dayscodingchallenge"]   # <- add the end of the url to the contests list  
    #DS
    # ●https://www.hackerrank.com/100dayscodingchallenge
    # JAVA
    # ●https://www.hackerrank.com/java-mystery-phase-1
    # basically add the end of the url to the contests list 
    # or example https://www.hackerrank.com/domains/data-structures
    # for that add data-structures to the contests list

    if len(sys.argv) > 1:
        cookie_file = sys.argv[1]
        try:
            with open(cookie_file, "r") as f:
                accounts = json.load(f)
                if not isinstance(accounts, list):
                    accounts = [accounts]
                
                account_data = accounts[0]
                log.info("Using provided cookies from", file=cookie_file)
                user = HackerRank(contest=contests[0])
                session = user.session
                for cookie_name, cookie_value in account_data["cookies"].items():
                    session.cookies.set(cookie_name, cookie_value)
                user.csrf_token = account_data["csrf_token"]
                log.info("Using existing account", username=account_data["username"])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log.error(f"Error loading cookies from {cookie_file}: {str(e)}")
            sys.exit(1)
    else:
        user = HackerRank(contest=contests[0])
        session = user.session
        user.register()
        log.info("Registered as", user=user.user.name)
        
        account_data = {
            "username": user.user.name,
            "email": user.user.email,
            "password": user.user.password,
            "cookies": dict(session.cookies),
            "csrf_token": user.csrf_token
        }
        
        try:
            with open("account_cookies.json", "r") as f:
                accounts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            accounts = []
        
        accounts.append(account_data)
        with open("account_cookies.json", "w") as f:
            json.dump(accounts, f, indent=4)
    
    for contest in contests:
        try:
            process_contest(contest, user, session, user.csrf_token)
        except Exception as e:
            log.error(f"Error processing contest {contest}: {str(e)}")


    

if __name__ == "__main__":
    main()