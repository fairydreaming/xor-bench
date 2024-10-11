# xor-bench
Can LLMs calculate XOR?

This project is a way to vent my frustrations resulting from trying to use large language models to reliably solve problems.
After rewriting my prompts a hundred times, I asked myself: Can large language models reliably solve even the simplest possible problem of arbitrary length?
(assuming it fits in the context window)

## The XOR problem

The problem that LLMs are supposed to solve in this benchmark is to evaluate a boolean expression:

```[NOT] x_1 XOR [NOT] x_2 XOR [NOT] x_3 XOR ... XOR [NOT] x_n```

`[NOT]` means that negation is optional. Whether a variable will be negated or not is random.
The values of the variables are also random.

I decided to base the problem on boolean logic to avoid calculating numbers - we all know that large language models are bad at this.
I chose the XOR function because it allows to construct boolean expressions in which the result depends on the value of each variable.
Additionally, I decided to use NOT so that the result also depends on the correct interpretation of the order of arguments in the boolean expression.

Example generated prompt:

```
Given the following boolean variables:
x_1 = True
x_2 = False
x_3 = False
x_4 = True
x_5 = False
x_6 = False
x_7 = False
x_8 = True
Evaluate the boolean expression: not x_1 xor x_2 xor x_3 xor x_4 xor x_5 xor x_6 xor x_7 xor not x_8
Do not write any computer programs, evaluate the expression by yourself.
If the evaluation result is True, output this text: '<ANSWER>True</ANSWER>'.
If the evaluation result is False, output this text: '<ANSWER>False</ANSWER>'.
```

Initially I wanted to avoid using variables and directly use True/False in boolean expressions.
Unfortunately, this causes many models to enter an infinite generation loop.

## Results

Here are some initial results of my benchmark. None of the tested models is able to solve this problem for an arbitrary number of variables.
The numbers in the table header represent the number of variables in the boolean expression.
The numbers in table rows represent accuracy of the model in solving the task.
I didn't check a higher number of variables if a given model couldn't reliably solve the task for a lower number of variables, these table cells have N/A inside.

| model author   | model name              |   2 |   4 |   8 |   16 |   32 |   64 |   128 |
|:---------------|:------------------------|----:|----:|----:|-----:|-----:|-----:|------:|
| openai         | o1-mini                 | 100 | 100 | 100 |  100 |  100 |  100 |    80 |
| google         | gemini-pro-1.5          | 100 | 100 | 100 |  100 |   70 |  N/A |   N/A |
| deepseek       | deepseek-chat           | 100 | 100 | 100 |   90 |  N/A |  N/A |   N/A |
| anthropic      | claude-3-opus           | 100 | 100 | 100 |   80 |  N/A |  N/A |   N/A |
| meta-llama     | llama-3.1-405b-instruct | 100 | 100 | 100 |   70 |  N/A |  N/A |   N/A |
| openai         | o1-preview              | 100 | 100 |  90 |  N/A |  N/A |  N/A |   N/A |
| qwen           | qwen-2.5-72b-instruct   | 100 | 100 |  90 |  N/A |  N/A |  N/A |   N/A |
| mistralai      | mistral-large           | 100 | 100 |  90 |  N/A |  N/A |  N/A |   N/A |
| anthropic      | claude-3.5-sonnet       | 100 | 100 |  90 |  N/A |  N/A |  N/A |   N/A |
| openai         | gpt-4o                  | 100 | 100 |  90 |  N/A |  N/A |  N/A |   N/A |
| meta-llama     | llama-3.1-70b-instruct  | 100 |  90 | N/A |  N/A |  N/A |  N/A |   N/A |
| google         | gemma-2-27b-it          | 100 |  90 | N/A |  N/A |  N/A |  N/A |   N/A |
| openai         | gpt-4                   |  80 | N/A | N/A |  N/A |  N/A |  N/A |   N/A |

There are only 10 iterations for each problem length, hence full tens in the accuracy values.

