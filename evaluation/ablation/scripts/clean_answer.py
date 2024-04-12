import os
import json
import sys

def main(input_file, language):
    with open(input_file, "r") as f:
        answers = json.load(f)

    for item in answers.keys():
        if "LLM_answers_cleaned" in answers[item]:
            continue
        else:
            answers[item]["LLM_answers_cleaned"] = {}

        for model in answers[item]["LLM_answers"].keys():
            answers[item]["LLM_answers_cleaned"][model] = {}
            for sample_num in answers[item]["LLM_answers"][model].keys():
                answers[item]["LLM_answers_cleaned"][model][sample_num] = {}
                for prompt in answers[item]["LLM_answers"][model][sample_num].keys():
                    if len(answers[item]["LLM_answers"][model][sample_num][prompt]) == 0:
                        answers[item]["LLM_answers_cleaned"][model][sample_num][prompt] = ""
                    else:
                        
                        answers[item]["LLM_answers_cleaned"][model][sample_num][prompt] = answers[item]["LLM_answers"][model][sample_num][prompt].split(f"```{language}",1)[-1].split("```",1)[0]
        
        answers[item]["class_file_path"] = answers[item]["class_file_path"].replace(f"/cpfs/29a75185021b187f/aigccode/user/cuizhe/UT-LM/evaluation/ablation/RawData/{language}/","")
        if len(answers[item]["test_file_path"]) > 0:
            for i in range(len(answers[item]["test_file_path"])):
                answers[item]["test_file_path"][i] = answers[item]["test_file_path"][i].replace(f"/cpfs/29a75185021b187f/aigccode/user/cuizhe/UT-LM/evaluation/ablation/RawData/{language}/","")
        
    output_file = input_file.replace(".json", "_cleaned.json")
    with open(output_file, "w") as f:
        json.dump(answers, f, indent=4)
                    

if __name__ == "__main__":

    language = "java" if len(sys.argv) < 2 else sys.argv[1]
    input_file = "/cpfs/29a75185021b187f/aigccode/user/cuizhe/UT-LM/evaluation/promptsOutput/java/ut-lm/single_unit_test.json" if len(sys.argv) <3 else sys.argv[2]
    # output_file = "/cpfs/29a75185021b187f/aigccode/user/cuizhe/UT-LM/evaluation/promptsOutput/java/ut-lm/single_unit_test_cleaned.json" if len(sys.argv) <4 else sys.argv[3]

    main(input_file, language)
