import os
import json
import sys
import csv

def main(results_path, output_path):
    
    output_csv = []
    output_csv.append(["model", "id", "prompt","sample_num", "sample_status","sample_reason"])

    output_file = os.path.join(output_path, "evaluation_results.csv")
    output_json =[]
    output_json_file = os.path.join(output_path, "evaluation_results.json")

    summary_csv = []
    summary_csv.append(["model", "id", "prompt","prompt_status", "prompt_reason", "sample_status","sample_reason"])
    summary_file = os.path.join(output_path, "evaluation_summary.csv")
    summary_json = []
    summary_json_file = os.path.join(output_path, "evaluation_summary.json")

    for results_file in os.listdir(results_path):
        if results_file.endswith("result.json"):
            with open(os.path.join(results_path,results_file), "r") as f:
                results = json.load(f)
            for item in results:
                if "results" in results[item]:
                    id = item
                    for m in results[item]["results"].keys():
                        model = m
                        prompt_status = {
                            "prompt_tdd1" :"FAILED",
                            "prompt_tdd1_one_shot" :"FAILED",
                            "prompt_tdd2" :"FAILED",
                            "prompt_tdd2_full" :"FAILED"
                        }
                        prompt_reason = {
                            "prompt_tdd1" :[],
                            "prompt_tdd1_one_shot" :[],
                            "prompt_tdd2" :[],
                            "prompt_tdd2_full" :[]
                        }
                        sample_status_list = {
                            "prompt_tdd1" :[],
                            "prompt_tdd1_one_shot" :[],
                            "prompt_tdd2" :[],
                            "prompt_tdd2_full" :[]
                        }
                        sample_reason_list = {
                            "prompt_tdd1" :[],
                            "prompt_tdd1_one_shot" :[],
                            "prompt_tdd2" :[],
                            "prompt_tdd2_full" :[]
                        }
                        for s in results[item]["results"][m].keys():
                            sample_num = s
                            for prompt in results[item]["results"][m][s].keys():
                                if prompt != "prompt_tdd2_full":
                                    if results[item]["results"][m][s][prompt][0] == "":
                                        sample_status = "FAILED"
                                        sample_reason = "Code not fully completed"
                                    else:
                                        sample_status = results[item]["results"][m][s][prompt][0]["status"]
                                        sample_reason = ""
                                        if sample_status == "FAILED":
                                            if isinstance(results[item]["results"][m][s][prompt][0]["reason"], dict):
                                                if "compile" in results[item]["results"][m][s][prompt][0]["reason"].keys():
                                                    sample_reason = "compile"
                                            else:
                                                sample_reason = results[item]["results"][m][s][prompt][0]["reason"]
                                                
                                    if sample_status == "SUCCESS":
                                        prompt_status[prompt] = "SUCCESS"
                                        prompt_reason[prompt].append(sample_num)
                                    
                                    sample_status_list[prompt].append(sample_status)
                                    sample_reason_list[prompt].append(sample_reason)

                                    output_csv.append([model, id, prompt, sample_num, sample_status, sample_reason])
                                    
                                    output_json.append({
                                        'model': model,
                                        'id': id,
                                        'prompt': prompt,
                                        'sample_num': sample_num,
                                        'sample_status': sample_status,
                                        'sample_reason': sample_reason
                                    })
                                else:
                                    sample_status = "FAILED"
                                    sample_reason = ""
                                    for ss in results[item]["results"][m][s][prompt]:
                                        if ss == "":
                                            continue
                                        else:
                                            if ss['status'] == "SUCCESS":
                                                sample_status = "SUCCESS"
                                                break
                                                
                                    if sample_status == "SUCCESS":
                                        prompt_status[prompt] = "SUCCESS"
                                        prompt_reason[prompt].append(sample_num)
                                    
                                    sample_status_list[prompt].append(sample_status)
                                    sample_reason_list[prompt].append(sample_reason)

                                    output_csv.append([model, id, prompt, sample_num, sample_status, sample_reason])
                                    
                                    output_json.append({
                                        'model': model,
                                        'id': id,
                                        'prompt': prompt,
                                        'sample_num': sample_num,
                                        'sample_status': sample_status,
                                        'sample_reason': sample_reason
                                    })

                        for prompt in prompt_status.keys():
                            summary_csv.append([model, id, prompt, prompt_status[prompt], prompt_reason[prompt], sample_status_list[prompt], sample_reason_list[prompt]])
                        
                            summary_json.append({
                                'model': model,
                                'id': id,
                                'prompt': prompt,
                                'prompt_status': prompt_status[prompt],
                                'prompt_reason': prompt_reason[prompt],
                                'sample_status': sample_status_list[prompt],
                                'sample_reason': sample_reason_list[prompt]
                            })
        

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with open(output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerows(output_csv)

    with open(summary_file, "w") as f:
        writer = csv.writer(f)
        writer.writerows(summary_csv)
    
    with open(output_json_file, "w") as f:
        json.dump(output_json, f, indent=4)
    
    with open(summary_json_file, "w") as f:
        json.dump(summary_json, f, indent=4)



if __name__  == "__main__":
    results_path = sys.argv[1]
    output_path = sys.argv[2]
    
    main(results_path, output_path)