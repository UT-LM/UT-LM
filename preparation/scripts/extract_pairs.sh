github_link=$1
language=$2

input_dir=/cpfs/29a75185021b187f/aigccode/user/cuizhe/UT-LM/data/GitHubMining/RawData/$language/
output_dir=/cpfs/29a75185021b187f/aigccode/user/cuizhe/UT-LM/data/GitHubMining/RawDataOutput/$language/

mkdir -p $output_dir
mkdir -p $output_dir/FilePairs
mkdir -p $output_dir/MetaData
python3 extract_file_pairs.py $input_dir $output_dir $github_link $language