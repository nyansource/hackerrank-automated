# HackerRank Automated Challenge Solver

A tool for solving HackerRank coding challenges using AI. I made it as was lazy to manually do that.

## Contact

For questions, issues, or contributions:
- Email: nyansourcesigma@gmail.com

## System Requirements

- Python 3.8+
- pip
- Internet connection
- HackerRank account (optional)

### OS Compatibility
- **Linux (Recommended)**: Fully tested on Arch Linux
- **Windows**: May need changes
- **macOS**: Untested, may need modifications

## Installation

```bash
git clone https://github.com/nyansource/hackerrank-automated.git
cd hackerrank-automated
pip install -r requirements.txt
```

## Tutorial

### 1. Setting Up Contests

To add new contests, edit the `contests` list in `main.py`:

```python
contests = ["100dayscodingchallenge", "java-mystery-phase-1"]
```

Add the contest slug from the HackerRank URL. For example:
- URL: https://www.hackerrank.com/100dayscodingchallenge
- Slug: "100dayscodingchallenge"
or
- URL : https://www.hackerrank.com/domains/data-structures
- Slug: "data-structures"

### 2. Using Existing Account

1. Create a `cookies.json` file with your account details:
```json
{
    "username": "your_username",
    "email": "your_email",
    "password": "your_password",
    "cookies": {
        "cookie1": "your_cookie_value",
        "other_cookie": "value"
    },
    "csrf_token": "your_csrf_token"
}
```

2. Run the tool with your cookies:
```bash
python main.py cookies.json
```

### 3. Automatic Account Creation

If you don't provide cookies, the tool will:
1. Create a new account automatically
2. Save account details to `account_cookies.json`
3. Use the account for future runs

### 4. Customization Options

#### Retry Behavior
In `main.py`, modify the retry parameters:
```python
max_retries = 2  # Number of retry attempts
time.sleep(2)    # Delay between retries
```

#### Test Mode
Enable test mode in `main.py`:
```python
test_mode = True  # Set to True for testing
```

Test mode will:
- Not submit the ones which are already solved and saved in solutions.json
- Skip actual submissions
- Log all actions

#### Email Domains
In `register.py`, modify the email domains:
```python
domains = ["rescueteam.com", "fastmail.com", "protonmail.com", "tmail.com"]
```

#### Request Handling
In `register.py`, modify the request settings:
```python
self.session = requests.Session(impersonate="chrome131" if os.name == "posix" else "chrome124")
```

#### Solution Cache
Solutions are cached in `solutions.json`. You can:
- Clear the cache by deleting the file
- Modify cache behavior in `solutions.py`
- Change cache file location in `solutions.py`

#### Logging
In `main.py`, modify logging levels:
```python
import structlog
log = structlog.get_logger(__name__)
```

#### Challenge Processing
In `main.py`, modify processing parameters:
```python
max_workers = 5  # Number of concurrent workers
challenge_batch_size = 10  # Number of challenges to process in parallel
```

#### AI Model
In `utils/ai.py`, modify the AI model:
```python
response = self.client.chat.completions.create(
    model="qwen-2.5-coder-32b", # you can change it if you want to
    messages=[{"role": "user", "content": prompt}],
    web_search=False,
)
```

## Technical Overview

- Concurrent challenge processing with ThreadPoolExecutor
- Structured logging with structlog
- Cookie-based session management with CSRF token handling
- Solution caching with JSON persistence
- AI-powered solution generation with retry mechanisms
- Challenge information extraction and parsing
- Automated submission with error handling
- Multi-contest support with dynamic URL parsing
- Comprehensive error tracking and statistics

## Project Structure
```
hackerrank-automated/
├── main.py              # Core application logic
├── requirements.txt     # Dependencies
├── solutions.json       # Solution cache
├── account_cookies.json # Session data
└── utils/              # Core modules
    ├── register.py     # Account management
    ├── fetch.py        # Challenge retrieval
    ├── submit.py       # Solution submission
    ├── ai.py          # AI integration
    ├── parse.py       # Challenge parsing
    ├── solutions.py   # Cache management
    └── getchallenge.py # Data retrieval
```

## License

MIT License

## Disclaimer

This tool is for educational purposes only. Use in accordance with HackerRank's terms of service.