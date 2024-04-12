#/bin/bash

pro_path=$3
num=$2
language=$1

cd $pro_path/UT-LM/scripts; docker build -t ut-lm .

file_path=$pro_path/UT-LM/data/GitHubMining/RawDataOutput/$language/FilePairs/$num/
output_path=$pro_path/UT-LM/output/$language/method_with_focal_context/$num
repo_path=$pro_path/UT-LM/data/GitHubMining/RawData/$language/

mkdir -p $output_path


if [ "$language" = "java" ]; then
find "$file_path" -type f -name '*.json' | xargs -P 80 -I {} bash -c ' \
    filename=$(basename {}); \
    output_file='"$output_path"'/$(basename {} .json).jsonl; \
    echo "Processing JSON: $filename"; \
    timeout 28800s docker run -v '"$pro_path"':'"$pro_path"' ut-lm java -jar '"$pro_path"'/UT-LM/scripts/java-1.0.0-jar-with-dependencies.jar /testunit {} $output_file '"$repo_path"'; \
    echo "Finished: $filename"; \
    echo "Finished: $filename" >> '"$output_path"'.txt; \
    '
fi

if [ "$language" = "python" ]; then
find "$file_path" -type f -name '*.json' | xargs -P 80 -I {} bash -c ' \
    filename=$(basename {}); \
    output_file='"$output_path"'/$(basename {} .json).jsonl; \
    echo "Processing JSON: $filename"; \
    timeout 28800s docker run -v '"$pro_path"':$pro_path"' ut-lm java -jar '"$pro_path"'/UT-LM/scripts/python-1.0.0-jar-with-dependencies.jar /unittest {} $output_file '"$repo_path"'; \
    echo "Finished: $filename"; \
    echo "Finished: $filename" >> '"$output_path"'.txt; \
    '
fi