#sh evaluate_results.sh ../promptsOutput/java ../TestResults/java
#sh evaluate_results.sh ../promptsOutput/python ../TestResults/python
folders=$(find $1 -mindepth 1 -maxdepth 1 -type d)

# 遍历每个文件夹并执行相应的Python脚本
for folder in $folders
do
    # 排除当前文件夹以及上级目录
    if [ "$folder" != "." ] && [ "$folder" != ".." ]; then
        foldername=$(basename "$folder")
        # 执行Python脚本
        echo "python evaluate_results.py $1/$foldername $2/$foldername"
        python evaluate_results.py $1/$foldername $2/$foldername
        # echo $1/$foldername $2/$foldername
        
    fi
done

echo "python evaluate_statistics.py $2 $2"
python evaluate_statistics.py $2 $2
# language=$(basename "$1")
# find $2 -name '*.csv' -exec cat {} + > "$2"_evaluation_results.csv