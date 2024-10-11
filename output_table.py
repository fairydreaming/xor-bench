#!/usr/bin/env -S python3 -u

import os
import re
import pandas as pd

# List of predefined model authors
model_authors = ['google', 'openai', 'anthropic', 'meta-llama', 'deepseek', 'qwen', 'mistralai']

# Initialize dictionary to store data
data = {}

# Define the path to the results directory
results_dir = './results'

line_pattern = re.compile(r'^(\d+):\s*([\d.]+)')

# Traverse through the directory and read the log files
for root, dirs, files in os.walk(results_dir):
    for file in files:
        # Only process .log files
        if file.endswith('.log'):
            # Extract information from the file path
            relative_path = os.path.relpath(os.path.join(root, file), results_dir)
            path_parts = relative_path.split(os.sep)

            # Extract problem length (as the first part of the path)
            problem_length = int(path_parts[0])

            # Split the filename into model_author and model_name
            file_name = path_parts[1].replace('.log', '')

            # Find which model author the file belongs to
            model_author = None
            for author in model_authors:
                if file_name.startswith(author):
                    model_author = author
                    break

            if model_author is None:
                print(f"Unknown model author in file: {file_name}")
                continue

            # Extract model name (everything after the model author)
            model_name = file_name[len(model_author) + 1:]  # Skip the author and hyphen

            # Initialize a dictionary entry for the model if it doesn't exist
            if (model_author, model_name) not in data:
                data[(model_author, model_name)] = {}

            # Open the log file and read the last line
            with open(os.path.join(root, file), 'r') as log_file:
                lines = log_file.readlines()
                if lines:
                    last_line = lines[-1].strip()

                    # Use regex to extract the problem length and accuracy
                    match = line_pattern.match(last_line)
                    if match:
                        last_problem_length = int(match.group(1))
                        accuracy = float(match.group(2))

                        # Ensure problem length matches the extracted one
                        if last_problem_length == problem_length:
                            # Store accuracy in the dictionary with problem_length as key
                            data[(model_author, model_name)][problem_length] = accuracy
                    else:
                        print(f"Error parsing the last line in {file}: {last_line}")

# Convert dictionary to pandas DataFrame
df = pd.DataFrame.from_dict(data, orient='index')

# Reset index to get 'model_author' and 'model_name' as columns
df.reset_index(inplace=True)
df.rename(columns={'level_0': 'model_author', 'level_1': 'model_name'}, inplace=True)

# Sort the DataFrame columns, ordering the problem length columns from smallest to largest
# Column names are model_author, model_name, and problem lengths, so we order the latter
problem_length_columns = sorted(df.columns[2:], key=int)  # Sort problem length columns as integers
df = df[['model_author', 'model_name'] + problem_length_columns]  # Reorder the DataFrame columns

# Sort the DataFrame by columns (problem lengths), treating NA values as lower
df = df.sort_values(by=list(df.columns[2:]), na_position='last', ascending=False)

# Output the DataFrame in markdown format
print(df.to_markdown(index=False))
