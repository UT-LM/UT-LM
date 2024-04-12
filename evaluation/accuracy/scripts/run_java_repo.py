#docker run --rm -it --mount type=bind,src=PROJ_PATH/evaluation/scripts,dst=/code --mount type=bind,src=/cpfs/29583eqvgtdvw5cvegg/data/user,dst=/cpfs/29583eqvgtdvw5cvegg/data/user java8maven /bin/bash
#docker run --rm -it --mount type=bind,src=PROJ_PATH/evaluation/scripts,dst=/code --mount type=bind,src=/cpfs/29583eqvgtdvw5cvegg/data/user,dst=/cpfs/29583eqvgtdvw5cvegg/data/user java17maven /bin/bash
#docker run --rm -it --mount type=bind,src=PROJ_PATH/evaluation/scripts,dst=/code --mount type=bind,src=/cpfs/29583eqvgtdvw5cvegg/data/user,dst=/cpfs/29583eqvgtdvw5cvegg/data/user java8gradle /bin/bash
import json
import sys
import os
import glob
import subprocess
import xmltodict
import pandas as pd

JACOCO_DEFAULT = {'groupId': 'org.jacoco', 'artifactId': 'jacoco-maven-plugin', 'version': '0.8.6', 'executions': {'execution': [{'id': 'prepare-agent', 'goals': {'goal': 'prepare-agent'}}, {'id': 'report', 'phase': 'test', 'goals': {'goal': 'report'}}]}}


def update_pom_file(pom_xml):
    with open(pom_xml, "r") as f:
        pom = xmltodict.parse(f.read())

    try:
        if "build" not in pom["project"]:
            pom["project"]["build"] = {
                "plugins": {
                    "plugin": []
                }
            }
        else:
            if "plugins" not in pom["project"]["build"]:
                pom["project"]["build"]["plugins"] = {
                    "plugin": []
                }
            else:
                if "plugin" not in pom["project"]["build"]["plugins"]:
                    pom["project"]["build"]["plugins"] = {
                        "plugin": []
                    }
        plugins = pom["project"]["build"]["plugins"]["plugin"]
        if not isinstance(plugins, list):
            plugins = [plugins]
            pom["project"]["build"]["plugins"]["plugin"] = plugins
        # print(plugins)
        found_jacoco = "NO"
        for i, plugin in enumerate(plugins):
            if plugin.get("artifactId") == "jacoco-maven-plugin":
                found_jacoco = "YES"
                break
        if found_jacoco == "NO":
            pom["project"]["build"]["plugins"]["plugin"].append(JACOCO_DEFAULT)
            with open(pom_xml, "w") as f:
                f.write(xmltodict.unparse(pom))
        return found_jacoco
    except Exception as e:
        print(e)
        return "ERROR"

def update_gradle_file(build_gradle):
    with open(build_gradle, "r") as f:
        lines = f.read().split("\n")
    
    new_lines = []
    new_lines += lines
    new_lines += ["apply plugin: 'jacoco'"]
    new_lines += ["jacocoTestReport {", "reports {", "csv.required = true", "}", "}"]

    with open(build_gradle, "w") as f:
        f.write("\n".join(new_lines))


