#docker run --rm -it --mount type=bind,src=PROJ_PATH/evaluation/scripts,dst=/code --mount type=bind,src=/cpfs/29583eqvgtdvw5cvegg/data/user,dst=/cpfs/29583eqvgtdvw5cvegg/data/user python38 /bin/bash
#docker run --rm -it --mount type=bind,src=PROJ_PATH/evaluation/scripts,dst=/code --mount type=bind,src=/cpfs/29583eqvgtdvw5cvegg/data/user,dst=/cpfs/29583eqvgtdvw5cvegg/data/user python310 /bin/bash

import json
import sys
import os
import subprocess

def run_cmd(cmd,timeout=600):
    if isinstance(cmd, list):
        cmd = " ".join(cmd)
    # cmd= "pwd"
    print(f"Running {cmd}")
    
    try: 
        cmd_output = subprocess.run(cmd, stdout=subprocess.PIPE, timeout=timeout,shell=True)
        # print(cmd_output)
        return cmd_output, False
    except subprocess.TimeoutExpired as e:
        return None, True

# checks code in /data
def check_python_generation(repo_path,compile_cmd,test_cmd,cov_cmd,timeout,run_dir,new_test_file_path,prompt):
    print(f"check_python {repo_path}")
    setup_steps = []
    os.chdir(repo_path)
    print(f"changing to {repo_path}")

    run_cmd(['git', 'clean', "-xdf"],timeout)
    run_cmd(['git', 'reset', "--hard"],timeout)
    
    if os.path.exists(os.path.join(repo_path,"pyproject.toml")):
        print("removing pyproject.toml")
        os.remove(os.path.join(repo_path,"pyproject.toml"))


    # if os.path.isfile("setup.py"):
    #     setup_cmd = ["pip3", "install", ".[test]"]
    #     setup_steps.append(setup_cmd)
    #     run_cmd(setup_cmd,timeout)

    # elif os.path.isfile("requirements.txt"):
    #     requirements_cmd = ["pip3", "install", "-r", "requirements.txt"]
    #     setup_steps.append(requirements_cmd)
    #     run_cmd(requirements_cmd,timeout)
    
    os.chdir(run_dir)
    print(f"changing to {run_dir}")


    with open(new_test_file_path, "w") as f:
        f.write(prompt)

    file_name = new_test_file_path.split("/")[-1]

    test_cmd.append(file_name)
    test_result, test_timeout = run_cmd(test_cmd,timeout)
    test_cmd.pop()
    if test_timeout or test_result.returncode != 0:
        # print(test_result)
        print("Unable to run or failing tests -- skipping")
        result = test_result.stdout.decode("utf-8") if not test_timeout else "testing timeout"
        return {"status": "FAILED", "reason": {"test": result}}

    cov_cmd.append(file_name)
    coverage_result, coverage_timeout = run_cmd(cov_cmd,timeout)
    cov_cmd.pop()
    if coverage_timeout or coverage_result.returncode != 0:
        print("Unable to run coverage -- skipping")
        result = coverage_result.stdout.decode("utf-8") if not coverage_timeout else "coverage timeout"
        return {"status": "FAILED", "reason": {"coverage": result}}

    return {"status": "SUCCESS", "reason":{"test": test_result.stdout.decode("utf-8"), "coverage": coverage_result.stdout.decode("utf-8")}}

# def check_python_init(repo_path,compile_cmd,test_cmd,cov_cmd,timeout,run_dir):
#     print(f"check_python {repo_path}")
#     setup_steps = []
#     os.chdir(repo_path)

#     run_cmd(['git', 'clean', "-xdf"],timeout)
#     run_cmd(['git', 'reset', "--hard"],timeout)
    

#     if os.path.isfile("setup.py"):
#         setup_cmd = ["pip3", "install", ".[test]"]
#         setup_steps.append(setup_cmd)
#         run_cmd(setup_cmd,timeout)

#     elif os.path.isfile("requirements.txt"):
#         requirements_cmd = ["pip3", "install", "-r", "requirements.txt"]
#         setup_steps.append(requirements_cmd)
#         run_cmd(requirements_cmd,timeout)
    
#     os.chdir(run_dir)

#     test_result, test_timeout = run_cmd(test_cmd,timeout)
#     if test_timeout or (test_result.returncode != 0 and test_result.returncode != 5):
#         # print(test_result)
#         print("Unable to run or failing tests -- skipping")
#         result = test_result.stdout.decode("utf-8") if not test_timeout else "testing timeout"
#         return {"status": "FAILED", "reason": {"test": result}}

