import curl_cffi.requests as requests
import time
import random
import string
import structlog

log = structlog.get_logger(__name__)

class Reciever:
    def __init__(self, session, csrf_token, contest, is_domain_type=False):
        self.session = session
        self.csrf_token = csrf_token
        self.contest = contest
        self.is_domain_type = is_domain_type


    def generate_request_id(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))

    def get_challenge(self, slug):
        timestamp = int(time.time() * 1000)
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': f'https://www.hackerrank.com/contests/{self.contest}/challenges/{slug}',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-csrf-token': self.csrf_token,
            'x-request-unique-id': self.generate_request_id(),
            'x-requested-with': 'XMLHttpRequest',
        }
        
        if self.is_domain_type:
            url = f'https://www.hackerrank.com/rest/contests/master/challenges/{slug}?&_={timestamp}'
        else:
            url = f'https://www.hackerrank.com/rest/contests/{self.contest}/challenges/{slug}?&_={timestamp}'
            
        for i in range(3):
            try:
                response = self.session.get(url, headers=headers)
                break
            except Exception as e:
                log.error("Request failed", error=e)
                time.sleep(1)
        
        if "Not Found" in response.text:
            log.error("Challenge not found", slug=slug)
            return None

        if "accept your submission right now" in response.text:
            log.info("Rate limited, trying again in 10 seconds")
            time.sleep(10)
            return self.get_challenge(slug)
        
        if response.status_code == 200:
            log.info("Challenge", name=response.json()['model']['name'], difficulty=response.json()['model']['difficulty_name'], solved_by=response.json()['model']['solved_count'])
            return response.json()
        
        if response.status_code == 429:
            log.info("Rate limited, trying again in 15 seconds")
            time.sleep(15)
            return self.get_challenge(slug)
        
        return None