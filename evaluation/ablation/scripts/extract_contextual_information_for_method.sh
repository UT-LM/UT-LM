#/bin/bash

PROJ_PATH=$2
language=$1

file_path=$PROJ_PATH/evaluation/ablation/RawDataOutput/$language/FilePairs/
output_path=$PROJ_PATH/evaluation/ablation/method_with_focal_context/$language
repo_path=$PROJ_PATH/evaluation/ablation/RawData/$language/

mkdir -p $output_path


# 查找所有的 .json 文件并使用 xargs 并行处理
if [ "$language" = "java" ]; then
find "$file_path" -type f -name '*.json' | xargs -P 80 -I {} bash -c ' \
    filename=$(basename {}); \
    output_file='"$output_path"'/$(basename {} .json).jsonl; \
    echo "处理JSON文件: $filename"; \
    timeout 28800s docker run -v /cpfs/29a75185021b187f/aigccode/user:/cpfs/29a75185021b187f/aigccode/user ut_java java -jar '"$PROJ_PATH"'/evaluation/scripts/java-1.0.0-jar-with-dependencies.jar /testunit {} $output_file '"$repo_path"'; \
    echo "文件处理完成: $filename"; \
    echo "文件处理完成: $filename" >> '"$output_path"'.txt; \
    '
fi

if [ "$language" = "python" ]; then
find "$file_path" -type f -name '*.json' | xargs -P 80 -I {} bash -c ' \
    filename=$(basename {}); \
    output_file='"$output_path"'/$(basename {} .json).jsonl; \
    echo "处理JSON文件: $filename"; \
    timeout 28800s docker run -v /cpfs/29a75185021b187f/aigccode/user:/cpfs/29a75185021b187f/aigccode/user ut_python java -jar '"$PROJ_PATH"'/evaluation/scripts/python-1.0.0-jar-with-dependencies.jar /unittest {} $output_file '"$repo_path"'; \
    echo "文件处理完成: $filename"; \
    echo "文件处理完成: $filename" >> '"$output_path"'.txt; \
    '
fi