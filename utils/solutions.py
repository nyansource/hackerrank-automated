import json
import os
import structlog
import time

log = structlog.get_logger(__name__)

class SolutionManager:
    def __init__(self):
        self.solutions_file = "solutions.json"
        self.solutions = self._load_solutions()
    
    def _load_solutions(self):
        """Load solutions from JSON file."""
        if os.path.exists(self.solutions_file):
            try:
                with open(self.solutions_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                log.error("Failed to load solutions file, creating new one")
                return {}
        return {}
    
    def _save_solutions(self):
        """Save solutions to JSON file."""
        with open(self.solutions_file, 'w') as f:
            json.dump(self.solutions, f, indent=2)
    
    def get_solution(self, challenge_slug, language):
        """Get solution if it exists."""
        key = f"{challenge_slug}_{language}"
        if key in self.solutions:
            log.info("Found existing solution", slug=challenge_slug, language=language)
            return self.solutions[key]['code']
        return None
    
    def save_solution(self, challenge_slug, language, code):
        """Save accepted solution."""
        key = f"{challenge_slug}_{language}"
        self.solutions[key] = {
            'code': code,
            'timestamp': time.time()
        }
        self._save_solutions()
        log.info("Saved accepted solution", slug=challenge_slug, language=language)
    