#     coverage_result, coverage_timeout = run_cmd(cov_cmd,timeout)
#     if coverage_timeout or (coverage_result.returncode != 0 and test_result.returncode != 5):
#         print("Unable to run coverage -- skipping")
#         result = coverage_result.stdout.decode("utf-8") if not coverage_timeout else "coverage timeout"
#         return {"status": "FAILED", "reason": {"coverage": result}}

#     return {"status": "SUCCESS", "reason": {"test": test_result.stdout.decode("utf-8"), "coverage": coverage_result.stdout.decode("utf-8")}}



def main_python(answers_file, repo_dir,in_repo):
    output_file = answers_file.replace(".json", f"_with_{in_repo}_result.json")
    with open(answers_file, "r") as f:
        answers = json.load(f)

    for item in answers.keys():
        class_file_path_dir = os.path.dirname(answers[item]["class_file_path"])
        file = answers[item]["file"]
        method_name = answers[item]["method_name"]
        test_file_path = answers[item]["test_file_path"]
        compile_cmd = answers[item]["compile_cmd"]
        test_cmd = [
            "pytest"
        ]
        cov_cmd = [
            "coverage",
            "run",
            "-m",
            "pytest"
        ]
        org = file.split("_")[1]
        repo = file.split("__")[1].split(".jsonl")[0]

        if in_repo != repo:
            print(f"Skipping answer id {item} as it is not in the repo")
            continue
        else:
            print(f"Running answer id {item}")
        

        # code_path = "PROJ_PATH/evaluation/scripts"
        # user_path = "/cpfs/29583eqvgtdvw5cvegg/data/user"

        

        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                output_answers = json.load(f)
        else:
            output_answers = answers


        if "results" not in output_answers[item]:
            output_answers[item]["results"] = {}

    
        if "LLM_answers_cleaned" in answers[item]:
            LLM_answers_cleaned = answers[item]["LLM_answers_cleaned"]
        else:
            return

        for model in LLM_answers_cleaned.keys():
            if model not in output_answers[item]["results"]:
                output_answers[item]["results"][model] = {}
            for sample_num in LLM_answers_cleaned[model].keys():
                if sample_num not in output_answers[item]["results"][model]:
                    output_answers[item]["results"][model][sample_num] = {}
                for prompt in LLM_answers_cleaned[model][sample_num].keys():
                    if prompt not in output_answers[item]["results"][model][sample_num]:
                        result = []
                        if LLM_answers_cleaned[model][sample_num][prompt] == "":
                            result.append("")
                        elif  LLM_answers_cleaned[model][sample_num][prompt] == "NO CODE AVAILABLE":
                            result.append({"status": "FAILED", "reason": "No clean code available"})
                        else:
                            print(f"Running answer id {item} {model} {sample_num} {prompt}")
                            if len(test_file_path) == 0:
                                if method_name in LLM_answers_cleaned[model][sample_num][prompt]:
                                    test_file_name = "test_"+answers[item]["class_name"]
                                else:
                                    test_file_name = ""
                                if test_file_name != "":
                                    new_test_file_path = os.path.join(repo_dir, class_file_path_dir, test_file_name+".py")
                                    print(f"checking {org} {repo} {new_test_file_path}")
                                    result.append(check_python_generation(os.path.join(repo_dir,org,repo),compile_cmd,test_cmd,cov_cmd,600,os.path.dirname(new_test_file_path),new_test_file_path,LLM_answers_cleaned[model][sample_num][prompt]))
                                else:
                                    result.append({
                                        "status": "FAILED",
                                        "reason": "No test method found in answer"
                                    })
                            else:

                                for new_test_file_path in test_file_path:
                                    new_test_file_path = os.path.join(repo_dir,new_test_file_path)
                                    print(f"checking {org} {repo} {new_test_file_path}")
                                    
                                    result.append(check_python_generation(os.path.join(repo_dir,org,repo),compile_cmd,test_cmd,cov_cmd,600,os.path.dirname(new_test_file_path),new_test_file_path,LLM_answers_cleaned[model][sample_num][prompt]))

                                            
                        output_answers[item]["results"][model][sample_num][prompt] = result
                        with open(output_file, "w") as f:
                            json.dump(output_answers, f, indent=4,ensure_ascii=False)
                        print(f"Finished answer id {item} {model} {sample_num} {prompt}")
                    else:
                        print(f"Skipping answer id {item} {model} {sample_num} {prompt}")


if __name__ == "__main__":

    answers_file = sys.argv[1]
    repo_dir= sys.argv[2]
    in_repo = sys.argv[3]

    main_python(answers_file, repo_dir,in_repo)