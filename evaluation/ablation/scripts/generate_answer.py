# import openai
import os
import requests
import json
import sys
import time
import gzip
import numpy as np
from time import sleep
# import tiktoken

def ut_lm(prompts, url="http://0.0.0.0:8888/generate", samples=10):
    answers = {}
    for id in range(1,samples+1):
        answers[id] = {}

    for prompt in prompts.keys():
        print(f"{prompt}")
        if prompts[prompt] == "":
            for id in range(1,samples+1):
                answers[id][prompt] = ""
        else:
            prompt_ask = f"""You are an AI programming assistant, utilizing the HiPilot model, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.\n###Instruction:\n{prompts[prompt]}\n\n### Response:\n"""

            obj = {
                "prompt": prompt_ask,
                "temperature": 0.2,
                "max_tokens": 4096,
                "n": samples

            }
            # print(prompt)
            
            
            while True:
                try:
                    response = requests.post(url, json=obj, stream=False)
                    message = response.json()
                    # print(message)
                    for id in range(1,samples+1):
                        answers[id][prompt] = message['text'][id-1].split("### Response:\n")[-1]
                        
                except:
                    print(f"Error, skip {prompt}")
                    for id in range(1,samples+1):                        
                        answers[id][prompt] = ""
                    break
                else:
                    break

    return answers

    
def wizardcoder(prompts, url="http://0.0.0.0:8888/generate", samples=10):
    answers = {}
    for id in range(1,samples+1):
        answers[id] = {}

    for prompt in prompts.keys():
        print(f"{prompt}")
        if prompts[prompt] == "":
            for id in range(1,samples+1):
                answers[id][prompt] = ""
        else:
            prompt_ask = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{prompts[prompt]}

### Response:
"""
            obj = {
                "prompt": prompt_ask,
                "temperature": 0.2,
                "max_tokens": 4096,
                "n": 10
            }
            # print(prompt)
            
            while True:
                try:
                    response = requests.post(url, json=obj, stream=False)
                    message = response.json()
                    for id in range(1,samples+1):                        
                        answers[id][prompt] = message['text'][id-1].split("### Response:\n")[-1]
                except:
                    print(f"Error, skip {prompt}")
                    for id in range(1,samples+1):                        
                        answers[id][prompt] = ""
                    break
                else:
                    break

    return answers

def deepseek(prompts, url="http://0.0.0.0:9999/generate", samples=10):
    answers = {}
    for id in range(1,samples+1):
        answers[id] = {}

    for prompt in prompts.keys():
        print(f"{prompt}")
        if prompts[prompt] == "":
            for id in range(1,samples+1):
                answers[id][prompt] = ""
        else:
            prompt_ask = f"""You are an AI programming assistant, utilizing the Deepseek Coder model, developed by Deepseek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
