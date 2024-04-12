import sys
import os
import json
# import subprocess
import gzip
import csv

max_string_length = 12000

def read_gz(path):
    data = []
    input_code = gzip.open(path,"r").readlines()
    for item in input_code:
        data.append(json.loads(item))

    return data


def create_dict(paths):
    codesearchnet = {}
    i = 0
    for path in paths:
        i += 1
        data = read_gz(path)
        for item in data:
            codesearchnet[item['repo']+"/"+item['path']+":"+item['func_name']] = {
                'repo':item['repo'],
                'path':item['path'],
                'code':item['code'],
                'docstring':item['docstring']
            }
        print(f"Finish {i} files")
    
    return codesearchnet

def generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string):
    instruction_text = f"""You are a professional {language} software engineer. An unit test class for a focal method is under development, your task is to generate a new test method for this test class to test new aspects that have not been covered before.
You will be given the following information of the unit test class and its focal method:
1. Source code of the focal method.
2. Source code of the focal class(Code that is not relevant to focal method's execution is filtered).
3. Source code of callee examples of the focal method.
4. Source code of unit test method that is already developed(With imports and dependencies).
You will ONLY return unit test code for the focal method including necessary imports and dependencies, make sure it compile without errors, and use reflection to invoke private methods. 
Note that NO additional explanations required.

Here are the information of the focal method:
1. Source code of the focal method.
{methodCode}

2. Source code of the focal class(Codes that are may not related to focal method are filtered).
{methodTotalCode}

3. Source code of callee examples of the focal method.
{callCode_callees_string}

4. Source code of unit test method that is already developed(With imports and dependencies).
{callCode_tests_string}
"""

    return instruction_text


def create_prompt_method_only(language,methodCode,status):
    methodCode = f"```{language}\n"+methodCode+"\n```"
    methodTotalCode = "No focal class provided."
    callCode_callees_string = "No callee examples provided."
    callCode_tests_string = "No unit test examples provided."
    
    if status == "single":
        instruction_text = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
    elif status == "multi":
        instruction_text = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)

    return instruction_text


def create_prompt_method_class(language,methodCode,methodTotalCode,status):
    methodCode = f"```{language}\n"+methodCode+"\n```"
    methodTotalCode = f"```{language}\n"+methodTotalCode+"\n```"
    callCode_callees_string = "No callee examples provided."
    callCode_tests_string = "No unit test examples provided."
    
    if status == "single":
        instruction_text = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
    elif status == "multi":
        instruction_text = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)

    return instruction_text


def create_prompt_method_class_callee(language,methodCode,methodTotalCode,callCode_callees,status):
    methodCode = f"```{language}\n"+methodCode+"\n```"
    methodTotalCode = f"```{language}\n"+methodTotalCode+"\n```"    
    callCode_callees_string = ""
    callCode_tests_string = "No unit test examples provided."

    instruction_text_1 = ""
    instruction_text_3 = ""

    if len(callCode_callees) == 0:
        instruction_text_1 = ""
        instruction_text_3 = ""
    elif len(callCode_callees) <3:
        callCode_callees_string = f">>>Callee example 1\n```{language}\n"+callCode_callees[0]["totalCode"]+"\n```\n" 
        if status == "single":
            instruction_text_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
        elif status == "multi":
            instruction_text_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
    else:     
        #1_0
        callCode_callees_string = f">>>Callee example 1\n```{language}\n"+callCode_callees[0]["totalCode"]+"\n```\n"
        if status == "single":
            instruction_text_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
        elif status == "multi":
            instruction_text_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
        #3_0
        callCode_callees_string = ""
        for i in range(min(3,len(callCode_callees))):
            callCode_callees_string += f">>>Callee example {i+1}\n```{language}\n"+callCode_callees[i]["totalCode"]+"\n```\n"        
        if status == "single":
            instruction_text_3 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
        elif status == "multi":
            instruction_text_3 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)

    return instruction_text_1, instruction_text_3


