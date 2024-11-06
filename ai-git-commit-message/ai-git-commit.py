#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import requests

# Constants
# gc-logs means ai based git commit message logs
STARSHIP_LOGS = os.path.expanduser("~/.config/starship/gc-logs")
CACHE_FILE = os.path.join(STARSHIP_LOGS, "ai-commit-cache")
LAST_RESPONSE_LOG = os.path.join(STARSHIP_LOGS, "last-openai-response.log")
REQUEST_LOG = os.path.join(STARSHIP_LOGS, "openai-request-payload.log")
OPEN_API_KEY_PATH = os.path.expanduser("~/.ssh/openai-api-key")
GEMINI_API_KEY_PATH = os.path.expanduser("~/.ssh/gemini-api-key")


MODEL_DESCRIPTIONS = {
    "gpt-3.5-turbo": "Fastest and most cost-effective model.",
    "gpt-4": "More capable model, better for complex tasks.",
    "gpt-4-turbo": "Most advanced model for demanding applications.",
    "gemini": "Google's Gemini model for generative tasks.",
}

DEFAULT_MODEL = "gemini"
#DEFAULT_MODEL = "gpt-3.5-turbo"
#DEFAULT_MODEL = "crosshatch-model"
MODEL = DEFAULT_MODEL  # Pre-set this model

# Load API key
def load_api_key(key_type='OPENAI_API_KEY'):
    api_key_path = OPEN_API_KEY_PATH if key_type == 'OPENAI_API_KEY' else GEMINI_API_KEY_PATH
    try:
        with open(api_key_path) as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: API key not found at {api_key_path}.")
        return None

# Log to file
def log_to_file(log_file_path, content, mode="w"):
    with open(log_file_path, mode) as log_file:
        log_file.write(content)

# Git operations
def run_git_command(command):
    return subprocess.check_output(command).decode("utf-8").strip()

def is_git_repo():
    return run_git_command(["git", "rev-parse", "--is-inside-work-tree"]) is not None

def has_staged_changes():
    try:
        subprocess.check_call(["git", "diff", "--staged", "--quiet"])
        return False
    except subprocess.CalledProcessError:
        return True

def get_staged_files():
    return run_git_command(["git", "diff", "--name-only", "--cached"]).splitlines()

def get_file_diff(file):
    return run_git_command(["git", "diff", "--cached", file])

def commit_changes(commit_message):
    subprocess.run(["git", "commit", "-m", commit_message])

# OpenAI API Interaction
def send_request_to_openai(prompt, model):
    api_key = load_api_key('OPENAI_API_KEY')
    if not api_key:
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200,
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    print(f"Error: OpenAI API request failed with status {response.status_code}")
    return None

# Google Gemini API Interaction
def send_gemini_request(prompt):
    gemini_api_key = load_api_key('GEMINI_API_KEY')
    if not gemini_api_key:
        print("Gemini API key not found.")
        return None

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    # Correctly append the API key to the URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_api_key}"

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        return response.json()
    except requests.HTTPError as e:
        logging.error(f"Gemini API request failed: {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

# Logging
def log_request(prompt, model):
    content = f"Model: {model}\nPrompt: {prompt}\n"
    log_to_file(REQUEST_LOG, content)

def log_response(response):
    content = json.dumps(response, indent=4)
    log_to_file(LAST_RESPONSE_LOG, content)

# User Interaction
def prompt_commit_message(suggestions, model):
    # Filter out empty messages
    filtered_suggestions = [msg for msg in suggestions if msg.strip()]

    if not filtered_suggestions:
        print("No valid commit messages generated.")
        return ""

    print("Select a commit message:")

    # Customize the message format based on the selected model
    if model == 'gpt-3.5-turbo':
        print("Suggestions generated using the GPT-3.5 Turbo model:")
    elif model == 'gpt-4':
        print("Suggestions generated using the GPT-4 model:")
    elif model == 'gpt-4-turbo':
        print("Suggestions generated using the GPT-4 Turbo model:")
    elif model == 'gemini':
        print("Suggestions generated using the Gemini model:")

    sys.stdout = open("/dev/tty", "w")
    for i, message in enumerate(filtered_suggestions, 1):
        print(f"{i}. {message}")
    print(f"{len(filtered_suggestions) + 1}. Enter custom message")

    sys.stdin = open("/dev/tty")

    while True:
        user_input = input("Choose a commit message (or enter number): ").strip()
        if user_input.isdigit() and 1 <= int(user_input) <= len(filtered_suggestions):
            return filtered_suggestions[int(user_input) - 1]
        if user_input == str(len(filtered_suggestions) + 1):
            custom_message = input("Enter your custom commit message: ").strip()
            if custom_message:
                return custom_message
            print("Custom message cannot be empty.")

# Fetch commit messages
def get_commit_messages(diff_output, model):
    prompt = f"Generate 3 commit messages for the following git diff:\n{diff_output}\nProvide only the messages."
    log_request(prompt, model)

    if model == 'gemini':
        response = send_gemini_request(prompt)
    else:
        response = send_request_to_openai(prompt, model)

    if response:
        log_response(response)
        # Update this line to correctly parse the response from Gemini
        if model == 'gemini':
            commit_messages = response['candidates'][0]['content']['parts'][0]['text']
        else:
            commit_messages = response.get("choices", [{}])[0].get("message", {}).get("content", "")

        return commit_messages.strip().split("\n")
    return ["Failed to generate commit messages. Please try again."]

def push_changes():
    try:
        # Get the current branch name
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')

        # Push the changes to the current branch
        subprocess.run(['git', 'push', 'origin', branch], check=True)
        print("Push successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error during push: {e}")
        sys.exit(1)

# AI Git Commit Process
def ai_git_commit():
    global DEFAULT_MODEL
    if not is_git_repo():
        print("Error: Not inside a Git repository.")
        return
    if not has_staged_changes():
        print("No staged changes to commit.")
        return

    staged_files = get_staged_files()
    if not staged_files:
        print("No staged files found.")
        return

    all_suggestions = {}

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(get_commit_messages, get_file_diff(file), DEFAULT_MODEL): file for file in staged_files}
        for future in futures:
            file = futures[future]
            all_suggestions[file] = future.result()

    commit_messages = {}
    for file, suggestions in all_suggestions.items():
        print(f"\nFile: {file}")
        commit_message = prompt_commit_message(suggestions, DEFAULT_MODEL)
        commit_messages[file] = commit_message

    for file, message in commit_messages.items():
        commit_changes(f"{message} [{file}]")

    push_changes()

if __name__ == "__main__":
    ai_git_commit()
