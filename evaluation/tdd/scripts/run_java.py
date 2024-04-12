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
                        with open(os.path.join(tmp_path, "Solution.java"), "w") as f:
                            f.write(code)
                        with open(os.path.join(tmp_path, "SolutionTest.java"), "w") as f:
                            f.write(tmp_test)
                        status, reason=run_java_junit(tmp_path)
                        output_answers[item]["results"][model][sample][prompt].append({"status": status, "reason": reason})
                    elif prompt == "prompt_tdd2":
                        tmp_code = output_answers[item]["LLM_answers_cleaned"][model][sample][prompt]
                        with open(os.path.join(tmp_path, "Main.java"), "w") as f:
                            f.write(tmp_code+"\n"+test)
                        status, reason=run_java(tmp_path)
                        output_answers[item]["results"][model][sample][prompt].append({"status": status, "reason": reason})
                    elif prompt == "prompt_tdd2_full":
                        tmp_code_dict = output_answers[item]["LLM_answers_cleaned"][model][sample][prompt]
                        for tc in tmp_code_dict.keys():
                            tmp_code = tmp_code_dict[tc]
                            with open(os.path.join(tmp_path, "Main.java"), "w") as f:
                                f.write(tmp_code+"\n"+test)
                            status, reason=run_java(tmp_path)
                            output_answers[item]["results"][model][sample][prompt].append({"status": status, "reason": reason})
                    print(f"Finished running answer id {item} {model} {sample} {prompt}")

                    with open(output_file, "w") as f:
                        json.dump(output_answers, f, indent=4)

def run_java(path):
    status = "SUCCESS"
    reason = {}
    try:
        # 编译 Java 文件
        compile_process = subprocess.run(["javac", os.path.join(path,"Main.java")], capture_output=True, text=True,timeout=60)
        if compile_process.returncode != 0:
            status = "FAILED"
            reason["compile"] = compile_process.stderr.strip()
        else:
            # 运行 Java 类
            java_process = subprocess.run(["java","-cp", path, "Main"], capture_output=True, text=True,timeout=60)
            if java_process.returncode != 0:
                status = "FAILED"
                reason["exec"] = java_process.stderr.strip()
    except Exception as e:
        status = "FAILED"
        reason["exception"] = str(e)
    
    # 删除编译生成的 class 文件
    for file in os.listdir(path):
        if file.endswith(".class") or file.endswith(".java"):
            os.remove(os.path.join(path, file))
    

    return status, reason

def run_java_junit(path):
    status = "SUCCESS"
    reason = {}
    try:
        # 编译 Java 文件
        os.chdir(path)
        # pwd = subprocess.run(["pwd"], capture_output=True, text=True,timeout=60)
        # ls = subprocess.run(["ls"], capture_output=True, text=True,timeout=60)
        # print(pwd.stdout)
        # print(ls.stdout)
        compile_process = subprocess.run("javac -cp junit-platform-console-standalone-1.10.0.jar Solution.java SolutionTest.java", capture_output=True, text=True,timeout=60, shell=True)
        if compile_process.returncode != 0:
            status = "FAILED"
            reason["compile"] = compile_process.stderr.strip()
        else:
            # 运行 Java 类
            java_process = subprocess.run("java -jar junit-platform-console-standalone-1.10.0.jar -f SolutionTest", capture_output=True, text=True,timeout=60,shell=True)
            if java_process.returncode != 0:
                status = "FAILED"
                reason["exec"] = java_process.stderr.strip()
            else:
                print("Java tdd1 success!")
    except Exception as e:
        status = "FAILED"
        reason["exception"] = str(e)
    
    # 删除编译生成的 class 文件
    for file in os.listdir(path):
        if file.endswith(".class") or file.endswith(".java"):
            os.remove(os.path.join(path, file))

    return status, reason


if __name__ == "__main__":
    
    tdd_answer_file = sys.argv[1]

    main(tdd_answer_file)