def create_prompt_method_class_callee_test(language,methodCode,methodTotalCode,callCode_callees,callCode_tests,status):
    methodCode = f"```{language}\n"+methodCode+"\n```"
    methodTotalCode = f"```{language}\n"+methodTotalCode+"\n```"
    callCode_callees_string = ""
    callCode_tests_string = ""
    instruction_text_0_1 = ""
    instruction_text_0_3 = ""
    instruction_text_1_1 = ""
    instruction_text_1_3 = ""
    instruction_text_3_1 = ""
    instruction_text_3_3 = ""

    if len(callCode_callees) == 0:
        if len(callCode_tests) == 0:
            instruction_text_0_1 = ""
            instruction_text_0_3 = ""
            instruction_text_1_1 = ""
            instruction_text_1_3 = ""
            instruction_text_3_1 = ""
            instruction_text_3_3 = ""
        elif len(callCode_tests) < 3:
            #0_1
            callCode_callees_string = "No callee examples provided."
            callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_0_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_0_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)

        else:
            #0_1
            callCode_callees_string = "No callee examples provided."
            callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_0_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_0_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #0_3
            callCode_tests_string = ""
            for i in range(min(3,len(callCode_tests))):
                callCode_tests_string += f">>>Unit test example {i+1}\n```{language}\n"+callCode_tests[i]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_0_3 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_0_3 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
        
    elif len(callCode_callees) <3:
        if len(callCode_tests) == 0:
            instruction_text_0_1 = ""
            instruction_text_0_3 = ""
            instruction_text_1_1 = ""
            instruction_text_1_3 = ""
            instruction_text_3_1 = ""
            instruction_text_3_3 = ""
        elif len(callCode_tests) < 3:
            #0_1
            callCode_callees_string = "No callee examples provided."
            callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_0_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_0_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #1_1
            callCode_callees_string = f">>>Callee example 1\n```{language}\n"+callCode_callees[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_1_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_1_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
        else:
            #0_1
            callCode_callees_string = "No callee examples provided."
            callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_0_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_0_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #0_3
            callCode_tests_string = ""
            for i in range(min(3,len(callCode_tests))):
                callCode_tests_string += f">>>Unit test example {i+1}\n```{language}\n"+callCode_tests[i]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_0_3 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_0_3 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #1_1
            callCode_callees_string = f">>>Callee example 1\n```{language}\n"+callCode_callees[0]["totalCode"]+"\n```\n"
            callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_1_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_1_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #1_3
            callCode_tests_string = ""
            for i in range(min(3,len(callCode_tests))):
                callCode_tests_string += f">>>Unit test example {i+1}\n```{language}\n"+callCode_tests[i]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_1_3 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_1_3 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)

    else:
        if len(callCode_tests) == 0:
            instruction_text_0_1 = ""
            instruction_text_0_3 = ""
            instruction_text_1_1 = ""
            instruction_text_1_3 = ""
            instruction_text_3_1 = ""
            instruction_text_3_3 = ""
        elif len(callCode_tests) < 3:
            #0_1
            callCode_callees_string = "No callee examples provided."
            callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_0_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_0_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #1_1
            callCode_callees_string = f">>>Callee example 1\n```{language}\n"+callCode_callees[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_1_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_1_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #3_1
            callCode_callees_string = ""
            for i in range(min(3,len(callCode_callees))):
                callCode_callees_string += f">>>Callee example {i+1}\n```{language}\n"+callCode_callees[i]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_3_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_3_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
        else:
            #0_1
            callCode_callees_string = "No callee examples provided."
            callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_0_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_0_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #0_3
            callCode_tests_string = ""
            for i in range(min(3,len(callCode_tests))):
                callCode_tests_string += f">>>Unit test example {i+1}\n```{language}\n"+callCode_tests[i]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_0_3 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_0_3 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #1_1
            callCode_callees_string = f">>>Callee example 1\n```{language}\n"+callCode_callees[0]["totalCode"]+"\n```\n"
            callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_1_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_1_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #1_3
            callCode_tests_string = ""
            for i in range(min(3,len(callCode_tests))):
                callCode_tests_string += f">>>Unit test example {i+1}\n```{language}\n"+callCode_tests[i]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_1_3 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_1_3 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #3_1
            callCode_callees_string = ""
            for i in range(min(3,len(callCode_callees))):
                callCode_callees_string += f">>>Callee example {i+1}\n```{language}\n"+callCode_callees[i]["totalCode"]+"\n```\n"
            callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_3_1 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_3_1 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            #3_3
            callCode_tests_string = ""
            for i in range(min(3,len(callCode_tests))):
                callCode_tests_string += f">>>Unit test example {i+1}\n```{language}\n"+callCode_tests[i]["totalCode"]+"\n```\n"
            if status == "single":
                instruction_text_3_3 = generate_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
            elif status == "multi":
                instruction_text_3_3 = generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string)
              
            
    return instruction_text_0_1, instruction_text_0_3, instruction_text_1_1, instruction_text_1_3, instruction_text_3_1, instruction_text_3_3
    
