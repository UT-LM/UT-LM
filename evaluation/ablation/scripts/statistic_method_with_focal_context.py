import sys
import os
import json
# import subprocess
import gzip
import csv

max_string_length = 12000

def statistics(language,input_path,output_path,checking_path):
    statistics_csv = []
    statistics_csv.append([ "id",
                            "file",
                            "class_name",
                            "method_name",
                            "callee_num",
                            "single_test_num",
                            "multi_test_num",
                            "is_training_data"])
    processed_num = 0

    checking_file = {}
    for dir in os.listdir(checking_path):
        if not os.path.isdir(os.path.join(checking_path,dir)):
            continue
        for file in os.listdir(os.path.join(checking_path,dir)):
            if file.endswith(".jsonl"):
                checking_file[file] = 1

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
                    methodAndParams = json_dict["methodAndParams"]
                    for methodAndParam in methodAndParams:
                        processed_num += 1
                        print(f"Processing {processed_num}th method...")

                        methodName = methodAndParam["methodName"]
                        methodCode = methodAndParam["methodCode"]
                        methodTotalCode = methodAndParam["totalCode"]
                        # calleeTotalCallCodes = methodAndParams["calleeTotalCallCodes"]
                        calleeSingleCallCodes = methodAndParam["calleeSingleCallCodes"]
                        testTotalCallCodes = methodAndParam["testTotalCallCodes"]
                        testSingleCallCodes = methodAndParam["testSingleCallCodes"]
                        
                        # filtered_calleeTotalCallCodes = []
                        filtered_calleeSingleCallCodes = []
                        filtered_testTotalCallCodes = []
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
                                    # 消融实验需要确保没有python自带包的代码
                                    if "python3." not in json_dict['path'] and "python2." not in json_dict['path']:
                                        if class_name in callClass:
                                            if "assert" in testSingleCallCode["code"]:
                                                filtered_testSingleCallCodes.append(testSingleCallCode)
                        
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
                                    # 消融实验需要确保没有python自带包的代码
                                    if "python3." not in json_dict['path'] and "python2." not in json_dict['path']:
                                        if class_name in callClass:
                                            if "assert" in testTotalCallCode["totalCode"]:
                                                filtered_testTotalCallCodes.append(testTotalCallCode)

                        callee_num = len(filtered_calleeSingleCallCodes)
                        single_test_num = len(filtered_testSingleCallCodes)
                        multi_test_num = len(filtered_testTotalCallCodes)
                        is_training_data = "True" if file in checking_file else "False"

                        statistics_csv.append([processed_num,
                                               file,
                                                class_name,
                                                methodName,
                                                callee_num,
                                                single_test_num,
                                                multi_test_num,
                                                is_training_data])
                                                
                                
    print(f"Writting to file...")

    with open(os.path.join(output_path,f"{language}_statistics.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerows(statistics_csv)



if __name__ == "__main__":
    language = sys.argv[1] 
    input_path = sys.argv[2]
    output_path = sys.argv[3]
    checking_path = sys.argv[4] 
    # single_unit_test(language,input_path,output_path)
    # multi_unit_test(language,input_path,output_path)
    statistics(language,input_path,output_path,checking_path)
