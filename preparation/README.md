# Preparation for training data

1. Download public repos.
    python gh_crawler.py python
    python gh_crawler.py java
2. Extract all file pairs.
    ./mine_code_test_pairs_python.sh python-top-repos.txt 2>&1 | tee output_python-top-repos.txt
    ./mine_code_test_pairs_java.sh java-top-repos.txt 2>&1 | tee output_java-top-repos.txt
3. Extract focal context for each method.
    sh extract_contextual_information_for_method.sh python PROJ_PATH
    sh extract_contextual_information_for_method.sh java PROJ_PATH

4. Download CodeSearchData if needed
    https://huggingface.co/datasets/code_search_net

5. Generate dataset for AD tasks' fine-tuning (Method-test dataset) and TDD tasks' fine-tuning(Docstring-method-test dataset).
    python generate_ft_data.py python PROJ_PATH/output/java/method_with_focal_context PROJ_PATH/output/python/finetune-dataset/conversation PROJ_PATH/data/codesearchnet/source_data/python PROJ_PATH/scripts/test_python.txt
    python generate_ft_data.py java PROJ_PATH/output/java/method_with_focal_context PROJ_PATH/output/java/finetune-dataset/conversation PROJ_PATH/data/codesearchnet/source_data/java PROJ_PATH/scripts/test_java.txt
    
6. Fine-tuning Dataset is available at our Huggingface space.
    https://huggingface.co/Arain