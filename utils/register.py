import os
import curl_cffi.requests as requests
from dataclasses import dataclass
import uuid
import time
import random
import string
import json
import structlog

log = structlog.get_logger(__name__)

@dataclass
class HackerRankSignup:
    name: str
    email: str
    password: str
    contest: str
    timezone: str = "Tokyo/Asia"

class HackerRank:
    def __init__(self, contest="100dayscodingchallenge"):
        self.session = requests.Session(impersonate="chrome131" if os.name == "posix" else "chrome124") #chrome131 is not working on windows or other platforms
        self.contest = contest
        self.csrf_token = None
        self.user = None
    
    def generate_request_id(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    
    def generate_email(self):
        domains = ["rescueteam.com", "fastmail.com", "protonmail.com", "tmail.com"] # you can input any domains you want to be used for the email.
        name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
        domain = random.choice(domains)
        return f"{name}@{domain}"
    
    def register(self):
        email = self.generate_email()
        self.user = HackerRankSignup(
            name=f"User {random.randint(1000, 9999)}",
            email=email,
            password=email,
            contest=self.contest
        )
        
        response = self.session.get(f'https://www.hackerrank.com/{self.contest}')
        self.csrf_token = response.text.split('csrf-token" content="')[1].split('"')[0]
        
        email_headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://www.hackerrank.com',
            'pragma': 'no-cache',
            'referer': f'https://www.hackerrank.com/auth/signup/{self.contest}',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'x-csrf-token': self.csrf_token,
            'x-request-unique-id': self.generate_request_id()
        }
        
        self.session.post(
            'https://www.hackerrank.com/auth/valid_email',
            headers=email_headers,
            json={"email": self.user.email}
        )
        
        uid = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        session_id = f"h{uuid.uuid4().hex[:7]}-{timestamp}"
        
        metrics_headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.hackerrank.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.hackerrank.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-GPC': '1',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'x-request-unique-id': self.generate_request_id()
        }
        
        metrics_data = {
            'product': 'hackerrank',
            'event_name': 'Click',
            'event_value': 'SignupPassword',
            'params[session_id]': session_id,
            'uid': uid,
        }
        
        self.session.post(
            'https://metrics.hackerrank.com/metrics', 
            headers=metrics_headers,
            data=metrics_data
        )
        
        signup_headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://www.hackerrank.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': f'https://www.hackerrank.com/auth/signup/{self.contest}',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-mobile': '?0', 
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-csrf-token': self.csrf_token,
            'x-request-unique-id': self.generate_request_id()
        }
        
        signup_data = {
            'name': self.user.name,
            'email': self.user.email,
            'password': self.user.password,
            'confirm_password': self.user.password,
            'timezone': self.user.timezone,
            'tos_accepted': True,
            'new_hrc': True
        }
        
        signup_response = self.session.post(
            f'https://www.hackerrank.com/rest/auth/signup/{self.contest}',
            headers=signup_headers,
            json=signup_data
        )
        
        result = signup_response.json()
        success = result.get("status", False) and result.get("account_created", False)
        
        if success:
            log.info("Successfully registered", email=self.user.email)
            self.csrf_token = result.get("csrf_token", self.csrf_token)
            
            self.complete_onboarding()
            
            self.send_navigation_metrics()
            
            return True
        else:
            log.error("Registration failed", errors=result.get('errors', 'Unknown error'))
            return False
    
    def complete_onboarding(self):
        onboarding_headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://www.hackerrank.com',
            'pragma': 'no-cache',
            'referer': 'https://www.hackerrank.com/onboarding?redirect=%2Fdashboard',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-csrf-token': self.csrf_token,
            'x-request-unique-id': self.generate_request_id()
        }
        
        onboarding_data = {
            'onboarding_status': 'done',
            'sourcing_jobs_consent': False,
        }
        
        response = self.session.put(
            'https://www.hackerrank.com/rest/contests/master/hackers/me',
            headers=onboarding_headers,
            json=onboarding_data
        )
        
        if response.status_code == 200:
            log.info("Onboarding completed")
    
    def send_navigation_metrics(self):
        timestamp = int(time.time() * 1000)
        session_id = f"h{uuid.uuid4().hex[:7]}-{timestamp-3000}"
        
        cookies = self.session.cookies.get_dict()
        metrics_id = cookies.get('metrics_user_identifier', f"1b37{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:32]}")
        mixpanel_token = cookies.get('hackerrank_mixpanel_token', str(uuid.uuid4()))
        
        metrics_headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.hackerrank.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.hackerrank.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'x-request-unique-id': self.generate_request_id()
        }
        
        data_array = [
            {
                "time": timestamp - 2000,
                "url": f"https://www.hackerrank.com/contests/{self.contest}/challenges",
                "track_data": {
                    "event_name": "Navigation",
                    "event_value": f"/contests/{self.contest}/challenges",
                    "params": {
                        "attribute1": ''.join(random.choice(string.ascii_letters) for _ in range(10)),
                        "attribute2": f"/contests/{self.contest}/challenges",
                        "session_id": session_id
                    }
                }
            },
            {
                "time": timestamp - 769,
                "url": f"https://www.hackerrank.com/contests/{self.contest}/challenges",
                "track_data": {
                    "event_name": "PageLoad",
                    "event_value": f"/contests/{self.contest}/challenges",
                    "params": {
                        "attribute1": f"/contests/{self.contest}/challenges",
                        "session_id": session_id
                    }
                }
            },
            {
                "time": timestamp - 769,
                "url": f"https://www.hackerrank.com/contests/{self.contest}/challenges",
                "track_data": {
                    "event_name": "DwellTime",
                    "event_value": f"/contests/{self.contest}/challenges",
                    "params": {
                        "attribute7": 1,
                        "session_id": session_id
                    }
                }
            }
        ]
        
        metrics_data = {
            'product': 'hackerrank',
            'batch_request': 'true',
            'current_time': str(timestamp),
            'data_array': json.dumps(data_array),
            'session_params': '{}',
            'uid': mixpanel_token,
            'uid_token': metrics_id,
        }
        
        response = self.session.post(
            'https://metrics.hackerrank.com/metrics', 
            headers=metrics_headers, 
            data=metrics_data
        )
        
        if response.status_code == 200:
            log.info("Navigation metrics sent")
    


def main():
    hr = HackerRank()
    if hr.register():
        log.info("Credentials", email=hr.user.email)
    
if __name__ == "__main__":
    main()