def generate_multi_test_prompt(language,methodCode,methodTotalCode,callCode_callees_string,callCode_tests_string):
    instruction_text = f"""You are a professional {language} software engineer. You are asked to generate a complete test class for a focal method in a focal class.
You will be given the following information of the focal method:
1. Source code of the focal method.
2. Source code of the focal class(Code that is not relevant to focal method's execution is filtered).
3. Source code of callee examples of the focal method.
4. Source code of unit test method that is already developed(With imports and dependencies).
You will ONLY return unit test code for the focal method including necessary imports and dependencies, make sure it compile without errors, and use reflection to invoke private methods. 
Note that no additional explanations required.

Here are the information of the focal method:
1. Source code of the focal method.
{methodCode}

2. Source code of the focal class(Codes that are may not related to focal method are filtered).
{methodTotalCode}

3. Source code of callee examples of the focal method.
{callCode_callees_string}

4. Source code of unit test method that is already developed(With imports and dependencies).
{callCode_tests_string}

Please note that the test class you return should include multiple test cases covering different functionalities. There is no upper limit on the number of test cases, but you need to ensure that the test cases provide high test coverage and test extreme and special cases of the code as much as possible.
"""
    return instruction_text


def single_unit_test(language,input_path,output_path):
    output_dict = {}
    statistics_csv = []
    statistics_csv.append([ "id",
                            "file",
                            "class_name",
                            "class_file_path",
                            "method_name",
                            "callee_num",
                            "test_num",
                            "test_file_path",
                            "prompt_method_only",
                            "prompt_method_class",
                            "prompt_method_class_callee_1",
                            "prompt_method_class_callee_3",
                            "prompt_method_class_callee_0_test_1",
                            "prompt_method_class_callee_0_test_3",
                            "prompt_method_class_callee_1_test_1",
                            "prompt_method_class_callee_1_test_3",
                            "prompt_method_class_callee_3_test_1",
                            "prompt_method_class_callee_3_test_3",
                            "compile_cmd", 
                            "test_cmd",
                            "cov_cmd",
                            "image"])
    processed_num = 0

    for file in os.listdir(input_path):
        if file.endswith(".jsonl"):
            with open(os.path.join(input_path,file), "r") as f:
                #读取jsonl文件
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    #将json字符串转换为字典
                    json_dict = eval(line)
                    class_name = json_dict["className"]
                    class_file_path = json_dict["path"]
                    methodAndParams = json_dict["methodAndParams"]
                    compile_cmd = []
                    test_cmd = []
                    cov_cmd = []
                    image = ""
                    for methodAndParam in methodAndParams:
                        processed_num += 1

                        methodName = methodAndParam["methodName"]
                        methodCode = methodAndParam["methodCode"]
                        methodTotalCode = methodAndParam["totalCode"]
                        # calleeTotalCallCodes = methodAndParams["calleeTotalCallCodes"]
                        calleeSingleCallCodes = methodAndParam["calleeSingleCallCodes"]
                        # testTotalCallCodes = methodAndParams["testTotalCallCodes"]
                        testSingleCallCodes = methodAndParam["testSingleCallCodes"]
                        
                        # filtered_calleeTotalCallCodes = []
                        filtered_calleeSingleCallCodes = []
                        # filtered_testTotalCallCodes = []
                        filtered_testSingleCallCodes = []

                        for calleeSingleCallCode in calleeSingleCallCodes:
                            callClass = calleeSingleCallCode["callClass"]
                            if len(calleeSingleCallCode["totalCode"]) > max_string_length:
                                #过滤字符数>12000的代码
                                continue
                            elif "test" in callClass.lower():
                                #测试代码不属于callee，去除
                                continue
                            else:
                                #属于callee
                                filtered_calleeSingleCallCodes.append(calleeSingleCallCode)

                        test_file_path = []
                        for testSingleCallCode in testSingleCallCodes:
                            callClass = testSingleCallCode['callClass']
                            
                            if len(testSingleCallCode["totalCode"]) > max_string_length:
                                #过滤字符数>12000的代码
                                continue
                            else:
                                #属于test
                                if language == "java":
                                    if "@Test" in testSingleCallCode["code"]:
                                        filtered_testSingleCallCodes.append(testSingleCallCode)
                                        test_file_path.append(testSingleCallCode['callPath'])
                                if language == "python":
                                    # 消融实验需要确保没有python自带包的代码
                                    if "python3." not in json_dict['path'] and "python2." not in json_dict['path']:
                                        if class_name in callClass:
                                            if "assert" in testSingleCallCode["code"]:
                                                filtered_testSingleCallCodes.append(testSingleCallCode)
                                                test_file_path.append(testSingleCallCode['callPath'])
                        

                        callee_num = len(filtered_calleeSingleCallCodes)
                        test_num = len(filtered_testSingleCallCodes)

                        #只有method，没有上下文
                        prompt_method_only = create_prompt_method_only(language,methodCode,"single")
                        #有method和class，没有callee和test
                        prompt_method_class = create_prompt_method_class(language,methodCode,methodTotalCode,"single")
                        #有method和class，有callee，没有test
                        prompt_method_class_callee_1, prompt_method_class_callee_3= create_prompt_method_class_callee(language,methodCode,methodTotalCode,filtered_calleeSingleCallCodes,"single")
                        #有method和class，有callee，有test
                        prompt_method_class_callee_0_test_1, prompt_method_class_callee_0_test_3, prompt_method_class_callee_1_test_1, prompt_method_class_callee_1_test_3, prompt_method_class_callee_3_test_1, prompt_method_class_callee_3_test_3= create_prompt_method_class_callee_test(language,methodCode,methodTotalCode,filtered_calleeSingleCallCodes,filtered_testSingleCallCodes,"single")

                        prompt_method_only_status = True if len(prompt_method_only) > 0 else False
                        prompt_method_class_status = True if len(prompt_method_class) > 0 else False
                        prompt_method_class_callee_1_status = True if len(prompt_method_class_callee_1) > 0 else False
                        prompt_method_class_callee_3_status = True if len(prompt_method_class_callee_3) > 0 else False
                        prompt_method_class_callee_0_test_1_status = True if len(prompt_method_class_callee_0_test_1) > 0 else False
                        prompt_method_class_callee_0_test_3_status = True if len(prompt_method_class_callee_0_test_3) > 0 else False
                        prompt_method_class_callee_1_test_1_status = True if len(prompt_method_class_callee_1_test_1) > 0 else False
                        prompt_method_class_callee_1_test_3_status = True if len(prompt_method_class_callee_1_test_3) > 0 else False
                        prompt_method_class_callee_3_test_1_status = True if len(prompt_method_class_callee_3_test_1) > 0 else False
                        prompt_method_class_callee_3_test_3_status = True if len(prompt_method_class_callee_3_test_3) > 0 else False

                        if prompt_method_only_status and prompt_method_class_status and prompt_method_class_callee_1_status and prompt_method_class_callee_3_status and prompt_method_class_callee_0_test_1_status and prompt_method_class_callee_0_test_3_status and prompt_method_class_callee_1_test_1_status and prompt_method_class_callee_1_test_3_status and prompt_method_class_callee_3_test_1_status and prompt_method_class_callee_3_test_3_status:
                            output_dict[processed_num] = {
                                "id" : processed_num,
                                "file": file,
                                "class_name": class_name,
                                "class_file_path": class_file_path,
                                "method_name": methodName,
                                "callee_num": callee_num,
                                "test_num": test_num,
                                "test_file_path" : test_file_path,
                                "prompts":{
                                    "prompt_method_only": prompt_method_only,
                                    "prompt_method_class": prompt_method_class,
                                    "prompt_method_class_callee_1": prompt_method_class_callee_1,
                                    "prompt_method_class_callee_3": prompt_method_class_callee_3,
                                    "prompt_method_class_callee_0_test_1": prompt_method_class_callee_0_test_1,
                                    "prompt_method_class_callee_0_test_3": prompt_method_class_callee_0_test_3,
                                    "prompt_method_class_callee_1_test_1": prompt_method_class_callee_1_test_1,
                                    "prompt_method_class_callee_1_test_3": prompt_method_class_callee_1_test_3,
                                    "prompt_method_class_callee_3_test_1": prompt_method_class_callee_3_test_1,
                                    "prompt_method_class_callee_3_test_3": prompt_method_class_callee_3_test_3
                                },
                                "compile_cmd": compile_cmd, 
                                "test_cmd": test_cmd,
                                "cov_cmd": cov_cmd,
                                "image": image
                            }

                       
                            statistics_csv.append([processed_num,
                                                file,
                                                    class_name,
                                                    class_file_path,
                                                    methodName,
                                                    callee_num,
                                                    test_num,
                                                    test_file_path,
                                                    prompt_method_only_status,
                                                    prompt_method_class_status,
                                                    prompt_method_class_callee_1_status,
                                                    prompt_method_class_callee_3_status,
                                                    prompt_method_class_callee_0_test_1_status,
                                                    prompt_method_class_callee_0_test_3_status,
                                                    prompt_method_class_callee_1_test_1_status,
                                                    prompt_method_class_callee_1_test_3_status,
                                                    prompt_method_class_callee_3_test_1_status,
                                                    prompt_method_class_callee_3_test_3_status,
                                                    compile_cmd, 
                                                    test_cmd,
                                                    cov_cmd,
                                                    image
                                                ])
                                
    print(f"Writting to file...")
    with open(os.path.join(output_path,"single_unit_test.json"), "w") as f:
        json.dump(output_dict,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"single_unit_test.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerows(statistics_csv)

def multi_unit_test(language,input_path,output_path):
    output_dict = {}
    statistics_csv = []
    statistics_csv.append([ "id",
                            "file",
                            "class_name",
                            "class_file_path",
                            "method_name",
                            "callee_num",
                            "test_num",
                            "test_file_path",
                            "prompt_method_only",
                            "prompt_method_class",
                            "prompt_method_class_callee_1",
                            "prompt_method_class_callee_3",
                            "prompt_method_class_callee_0_test_1",
                            "prompt_method_class_callee_0_test_3",
                            "prompt_method_class_callee_1_test_1",
                            "prompt_method_class_callee_1_test_3",
                            "prompt_method_class_callee_3_test_1",
                            "prompt_method_class_callee_3_test_3",
                            "compile_cmd",
                            "test_cmd",
                            "cov_cmd",
                            "image"])

    processed_num = 0
    for file in os.listdir(input_path):
        if file.endswith(".jsonl"):
            with open(os.path.join(input_path,file), "r") as f:
                #读取jsonl文件
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    #将json字符串转换为字典
                    json_dict = eval(line)
                    class_name = json_dict["className"]
                    class_file_path = json_dict["path"]
                    methodAndParams = json_dict["methodAndParams"]
                    compile_cmd = []
                    test_cmd = []
                    cov_cmd = []
                    image = ""

                    for methodAndParam in methodAndParams:
                        processed_num += 1
                        
                        methodName = methodAndParam["methodName"]
                        methodCode = methodAndParam["methodCode"]
                        methodTotalCode = methodAndParam["totalCode"]
                        # calleeTotalCallCodes = methodAndParams["calleeTotalCallCodes"]
                        calleeSingleCallCodes = methodAndParam["calleeSingleCallCodes"]
                        testTotalCallCodes = methodAndParam["testTotalCallCodes"]
                        # testSingleCallCodes = methodAndParams["testSingleCallCodes"]
                        
                        # filtered_calleeTotalCallCodes = []
                        filtered_calleeSingleCallCodes = []
                        filtered_testTotalCallCodes = []
                        # filtered_testSingleCallCodes = []
                    
                        for calleeSingleCallCode in calleeSingleCallCodes:
                            callClass = calleeSingleCallCode["callClass"]
                            if len(calleeSingleCallCode["totalCode"]) > max_string_length:
                                #过滤字符数>12000的代码
                                continue
                            elif "test" in callClass.lower():
                                #测试代码不属于callee，去除
                                continue
                            else:
                                #属于callee
                                filtered_calleeSingleCallCodes.append(calleeSingleCallCode)

                        test_file_path = []
                        for testTotalCallCode in testTotalCallCodes:
                            callClass = testTotalCallCode['callClass']

                            if len(testTotalCallCode["totalCode"]) > max_string_length:
                                #过滤字符数>12000的代码
                                continue
                            else:
                                #属于test
                                if language == "java":
                                    if "@Test" in testTotalCallCode["totalCode"]:
                                        filtered_testTotalCallCodes.append(testTotalCallCode)
                                        test_file_path.append(testTotalCallCode['callPath'])
                                if language == "python":
                                    # 消融实验需要确保没有python自带包的代码
                                    if "python3." not in json_dict['path'] and "python2." not in json_dict['path']:
                                        if class_name in callClass:
                                            if "assert" in testTotalCallCode["totalCode"]:
                                                filtered_testTotalCallCodes.append(testTotalCallCode)
                                                test_file_path.append(testTotalCallCode['callPath'])
                        
                        callee_num = len(filtered_calleeSingleCallCodes)
                        test_num = len(filtered_testTotalCallCodes)

                         #只有method，没有上下文
                        prompt_method_only = create_prompt_method_only(language,methodCode,"multi")
                        #有method和class，没有callee和test
                        prompt_method_class = create_prompt_method_class(language,methodCode,methodTotalCode,"multi")
                        #有method和class，有callee，没有test
                        prompt_method_class_callee_1, prompt_method_class_callee_3= create_prompt_method_class_callee(language,methodCode,methodTotalCode,filtered_calleeSingleCallCodes,"multi")
                        #有method和class，有callee，有test
                        prompt_method_class_callee_0_test_1, prompt_method_class_callee_0_test_3, prompt_method_class_callee_1_test_1, prompt_method_class_callee_1_test_3, prompt_method_class_callee_3_test_1, prompt_method_class_callee_3_test_3= create_prompt_method_class_callee_test(language,methodCode,methodTotalCode,filtered_calleeSingleCallCodes,filtered_testTotalCallCodes,"multi")

                        prompt_method_only_status = True if len(prompt_method_only) > 0 else False
                        prompt_method_class_status = True if len(prompt_method_class) > 0 else False
                        prompt_method_class_callee_1_status = True if len(prompt_method_class_callee_1) > 0 else False
                        prompt_method_class_callee_3_status = True if len(prompt_method_class_callee_3) > 0 else False
                        prompt_method_class_callee_0_test_1_status = True if len(prompt_method_class_callee_0_test_1) > 0 else False
                        prompt_method_class_callee_0_test_3_status = True if len(prompt_method_class_callee_0_test_3) > 0 else False
                        prompt_method_class_callee_1_test_1_status = True if len(prompt_method_class_callee_1_test_1) > 0 else False
                        prompt_method_class_callee_1_test_3_status = True if len(prompt_method_class_callee_1_test_3) > 0 else False
                        prompt_method_class_callee_3_test_1_status = True if len(prompt_method_class_callee_3_test_1) > 0 else False
                        prompt_method_class_callee_3_test_3_status = True if len(prompt_method_class_callee_3_test_3) > 0 else False

                        if prompt_method_only_status and prompt_method_class_status and prompt_method_class_callee_1_status and prompt_method_class_callee_3_status and prompt_method_class_callee_0_test_1_status and prompt_method_class_callee_0_test_3_status and prompt_method_class_callee_1_test_1_status and prompt_method_class_callee_1_test_3_status and prompt_method_class_callee_3_test_1_status and prompt_method_class_callee_3_test_3_status:

                            output_dict[processed_num] = {
                                "id" : processed_num,
                                "file": file,
                                "class_name": class_name,
                                "class_file_path": class_file_path,
                                "method_name": methodName,
                                "callee_num": callee_num,
                                "test_num": test_num,
                                "test_file_path" : test_file_path,
                                "prompts":{
                                    "prompt_method_only": prompt_method_only,
                                    "prompt_method_class": prompt_method_class,
                                    "prompt_method_class_callee_1": prompt_method_class_callee_1,
                                    "prompt_method_class_callee_3": prompt_method_class_callee_3,
                                    "prompt_method_class_callee_0_test_1": prompt_method_class_callee_0_test_1,
                                    "prompt_method_class_callee_0_test_3": prompt_method_class_callee_0_test_3,
                                    "prompt_method_class_callee_1_test_1": prompt_method_class_callee_1_test_1,
                                    "prompt_method_class_callee_1_test_3": prompt_method_class_callee_1_test_3,
                                    "prompt_method_class_callee_3_test_1": prompt_method_class_callee_3_test_1,
                                    "prompt_method_class_callee_3_test_3": prompt_method_class_callee_3_test_3
                                },
                                "compile_cmd": compile_cmd,
                                "test_cmd": test_cmd,
                                "cov_cmd": cov_cmd,
                                "image": image
                            }          

                        

                            statistics_csv.append([processed_num,
                                                file,
                                                    class_name,
                                                    class_file_path,
                                                    methodName,
                                                    callee_num,
                                                    test_num,
                                                    test_file_path,
                                                    prompt_method_only_status,
                                                    prompt_method_class_status,
                                                    prompt_method_class_callee_1_status,
                                                    prompt_method_class_callee_3_status,
                                                    prompt_method_class_callee_0_test_1_status,
                                                    prompt_method_class_callee_0_test_3_status,
                                                    prompt_method_class_callee_1_test_1_status,
                                                    prompt_method_class_callee_1_test_3_status,
                                                    prompt_method_class_callee_3_test_1_status,
                                                    prompt_method_class_callee_3_test_3_status,
                                                    compile_cmd,
                                                    test_cmd,
                                                    cov_cmd,
                                                    image
                                                ])

    print(f"Writting to file...")
    with open(os.path.join(output_path,"multi_unit_test.json"), "w") as f:
        json.dump(output_dict,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"multi_unit_test.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerows(statistics_csv)


if __name__ == "__main__":
    language = "java" if len(sys.argv) < 2 else sys.argv[1] 
    input_path = sys.argv[2]
    output_path =  sys.argv[3]

    single_unit_test(language,input_path,output_path)
    multi_unit_test(language,input_path,output_path)

