1. Generate prompt
    python generate_evaluate_data.py java PROJ_PATH/evaluation/tdd/RawData/java/data_java_data_humaneval.jsonl PROJ_PATH/evaluation/tdd/prompts/java

    python generate_evaluate_data.py python PROJ_PATH/evaluation/tdd/RawData/python/data_python_data_humaneval.jsonl PROJ_PATH/evaluation/tdd/prompts/python

2. Generate answers for each model.
    models = {cat-lm, chatgpt3.5, codellama, deepseek-7b, deepseek-33b, gpt4, ut-lm-python-java-7b, ut-lm-python-java-33b, wizardcoder}

    {model}
        python generate_answer.py ../prompts/java/tdd.json ../promptsOutput/java {model}
        python generate_answer.py ../prompts/python/tdd.json ../promptsOutput/python {model}

4. Clean and extract code from generated answers
    sh clean_answers.sh ../promptsOutput/python/{model}

5. Compile, test, and run coverage
    {model}
        python run_python.py PROJ_PATH/evaluation/tdd/promptsOutput/python/{model}/tdd_cleaned.json 
        python run_java.py PROJ_PATH/evaluation/tdd/promptsOutput/java/{model}/tdd_cleaned.json

8. Stastic
    {model}
        python generate_evaluate_data.py ../promptsOut/java/{model} ../TestResults/java/{model}
        python generate_evaluate_data.py ../promptsOut/python/{model} ../TestResults/python/{model}
