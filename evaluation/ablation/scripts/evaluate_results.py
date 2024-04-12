import os
import json
import sys
import csv

def main(results_path, output_path):
    
    output_csv = []
    output_csv.append(["model", "id", "prompt","sample_num", "sample_status","sample_reason","task","repo"])

    output_file = os.path.join(output_path, "evaluation_results.csv")
    output_json =[]
    output_json_file = os.path.join(output_path, "evaluation_results.json")

    summary_csv = []
    summary_csv.append(["model", "id", "prompt","prompt_status", "prompt_reason", "sample_status","sample_reason","task","repo"])
    summary_file = os.path.join(output_path, "evaluation_summary.csv")
    summary_json = []
    summary_json_file = os.path.join(output_path, "evaluation_summary.json")

    for results_file in os.listdir(results_path):
        if results_file.endswith("result.json"):
            with open(os.path.join(results_path,results_file), "r") as f:
                results = json.load(f)
            for item in results:
                task = results_file.split("_")[0]
                repo = results[item]['file']
                if "results" in results[item]:
                    id = item
                    for m in results[item]["results"].keys():
                        model = m
                        prompt_status = {
                            "prompt_method_only" :"FAILED",
                            "prompt_method_class" :"FAILED",
                            "prompt_method_class_callee_1" :"FAILED",
                            "prompt_method_class_callee_3" :"FAILED",
                            "prompt_method_class_callee_0_test_1" :"FAILED",
                            "prompt_method_class_callee_0_test_3" :"FAILED",
                            "prompt_method_class_callee_1_test_1" :"FAILED",
                            "prompt_method_class_callee_1_test_3" :"FAILED",
                            "prompt_method_class_callee_3_test_1" :"FAILED",
                            "prompt_method_class_callee_3_test_3" :"FAILED"
                        }
                        prompt_reason = {
                            "prompt_method_only" :[],
                            "prompt_method_class" :[],
                            "prompt_method_class_callee_1" :[],
                            "prompt_method_class_callee_3" :[],
                            "prompt_method_class_callee_0_test_1" :[],
                            "prompt_method_class_callee_0_test_3" :[],
                            "prompt_method_class_callee_1_test_1" :[],
                            "prompt_method_class_callee_1_test_3" :[],
                            "prompt_method_class_callee_3_test_1" :[],
                            "prompt_method_class_callee_3_test_3" :[]
                        }
                        sample_status_list = {
                            "prompt_method_only" :[],
                            "prompt_method_class" :[],
                            "prompt_method_class_callee_1" :[],
                            "prompt_method_class_callee_3" :[],
                            "prompt_method_class_callee_0_test_1" :[],
                            "prompt_method_class_callee_0_test_3" :[],
                            "prompt_method_class_callee_1_test_1" :[],
                            "prompt_method_class_callee_1_test_3" :[],
                            "prompt_method_class_callee_3_test_1" :[],
                            "prompt_method_class_callee_3_test_3" :[]
                        }
                        sample_reason_list = {
                            "prompt_method_only" :[],
                            "prompt_method_class" :[],
                            "prompt_method_class_callee_1" :[],
                            "prompt_method_class_callee_3" :[],
                            "prompt_method_class_callee_0_test_1" :[],
                            "prompt_method_class_callee_0_test_3" :[],
                            "prompt_method_class_callee_1_test_1" :[],
                            "prompt_method_class_callee_1_test_3" :[],
                            "prompt_method_class_callee_3_test_1" :[],
                            "prompt_method_class_callee_3_test_3" :[]
                        }
                        for s in results[item]["results"][m].keys():
                            sample_num = s
                            for prompt in results[item]["results"][m][s].keys():

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
                                            elif "test" in results[item]["results"][m][s][prompt][0]["reason"].keys():
                                                sample_reason = "test"
                                        else:
                                            sample_reason = results[item]["results"][m][s][prompt][0]["reason"]
                                            
                                if sample_status == "SUCCESS":
                                    prompt_status[prompt] = "SUCCESS"
                                    prompt_reason[prompt].append(sample_num)
                                
                                sample_status_list[prompt].append(sample_status)
                                sample_reason_list[prompt].append(sample_reason)

                                output_csv.append([model, id, prompt, sample_num, sample_status, sample_reason,task,repo])
                                
                                output_json.append({
                                    'model': model,
                                    'id': id,
                                    'prompt': prompt,
                                    'sample_num': sample_num,
                                    'sample_status': sample_status,
                                    'sample_reason': sample_reason,
                                    'task': task,
                                    'repo': repo
                                })
                                
                        for prompt in prompt_status.keys():
                            summary_csv.append([model, id, prompt, prompt_status[prompt], prompt_reason[prompt], sample_status_list[prompt], sample_reason_list[prompt],task,repo])
                        
                            summary_json.append({
                                'model': model,
                                'id': id,
                                'prompt': prompt,
                                'prompt_status': prompt_status[prompt],
                                'prompt_reason': prompt_reason[prompt],
                                'sample_status': sample_status_list[prompt],
                                'sample_reason': sample_reason_list[prompt],
                                'task': task,
                                'repo': repo
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