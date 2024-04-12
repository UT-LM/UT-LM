import os
import json
import sys
import csv


def main(results_path, output_path):
    dir_list = os.listdir(results_path)

    statistics_total_csv_file = os.path.join(output_path,"total_statistics.csv")
    output_total_csv = []
    output_total_csv.append(["model", "id", "prompt", "pass@10", "pass@1", "pass@1_best", "pass@1_worst"])

    for dir in dir_list:
        results_list = os.listdir(os.path.join(results_path, dir))
        summary_file = ""
        for file in results_list:
            if file.endswith("summary.json"):
                summary_file = os.path.join(results_path, dir, file)
                break
        

        with open(summary_file, 'r') as f:
            summary_content = json.load(f)

        print(f'processing {dir}')
        
        output_dict = {}
        output_csv =[]
        output_csv.append(["model", "id", "prompt", "pass_num", "pass@10", "pass@1", "pass@1_best", "pass@1_worst"])
        statistics_json_file = os.path.join(output_path,dir,"statistics.json")
        statistics_csv_file = os.path.join(output_path,dir,"statistics.csv")
        
        total_pass10 = {}
        total_pass1 = {}
        total_pass1_best = {}
        total_pass1_worst = {}
        total_init_success = {}
        for result in summary_content:
            model = result['model']
            id = result['id']
            prompt = result['prompt']
            prompt_status = result['prompt_status']
            prompt_reason = result['prompt_reason']
            sample_status = result['sample_status']
            sample_reason = result['sample_reason']
            
            if len(sample_status) == 0:
                continue
            
            
            pass1_num = len(prompt_reason)
            
            pass1_best = 1 if pass1_num >0 else 0
            pass1 = float(pass1_num/len(sample_status))
            pass1_worst = 0 if pass1_num < len(sample_status) else 1

            pass10 = 1 if prompt_status == "SUCCESS" else 0
            if prompt not in total_pass10:
                total_pass10[prompt] = 0
                total_pass1[prompt] = 0
                total_pass1_best[prompt] = 0
                total_pass1_worst[prompt] = 0
                total_init_success[prompt] = 0

            total_pass10[prompt] += pass10 
            total_pass1[prompt] += pass1 
            total_pass1_best[prompt] += pass1_best 
            total_pass1_worst[prompt] += pass1_worst
            total_init_success[prompt] += 1

            if model not in output_dict:
                output_dict[model] = {}
            output_dict[model][id] = {
                        "prompt": prompt,
                        "pass_num": pass1_num,
                        "pass@10": pass10,
                        "pass@1" : pass1,
                        "pass@1_best": pass1_best,
                        "pass@1_worst":pass1_worst
                    }
            output_csv.append([model, id, prompt, pass1_num, pass10, pass1, pass1_best, pass1_worst])
        
        for prompt in total_pass10:
            output_csv.append(["", "Total", prompt, "", total_pass10[prompt], total_pass1[prompt], total_pass1_best[prompt], total_pass1_worst[prompt]])
            output_total_csv.append([model, "Total", prompt, total_pass10[prompt], total_pass1[prompt], total_pass1_best[prompt], total_pass1_worst[prompt]])
            

        with open(statistics_json_file,'w') as f:
            json.dump(output_dict, f, indent=4)

        with open(statistics_csv_file, "w") as f:
            writer = csv.writer(f)
            writer.writerows(output_csv)


    with open(statistics_total_csv_file, "w") as f:
        writer = csv.writer(f)
        writer.writerows(output_total_csv)
            

if __name__  == "__main__":
    results_path = sys.argv[1]
    output_path = sys.argv[2]
    
    main(results_path, output_path)