def check_java_mvn_init(repo_path,compile_cmd,test_cmd,cov_cmd,timeout=600):
    print(f"check_java_mvn {repo_path}")
    pom_files = glob.glob(f'{repo_path}/**/pom.xml', recursive=True)
    
    # check if maven
    if len(pom_files) == 0:
        print("Not maven -- skipping")
        return {"status": "FAILED", "reason": "Not maven", "pom_files": pom_files}

    # check single module
    if len(pom_files) > 1:
        print("Not single module -- skipping")
        return {"status": "FAILED", "reason": "Multi-module", "pom_files": pom_files}

    pom_file = pom_files[0]
    # clean anything that is there
    pom_file = pom_files[0]
    pom_dir = os.path.dirname(pom_file)
    os.chdir(pom_dir)

    run_cmd(['mvn', 'clean'],timeout)
    run_cmd(['git', 'clean', "-xdf"],timeout)
    run_cmd(['git', 'reset', "--hard"],timeout)

    compile_result, compile_timeout = run_cmd(compile_cmd,timeout)

    if compile_timeout or compile_result.returncode != 0:
        print("Unable to compile -- skipping")
        result = compile_result.stdout.decode("utf-8") if not compile_timeout else "compiling timeout"
        return {"status": "FAILED", "reason": {"compile": result}}

    test_result, test_timeout = run_cmd(test_cmd,timeout)
    if test_timeout or test_result.returncode != 0:
        print("Unable to run or failing tests -- skipping")
        result = test_result.stdout.decode("utf-8") if not test_timeout else "testing timeout"
        return {"status": "FAILED", "reason": {"test": result}}

    # print(pom_file)
    found_jacoco = update_pom_file(pom_file)    

    if found_jacoco == "ERROR":
        print("Unable to run coverage -- skipping")
        return {"status": "FAILED", "reason": {"coverage": "Not able to update POM"}}
    else:
        jacoco_result, jacoco_timeout = run_cmd(['mvn','jacoco:report'],timeout)
        if jacoco_timeout or jacoco_result.returncode != 0:
            print("Unable to run coverage -- skipping")
            result = jacoco_result.stdout.decode("utf-8") if not jacoco_timeout else "coverage timeout"
            return {"status": "FAILED", "reason": {"coverage": result}}
    
    return {"status": "SUCCESS", "reason": {"compile": compile_result.stdout.decode("utf-8"), "test": test_result.stdout.decode("utf-8"), "coverage": jacoco_result.stdout.decode("utf-8")}}


def check_java_gradle_init(repo_path,compile_cmd,test_cmd,cov_cmd,timeout=600):
    print(f"check_java_gradle {repo_path}")
    build_files = glob.glob(f'{repo_path}/**/build.gradle', recursive=True)
    
    # check if maven
    if len(build_files) == 0:
        print("Not gradle -- skipping")
        return {"status": "FAILED", "reason": "Not gradle"}

    # check single module
    if len(build_files) > 1:
        print("Not single module -- skipping")
        return {"status": "FAILED", "reason": "Multi-module"}

    build_file = build_files[0]
    build_dir = os.path.dirname(build_file)
    os.chdir(build_dir)
    # clean anything that is there

    run_cmd(['gradle', 'clean'],timeout)
    run_cmd(['git', 'clean', "-xdf"],timeout)
    run_cmd(['git', 'reset', "--hard"],timeout)

    compile_result, compile_timeout = run_cmd(compile_cmd,timeout)

    if compile_timeout or compile_result.returncode != 0:
        print("Unable to compile -- skipping")
        result = compile_result.stdout.decode("utf-8") if not compile_timeout else "compiling timeout"
        return {"status": "FAILED", "reason": {"compile": result}}

    test_result, test_timeout = run_cmd(test_cmd,timeout)
    if test_timeout or test_result.returncode != 0:
        print("Unable to run or failing tests -- skipping")
        result = test_result.stdout.decode("utf-8") if not test_timeout else "testing timeout"
        return {"status": "FAILED", "reason": {"test": result}}

    update_gradle_file(build_file)    

    jacoco_result, jacoco_timeout = run_cmd(cov_cmd,timeout)
    if jacoco_timeout or jacoco_result.returncode != 0:
        print("Unable to run coverage -- skipping")
        result = jacoco_result.stdout.decode("utf-8") if not jacoco_timeout else "coverage timeout"
        return {"status": "FAILED", "reason": {"coverage":result}}

    return {"status": "SUCCESS", "reason": {"compile": compile_result.stdout.decode("utf-8"), "test": test_result.stdout.decode("utf-8"), "coverage": jacoco_result.stdout.decode("utf-8")}}

