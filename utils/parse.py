import json
import re


def extract_challenge_info(json_data):
    """
    Extract key information from a HackerRank challenge JSON response.
    Only keeps essential information needed for solving the challenge.
    """
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    if "model" in data:
        data = data["model"]
    
    priority_languages = ["c", "java"]
    languages = data.get("languages", [])
    
    if isinstance(languages, list) and languages:
        for language in priority_languages:
            if language in languages:
                selected_language = language
                break
        else:
            selected_language = languages[0]
    elif isinstance(languages, str):
        selected_language = languages
    else:
        selected_language = "c"

    challenge_info = {
        "name": data.get("name", ""),
        "slug": data.get("slug", ""),
        "difficulty": data.get("difficulty_name", ""),
        "problem_statement": data.get("problem_statement", ""),
        "input_format": data.get("input_format", ""),
        "output_format": data.get("output_format", ""),
        "constraints": data.get("constraints", ""),
        "languages": selected_language,
        "template": data.get(f"{selected_language}_template", ""),
        "test_weights": data.get("test_weights", None),
        "compile_and_test": data.get("compile_and_test", True),
        "custom_case": data.get("custom_case", False),
        "body_html": data.get("body_html", ""),
        "public_test_cases": data.get("public_test_cases", True),
    }
    sample_testcases = []
    if "sample_testcases" in data and data["sample_testcases"]:
        for test in data["sample_testcases"]:
            sample_testcases.append({
                "input": test.get("raw_input", ""),
                "output": test.get("raw_output", "")
            })
    
    challenge_info["sample_testcases"] = sample_testcases
    
    return challenge_info