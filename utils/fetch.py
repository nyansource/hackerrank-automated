import json
import time
import structlog

log = structlog.get_logger(__name__)

class HackerRankFetch:
    def __init__(self, session, csrf_token, contest):
        self.session = session
        self.csrf_token = csrf_token
        self.contest = contest
        self.is_domain_type = None  
        
    def fetch_challenges(self):
        """Fetch all challenges from a HackerRank contest"""
        all_challenges = []
        offset = 0
        
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': f'https://www.hackerrank.com/contests/{self.contest}/challenges/filters/page:1',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-platform': '"Linux"',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-csrf-token': self.csrf_token,
            'x-requested-with': 'XMLHttpRequest',
        }
        
        timestamp = int(time.time() * 1000)
        url1 = f'https://www.hackerrank.com/rest/contests/{self.contest}/challenges?offset=0&limit=50&filters=page:1&track_login=true&_={timestamp}'
        url2 = f'https://www.hackerrank.com/rest/contests/master/tracks/{self.contest}/challenges?offset=0&limit=50&track_login=true'
        
        base_url = None
        for url in [url1, url2]:
            try:
                response = self.session.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('models'): 
                        base_url = url.split('?')[0]  
                        self.is_domain_type = url == url2
                        break
            except Exception as e:
                log.error("Request failed", error=e)
                continue
        
        if not base_url:
            log.error("No valid API endpoint found")
            return []
            
        while True:
            timestamp = int(time.time() * 1000)
            url = f'{base_url}?offset={offset}&limit=50&track_login=true&_={timestamp}'
            
            for _ in range(3):
                try:
                    response = self.session.get(url, headers=headers)
                    break
                except Exception as e:
                    log.error("Request failed", error=e)
                    time.sleep(1)
            
            if response.status_code != 200:
                log.error("Request failed", status_code=response.status_code)
                break
                
            try:
                data = response.json()
            except json.JSONDecodeError:
                log.error("Invalid JSON response", text=response.text)
                break
                
            current_challenges = data.get('models', [])
            total_challenges = data.get('total', 0)
            
            if not current_challenges:
                break
                
            all_challenges.extend(current_challenges)
            
            offset += len(current_challenges)
            
            if len(all_challenges) >= total_challenges:
                log.info("Challenges fetched", count=len(all_challenges), total=total_challenges)
                break
                
            time.sleep(0.5)
        
        return all_challenges
 