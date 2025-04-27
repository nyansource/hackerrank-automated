import json
import random
import time
import structlog

log = structlog.get_logger(__name__)

class HackerRankSubmit:
    def __init__(self, session, csrf_token, contest, is_domain_type=False):
        self.session = session
        self.csrf_token = csrf_token
        self.contest = contest
        self.is_domain_type = is_domain_type
        
    def submit(self, challenge_slug, code, language):
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/json',
            'origin': 'https://www.hackerrank.com',
            'referer': f'https://www.hackerrank.com/contests/{self.contest}/challenges/{challenge_slug}/problem',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-platform': '"Linux"',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-csrf-token': self.csrf_token,
            'x-requested-with': 'XMLHttpRequest',
        }
        
        json_data = {
            'code': code,
            'language': language,
            'contest_slug': self.contest,
        }
        
        if self.is_domain_type:
            url = f'https://www.hackerrank.com/rest/contests/master/challenges/{challenge_slug}/submissions'
            json_data['contest_slug'] = "master"
            json_data['playlist_slug'] = ""
        else:
            url = f'https://www.hackerrank.com/rest/contests/{self.contest}/challenges/{challenge_slug}/submissions'
        
        for i in range(3):
            try:
                response = self.session.post(url, headers=headers, json=json_data)
                break
            except Exception as e:
                log.error("Request failed", error=e)
                time.sleep(1)

        if "Sorry you can't make a submission!" in response.text:
            return False, "not allowed to submit"

        if not response.text.strip():
            return False, "Empty response received"
        
        try:
            result = response.json()
        except json.JSONDecodeError:
            log.error("Invalid JSON response", text=response.text)
            return False, "Invalid JSON response"
        
        if (result.get('model') is False and 
            result.get('status') is False and 
            "can't accept your submission" in str(result.get('message', ''))):
            log.info("Rate limited", message=result.get('message', 'Unknown reason'))
            time.sleep(10)
            return self.submit(challenge_slug, code)
        
        if "accept your submission right now" in str(result):
            log.info("Rate limited, trying again in 5 seconds")
            time.sleep(5)
            return self.submit(challenge_slug, code)
        
        if result.get('status') == True and 'id' in result.get('model', {}):
            submission_id = result['model']['id']
            time_stamp = int(time.time() * 1000)
            
            max_checks = 60
            for _ in range(max_checks):
                for i in range(3):
                    try:
                        if self.is_domain_type:
                            check_url = f'https://www.hackerrank.com/rest/contests/master/challenges/{challenge_slug}/submissions/{submission_id}?&_={time_stamp}'
                        else:
                            check_url = f'https://www.hackerrank.com/rest/contests/{self.contest}/challenges/{challenge_slug}/submissions/{submission_id}?&_={time_stamp}'
                        response = self.session.get(check_url, headers=headers)
                        break
                    except Exception as e:
                        log.error("Request failed", error=e)
                        time.sleep(1)
                
                try:
                    check_result = response.json()
                except json.JSONDecodeError:
                    log.error("Invalid JSON response", text=response.text)
                    return False, "Invalid JSON response"

                model = check_result.get('model', {})
                if not isinstance(model, dict):
                    log.info("Rate limit rechecking [Happens due to sending many at same time you can ignore it]")
                    time.sleep(19)
                    continue
                
                status = model.get('status', '')
                if status == 'Accepted':
                    log.info("Accepted", challenge_slug=challenge_slug)
                    return True, "Accepted"
                elif status in ['Processing', 'Queued']:
                    time.sleep(2)
                    continue
                elif status == 'Wrong Answer':
                    testcase_messages = model.get('testcase_message', [])
                    testcase_status = model.get('testcase_status', [])
                    compile_message = model.get('compile_message', '')
                    
                    error_details = {
                        'status': 'Wrong Answer',
                        'testcase_messages': testcase_messages,
                        'testcase_status': testcase_status,
                        'compile_message': compile_message,
                        'model': model
                    }
                    
                    log.info("Wrong Answer", challenge_slug=challenge_slug, testcase_status=testcase_status)
                    return False, error_details
                
                elif status == 'Terminated due to timeout':
                    error_msg = model.get('compilemessage', 'Terminated due to timeout')
                    log.info("Terminated due to timeout", challenge_slug=challenge_slug)
                    return False, f"Terminated due to timeout: {error_msg}"
                elif status == 'Runtime Error':
                    error_msg = model.get('compilemessage', 'Runtime Error')
                    log.info("Runtime Error", challenge_slug=challenge_slug)
                    return False, f"Runtime Error: {error_msg}"
                
                elif status == 'Compilation error':
                    error_msg = model.get('compilemessage', 'Compilation error')
                    log.info("Compilation error", challenge_slug=challenge_slug)
                    return False, f"Compilation error: {error_msg}"
                else:
                    log.info("Unexpected status", result=check_result)
                    time.sleep(2)
            
            return False, "Max checks reached without final status"
        else:
            error_msg = result.get('message', 'Unknown error')
            log.error("Submission failed", result=result)
            return False, f"Submission failed: {error_msg}"