def compute_coverage_java(coverage_csv, source_fn):
    try:
        csv_df = pd.read_csv(coverage_csv)
    except Exception as e:
        print(e)
        return "NO COVERAGE FILE FOUND"
    
    filtered_rows = csv_df[csv_df["CLASS"] == source_fn.split("/")[-1].split(".")[0]]
    if len(filtered_rows) == 0:
        return "NOT FOUND"

    cov_row = filtered_rows.iloc[0]
    if len(filtered_rows) > 1:
        for index, row in filtered_rows.iterrows():
            if row["PACKAGE"].replace(".", "/") in source_fn:
                cov_row = row
    return cov_row["LINE_COVERED"] / (cov_row["LINE_COVERED"] + cov_row["LINE_MISSED"])


def check_java_mvn_generation(repo_path,compile_cmd,test_cmd,cov_cmd,timeout,new_test_file_path,prompt,source_fn):
    print(f"check_java_mvn {repo_path}")
    pom_files = glob.glob(f'{repo_path}/**/pom.xml', recursive=True)
    
    # check if maven
    if len(pom_files) == 0:
        print("Not maven -- skipping")
        return {"status": "FAILED", "reason": "Not maven", "pom_files": pom_files}

    # check single module
    if len(pom_files) > 1:
        print("Not single module -- skipping")
        return {"status": "FAILED", "reason": "Multi-module", "pom_files": pom_files}

    pom_file = pom_files[0]
    # clean anything that is there
    pom_file = pom_files[0]
    pom_dir = os.path.dirname(pom_file)
    os.chdir(pom_dir)

    run_cmd(['mvn', 'clean'],timeout)
    run_cmd(['git', 'clean', "-xdf"],timeout)
    run_cmd(['git', 'reset', "--hard"],timeout)

    if not os.path.exists(os.path.dirname(new_test_file_path)):
        os.system("mkdir -p "+os.path.dirname(new_test_file_path))

    with open(new_test_file_path, "w") as f:

        f.write(prompt)
    f.close()

    compile_result, compile_timeout = run_cmd(compile_cmd,timeout)

    if compile_timeout or compile_result.returncode != 0:
        print("Unable to compile -- skipping")
        result = compile_result.stdout.decode("utf-8") if not compile_timeout else "compiling timeout"
        return {"status": "FAILED", "reason": {"compile": result}}

    test_result, test_timeout = run_cmd(edit_test_cov_cmd(test_cmd, new_test_file_path),timeout)
    if test_timeout or test_result.returncode != 0:
        print("Unable to run or failing tests -- skipping")
        result = test_result.stdout.decode("utf-8") if not test_timeout else "testing timeout"
        return {"status": "FAILED", "reason": {"test": result}}

    # print(pom_file)
    found_jacoco = update_pom_file(pom_file)    

    if found_jacoco == "ERROR":
        print("Unable to run coverage -- skipping")
        return {"status": "FAILED", "reason": {"coverage": "Not able to update POM"}}
    else:
        jacoco_result, jacoco_timeout = run_cmd(edit_test_cov_cmd(['mvn','jacoco:report'], new_test_file_path),timeout)
        if jacoco_timeout or jacoco_result.returncode != 0:
            print("Unable to run coverage -- skipping")
            result = jacoco_result.stdout.decode("utf-8") if not jacoco_timeout else "coverage timeout"
            return {"status": "FAILED", "reason": {"coverage": result}}
        
    file_path = "target/site/jacoco/jacoco.csv" #maven
    print(f"read coverage file {file_path}")
    line_coverage = compute_coverage_java(file_path, source_fn)
    
    return {"status": "SUCCESS", "reason": {"compile": compile_result.stdout.decode("utf-8"), "test": test_result.stdout.decode("utf-8"), "coverage": jacoco_result.stdout.decode("utf-8"),"line_coverage": line_coverage}}


