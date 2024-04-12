
import sys
import os
import json
import subprocess

def main(tdd_answer_file):
    with open(tdd_answer_file, "r") as f:
        answers = json.load(f)

    output_file = tdd_answer_file.replace(".json", "_with_result.json")

    output_answers = {}

    tmp_path = os.path.join(os.path.dirname(tdd_answer_file),"tmp")
    # print(tmp_path)
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            output_answers = json.load(f)
    else:
        output_answers = answers

    for item in answers.keys():
        test = answers[item]["test"]
        code = answers[item]["code"]

        if "results" not in output_answers[item]:
            output_answers[item]["results"] = {}

        LLM_answers_cleaned = answers[item]["LLM_answers_cleaned"]
        for model in LLM_answers_cleaned.keys():
            if model not in output_answers[item]["results"]:
                output_answers[item]["results"][model] = {}
            for sample in LLM_answers_cleaned[model].keys():
                if sample not in output_answers[item]["results"][model]:
                    output_answers[item]["results"][model][sample] = {}
                for prompt in LLM_answers_cleaned[model][sample].keys():
                    if prompt not in output_answers[item]["results"][model][sample]:
                        output_answers[item]["results"][model][sample][prompt] = []
                    if len(output_answers[item]["results"][model][sample][prompt]) > 0:
                        continue
                    print(f"Running answer id {item} {model} {sample} {prompt}")
                    if prompt == "prompt_tdd1" or prompt == "prompt_tdd1_one_shot":
                        tmp_test = output_answers[item]["LLM_answers_cleaned"][model][sample][prompt]
                        # print(os.path.join(tmp_path, "main.py"))
                        with open(os.path.join(tmp_path, "main.py"), "w") as f:
                            f.write(code+"\n"+tmp_test)
                        status, reason=run_python(tmp_path)
                        output_answers[item]["results"][model][sample][prompt].append({"status": status, "reason": reason})
                    elif prompt == "prompt_tdd2":
                        tmp_code = output_answers[item]["LLM_answers_cleaned"][model][sample][prompt]
                        # print(os.path.join(tmp_path, "main.py"))
                        with open(os.path.join(tmp_path, "main.py"), "w") as f:
                            f.write(tmp_code+"\n"+test)
                        status, reason=run_python(tmp_path)
                        output_answers[item]["results"][model][sample][prompt].append({"status": status, "reason": reason})
                    elif prompt == "prompt_tdd2_full":
                        tmp_code_dict = output_answers[item]["LLM_answers_cleaned"][model][sample][prompt]
                        for tc in tmp_code_dict.keys():
                            tmp_code = tmp_code_dict[tc]
                            # print(os.path.join(tmp_path, "main.py"))
                            with open(os.path.join(tmp_path, "main.py"), "w") as f:
                                f.write(tmp_code+"\n"+test)
                            status, reason=run_python(tmp_path)
                            output_answers[item]["results"][model][sample][prompt].append({"status": status, "reason": reason})
                    print(f"Finished running answer id {item} {model} {sample} {prompt}")

                    with open(output_file, "w") as f:
                        json.dump(output_answers, f, indent=4)


def run_python(path):
    status = "SUCCESS"
    reason = {}
    try:
        # 运行 Python 文件
        python_process = subprocess.run(["python",os.path.join(path,"main.py")], capture_output=True, text=True,timeout=60)
        
        if python_process.returncode != 0:
            status = "FAILED"
            reason["compile"] = python_process.stderr.strip()
    except Exception as e:
        status = "FAILED"
        reason["exception"] = str(e)

    #删除python文件
    if os.path.exists(os.path.join(path,"main.py")):
        os.remove(os.path.join(path,"main.py"))

    return status, reason


if __name__ == "__main__":
    
    tdd_answer_file = sys.argv[1]

    main(tdd_answer_file)
