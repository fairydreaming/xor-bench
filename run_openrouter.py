#!/usr/bin/env -S python3 -u

import re
import os
import csv
import sys
import time
import codecs
import argparse
import subprocess
from collections import defaultdict
from openai import OpenAI

DEFAULT_SYSTEM_PROMPT="You are a reasoning engine designed to evaluate complex Boolean expressions with step-by-step explanations. Your task is to break down each Boolean expression into smaller components, explain how each part works, and show how the overall expression simplifies to a final result. Use logical reasoning and the basic rules of Boolean algebra (AND, OR, NOT, XOR, etc.) to solve the problem. Always start by parsing the expression, then follow a chain-of-thought reasoning process to ensure clarity."

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", help="OpenAI model name.", required=True)
parser.add_argument("-s", "--system-prompt", help="Use given system prompt. Can be either a system prompt text or a path to a text file containing the system prompt. By default, the system prompt is not used. When this option is passed without a value, the default system prompt value is used: " + repr(DEFAULT_SYSTEM_PROMPT), const=DEFAULT_SYSTEM_PROMPT, default=None, nargs='?')
parser.add_argument("-d", "--delay", help="Delay in seconds between API calls", default=None, type=int)
args = parser.parse_args()
model_name = args.model
system_prompt = args.system_prompt
delay = args.delay

if system_prompt is not None and os.path.isfile(system_prompt):
    with open(system_prompt, 'r', encoding='utf-8') as file:
        system_prompt = file.read()

quiz_reader = csv.reader(sys.stdin, delimiter=',', quotechar='"')

correct_answers = defaultdict(lambda: 0)
incorrect_answers = defaultdict(lambda: 0)
missing_answers = defaultdict(lambda: 0)
all_answers = defaultdict(lambda: 0)

for label, correct_answer, quiz in quiz_reader:
    quiz = codecs.escape_decode(bytes(quiz, "utf-8"))[0].decode("utf-8")

    system_messages=[{"role": "system", "content": system_prompt }]
    messages=[{"role": "user", "content": quiz }]
    if system_prompt is not None:
        messages = system_messages + messages
    print(messages)
    while True:
        try:
            response = client.chat.completions.create(model=model_name, messages=messages, temperature=0.01, seed=42)
            break;
        except Exception as ex:
            print(f"Caught exception: {ex}, retrying after 60s", file=sys.stderr)
            time.sleep(60)

    model_response = response.choices[0].message.content if response.choices else ""
    print(model_response)

    all_answers[label] += 1
    matches = re.findall(r'<ANSWER>(.*?)</ANSWER>', model_response)
    if matches:
        if correct_answer == matches[0].strip():
            correct_answers[label] += 1
        else:
            incorrect_answers[label] += 1
    else:
        missing_answers[label] += 1

    if delay is not None:
        time.sleep(delay)

for label in all_answers.keys():
    num_correct = correct_answers[label]
    num_incorrect = incorrect_answers[label]
    num_missing = missing_answers[label]
    num_all = all_answers[label]
    percent_correct = 100 * num_correct / num_all
    print(f"{label}: {percent_correct:.2f} (C: {num_correct}, I: {num_incorrect}, M: {num_missing} A: {num_all})")
