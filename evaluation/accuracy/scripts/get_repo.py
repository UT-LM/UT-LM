import os
import sys
import json

def main(language,input):
    with open(input, 'r') as f:
        filepairs = json.load(f)
    new_filepairs = {}
    
    for owner in filepairs:
        for repo in filepairs[owner]:
            filepairs_repo = {
                "code_filename" :[],
                "test_filename" :[]
            }
            ori_path = f"data/GitHubMining/RawData/{language}/{owner}/{repo}"
            if not os.path.exists(ori_path):
                continue
            new_filepairs[owner] = {
                repo: []
            }
            new_path = f"evaluation/RawData/{language}/{owner}"
            os.system(f"mkdir -p {new_path}")
            os.system(f"cp -r {ori_path} {new_path}")
            filepair_list = filepairs[owner][repo]
            for filepair in filepair_list:
                code_file = filepair[0]
                test_file = filepair[1]
                new_filepairs[owner][repo].append([code_file,test_file])

                filepairs_repo["code_filename"].append(code_file)
                filepairs_repo["test_filename"].append(test_file)
            
            os.system(f"mkdir -p evaluation/accuracy/RawDataOutput/{language}/FilePairs")
            with open(f"evaluation/accuracy/RawDataOutput/{language}/FilePairs/filepairs_{owner}__{repo}.json",'w') as f:
                json.dump(filepairs_repo,f,indent=4,ensure_ascii=False)
            
    
    with open(f"evaluation/accuracy/RawDataOutput/{language}/{language}_filepairs_20240314.json",'w') as f:
        json.dump(new_filepairs,f,indent=4,ensure_ascii=False)


if __name__ == '__main__':
    language = sys.argv[1]
    input = sys.argv[2]
    main(language,input)