language=$2
# in_file=$language-top-repos-10001-20000.txt
in_file=$1
less $in_file | xargs -P32 -n1 -I% bash -c 'echo %; \
line=$"%";\
line_array=($line);\
github_link=${line_array[0]};\
sh cloner_current_state.sh $github_link '$language'; \
sh extract_pairs.sh $github_link '$language
