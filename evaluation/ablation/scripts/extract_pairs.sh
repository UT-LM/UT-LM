github_link=$1
language=$2
PROJ_PATH=$3

input_dir=$PROJ_PATH/evaluation/ablation/RawData/$language/
output_dir=$PROJ_PATH/evaluation/ablation/RawDataOutput/$language/

mkdir -p $output_dir
mkdir -p $output_dir/FilePairs
mkdir -p $output_dir/MetaData
python3 extract_file_pairs.py $input_dir $output_dir $github_link $language