def check_java_gradle_generation(repo_path,compile_cmd,test_cmd,cov_cmd,timeout,new_test_file_path,prompt,source_fn):
    print(f"check_java_gradle {repo_path}")
    build_files = glob.glob(f'{repo_path}/**/build.gradle', recursive=True)
    
    # check if maven
    if len(build_files) == 0:
        print("Not gradle -- skipping")
        return {"status": "FAILED", "reason": "Not gradle"}

    # check single module
    if len(build_files) > 1:
        print("Not single module -- skipping")
        return {"status": "FAILED", "reason": "Multi-module"}

    build_file = build_files[0]
    build_dir = os.path.dirname(build_file)
    os.chdir(build_dir)
    # clean anything that is there

    run_cmd(['gradle', 'clean'],timeout)
    run_cmd(['git', 'clean', "-xdf"],timeout)
    run_cmd(['git', 'reset', "--hard"],timeout)

    if not os.path.exists(os.path.dirname(new_test_file_path)):
        os.system("mkdir -p "+os.path.dirname(new_test_file_path))
    with open(new_test_file_path, "w") as f:
        f.write(prompt)
    f.close()

    compile_result, compile_timeout = run_cmd(compile_cmd,timeout)

    if compile_timeout or compile_result.returncode != 0:
        print("Unable to compile -- skipping")
        result = compile_result.stdout.decode("utf-8") if not compile_timeout else "compiling timeout"
        return {"status": "FAILED", "reason": {"compile":result}}

    test_result, test_timeout = run_cmd(edit_test_cov_cmd(test_cmd, new_test_file_path),timeout)
    if test_timeout or test_result.returncode != 0:
        print("Unable to run or failing tests -- skipping")
        result = test_result.stdout.decode("utf-8") if not test_timeout else "testing timeout"
        return {"status": "FAILED", "reason": {"test": result}}

    update_gradle_file(build_file)    

    jacoco_result, jacoco_timeout = run_cmd(edit_test_cov_cmd(cov_cmd, new_test_file_path),timeout)
    if jacoco_timeout or jacoco_result.returncode != 0:
        print("Unable to run coverage -- skipping")
        result = jacoco_result.stdout.decode("utf-8") if not jacoco_timeout else "coverage timeout"
        return {"status": "FAILED", "reason": {"coverage": result}}

    file_path = "build/reports/jacoco/test/jacocoTestReport.csv" #gradle
    print(f"read coverage file {file_path}")
    line_coverage = compute_coverage_java(file_path, source_fn)

    return {"status": "SUCCESS", "reason": {"compile": compile_result.stdout.decode("utf-8"), "test": test_result.stdout.decode("utf-8"), "coverage": jacoco_result.stdout.decode("utf-8"), "line_coverage": line_coverage}}

def edit_test_cov_cmd(cmd, test_fn):
    test_class = test_fn.split("/")[-1].split(".")[0]
    return cmd + [f"-Dtest={test_class}"]

def run_cmd(cmd,timeout=600):
    if isinstance(cmd, list):
        cmd = " ".join(cmd)
    print(f"Running {cmd}")
    
    try: 
        cmd_output = subprocess.run(cmd, stdout=subprocess.PIPE, timeout=timeout,shell=True)
        
        return cmd_output, False

    except subprocess.TimeoutExpired as e:
        return None, True


