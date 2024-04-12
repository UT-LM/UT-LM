import sys
import os
import json
import subprocess
import gzip

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


def create_codesearchnet_dict(codesearchnet_path):
    if os.path.exists(codesearchnet_path):
        os.chdir(codesearchnet_path)
    else:
        print("No such directory for codesearchnet")
        return 
    try:
        paths = subprocess.check_output(['find', '-name', '*.jsonl.gz'])
        paths = paths.decode('ascii').splitlines()
        paths = [path.replace("./", "") for path in paths]
    except:
        print("Error during find jsonl.gz file" + '\n')
        return 
    else:
        print(f"Creating codesearchnet dict with {len(paths)} files")
        codesearchnet = create_dict(paths)
    return codesearchnet

def create_exclude_repo_dict(exclude_repo_path):
    exclude_repo = {}
    with open(exclude_repo_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            owner = line.split(":")[1].strip().split("/")[-2]
            repo = line.split(":")[1].strip().split("/")[-1]
            exclude_repo[owner+"__"+repo] = "1"
    return exclude_repo


def create_prompt_few_shot(language,methodCode,methodTotalCode,callCode_tests,callCode_callees):
    methodCode = f"```{language}\n"+methodCode+"\n```"
    methodTotalCode = f"```{language}\n"+methodTotalCode+"\n```"
    callCode_callees_string = ""
    while len(callCode_callees) > 0:
        #只取前3个callee examples
        for i in range(min(3,len(callCode_callees))):
            callCode_callees_string += f">>>Callee example {i+1}\n```{language}\n"+callCode_callees[i]["totalCode"]+"\n```\n"        
        if len(callCode_callees_string) <= max_string_length:
            break
        else:
            callCode_callees.pop(0)
            callCode_callees_string = ""
    if len(callCode_callees) == 0:
        callCode_callees_string = "No callee examples provided."
    callCode_tests_string = ""

    #few-shot 只取前3个unit test examples
    while len(callCode_tests) > 1:
        for i in range(0,len(callCode_tests)-1):
            callCode_tests_string += f">>>Unit test example {i+1}\n```{language}\n"+callCode_tests[i]["totalCode"]+"\n```\n"
        if len(callCode_tests_string) <= max_string_length:
            break
        else:
            callCode_tests.pop(0)
            callCode_tests_string = ""
    if len(callCode_tests) == 1:
        callCode_tests_string += f"No unit test examples provided."
    
    conversations = []
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
    conversations.append({
        "from": "### Instruction",
        "value": instruction_text
    })
    #response取最后unit test
    response_text = f"```{language}\n"+callCode_tests[-1]["totalCode"]+"\n```\n"
    conversations.append({
        "from": "### Response",
        "value": response_text
    })

    return conversations


def create_prompt_one_shot(language,methodCode,methodTotalCode,callCode_tests,callCode_callees):
    methodCode = f"```{language}\n"+methodCode+"\n```"
    methodTotalCode = f"```{language}\n"+methodTotalCode+"\n```"
    callCode_callees_string = ""
    while len(callCode_callees) > 0:
        #只取前3个callee examples
        for i in range(min(3,len(callCode_callees))):
            callCode_callees_string += f">>>Callee example {i+1}\n```{language}\n"+callCode_callees[i]["totalCode"]+"\n```\n"        
        if len(callCode_callees_string) <= max_string_length:
            break
        else:
            callCode_callees.pop(0)
            callCode_callees_string = ""
    if len(callCode_callees) == 0:
        callCode_callees_string = "No callee examples provided."

    #one-shot 只取第1个unit test examples
    callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
    
    conversations = []
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
    conversations.append({
        "from": "### Instruction",
        "value": instruction_text
    })
    #response取第2个unit test
    response_text = f"```{language}\n"+callCode_tests[1]["totalCode"]+"\n```\n"
    conversations.append({
        "from": "### Response",
        "value": response_text
    })

    return conversations
    
def create_prompt_zero_shot(language,methodCode,methodTotalCode,callCode_tests,callCode_callees):
    methodCode = f"```{language}\n"+methodCode+"\n```"
    methodTotalCode = f"```{language}\n"+methodTotalCode+"\n```"
    callCode_callees_string = ""
    while len(callCode_callees) > 0:
        #只取前3个callee examples
        for i in range(min(3,len(callCode_callees))):
            callCode_callees_string += f">>>Callee example {i+1}\n```{language}\n"+callCode_callees[i]["totalCode"]+"\n```\n"        
        if len(callCode_callees_string) <= max_string_length:
            break
        else:
            callCode_callees.pop(0)
            callCode_callees_string = ""
    if len(callCode_callees) == 0:
        callCode_callees_string = "No callee examples provided."
    callCode_tests_string = ""

    #zero-shot不提供unit test examples 
    callCode_tests_string = "No unit test examples provided."
    
    conversations = []
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
    conversations.append({
        "from": "### Instruction",
        "value": instruction_text
    })
    #response取第1个unit test
    response_text = f"```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
    conversations.append({
        "from": "### Response",
        "value": response_text
    })

    return conversations

def create_tdd1_prompt_zero_shot(language,doctring,callCode_tests):
    #zero-shot不提供unit test examples 
    callCode_tests_string = "No unit test examples provided."
    
    conversations = []
    instruction_text = f"""You are a professional {language} software engineer proficient in utilizing the Test-Driven Development (TDD) methodology. Your development process consists of two steps: first, generating test cases based on natural language requirements, and second, creating functional code.
Currently, you're embarking on the first step and a unit test class for a requirement is under development, your task is to generate a new test method for this test class to test new aspects that have not been covered before.
You'll be provided with the following information:
1. A development requirement described in natural language.
2. Source code of unit test method that is already developed(With imports and dependencies).
You will ONLY return unit test code including necessary imports and dependencies, make sure it compile without errors, use reflection to invoke private methods, and won't test scenarios beyond the stated development requirement. 
Note that no additional explanations required.

Here are the information:
1. A development requirement described in natural language.
{doctring}

2. Source code of unit test method that is already developed(With imports and dependencies).
{callCode_tests_string}
"""
    conversations.append({
        "from": "### Instruction",
        "value": instruction_text
    })
    #response取第1个unit test
    response_text = f"```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
    conversations.append({
        "from": "### Response",
        "value": response_text
    })

    return conversations

def create_tdd1_prompt_one_shot(language,doctring,callCode_tests):
    #one-shot 只取第1个unit test examples
    callCode_tests_string = f">>>Unit test example 1\n```{language}\n"+callCode_tests[0]["totalCode"]+"\n```\n"
    
    conversations = []
    instruction_text = f"""You are a professional {language} software engineer proficient in utilizing the Test-Driven Development (TDD) methodology. Your development process consists of two steps: first, generating test cases based on natural language requirements, and second, creating functional code.
Currently, you're embarking on the first step and a unit test class for a requirement is under development, your task is to generate a new test method for this test class to test new aspects that have not been covered before.
You'll be provided with the following information:
1. A development requirement described in natural language.
2. Source code of unit test method that is already developed(With imports and dependencies).
You will ONLY return unit test code including necessary imports and dependencies, make sure it compile without errors, use reflection to invoke private methods, and won't test scenarios beyond the stated development requirement. 
Note that no additional explanations required.

Here are the information:
1. A development requirement described in natural language.
{doctring}

2. Source code of unit test method that is already developed(With imports and dependencies).
{callCode_tests_string}
"""
    conversations.append({
        "from": "### Instruction",
        "value": instruction_text
    })
    #response取第2个unit test
    response_text = f"```{language}\n"+callCode_tests[1]["totalCode"]+"\n```\n"
    conversations.append({
        "from": "### Response",
        "value": response_text
    })

    return conversations

def create_tdd1_prompt_few_shot(language,doctring,callCode_tests):
    #few-shot 只取前3个unit test examples
    callCode_tests_string = ""
    while len(callCode_tests) > 1:
        for i in range(0,len(callCode_tests)-1):
            callCode_tests_string += f">>>Unit test example {i+1}\n```{language}\n"+callCode_tests[i]["totalCode"]+"\n```\n"
        if len(callCode_tests_string) <= max_string_length:
            break
        else:
            callCode_tests.pop(0)
            callCode_tests_string = ""
    if len(callCode_tests) == 1:
        callCode_tests_string += f"No unit test examples provided."
    conversations = []
    instruction_text = f"""You are a professional {language} software engineer proficient in utilizing the Test-Driven Development (TDD) methodology. Your development process consists of two steps: first, generating test cases based on natural language requirements, and second, creating functional code.
Currently, you're embarking on the first step and a unit test class for a requirement is under development, your task is to generate a new test method for this test class to test new aspects that have not been covered before.
You'll be provided with the following information:
1. A development requirement described in natural language.
2. Source code of unit test method that is already developed(With imports and dependencies).
You will ONLY return unit test code including necessary imports and dependencies, make sure it compile without errors, use reflection to invoke private methods, and won't test scenarios beyond the stated development requirement. 
Note that no additional explanations required.

Here are the information:
1. A development requirement described in natural language.
{doctring}

2. Source code of unit test method that is already developed(With imports and dependencies).
{callCode_tests_string}
"""
    conversations.append({
        "from": "### Instruction",
        "value": instruction_text
    })
    #response只取最后unit test
    response_text = f"```{language}\n"+callCode_tests[-1]["totalCode"]+"\n```\n"
    conversations.append({
        "from": "### Response",
        "value": response_text
    })

    return conversations

def create_tdd2_prompt(language,doctring,methodTotalCode,callCode_test):
    callCode_tests_string = f"```{language}\n"+callCode_test+"\n```\n"
    
    conversations = []
    instruction_text = f"""You are a professional {language} software engineer proficient in utilizing the Test-Driven Development (TDD) methodology. Your development process consists of two steps: first, generating test cases based on natural language requirements, and second, creating functional code that ensures passing those test cases.
Currently, you're embarking on the Second step, which involves generating functional code that ensures passing of all tests and can be directly executed.
You'll be provided with the following information:
1. A development requirement described in natural language.
2. Test cases generated by you in the first step of TDD development based on the aforementioned requirement.
You will ONLY return functional code including necessary imports and dependencies, make sure it compile without errors, use reflection to invoke private methods. 
Note that no additional explanations required.

Here are the information:
1. A development requirement described in natural language.
{doctring}

2. Test cases generated by you in the first step of TDD development based on the aforementioned requirement.
{callCode_tests_string}
"""
    conversations.append({
        "from": "### Instruction",
        "value": instruction_text
    })
    #response取第1个unit test
    response_text = f"```{language}\n"+methodTotalCode+"\n```"
    conversations.append({
        "from": "### Response",
        "value": response_text
    })

    return conversations

def create_prompt_multi_unit_test_zero_shot(language,methodCode,methodTotalCode,callCode_test,callCode_callees):
    methodCode = f"```{language}\n"+methodCode+"\n```"
    methodTotalCode = f"```{language}\n"+methodTotalCode+"\n```"
    callCode_callees_string = ""
    while len(callCode_callees) > 0:
        #只取前3个callee examples
        for i in range(min(3,len(callCode_callees))):
            callCode_callees_string += f">>>Callee example {i+1}\n```{language}\n"+callCode_callees[i]["totalCode"]+"\n```\n"        
        if len(callCode_callees_string) <= max_string_length:
            break
        else:
            callCode_callees.pop(0)
            callCode_callees_string = ""
    if len(callCode_callees) == 0:
        callCode_callees_string = "No callee examples provided."

    conversations = []
    instruction_text = f"""You are a professional {language} software engineer. You are asked to generate a complete test class for a focal method in a focal class.
You will be given the following information of the focal method:
1. Source code of the focal method.
2. Source code of the focal class(Code that is not relevant to focal method's execution is filtered).
3. Source code of callee examples of the focal method.
You will ONLY return unit test code for the focal method including necessary imports and dependencies, make sure it compile without errors, and use reflection to invoke private methods. 
Note that no additional explanations required.

Here are the information of the focal method:
1. Source code of the focal method.
{methodCode}

2. Source code of the focal class(Codes that are may not related to focal method are filtered).
{methodTotalCode}

3. Source code of callee examples of the focal method.
{callCode_callees_string}

Please note that the test class you return should include multiple test cases covering different functionalities. There is no upper limit on the number of test cases, but you need to ensure that the test cases provide high test coverage and test extreme and special cases of the code as much as possible.
"""
    conversations.append({
        "from": "### Instruction",
        "value": instruction_text
    })
    #response取第1个unit test
    response_text = f"```{language}\n"+callCode_test+"\n```\n"
    conversations.append({
        "from": "### Response",
        "value": response_text
    })

    return conversations

def create_tdd1_prompt_multi_unit_test_zero_shot(language,doctring,callCode_test):
    #zero-shot不提供unit test examples 
    callCode_tests_string = "No unit test examples provided."
    
    conversations = []
    instruction_text = f"""You are a professional {language} software engineer proficient in utilizing the Test-Driven Development (TDD) methodology. Your development process consists of two steps: first, generating test cases based on natural language requirements, and second, creating functional code.
Currently, you're embarking on the first step, where you'll derive a complete test class for a focal method from a development requirement described in natural language.
You will ONLY return unit test code including necessary imports and dependencies, make sure it compile without errors, use reflection to invoke private methods, and won't test scenarios beyond the stated development requirement. 
Note that no additional explanations required.

Here are the development requirement described in natural language:
{doctring}

Please note that the test class you return should include multiple test cases covering different functionalities. There is no upper limit on the number of test cases, but you need to ensure that the test cases provide high test coverage and test extreme and special cases of the code as much as possible.
"""
    conversations.append({
        "from": "### Instruction",
        "value": instruction_text
    })
    #response取第1个unit test
    response_text = f"```{language}\n"+callCode_test+"\n```\n"
    conversations.append({
        "from": "### Response",
        "value": response_text
    })

    return conversations

def single_unit_test(language,input_path,output_path,codesearchnet_path,exclude_repo_path):
    codesearchnet_dict = create_codesearchnet_dict(codesearchnet_path)
    exclude_repo_dict = create_exclude_repo_dict(exclude_repo_path)
    check_num_zero_shot = 0
    check_num_one_shot = 0
    check_num_few_shot = 0
    check_num_zero_shot_tdd1 = 0
    check_num_one_shot_tdd1 = 0
    check_num_few_shot_tdd1 = 0
    check_num_tdd2 = 0
    num_zero_shot = 0
    num_one_shot = 0
    num_few_shot = 0
    num_zero_shot_tdd1 = 0
    num_one_shot_tdd1 = 0
    num_few_shot_tdd1 = 0
    num_tdd2 = 0
    prompts_zero_shot = []
    prompts_one_shot = []
    prompts_few_shot = []
    prompts_zero_shot_tdd1 = []
    prompts_one_shot_tdd1 = []
    prompts_few_shot_tdd1 = []
    prompts_tdd2 = []

    exclude_repo = []
    processed_num = 0
    # prompts_zero_shot = []
    # prompts_one_shot = []
    # prompts_few_shot = []
    # prompts_zero_shot_tdd1 = []
    # prompts_one_shot_tdd1 = []
    # prompts_few_shot_tdd1 = []
    # prompts_tdd2 = []
    for dir in os.listdir(input_path):
        if not os.path.isdir(os.path.join(input_path,dir)):
            continue
        for file in os.listdir(os.path.join(input_path,dir)):
            if file.endswith(".jsonl"):
                processed_num += 1
                if processed_num % 1000 == 0:
                    print(f"Processing {processed_num} in {dir}")
                owner_repo = file.split(".jsonl")[0].split("filepairs_")[1]
                if owner_repo in exclude_repo_dict.keys():
                    #排除指定repo
                    print(f"Exclude {owner_repo}")
                    exclude_repo.append({owner_repo:"1"})
                    continue
                with open(os.path.join(input_path,dir,file), "r") as f:
                    #读取jsonl文件
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if len(line) == 0:
                            continue
                        #将json字符串转换为字典
                        json_dict = eval(line)
                        class_name = json_dict["className"]
                        file_path = json_dict["path"]
                        methodAndParams = json_dict["methodAndParams"]
                        for methodAndParam in methodAndParams:
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
                            
                            if len(testSingleCallCodes) == 0:
                                continue
                                
                            # for calleeTotalCallCode in calleeTotalCallCodes:
                            #     callClass = calleeTotalCallCode["callClass"]
                            #     if len(calleeTotalCallCode["totalCode"]) > max_string_length:
                            #         #过滤字符数>12000的代码
                            #         continue
                            #     elif "test" in callClass.lower():
                            #         #测试代码不属于callee，去除
                            #         continue
                            #     else:
                            #         #属于callee
                            #         filtered_calleeTotalCallCodes.append(calleeTotalCallCode)

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

                            # for testTotalCallCode in testTotalCallCodes:
                            #     callClass = testTotalCallCode['callClass']
                            #     if len(testTotalCallCode["totalCode"]) > max_string_length:
                            #         #过滤字符数>12000的代码
                            #         continue
                            #     else:
                            #         #属于test
                            #         filtered_testTotalCallCodes.append(testTotalCallCode)
                            
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
                                    if language == "python":
                                        file_name = file_path.split("/")[-1].split(".py")[0]
                                        test_file_name = callClass
                                        if file_name in test_file_name:
                                            if "assert" in testSingleCallCode["code"]:
                                                filtered_testSingleCallCodes.append(testSingleCallCode)
                        
                            if language == "java":
                                index_string = json_dict['path'] + ":" + class_name+"."+methodName
                            elif language == "python":
                                index_string1 = json_dict['path']+ ":" +class_name + "." + methodName
                                index_string2 = json_dict['path'] + ":" + methodName
                                if index_string1 in codesearchnet_dict.keys():
                                    index_string = index_string1
                                elif index_string2 in codesearchnet_dict.keys():
                                    index_string = index_string2
                                else:
                                    index_string = ""
                            
                            if len(filtered_testSingleCallCodes) == 0:
                                continue
                            elif len(filtered_testSingleCallCodes) == 1:
                                conversations = create_prompt_zero_shot(language,methodCode,methodTotalCode,filtered_testSingleCallCodes,filtered_calleeSingleCallCodes)
                                num_zero_shot = num_zero_shot + 1
                                prompts_zero_shot.append({
                                    "id": num_zero_shot,
                                    "conversations": conversations
                                })
                                check_num_zero_shot += 1
                                if index_string in codesearchnet_dict.keys():
                                    doctring = codesearchnet_dict[index_string]["docstring"]
                                    num_zero_shot_tdd1 = num_zero_shot_tdd1 + 1
                                    prompts_zero_shot_tdd1.append({
                                        "id": num_zero_shot_tdd1,
                                        "conversations": create_tdd1_prompt_zero_shot(language,doctring,filtered_testSingleCallCodes)
                                    })
                                    check_num_zero_shot_tdd1 += 1
                                    num_tdd2 = num_tdd2 + 1
                                    prompts_tdd2.append({
                                        "id": num_tdd2,
                                        "conversations": create_tdd2_prompt(language,doctring,methodTotalCode,filtered_testSingleCallCodes[0]["totalCode"])
                                    })
                                    check_num_tdd2 += 1
                                    
                            elif len(filtered_testSingleCallCodes) == 2:
                                conversations = create_prompt_one_shot(language,methodCode,methodTotalCode,filtered_testSingleCallCodes,filtered_calleeSingleCallCodes)
                                num_one_shot = num_one_shot + 1
                                prompts_one_shot.append({
                                    "id": num_one_shot,
                                    "conversations": conversations
                                })
                                check_num_one_shot += 1
                                if index_string in codesearchnet_dict.keys():
                                    doctring = codesearchnet_dict[index_string]["docstring"]
                                    num_one_shot_tdd1 = num_one_shot_tdd1 + 1
                                    prompts_one_shot_tdd1.append({
                                        "id": num_one_shot_tdd1,
                                        "conversations": create_tdd1_prompt_one_shot(language,doctring,filtered_testSingleCallCodes)
                                    })
                                    check_num_one_shot_tdd1 += 1
                                    for i in range(len(filtered_testSingleCallCodes)):
                                        num_tdd2 = num_tdd2 + 1
                                        prompts_tdd2.append({
                                            "id": num_tdd2,
                                            "conversations": create_tdd2_prompt(language,doctring,methodTotalCode,filtered_testSingleCallCodes[i]["totalCode"])
                                        })
                                    check_num_tdd2 += 2
                                    
                            elif len(filtered_testSingleCallCodes) ==3:
                                for i in range(0,len(filtered_testSingleCallCodes)-1):
                                    conversations = create_prompt_one_shot(language,methodCode,methodTotalCode,filtered_testSingleCallCodes[i:i+2],filtered_calleeSingleCallCodes)
                                    num_one_shot = num_one_shot + 1
                                    prompts_one_shot.append({
                                        "id": num_one_shot,
                                        "conversations": conversations
                                    })
                                    if index_string in codesearchnet_dict.keys():
                                        doctring = codesearchnet_dict[index_string]["docstring"]
                                        num_one_shot_tdd1 = num_one_shot_tdd1 + 1
                                        prompts_one_shot_tdd1.append({
                                            "id": num_one_shot_tdd1,
                                            "conversations": create_tdd1_prompt_one_shot(language,doctring,filtered_testSingleCallCodes[i:i+2])
                                        })
                                check_num_one_shot += 2
                                
                                if index_string in codesearchnet_dict.keys():
                                    doctring = codesearchnet_dict[index_string]["docstring"]
                                    for i in range(len(filtered_testSingleCallCodes)):
                                        num_tdd2 = num_tdd2 + 1
                                        prompts_tdd2.append({
                                            "id": num_tdd2,
                                            "conversations": create_tdd2_prompt(language,doctring,methodTotalCode,filtered_testSingleCallCodes[i]["totalCode"])
                                        })
                                    check_num_one_shot_tdd1 += 2
                                    check_num_tdd2 += 3

                            else:
                                block = len(filtered_testSingleCallCodes) // 4 if len(filtered_testSingleCallCodes) % 4 == 0 else len(filtered_testSingleCallCodes) // 4 + 1
                                for i in range(0,block):
                                    conversations = create_prompt_few_shot(language,methodCode,methodTotalCode,filtered_testSingleCallCodes[i*4:i*4+4],filtered_calleeSingleCallCodes) if i*4+4 <= len(filtered_testSingleCallCodes) else create_prompt_few_shot(language,methodCode,methodTotalCode,filtered_testSingleCallCodes[-4:],filtered_calleeSingleCallCodes)
                                    num_few_shot = num_few_shot + 1
                                    prompts_few_shot.append({
                                        "id": num_few_shot,
                                        "conversations": conversations
                                    })
                                    if index_string in codesearchnet_dict.keys():
                                        doctring = codesearchnet_dict[index_string]["docstring"]
                                        num_few_shot_tdd1 = num_few_shot_tdd1 + 1
                                        prompts_few_shot_tdd1.append({
                                            "id": num_few_shot_tdd1,
                                            "conversations": create_tdd1_prompt_few_shot(language,doctring,filtered_testSingleCallCodes[i*4:i*4+4]) if i*4+4 <= len(filtered_testSingleCallCodes) else create_tdd1_prompt_few_shot(language,doctring,filtered_testSingleCallCodes[-4:])
                                        })
                                check_num_few_shot += block
                                if index_string in codesearchnet_dict.keys():
                                    doctring = codesearchnet_dict[index_string]["docstring"]
                                    for i in range(len(filtered_testSingleCallCodes)):
                                        num_tdd2 = num_tdd2 + 1
                                        prompts_tdd2.append({
                                            "id": num_tdd2,
                                            "conversations": create_tdd2_prompt(language,doctring,methodTotalCode,filtered_testSingleCallCodes[i]["totalCode"])
                                        })
                                    check_num_few_shot_tdd1 += block 
                                    check_num_tdd2 += len(filtered_testSingleCallCodes)
                                    
                    if processed_num % 1000 == 0:
                        print(f"Zero-shot:{num_zero_shot}({check_num_zero_shot}), One-shot:{num_one_shot}({check_num_one_shot}), Few-shot:{num_few_shot}({check_num_few_shot})\nZero-shot-tdd1:{num_zero_shot_tdd1}({check_num_zero_shot_tdd1}), One-shot-tdd1:{num_one_shot_tdd1}({check_num_one_shot_tdd1}), Few-shot-tdd1:{num_few_shot_tdd1}({check_num_few_shot_tdd1}), TDD2:{num_tdd2}({check_num_tdd2})")

    print(f"Writting to file...")
    with open(os.path.join(output_path,"zero_shot.json"), "w") as f:
        json.dump(prompts_zero_shot,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"one_shot.json"), "w") as f:
        json.dump(prompts_one_shot,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"few_shot.json"), "w") as f:
        json.dump(prompts_few_shot,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"zero_shot_tdd1.json"), "w") as f:
        json.dump(prompts_zero_shot_tdd1,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"one_shot_tdd1.json"), "w") as f:
        json.dump(prompts_one_shot_tdd1,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"few_shot_tdd1.json"), "w") as f:
        json.dump(prompts_few_shot_tdd1,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"tdd2.json"), "w") as f:
        json.dump(prompts_tdd2,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"exclude_repo.json"), "w") as f:
        json.dump(exclude_repo,f,indent=4,ensure_ascii=False)
        # with open(os.path.join(output_path,f"zero_shot_{dir}.json"), "w") as f:
        #     json.dump(prompts_zero_shot,f,indent=4,ensure_ascii=False)
        # with open(os.path.join(output_path,f"one_shot_{dir}.json"), "w") as f:
        #     json.dump(prompts_one_shot,f,indent=4,ensure_ascii=False)
        # with open(os.path.join(output_path,f"few_shot_{dir}.json"), "w") as f:
        #     json.dump(prompts_few_shot,f,indent=4,ensure_ascii=False)
        # with open(os.path.join(output_path,f"zero_shot_tdd1_{dir}.json"), "w") as f:
        #     json.dump(prompts_zero_shot_tdd1,f,indent=4,ensure_ascii=False)
        # with open(os.path.join(output_path,f"one_shot_tdd1_{dir}.json"), "w") as f:
        #     json.dump(prompts_one_shot_tdd1,f,indent=4,ensure_ascii=False)
        # with open(os.path.join(output_path,f"few_shot_tdd1_{dir}.json"), "w") as f:
        #     json.dump(prompts_few_shot_tdd1,f,indent=4,ensure_ascii=False)
        # with open(os.path.join(output_path,f"tdd2_{dir}.json"), "w") as f:
        #     json.dump(prompts_tdd2,f,indent=4,ensure_ascii=False)
        # print(f"Finetune dataset has been all generated") 

