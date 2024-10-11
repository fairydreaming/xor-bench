#!/usr/bin/env python3

import codecs
import random
import sys

DEFAULT_PROMPT = """Given the following boolean variables:
$QUIZ_VARIABLES
Evaluate the boolean expression: $QUIZ_FORMULA
Do not write any computer programs, evaluate the expression by yourself.
If the evaluation result is True, output this text: '<ANSWER>True</ANSWER>'.
If the evaluation result is False, output this text: '<ANSWER>False</ANSWER>'."""

def generate_variable_name(index):
    return f"x_{index}"

def generate_boolean_expression(num_vars):
    variables = []
    expression = ""
    for i in range(1, num_vars + 1):
        if i > 1:
            expression += " xor "
        variable_name = generate_variable_name(i)
        variable_value = random.choice([True, False])
        variables.append(f"{variable_name} = {variable_value}")
        is_negated = random.choice([True, False])
        if is_negated:
            expression += "not "
        expression += variable_name

    return variables, expression

def generate_quiz(quiz_variables, quiz_expression, prompt=DEFAULT_PROMPT, shuffle=False):
    if shuffle:
        random.shuffle(quiz_variables)

    quiz = prompt
    quiz = quiz.replace("$QUIZ_VARIABLES", "\n".join(quiz_variables).strip())
    quiz = quiz.replace("$QUIZ_FORMULA", quiz_expression.strip())
    return quiz

def generate_quizzes(length, num_quizzes=10, prompt=DEFAULT_PROMPT, shuffle=False, seed=None):
    if seed is not None:
        random.seed(seed)
    print(f"Boolean expressions with {length} variables", file=sys.stderr)
    for _ in range(num_quizzes):
        variables, expression = generate_boolean_expression(length)
        exec("\n".join(variables))
        expression_python = " ^ ".join(map(lambda v: "("+v+")", expression.split(" xor ")))
        correct_answer = eval(expression_python)
        quiz = generate_quiz(variables, expression, prompt, shuffle)
        yield (length, correct_answer , quiz)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--length", help = "Number of boolean variables.", type=int, required=True)
    parser.add_argument("-p", "--prompt", help = "Prompt template of the quiz. The default prompt template is: " + repr(DEFAULT_PROMPT), default=DEFAULT_PROMPT)
    parser.add_argument("-s", "--shuffle", help = "Shuffle the order of boolean variable values in the quiz.", action="store_true")
    parser.add_argument("-n", "--number", help = "Number of generated quizzes.", default=10, type=int)
    parser.add_argument("-r", "--seed", help = "Random seed value", default=None, type=int)
    args = parser.parse_args()

    prompt = codecs.escape_decode(bytes(args.prompt, "utf-8"))[0].decode("utf-8")

    for level, correct_answer, quiz in generate_quizzes(args.length, args.number, prompt, args.shuffle, args.seed):
        print(f"{level},{correct_answer},{repr(quiz)}")
 