### Instruction:
{prompts[prompt]}
### Response:
"""
            obj = {
                "prompt": prompt_ask,
                "temperature": 0.2,
                "max_tokens": 4096,
                "n": 10
            }
            # print(prompt)
            
            while True:
                try:
                    response = requests.post(url, json=obj, stream=False)
                    message = response.json()
                    for id in range(1,samples+1):                        
                        answers[id][prompt] = message['text'][id-1].split("### Response:\n")[-1]
                    
                except:
                    print(f"Error, skip {prompt}")
                    for id in range(1,samples+1):                        
                        answers[id][prompt] = ""
                    break
                else:
                    break

    return answers

def codellama(prompts, url="http://0.0.0.0:7777/generate", samples=10):
    answers = {}
    for id in range(1,samples+1):
        answers[id] = {}

    for prompt in prompts.keys():
        print(f"{prompt}")
        if prompts[prompt] == "":
            for id in range(1,samples+1):
                answers[id][prompt] = ""
        else:
            prompt_ask = f"[INST]\n{prompts[prompt]}\n[/INST]"

            obj = {
                "prompt": prompt_ask,
                "temperature": 0.2,
                "max_tokens": 4096,
                "n": 10
            }
            # print(prompt)
            
            while True:
                try:
                    response = requests.post(url, json=obj, stream=False)
                    message = response.json()
                    for id in range(1,samples+1):                        
                        answers[id][prompt] = message['text'][id-1].split("\n[/INST]")[-1]
                except:
                    print(f"Error, skip {prompt}")
                    for id in range(1,samples+1):                        
                        answers[id][prompt] = ""
                    break
                else:
                    break

    return answers

def chatgpt(prompts,model="gpt-3.5-turbo-0125",samples=10):
    if model == "gpt-4" or model == "gpt-3.5-turbo":
        def get_id_token():
            url = "http://avatar.aicubes.cn/vtuber/auth/api/oauth/v1/login"
            load = {
                    "app_id": "ID",
                    "app_secret": "SECRET"
                    }

            r = requests.post(url, json=load)
            user_id = r.json()["data"]["user_id"]
            token = r.json()["data"]["token"]
            return user_id, token
        user_id, token = get_id_token()
        api_qs_url = "http://avatar.aicubes.cn/vtuber/ai_access/chatgpt/v1/chat/completions"

        answers = {}
        for id in range(1,samples+1):
            answers[id] = {}
        for prompt in prompts.keys():
            print(f"{prompt}")
            if prompts[prompt] == "":
                for id in range(1,samples+1):
                    answers[id][prompt] = ""
            else:
                system_content, user_content = prompts[prompt].split("\n\n",maxsplit=1)

                messages = []
                messages.append({"role": "system", "content": system_content})
                messages.append({"role": "user", "content": user_content})
                payload_qs = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.2,
                    "n": samples,
                }
                headers = {
                    'userId': user_id,
                    'token': token,
                    'Content-Type': 'application/json'
                    }
                
                while True:
                    try:
                        response = requests.post(api_qs_url, headers=headers, json=payload_qs)

                        message = response.json()
                        # print(message)
                        for id in range(1,samples+1):
                            answers[id][prompt] = message["data"]['choices'][id-1]['message']['content']
                    except:
                        print(f"Error, {prompt} retrying...")
                        if len(payload_qs['messages'][-1]['content']) > 6000:
                            payload_qs['messages'][-1]['content'] = payload_qs['messages'][-1]['content'][:6000]
                        else:
                            payload_qs['messages'][-1]['content'] = payload_qs['messages'][-1]['content'][:-200]
                        # print(f"length: {len(payload_qs['messages'][-1]['content'])}")
                        sleep(10)
                        continue
                    else:
                        break
                    
    return answers


def main(input_path,output_path,model,samples,url):
    # print("Processing...",input_path)

    with open(input_path, 'r', encoding='utf8') as f:
        input_code = json.load(f)
    file_name = input_path.split("/")[-1]
 
    if model == "chatgpt35":
        #检查是否生成过
        output_file = os.path.join(output_path,'chatgpt35',file_name)
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf8') as f:
                output_code = json.load(f)
        else:
            output_code = input_code
    
        for item in input_code:
            print(item)
            prompts = input_code[item]['prompts']

            if 'LLM_answers' not in output_code[item].keys():
                output_code[item]['LLM_answers'] = {}
            
            if 'chatgpt3.5' in output_code[item]['LLM_answers'].keys() :
                print(f"skip {item}")
                continue

            #ask chatgpt3.5 for each prompt
            answer = chatgpt(prompts,"gpt-3.5-turbo",samples)
            output_code[item]['LLM_answers']['chatgpt3.5'] = answer

            os.system(f"mkdir -p {os.path.join(output_path,'chatgpt35')}")
            with open(output_file, 'w', encoding='utf8') as f:
                json.dump(output_code, f, ensure_ascii=False, indent=4)
        
    elif model == "gpt4":
        #检查是否生成过
        output_file = os.path.join(output_path,'gpt4',file_name)
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf8') as f:
                output_code = json.load(f)
        else:
            output_code = input_code

        for item in input_code:
            print(item)
            prompts = input_code[item]['prompts']
            
            if 'LLM_answers' not in output_code[item].keys():
                output_code[item]['LLM_answers'] = {}
            if 'gpt4' in output_code[item]['LLM_answers'].keys() :
                print(f"skip {item}")
                continue

            #ask gpt4 for each prompt
            answer = chatgpt(prompts,"gpt-4",samples)
            output_code[item]['LLM_answers']['gpt4'] = answer

            os.system(f"mkdir -p {os.path.join(output_path,'gpt4')}")
            with open(output_file, 'w', encoding='utf8') as f:
                json.dump(output_code, f, ensure_ascii=False, indent=4)

    elif model == "ut-lm-python-java-33b" or model == "ut-lm-python-java-7b": 
        #检查是否生成过
        output_file = os.path.join(output_path,model,file_name)
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf8') as f:
                output_code = json.load(f)
        else:
            output_code = input_code

        for item in input_code:
            print(f"{item}")
            prompts = input_code[item]['prompts']
            
            if 'LLM_answers' not in output_code[item].keys():
                output_code[item]['LLM_answers'] = {}
            skip = True
            if model in output_code[item]['LLM_answers'].keys() :
                for sample_num in output_code[item]['LLM_answers'][model].keys():
                    for prompt in output_code[item]['LLM_answers'][model][sample_num].keys():
                        if output_code[item]['LLM_answers'][model][sample_num][prompt] == "":
                            skip = False
                            break

            if skip:
                print(f"skip {item}")
                continue
            
            #ask ut-lm for each prompt

            answer = ut_lm(prompts,url,samples)
            output_code[item]['LLM_answers'][model] = answer
        
            os.system(f"mkdir -p {os.path.join(output_path,model)}")
            with open(output_file, 'w', encoding='utf8') as f:
                json.dump(output_code, f, ensure_ascii=False, indent=4)

    elif model == "codellama":
        #检查是否生成过
        output_file = os.path.join(output_path,'codellama',file_name)
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf8') as f:
                output_code = json.load(f)
        else:
            output_code = input_code

        for item in input_code:
            print(item)
            prompts = input_code[item]['prompts']
            
            if 'LLM_answers' not in output_code[item].keys():
                output_code[item]['LLM_answers'] = {}
            if 'codellama' in output_code[item]['LLM_answers'].keys() :
                print(f"skip {item}")
                continue
            
            #ask codellama for each prompt
            # CUDA_VISIBLE_DEVICES=5 python -m vllm.entrypoints.api_server --model /cpfs/29a75185021b187f/data/user/code_generation/codellama --host=0.0.0.0 --port 7777 --max-model-len=8192
            answer = codellama(prompts,url,10)
            output_code[item]['LLM_answers']['codellama'] = answer
        
            os.system(f"mkdir -p {os.path.join(output_path,'codellama')}")
            with open(output_file, 'w', encoding='utf8') as f:
                json.dump(output_code, f, ensure_ascii=False, indent=4)
    
    elif model == "deepseek-33b" or model == "deepseek-7b":
        #检查是否生成过
        output_file = os.path.join(output_path,model,file_name)
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf8') as f:
                output_code = json.load(f)
        else:
            output_code = input_code

        for item in input_code:
            print(item)
            prompts = input_code[item]['prompts']
            
            if 'LLM_answers' not in output_code[item].keys():
                output_code[item]['LLM_answers'] = {}
            if model in output_code[item]['LLM_answers'].keys() :
                print(f"skip {item}")
                continue
            
            #ask deepseek for each prompt
            #CUDA_VISIBLE_DEVICES=4 python -m vllm.entrypoints.api_server --model /cpfs/29a75185021b187f/data/user/code_generation/artrain/HiPilot-coder-7b-instruction-v1.5 --host=0.0.0.0 --port 9999 --max-model-len=8192
            answer = deepseek(prompts,url,10)

            output_code[item]['LLM_answers'][model] = answer
    
            os.system(f"mkdir -p {os.path.join(output_path,model)}")
            with open(output_file, 'w', encoding='utf8') as f:
                json.dump(output_code, f, ensure_ascii=False, indent=4)
    
    
    elif model == "wizardcoder":
        #检查是否生成过
        output_file = os.path.join(output_path,'wizardcoder',file_name)
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf8') as f:
                output_code = json.load(f)
        else:
            output_code = input_code

        for item in input_code:
            print(item)
            prompts = input_code[item]['prompts']
            
            if 'LLM_answers' not in output_code[item].keys():
                output_code[item]['LLM_answers'] = {}
            if 'wizardcoder' in output_code[item]['LLM_answers'].keys() :
                print(f"skip {item}")
                continue
            
            #ask wizardcoder for each prompt
            #CUDA_VISIBLE_DEVICES=6 python -m vllm.entrypoints.api_server --model /cpfs/29a75185021b187f/data/user/code_generation/artrain/mapleStory --host=0.0.0.0 --port 8888 --max-model-len=8192
            answer = wizardcoder(prompts,url,10)
            output_code[item]['LLM_answers']['wizardcoder'] = answer
        
            os.system(f"mkdir -p {os.path.join(output_path,'wizardcoder')}")
            with open(output_file, 'w', encoding='utf8') as f:
                json.dump(output_code, f, ensure_ascii=False, indent=4)




if __name__=="__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    model = sys.argv[3]
    samples = 10
    url = sys.argv[4]
    main(input_path,output_path,model,samples,url)