def multi_unit_test(language,input_path,output_path,codesearchnet_path,exclude_repo_path):
    codesearchnet_dict = create_codesearchnet_dict(codesearchnet_path)
    exclude_repo_dict = create_exclude_repo_dict(exclude_repo_path)
    check_num_zero_shot = 0
    check_num_zero_shot_tdd1 = 0
    check_num_tdd2 = 0
    num_zero_shot = 0
    num_zero_shot_tdd1 = 0
    num_tdd2 = 0
    prompts_zero_shot = []
    prompts_zero_shot_tdd1 = []
    prompts_tdd2 = []

    exclude_repo = []
    processed_num = 0
    for dir in os.listdir(input_path):
        if not os.path.isdir(os.path.join(input_path,dir)):
            continue
        for file in os.listdir(os.path.join(input_path,dir)):
            if file.endswith(".jsonl"):
                processed_num += 1
                if processed_num % 1000 == 0:
                    print(f"Processing {processed_num} in {dir}")
                owner_repo = file.split(".jsonl")[0].split("filepairs_")[1]
                if owner_repo in exclude_repo_dict.keys():
                    #排除指定repo
                    print(f"Exclude {owner_repo}")
                    exclude_repo.append({owner_repo:"1"})
                    continue
                with open(os.path.join(input_path,dir,file), "r") as f:
                    #读取jsonl文件
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if len(line) == 0:
                            continue
                        #将json字符串转换为字典
                        json_dict = eval(line)
                        class_name = json_dict["className"]
                        file_path = json_dict["path"]
                        methodAndParams = json_dict["methodAndParams"]
                        for methodAndParam in methodAndParams:
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
                            
                            if len(testTotalCallCodes) == 0:
                                continue
                                
                            # for calleeTotalCallCode in calleeTotalCallCodes:
                            #     callClass = calleeTotalCallCode["callClass"]
                            #     if len(calleeTotalCallCode["totalCode"]) > max_string_length:
                            #         #过滤字符数>12000的代码
                            #         continue
                            #     elif "test" in callClass.lower():
                            #         #测试代码不属于callee，去除
                            #         continue
                            #     else:
                            #         #属于callee
                            #         filtered_calleeTotalCallCodes.append(calleeTotalCallCode)

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
                                    if language == "python":
                                        file_name = file_path.split("/")[-1].split(".py")[0]
                                        test_file_name = callClass
                                        if file_name in test_file_name:
                                            if "assert" in testTotalCallCode["totalCode"]:
                                                filtered_testTotalCallCodes.append(testTotalCallCode)
                            

                            # for testSingleCallCode in testSingleCallCodes:
                            #     callClass = testSingleCallCode['callClass']
                            #     if len(testSingleCallCode["totalCode"]) > max_string_length:
                            #         #过滤字符数>12000的代码
                            #         continue
                            #     else:
                            #         #属于test
                            #         filtered_testSingleCallCodes.append(testSingleCallCode)
                            
                            if language == "java":
                                index_string = json_dict['path'] + ":" + class_name+"."+methodName
                            elif language == "python":
                                index_string1 = json_dict['path'] + ":" +class_name + "." + methodName
                                index_string2 = json_dict['path'] + ":" + methodName
                                if index_string1 in codesearchnet_dict.keys():
                                    index_string = index_string1
                                elif index_string2 in codesearchnet_dict.keys():
                                    index_string = index_string2
                                else:
                                    index_string = ""

                            if len(filtered_testTotalCallCodes) == 0:
                                continue
                            else:
                                for callCode_test in filtered_testTotalCallCodes:
                                    conversations = create_prompt_multi_unit_test_zero_shot(language,methodCode,methodTotalCode,callCode_test["totalCode"],filtered_calleeSingleCallCodes)
                                    num_zero_shot = num_zero_shot + 1
                                    prompts_zero_shot.append({
                                        "id": num_zero_shot,
                                        "conversations": conversations
                                    })
                                    check_num_zero_shot += 1
                                    if index_string in codesearchnet_dict.keys():
                                        doctring = codesearchnet_dict[index_string]["docstring"]
                                        num_zero_shot_tdd1 = num_zero_shot_tdd1 + 1
                                        prompts_zero_shot_tdd1.append({
                                            "id": num_zero_shot_tdd1,
                                            "conversations": create_tdd1_prompt_multi_unit_test_zero_shot(language,doctring,callCode_test["totalCode"])
                                        })
                                        check_num_zero_shot_tdd1 += 1
                                        num_tdd2 = num_tdd2 + 1
                                        prompts_tdd2.append({
                                            "id": num_tdd2,
                                            "conversations": create_tdd2_prompt(language,doctring,methodTotalCode,callCode_test["totalCode"])
                                        })
                                        check_num_tdd2 += 1
                if processed_num % 1000 == 0:                
                    print(f"Zero-shot:{num_zero_shot}({check_num_zero_shot})\nZero-shot-tdd1:{num_zero_shot_tdd1}({check_num_zero_shot_tdd1}), TDD2:{num_tdd2}({check_num_tdd2})")

    print(f"Writting to file...")
    with open(os.path.join(output_path,"zero_shot_multi_unit_test.json"), "w") as f:
        json.dump(prompts_zero_shot,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"zero_shot_tdd1_multi_unit_test.json"), "w") as f:
        json.dump(prompts_zero_shot_tdd1,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"tdd2_multi_unit_test.json"), "w") as f:
        json.dump(prompts_tdd2,f,indent=4,ensure_ascii=False)
    with open(os.path.join(output_path,"exclude_repo_multi.json"), "w") as f:
        json.dump(exclude_repo,f,indent=4,ensure_ascii=False)


if __name__ == "__main__":
    language = sys.argv[1] 
    input_path = sys.argv[2]
    output_path = sys.argv[3]
    codesearchnet_path =  sys.argv[4]
    exclude_repo_path = "test_java.txt" if len(sys.argv) < 6 else sys.argv[5]
    single_unit_test(language,input_path,output_path,codesearchnet_path,exclude_repo_path)
    multi_unit_test(language,input_path,output_path,codesearchnet_path,exclude_repo_path)


