# HackerRank Automated Challenge Solver

A high-performance automation tool for solving HackerRank coding challenges. Built with Python, this tool leverages AI to generate and submit solutions while maintaining session state and caching mechanisms.
I made it as was lazy to manually do that. 

## Contact

For questions, issues, or contributions:
- Email: nyansourcesigma@gmail.com

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

## System Requirements

- Python 3.8+
- pip
- Internet connection
- HackerRank account (optional)

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

### 4. Customizing Retry Behavior

In `main.py`, modify the retry parameters:
```python
max_retries = 2  # Number of retry attempts
time.sleep(2)    # Delay between retries
```

### 5. Test Mode

Enable test mode in `main.py`:
```python
test_mode = True  # Set to True for testing
```

Test mode will:
- Not submit the ones which are already solved and saved in solutions.json
- Skip actual submissions
- Log all actions

### 6. Solution Cache

Solutions are cached in `solutions.json`. 

### 7. Error Handling

The tool handles various errors:
- Wrong answers
- Runtime errors
- Compilation errors
- Timeouts
- Network issues

Each error triggers a retry with error-specific solution generation.

### 8. Logging

Logs are structured and include:
- Challenge processing status
- Solution generation attempts
- Submission results
- Error details

## Core Components

### Main Module (`main.py`)
- Entry point for the application
- Manages contest processing and challenge solving
- Handles account creation and session management
- Implements retry logic for failed submissions
- Supports multiple contest URLs (e.g., "100dayscodingchallenge", "java-mystery-phase-1")
- Dynamic contest URL parsing from HackerRank URLs
- Challenge statistics tracking (solved, failed, reused)
- Comprehensive error handling and logging

### Utility Modules
- `register.py`: Account registration and management
- `fetch.py`: Challenge retrieval and parsing
- `submit.py`: Solution submission and verification
- `ai.py`: AI solution generation
- `parse.py`: Challenge information extraction
- `solutions.py`: Solution caching and management
- `getchallenge.py`: Challenge data retrieval

## Usage

### Basic Execution
```bash
python main.py
```

### Using Existing Account
```bash
python main.py path/to/cookies.json
```

### Cookie Format
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "cookies": {
        "cookie1": "string",
        "other_cookie": "string"
    },
    "csrf_token": "string"
}
```

## Technical Implementation

### Contest Management
- Supports multiple contest URLs
- Extracts contest slugs from full HackerRank URLs
- Example contest URLs:
  - https://www.hackerrank.com/100dayscodingchallenge
  - https://www.hackerrank.com/java-mystery-phase-1
- Sequential contest processing with error isolation

### Session Management
- Automatic account registration if no cookies provided
- Cookie persistence in `account_cookies.json`
- CSRF token handling for secure submissions
- Session state maintenance across requests
- Cookie validation and error handling
- Support for multiple account configurations

### Challenge Processing
1. Fetches available challenges from specified contests
2. Extracts challenge information and requirements
3. Checks solution cache for existing implementations
4. Generates new solutions using AI if needed
5. Submits solutions with error handling
6. Implements retry mechanism for failed submissions
7. Tracks challenge statistics (solved, failed, reused)

### Error Handling
- Compilation errors
- Runtime errors
- Wrong answers
- Timeout issues
- Network errors
- Cookie validation errors
- JSON parsing errors
- Challenge fetch errors
- Solution generation failures
- Submission failures

### Performance Optimizations
- Solution caching to avoid redundant generation
- Concurrent processing of challenges
- Efficient session management
- Structured logging for debugging
- Cookie persistence for faster subsequent runs
- Retry mechanism with configurable attempts
- Error-based solution regeneration

## Configuration

Modify `main.py` to adjust:
- Contest list (add contest slugs from HackerRank URLs)
- Retry attempts (default: 2)
- Test mode (default: False)
- Logging levels
- Challenge processing parameters

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