def main_java(answers_file, repo_dir,in_image):
    output_file = answers_file.replace(".json", f"_with_{in_image}_result.json")
    with open(answers_file, "r") as f:
        answers = json.load(f)

    for item in answers.keys():
        class_file_path_dir = os.path.dirname(answers[item]["class_file_path"])
        file = answers[item]["file"]
        class_name = answers[item]["class_name"]
        test_file_path = answers[item]["test_file_path"]
        compile_cmd = answers[item]["compile_cmd"]
        test_cmd = answers[item]["test_cmd"]
        cov_cmd = answers[item]["cov_cmd"]
        image = answers[item]["image"]
        if in_image != image:
            print(f"Skipping answer id {item} as it is not in the image")
            continue
        else:
            print(f"Running answer id {item}")

        # code_path = "/PROJ_PATH/evaluation/scripts"
        # user_path = "/cpfs/29583eqvgtdvw5cvegg/data/user"
        org = file.split("_")[1]
        repo = file.split("__")[1].split(".jsonl")[0]
        

        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                output_answers = json.load(f)
        else:
            output_answers = answers

        if "results" not in output_answers[item]:
            output_answers[item]["results"] = {}
        # else:
        #     # print(image)
        #     if image == "java17maven":
        #         print(f"Delete results for {item}")
        #         output_answers[item].pop("results")
        #         with open(output_file, "w") as f:
        #             json.dump(output_answers, f, indent=4,ensure_ascii=False)
        #         continue

        if "init" not in output_answers[item]["results"]:
            print("Running initial test")
            if "maven" in image:
                result = check_java_mvn_init(os.path.join(repo_dir,org,repo),compile_cmd,test_cmd,cov_cmd,600)
            elif "gradle" in image:
                result = check_java_gradle_init(os.path.join(repo_dir,org,repo),compile_cmd,test_cmd,cov_cmd,600)

            output_answers[item]["results"] = {
                "init": {
                    "1": {
                        "init": [result]
                    }
                }
            }
            with open(output_file, "w") as f:
                json.dump(output_answers, f, indent=4,ensure_ascii=False)
        
            print(f"init test finished")

        if "LLM_answers_cleaned" in answers[item]:
            LLM_answers_cleaned = answers[item]["LLM_answers_cleaned"]
        else:
            print("No cleaned answers found")
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
                        elif LLM_answers_cleaned[model][sample_num][prompt] == "NO CODE AVAILABLE":
                            result.append({"status": "FAILED", "reason": "No clean code available"})
                        else:
                            print(f"Running answer id {item} {model} {sample_num} {prompt}")
                            if len(test_file_path) == 0:
                                if class_name+"Test" in LLM_answers_cleaned[model][sample_num][prompt]:
                                    test_class_name = class_name+"Test"
                                elif "Test"+class_name in LLM_answers_cleaned[model][sample_num][prompt]:
                                    test_class_name = "Test"+class_name
                                elif "test_"+class_name in LLM_answers_cleaned[model][sample_num][prompt]:
                                    test_class_name = "test"+class_name
                                elif class_name+"_test" in LLM_answers_cleaned[model][sample_num][prompt]:
                                    test_class_name = class_name+"_test"
                                else:
                                    test_class_name = ""
                                if test_class_name != "":
                                    new_test_file_path = os.path.join(repo_dir,class_file_path_dir.replace("/src/main/java/", "/src/test/java/"), test_class_name+".java")
                                    print(f"checking {org, repo, new_test_file_path}")
                                    
                                    if "maven" in image:
                                        result.append(check_java_mvn_generation(os.path.join(repo_dir,org,repo),compile_cmd,test_cmd,cov_cmd,600,new_test_file_path,LLM_answers_cleaned[model][sample_num][prompt],answers[item]["class_file_path"]))
                                    elif "gradle" in image:
                                        result.append(check_java_gradle_generation(os.path.join(repo_dir,org,repo),compile_cmd,test_cmd,cov_cmd,600,new_test_file_path,LLM_answers_cleaned[model][sample_num][prompt],answers[item]["class_file_path"]))
                                else:
                                    result.append({"status": "FAILED", "reason": "No test class found in answer"})
                            else:
                                new_test_file_path = os.path.join(repo_dir,test_file_path[0])
                                print(f"checking {org, repo, new_test_file_path}")

                                if "maven" in image:
                                    result.append(check_java_mvn_generation(os.path.join(repo_dir,org,repo),compile_cmd,test_cmd,cov_cmd,600,new_test_file_path,LLM_answers_cleaned[model][sample_num][prompt],answers[item]["class_file_path"]))
                                elif "gradle" in image:
                                    result.append(check_java_gradle_generation(os.path.join(repo_dir,org,repo),compile_cmd,test_cmd,cov_cmd,600,new_test_file_path,LLM_answers_cleaned[model][sample_num][prompt],answers[item]["class_file_path"]))

                        output_answers[item]["results"][model][sample_num][prompt] = result
                        with open(output_file, "w") as f:
                            json.dump(output_answers, f, indent=4,ensure_ascii=False)

                        print(f"Finished answer id {item} {model} {sample_num} {prompt}")
                    else:
                        print(f"Skipping answer id {item} {model} {sample_num} {prompt}")
                    

if __name__ == "__main__":

    answers_file = sys.argv[1]
    repo_dir= sys.argv[2]
    in_image = sys.argv[3]
    
    main_java(answers_file, repo_dir,in_image)

    