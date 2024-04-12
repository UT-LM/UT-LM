
language=$1
folders=$(find $2 -name "*.json" -maxdepth 2)

# 遍历每个文件夹并执行相应的Python脚本
for file in $folders
do
    # 排除当前文件夹以及上级目录
    if [ "$file" != "." ] && [ "$file" != ".." ]; then
        # 执行Python脚本
        echo "python clean_answer.py $1 $file"
        python clean_answer.py $1 $file

        
    fi
done