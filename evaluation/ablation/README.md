1. Get python and java repos first released after May 1st, 2023
    python gh_crawler.py python
    python gh_crawler.py java
    
2. Download repos and extract file pairs
    sh mine_code_test_pairs.sh python-evaluate-repos.txt python
    sh mine_code_test_pairs.sh java-evaluate-repos.txt java

3. Extract focal context for each method
    sh extract_contextual_information_for_method.sh java
    sh extract_contextual_information_for_method.sh python

4. Count the number of callees and tests, and exclude that trained in models
    python statistic_method_with_focal_context.py python PROJ_PATH/evaluation/ablation/method_with_focal_context/python PROJ_PATH/evaluation/ablation/method_with_focal_context PROJ_PATH/output/python/method_with_focal_context
    python statistic_method_with_focal_context.py java PROJ_PATH/evaluation/ablation/method_with_focal_context/java PROJ_PATH/evaluation/ablation/method_with_focal_context PROJ_PATH/output/java/method_with_focal_context

5. From the statistical files java.csv and python.csv obtained in step four, filter the data. Select the data where is_training_data=False, callee_num>=3, and single_test_num>=3, and manually move the corresponding failpairs files to the method_with_focal_context_manual_selected folder.

6. Generate new evaluate data from the method_with_focal_context_manual_selected folder for ablation experiments.
    models = {gpt-3.5, gpt-4, ut-lm-33b, ut-lm-7b}
    python generate_evaluate_data.py python PROJ_PATH/evaluation/ablation/method_with_focal_context_manual_selected/python PROJ_PATH/evaluation/ablation/prompts/python
    python generate_evaluate_data.py java PROJ_PATH/evaluation/ablation/method_with_focal_context_manual_selected/java PROJ_PATH/evaluation/ablation/prompts/java

7. Clean and extract code from generated answers
    sh clean_answers.sh ../promptsOutput/python/{model}

8. Compile, test, and run coverage
    {model}
        Assume in java8maven/java17maven/java8gradle/python38/python310 image
        python run_python_repo.py PROJ_PATH/evaluation/accuracy/promptsOutput/python/{model}/single_unit_test_cleaned.json PROJ_PATH/evaluation/accuracy/promptsOutput/python/model/single_unit_test_cleaned_with_result.json PROJ_PATH/evaluation/accuracy/RawData/python
        python run_java_repo.py PROJ_PATH/evaluation/accuracy/promptsOutput/java/{model}/single_unit_test_cleaned.json PROJ_PATH/evaluation/accuracy/TestResults/java/{model}/single_unit_test_cleaned_with_result.json PROJ_PATH/evaluation/accuracy/RawData/java

8. Stastic
    {model}
        python generate_evaluate_data.py ../promptsOut/java/{model} ../TestResults/java/{model}
        python generate_evaluate_data.py ../promptsOut/python/{model} ../TestResults/python/{model}





