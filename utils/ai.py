from g4f.client import Client
import g4f
import structlog
import time
log = structlog.get_logger(__name__)

class HackerRankAI:
    def __init__(self):
        self.client = Client(provider = g4f.Provider.PollinationsAI)
    
    def generate_solution(self, challenge_info, language , retried = None , old_code = None , error_reason = None , retries_left = 5):
        start_time = time.time()
        if retries_left == 0:
            log.error("Max retries reached", language=language)
            return None
        
        retries_left -= 1
        
        """
        Generate a solution for a HackerRank challenge.
        
        Args:
            challenge_info (dict): Challenge information
            language (str): Programming language to use
            retried (bool): Whether the solution has been retried
            old_code (str): The old code that didn't work
            error_reason (dict): Detailed error information
            retries_left (int): Number of retries remaining
            
        Returns:
            str: Generated solution code
        """
        prompt = f"""
            You are an elite competitive programmer creating optimal HackerRank solutions.
            Challenge: {challenge_info}
            From body_html scrape the problem data and use it to make the solution more accurate and correct
            CRITICAL REQUIREMENTS:
            - Language: {language} ONLY
            - Fully functional standalone solution
            - Handle ALL edge cases and constraints perfectly without any errors
            - Optimize time/space complexity
            - Include ALL necessary imports
            - Pass ALL test cases
            - Follow HackerRank's input/output format EXACTLY
            - Handle ALL possible input scenarios
            - Validate input when necessary
            - Use efficient data structures and algorithms
            - Consider memory constraints
            - Handle large input sizes
            - Consider time limits

            STRICT FORMAT RULES:
            - Return ONLY executable code
            - NO explanations, comments, or text blocks
            - NO markdown or code blocks (```)
            - NO introductory text or descriptions
            - NO copyright notices or headers
            - RAW code that compiles without modification
            - EXACT function names/signatures as specified
            - PROPERLY handle input/output per HackerRank standards
            - DO NOT ADD ``` etc or code block in the code
            - NO COMMENTS IN THE CODE
            - NO EXPLANATIONS
            - NO TEXT BLOCKS
            - NO MARKDOWN
            - NO INTRODUCTORY TEXT
            - NO COPYRIGHT NOTICES OR HEADERS

            CODE QUALITY:
            - Efficient algorithms matching problem constraints
            - Readable variable names
            - Clean implementation with minimal redundancy
            - Proper error handling
            - Input validation where needed
            - Memory efficient
            - Time efficient
            - Follow language best practices
            - Use appropriate data structures
            - Handle edge cases properly
            - Do not make any silly mistakes or assumptions on stupid things just do what it says and make sure you can handle all the edge cases and constraints
            """

        if retried and old_code and error_reason:
            error_type = error_reason.get('status', 'Unknown Error')
            error_details = []
            
            if error_type == 'Runtime Error':
                error_details.append(f"Runtime Error: {error_reason.get('stderr', 'No error details')}")
            elif error_type == 'Wrong Answer':
                test_messages = error_reason.get('testcase_messages', [])
                test_status = error_reason.get('testcase_status', [])
                for i, (msg, status) in enumerate(zip(test_messages, test_status)):
                    error_details.append(f"Test Case {i+1}: {msg} (Status: {status})")
            
            prompt += f"""
            PREVIOUS FAILURE:
            Error Type: {error_type}
            Error Details:
            {chr(10).join(error_details)}
            
            Previous code:
            {old_code}
            
            CRITICAL: Address ALL errors above and submit a FULLY CORRECTED solution.
            """
        
        try:
            response = self.client.chat.completions.create(
                model="qwen-2.5-coder-32b",
                messages=[{"role": "user", "content": prompt}],
                web_search=True,
            )
            solution_code = response.choices[0].message.content.strip()
            
            if "---" in solution_code:
                solution_code = solution_code.split("---")[0].strip()
            
            solution_code = solution_code.replace("[Learn more]", "").replace("[Support our mission]", "")
            
            lines = solution_code.split("\n")
            cleaned_lines = []
            for line in lines:
                cleaned_lines.append(line.rstrip())
            solution_code = "\n".join(cleaned_lines)
            
            log.info("Generated solution", language=language, time=time.time() - start_time, retries_left=retries_left)
            return solution_code
        except Exception as e:
            if "502" in str(e) or "Response 400: 400 Bad Request" in str(e):
                challenge_info["body_html"] = "NOT FETCHED"
                log.info("Retrying due to error", error=str(e), retries_left=retries_left)
                time.sleep(5)
                return self.generate_solution(challenge_info, language, retried, old_code, error_reason, retries_left)
            else:
                log.error("Failed to generate solution", error=str(e), retries_left=retries_left)
            return None
        

if __name__ == "__main__":
    ai = HackerRankAI()
    print(ai.generate_solution("make a function that takes a string and returns the string in reverse", "java"))