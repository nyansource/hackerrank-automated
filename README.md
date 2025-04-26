# HackerRank Automated Challenge Solver

An automated tool that solves HackerRank coding challenges using AI. This tool can automatically register accounts, fetch challenges, generate solutions, and submit them to HackerRank.

## Features

- 🔄 Automatic account registration
- 🤖 AI-powered solution generation
- 📝 Solution caching and reuse
- 🔍 Challenge information extraction
- ✅ Automatic submission and verification
- 🔐 Cookie-based session management
- 📊 Detailed logging and statistics

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nyansource/hackerrank-automated.git
cd hackerrank-automated
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

To run the tool with automatic account creation:
```bash
python main.py
```

### Using Existing Account

To use an existing account with cookies:
```bash
python main.py path/to/cookies.json
```

The cookies.json file should be in the following format:
```json
{
    "username": "your_username",
    "email": "your_email",
    "password": "your_password",
    "cookies": {
        "nsi": "your_cookie_value",
        "other_cookie": "value"
    },
    "csrf_token": "your_csrf_token"
}
```

## How It Works

1. **Account Management**:
   - Creates a new account if no cookies are provided
   - Uses existing account if cookies are provided
   - Saves account information for future use

2. **Challenge Processing**:
   - Fetches available challenges from specified contests
   - Extracts challenge information and requirements
   - Checks for existing solutions in the cache

3. **Solution Generation**:
   - Uses AI to generate solutions for challenges
   - Handles multiple programming languages
   - Implements retry mechanism for failed solutions

4. **Submission and Verification**:
   - Submits solutions to HackerRank
   - Verifies submission status
   - Handles various error cases (Wrong Answer, Runtime Error, etc.)

## File Structure

```
hackerrank-automated/
├── main.py              # Main entry point
├── requirements.txt     # Project dependencies
├── solutions.json       # Cached solutions
├── account_cookies.json # Saved account information
└── utils/
    ├── register.py      # Account registration
    ├── fetch.py         # Challenge fetching
    ├── submit.py        # Solution submission
    ├── ai.py           # AI solution generation
    ├── parse.py        # Challenge parsing
    ├── solutions.py    # Solution management
    └── getchallenge.py # Challenge retrieval
```

## Configuration

You can modify the following in `main.py`:
- Contest list: Add or remove contest slugs
- Retry attempts: Adjust max_retries for solution generation
- Test mode: Enable/disable test mode for debugging

## Logging

The tool uses structured logging to provide detailed information about:
- Account creation and management
- Challenge processing
- Solution generation and submission
- Error handling and retries

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Please use it responsibly and in accordance with HackerRank's terms of service. 

## PS
I just made it for my college assignment automation cause i was lazy to manually do those :3