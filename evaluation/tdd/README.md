# TDD Experiment

## 1. Generate prompt
    python generate_evaluate_data.py java PROJ_PATH/evaluation/tdd/RawData/java/data_java_data_humaneval.jsonl PROJ_PATH/evaluation/tdd/prompts/java

    python generate_evaluate_data.py python PROJ_PATH/evaluation/tdd/RawData/python/data_python_data_humaneval.jsonl PROJ_PATH/evaluation/tdd/prompts/python

## 2. LLM serving via vLLM.
    models = {cat-lm, chatgpt3.5, codellama, deepseek-7b, deepseek-33b, gpt4, ut-lm-python-java-7b, ut-lm-python-java-33b, wizardcoder}
    
    for model in models:
        CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.api_server --model model_path --host=0.0.0.0 --port 8888 --max-model-len=8192

## 3. Generate answers for each model.
    for model in models:
        python generate_answer.py ../prompts/java/tdd.json ../promptsOutput/java {model}
        python generate_answer.py ../prompts/python/tdd.json ../promptsOutput/python {model}

## 4. Clean and extract code from generated answers
    for model in models:
        sh clean_answers.sh ../promptsOutput/python/{model}

## 5. Compile, test, and run coverage
    for model in models:
        python run_python.py PROJ_PATH/evaluation/tdd/promptsOutput/python/{model}/tdd_cleaned.json 
        python run_java.py PROJ_PATH/evaluation/tdd/promptsOutput/java/{model}/tdd_cleaned.json

## 6. Statistics
    for model in models:
        python generate_evaluate_data.py ../promptsOut/java/{model} ../TestResults/java/{model}
        python generate_evaluate_data.py ../promptsOut/python/{model} ../TestResults/python/{model}
