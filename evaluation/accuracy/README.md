1. Extract filepairs for evaluation
    python get_repo.py java java_filepairs.json
    python get_repo.py python python_filepairs.json

2. Extract focal context for method
    sh extract_contextual_information_for_method.sh java
    sh extract_contextual_information_for_method.sh python

3. Generate prompts for evaluation
    python generate_evaluate_data.py java PROJ_PATH/evaluation/accuracy/method_with_focal_context/java PROJ_PATH/evaluation/accuracy/prompts/java PROJ_PATH/evaluation/accuracy/TestFiltering/test_exec_filtered.json
    python generate_evaluate_data.py python PROJ_PATH/evaluation/accuracy/method_with_focal_context/python PROJ_PATH/evaluation/accuracy/prompts/python PROJ_PATH/evaluation/accuracy/TestFiltering/test_exec_filtered.json

4. Generate answers for each model.
    models = {cat-lm, chatgpt3.5, codellama, deepseek-7b, deepseek-33b, gpt4, ut-lm-java-7b, ut-lm-java-33b, ut-lm-python-7b, ut-lm-python-33b, ut-lm-multi-7b, ut-lm-multi-33b, ut-lm-single-7b, ut-lm-single-33b, ut-lm-python-java-7b, ut-lm-python-java-33b, wizardcoder}
    
    CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.api_server --model model_path --host=0.0.0.0 --port 8888 --max-model-len=8192
    
5. Run answers for each model
    {model}
        python generate_answer.py ../prompts/java/single_unit_test.json ../promptsOutput/java {model}
        python generate_answer.py ../prompts/python/single_unit_test.json ../promptsOutput/python {model}
        python generate_answer.py ../prompts/java/multi_unit_test.json ../promptsOutput/java {model}
        python generate_answer.py ../prompts/python/multi_unit_test.json ../promptsOutput/python {model}

6. Clean and extract code from generated answers
    sh clean_answers.sh ../promptsOutput/python/{model}

7. Compile, test, and run coverage
    {model}
        Assume in java8maven/java17maven/java8gradle/python38/python310 image
        python run_python_repo.py PROJ_PATH/evaluation/accuracy/promptsOutput/python/{model}/single_unit_test_cleaned.json PROJ_PATH/evaluation/accuracy/promptsOutput/python/model/single_unit_test_cleaned_with_result.json PROJ_PATH/evaluation/accuracy/RawData/python
        python run_java_repo.py PROJ_PATH/evaluation/accuracy/promptsOutput/java/{model}/single_unit_test_cleaned.json PROJ_PATH/evaluation/accuracy/TestResults/java/{model}/single_unit_test_cleaned_with_result.json PROJ_PATH/evaluation/accuracy/RawData/java

8. Stastic
    {model}
        python generate_evaluate_data.py ../promptsOut/java/{model} ../TestResults/java/{model}
        python generate_evaluate_data.py ../promptsOut/python/{model} ../TestResults/python/{model}






