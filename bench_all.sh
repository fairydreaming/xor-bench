#!/bin/bash

for model in "deepseek/deepseek-chat" "qwen/qwen-2.5-72b-instruct" "google/gemma-2-27b-it" "google/gemini-pro-1.5" "meta-llama/llama-3.1-70b-instruct" "meta-llama/llama-3.1-405b-instruct" "mistralai/mistral-large" "anthropic/claude-3.5-sonnet" "anthropic/claude-3-opus" "openai/gpt-4" "openai/gpt-4o" "openai/o1-mini" "openai/o1-preview"
do
	echo "$model"
	./bench_model.sh "$model"
done