I'm amazed by the gpt-4 that is basically worthless for this task. Marvin Minsky is turning over in his grave.[^1]

Of course I'm aware that the accuracy can be improved by using some prompting techniques.
Here are example results for gpt-4 and mistral-large with additional system prompt:

| model author | model name    | prompting technique |   2 |   4 |   8 |  16 |  32 |  64 | 128 |
|:-------------|:--------------|---------------------|----:|----:|----:|----:|----:|----:|----:|
| mistralai    | mistral-large | meta prompting      | 100 | 100 | 100 | 100 | 100 | 100 |  70 |
| openai       | gpt-4         | meta prompting      | 100 | 100 | 100 | 100 | 100 | 100 | N/A |
| mistralai    | mistral-large | chain of thought    | 100 | 100 | 100 |  40 | N/A | N/A | N/A |
| openai       | gpt-4         | chain of thought    | 100 | 100 |  90 | N/A | N/A | N/A | N/A |
| mistralai    | mistral-large | none - reference    | 100 | 100 |  90 | N/A | N/A | N/A | N/A |
| openai       | gpt-4         | none - reference    |  80 | N/A | N/A | N/A | N/A | N/A | N/A |

For 128 variables the gpt-4 model answer exceeded available output length, so this result is not available.

While using prompting techniques improves the accuracy, the fundamental problem remains - models still fail for some number of variables.

## Usage

This benchmark includes two Python scripts: `xor_bench.py` and `run_openrouter.py`

To use the benchmark with OpenRouter, set the environment variable `OPENROUTER_API_KEY` to your OpenRouter API key value.
Then execute the scripts like this:

```
./xor_bench.py -l 128 -n 10|./run_openrouter.py -m "qwen/qwen-2.5-72b-instruct"
```

You can modify `run_openrouter.py` to use any OpenAI-like API endpoint by changing the URL in the code.

### xor_bench.py
```
usage: xor_bench.py [-h] -l LENGTH [-p PROMPT] [-s] [-n NUMBER] [-r SEED]

options:
  -h, --help            show this help message and exit
  -l LENGTH, --length LENGTH
                        Number of boolean variables.
  -p PROMPT, --prompt PROMPT
                        Prompt template of the quiz. The default prompt template is: "Given the following boolean
                        variables:\n$QUIZ_VARIABLES\nEvaluate the boolean expression: $QUIZ_FORMULA\nDo not write any computer
                        programs, evaluate the expression by yourself.\nIf the evaluation result is True, output this text:
                        '<ANSWER>True</ANSWER>'.\nIf the evaluation result is False, output this text: '<ANSWER>False</ANSWER>'."
  -s, --shuffle         Shuffle the order of boolean variable values in the quiz.
  -n NUMBER, --number NUMBER
                        Number of generated quizzes.
  -r SEED, --seed SEED  Random seed value
```

### run_openrouter.py
```
usage: run_openrouter.py [-h] -m MODEL [-s [SYSTEM_PROMPT]] [-d DELAY]

options:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        OpenAI model name.
  -s [SYSTEM_PROMPT], --system-prompt [SYSTEM_PROMPT]
                        Use given system prompt. Can be either a system prompt text or a path to a text file containing the system
                        prompt. By default, the system prompt is not used. When this option is passed without a value, the default
                        system prompt value is used: 'You are a reasoning engine designed to evaluate complex Boolean expressions
                        with step-by-step explanations. Your task is to break down each Boolean expression into smaller components,
                        explain how each part works, and show how the overall expression simplifies to a final result. Use logical
                        reasoning and the basic rules of Boolean algebra (AND, OR, NOT, XOR, etc.) to solve the problem. Always
                        start by parsing the expression, then follow a chain-of-thought reasoning process to ensure clarity.'
  -d DELAY, --delay DELAY
                        Delay in seconds between API calls
```

[^1]: Marvin Minsky noticed that perceptrons are unable to learn the XOR function, see https://en.wikipedia.org/wiki/Perceptrons_(book)
