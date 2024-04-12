import os
import json
import sys
import csv


def main(results_path, output_path):
    dir_list = os.listdir(results_path)
    init_status_dict = {}
    print("Create init dictionary")
    for dir in dir_list:
        if not os.path.isdir(os.path.join(results_path, dir)):
            continue
        results_list = os.listdir(os.path.join(results_path, dir))
        summary_file = ""
        for file in results_list:
            if file.endswith("summary.json"):
                summary_file = os.path.join(results_path, dir, file)
                break
        
        with open(summary_file, 'r') as f:
            summary_content = json.load(f)

        for item in summary_content:
            for result in summary_content[item]:
                init_status = result["init_status"]
                filepairs_name = result["filepairs_name"]
                if filepairs_name not in init_status_dict:
                    init_status_dict[filepairs_name] = init_status
                else:
                    init_status_dict[filepairs_name] = init_status if init_status == "SUCCESS" else init_status_dict[filepairs_name]
    
    print(f"length of dictionary: {len(init_status_dict)}")

    statistics_total_csv_file = os.path.join(output_path,"total_statistics.csv")
    output_total_csv = []
    output_total_csv.append(["model", "id", "init_status", "pass_num", "pass@10", "pass@1", "pass@1_best", "pass@1_worst", "no_test", "compile_error", "test_error"])
    coverage_json_file = os.path.join(output_path,"coverage.json")
    coverage_json = [{"single":[],"multi":[]}]
    assert_json_file = os.path.join(output_path,"assert.json")
    assert_json = [{"single":[],"multi":[]}]
    mock_json_file = os.path.join(output_path,"mock.json")
    mock_json = [{"single":[],"multi":[]}]
    test_method_num_file = os.path.join(output_path,"test_method_num.json")
    test_method_num_json = [{"single":[],"multi":[]}]

    for dir in dir_list:
        if not os.path.isdir(os.path.join(results_path, dir)):
            continue
        results_list = os.listdir(os.path.join(results_path, dir))
        summary_file = ""
        for file in results_list:
            if file.endswith("summary.json"):
                summary_file = os.path.join(results_path, dir, file)
                break
        
        output_single_dict = {}
        output_single_csv = []
        output_single_csv.append(["model", "id", "init_status", "pass_num", "pass@10", "pass@1", "pass@1_best", "pass@1_worst", "no_test", "compile_error", "test_error"])
        output_multi_dict = {}
        output_multi_csv =[]
        output_multi_csv.append(["model", "id", "init_status", "pass_num", "pass@10", "pass@1", "pass@1_best", "pass@1_worst", "no_test", "compile_error", "test_error"])
        statistics_single_json_file = os.path.join(output_path,dir,"single_statistics.json")
        statistics_multi_json_file = os.path.join(output_path,dir,"multi_statistics.json")
        statistics_single_csv_file = os.path.join(output_path,dir,"single_statistics.csv")
        statistics_multi_csv_file = os.path.join(output_path,dir,"multi_statistics.csv")

        
        
        with open(summary_file, 'r') as f:
            summary_content = json.load(f)

        print(f'processing {dir}')

        for item in summary_content:
            if item == "single":
                total_pass10 = 0
                total_pass1 = 0
                total_pass1_best = 0
                total_pass1_worst = 0
                total_init_success = 0
                no_test = 0
                compile_error = 0
                test_error = 0
                for result in summary_content[item]:
                    filepairs_name = result["filepairs_name"]
                    model = result['model']
                    id = result['id']
                    id_status = result['id_status']
                    id_reason = result['id_reason']
                    id_coverage = result['id_coverage']
                    id_assert = result['id_assert']
                    id_mock = result['id_mock']
                    id_test_method_num = result['id_test_method_num']

                    init_status = init_status_dict[filepairs_name]

                    sample_status = result['sample_status']
                    sample_reason = result['sample_reason']
                    pass1_num = len(id_reason)
                  
                    pass1_best = 1 if pass1_num >0 else 0
                    pass1 = float(pass1_num/len(sample_status))
                    pass1_worst = 0 if pass1_num < len(sample_status) else 1

                    pass10 = 1 if id_status == "SUCCESS" else 0
                    if id_status == "FAILED":
                        if "test" in sample_reason:
                            test_error += 1
                        elif "compile" in sample_reason:
                            compile_error += 1
                        else:
                            no_test += 1

                    total_pass10 += pass10 if init_status == "SUCCESS" else 0
                    total_pass1 += pass1 if init_status == "SUCCESS" else 0
                    total_pass1_best += pass1_best if init_status == "SUCCESS" else 0
                    total_pass1_worst += pass1_worst if init_status == "SUCCESS" else 0
                    total_init_success += 1 if init_status == "SUCCESS" else 0

                    if model not in output_single_dict:
                        output_single_dict[model] = {}
                    output_single_dict[model][id] = {
                                "init_status": init_status,
                                "pass_num": pass1_num,
                                "pass@10": pass10,
                                "pass@1" : pass1,
                                "pass@1_best": pass1_best,
                                "pass@1_worst":pass1_worst
                            }
                    output_single_csv.append([model, id, init_status, pass1_num, pass10, pass1, pass1_best, pass1_worst])

                    if id_status == "SUCCESS":
                        coverage_json[0]['single'].append({"model": model, "id": id, "coverage": id_coverage})
                        assert_json[0]['single'].append({"model": model, "id": id, "assert": id_assert})
                        mock_json[0]['single'].append({"model": model, "id": id, "mock": id_mock})
                        test_method_num_json[0]['single'].append({"model": model, "id": id, "test_method_num": id_test_method_num})


                output_single_csv.append(["", "Total", f"Init success num: {total_init_success}", f"Total num: {len(summary_content[item])}", total_pass10, total_pass1, total_pass1_best, total_pass1_worst, no_test, compile_error, test_error])
                output_total_csv.append([f"single_{dir}", "Total", f"Init success num: {total_init_success}", f"Total num: {len(summary_content[item])}", total_pass10, total_pass1, total_pass1_best, total_pass1_worst, no_test, compile_error, test_error])

            elif item == "multi":
                total_pass10 = 0
                total_pass1 = 0
                total_pass1_best = 0
                total_pass1_worst = 0
                total_init_success = 0
                no_test = 0
                compile_error = 0
                test_error = 0
                for result in summary_content[item]:
                    filepairs_name = result["filepairs_name"]
                    model = result['model']
                    id = result['id']
                    id_status = result['id_status']
                    id_reason = result['id_reason']
                    id_coverage = result['id_coverage']
                    id_assert = result['id_assert']
                    id_mock = result['id_mock']
                    id_test_method_num = result['id_test_method_num']
                    init_status = init_status_dict[filepairs_name]

                    sample_status = result['sample_status']
                    sample_reason = result['sample_reason']
                   
                    pass1_num = len(id_reason)
                  
                    pass1_best = 1 if pass1_num >0 else 0
                    pass1 = float(pass1_num/len(sample_status))
                    pass1_worst = 0 if pass1_num < len(sample_status) else 1

                    pass10 = 1 if id_status == "SUCCESS" else 0

                    if id_status == "FAILED":
                        if "test" in sample_reason:
                            test_error += 1
                        elif "compile" in sample_reason:
                            compile_error += 1
                        else:
                            no_test += 1
                    total_pass10 += pass10 if init_status == "SUCCESS" else 0
                    total_pass1 += pass1 if init_status == "SUCCESS" else 0
                    total_pass1_best += pass1_best if init_status == "SUCCESS" else 0
                    total_pass1_worst += pass1_worst if init_status == "SUCCESS" else 0
                    total_init_success += 1 if init_status == "SUCCESS" else 0

                    if model not in output_multi_dict:
                        output_multi_dict[model] = {}
                    output_multi_dict[model][id] = {
                                "init_status": init_status,
                                "pass_num": pass1_num,
                                "pass@10": pass10,
                                "pass@1" : pass1,
                                "pass@1_best": pass1_best,
                                "pass@1_worst":pass1_worst
                            }
                    output_multi_csv.append([model, id, init_status, pass1_num, pass10, pass1, pass1_best, pass1_worst])

                    if id_status == "SUCCESS":
                        coverage_json[0]['multi'].append({"model": model, "id": id, "coverage": id_coverage})
                        assert_json[0]['multi'].append({"model": model, "id": id, "assert": id_assert})
                        mock_json[0]['multi'].append({"model": model, "id": id, "mock": id_mock})
                        test_method_num_json[0]['multi'].append({"model": model, "id": id, "test_method_num": id_test_method_num})

                
                output_multi_csv.append(["", "Total", f"Init success num: {total_init_success}", f"Total num: {len(summary_content[item])}", total_pass10, total_pass1, total_pass1_best, total_pass1_worst, no_test, compile_error, test_error])
                output_total_csv.append([f"multi_{dir}", "Total", f"Init success num: {total_init_success}", f"Total num: {len(summary_content[item])}", total_pass10, total_pass1, total_pass1_best, total_pass1_worst, no_test, compile_error, test_error])

        with open(statistics_single_json_file,'w') as f:
            json.dump(output_single_dict, f, indent=4)
        with open(statistics_multi_json_file, 'w') as f:
            json.dump(output_multi_dict, f, indent=4)
        with open(statistics_single_csv_file, "w") as f:
            writer = csv.writer(f)
            writer.writerows(output_single_csv)
        with open(statistics_multi_csv_file, "w") as f:
            writer = csv.writer(f)
            writer.writerows(output_multi_csv)
    with open(statistics_total_csv_file, "w") as f:
        writer = csv.writer(f)
        writer.writerows(output_total_csv)
        
    with open(coverage_json_file, 'w') as f:
        json.dump(coverage_json, f, indent=4)
    with open(assert_json_file, 'w') as f:
        json.dump(assert_json, f, indent=4)
    with open(mock_json_file, 'w') as f:
        json.dump(mock_json, f, indent=4)
    with open(test_method_num_file, 'w') as f:
        json.dump(test_method_num_json, f, indent=4)
            

if __name__  == "__main__":
    results_path = sys.argv[1]
    output_path = sys.argv[2]
    
    main(results_path, output_path)