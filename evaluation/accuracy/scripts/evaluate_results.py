import os
import json
import sys
import csv

def merge_results_to_one(results):
    merged_status = "FAILED"
    merged_reason = results[0]["reason"]
    for result in results:
        if result["status"] == "SUCCESS":
            merged_status = "SUCCESS"
            merged_reason = result["reason"]
            break
    
    merged_result = [{
        "status": merged_status,
        "reason": merged_reason
    }]

    return merged_result


def assert_for_java(code):
    id_assert = {
        "assertEquals(":0,
        "assertTrue(":0,
        "assertFalse(":0,
        "assertThrows(":0,
        "assertNotNull(":0,
        "assertArrayEquals(":0,
        "assertSame(":0,
        "assertNull(":0,
        "assertNotEquals(":0,
        "assertNotSame(":0,
        "fail(":0,
        "assertDoseNotThrow(":0,
        "assertInstanceOf(":0,
        "assertAll(":0,
        "assertIterableEquals(":0
    }
    for assrt_method in id_assert.keys():
        id_assert[assrt_method] += code.count(assrt_method)
        
    return id_assert

def assert_for_python(code):
    id_assert = {
        "assertEqual(":0,
        "assertTrue(":0,
        "assertFalse(":0,
        "assertRaises(":0,
        "assertIsNotNone(":0,
        "assertIsNone(":0,
        "assertIs(":0,
        "assertIsNot(":0,
        "assertNotEqual(":0,
        "assertNotIs(":0,
        "fail(":0,
        "assertDictEqual(":0,
        "assertListEqual(":0,
        "assertTupleEqual(":0,
        "assertSetEqual(":0,
        "assertSequenceEqual(":0,
        "assertMultiLineEqual(":0,
        "assertLess(":0,
        "assertLessEqual(":0,
        "assertGreater(":0,
        "assertGreaterEqual(":0,
        "assertRegex(":0,
        "assertNotRegex(":0,
        "assertIn(":0,
        "assertNotIn(":0,
        "assertIsInstance(":0,
        "assertNotIsInstance(":0,
        "assertAlmostEqual(":0,
        "assertNotAlmostEqual(":0,
        "assertCountEqual(":0
    }
    for assrt_method in id_assert.keys():
        if assrt_method in code:
            id_assert[assrt_method] += code.count(assrt_method)
        
    return id_assert

def mock_for_java(code):
    id_mock = {
        "mock(":0,
        "when(":0,
        "verify(":0,
        "then(":0,
        "doReturn(":0,
        "doThrow(":0,
        "doNothing(":0,
        "doAnswer(":0,
        "doCallRealMethod(":0,
        "times(":0,
        "atLeastOnce(":0,
        "atLeast(":0,
        "atMost(":0,
        "never(":0,
        "timeout(":0,
        "thenReturn(":0,
        "thenThrow(":0,
        "thenAnswer(":0,
        "thenCallRealMethod(":0,
        "inOrder(":0,
        "spy(":0,
        "reset(":0,
        "resetMock(":0,
        "resetMocks(":0,
        "clearInvocations(":0,
        "clearInteractions(":0,
        "clearInvokes(":0,
        "clearMocks(":0,
        "clearStaticInvocations(":0,
        "clearStaticInteractions(":0,
        "clearStaticMocks(":0,
        "eq(":0,
        "any(":0,
        "anyInt(":0,
        "anyString(":0,
        "anyList(":0,
        "anyMap(":0,
        "anySet(":0,
        "anyCollection(":0,
        "anyIterable(":0,
        "anyObject(":0,
        "anyVararg(":0,
        "anyBoolean(":0,
        "anyByte(":0,
        "anyChar(":0,
        "anyDouble(":0,
        "anyFloat(":0,
        "anyLong(":0,
        "anyShort(":0,
        "mockStatic(":0,
        "mockStaticPartial(":0,
        "mockStaticClass(":0,
        "mockStaticClassPartial(":0,
        "spyStatic(":0,
        "spyStaticPartial(":0,
        "spyStaticClass(":0,
        "spyStaticClassPartial(":0, 
        "powerMock(":0,
        "powerMockStatic(":0,
        "powerMockIgnore(":0,
        "verifyStatic(":0,
        "verifyStaticClass(":0      
    }
    for mock_method in id_mock.keys():
        if mock_method in code:
            id_mock[mock_method] += code.count(mock_method)

    return id_mock

def mock_for_python(code):
    id_mock = {
        "patch(":0,
        "patch.object(":0,
        "patch.dict(":0,
        "patch.multiple(":0,
        "patch.stopall(":0,
        "patch.object.stopall(":0,
        "patch.dict.stopall(":0,
        "patch.multiple.stopall(":0,
        "Mock(":0,
        "MagicMock(":0,
        "PropertyMock(":0,
        "call_count(":0,
        "call_args(":0,
        "call_args_list(":0,
        "mock_calls(":0,
        "method_calls(":0,
        "reset_mock(":0,
        "assert_called(":0,
        "assert_called_once(":0,
        "assert_called_with(":0,
        "assert_called_once_with(":0,
        "assert_any_call(":0,
        "assert_has_calls(":0,
        "assert_not_called(":0,
        "start(":0,
        "stop(":0,
        "start_all(":0,
        "stop_all(":0,
        "start_object(":0,
        "stop_object(":0,
        "start_dict(":0,
        "stop_dict(":0,
        "start_multiple(":0,
        "stop_multiple(":0,
        "start_object_all(":0,
        "stop_object_all(":0,
        "start_dict_all(":0,
        "stop_dict_all(":0,
        "start_multiple_all(":0,
        "stop_multiple_all(":0,
        "start_mock(":0,
        "stop_mock(":0,
        "start_magicmock(":0,
        "stop_magicmock(":0,
        "start_propertymock(":0,
        "stop_propertymock(":0,
        "start_call_count(":0,
        "stop_call_count(":0
    }
    for mock_method in id_mock.keys():
        if mock_method in code:
            id_mock[mock_method] += code.count(mock_method)

    return id_mock

def test_method_num_for_java(code):
    test_method_num = code.count("@Test\n")
    return test_method_num

def test_method_num_for_python(code):
    test_method_num = code.count("def test_")
    return test_method_num


def main(results_path, output_path,language):
    
    output_csv = []
    output_csv.append(["file_name", "model", "id", "init_status", "init_reason","sample_num", "sample_status","sample_reason","filepairs_name","image"])

    output_file = os.path.join(output_path, "evaluation_results.csv")
    output_json ={}
    output_json['single'] = []
    output_json['multi'] = []
    output_json_file = os.path.join(output_path, "evaluation_results.json")

    summary_csv = []
    summary_csv.append(["file_name", "model", "id", "id_status", "id_reason", "id_coverage", "id_assert", "id_mock","id_test_method_num","init_status", "sample_status","sample_reason","filepairs_name","image"])
    summary_file = os.path.join(output_path, "evaluation_summary.csv")
    summary_json = {}
    summary_json['single'] = []
    summary_json['multi'] = []
    summary_json_file = os.path.join(output_path, "evaluation_summary.json")

    for results_file in os.listdir(results_path):
        if results_file.endswith("result.json"):
            with open(os.path.join(results_path,results_file), "r") as f:
                results = json.load(f)
            for item in results:
                if "results" in results[item]:
                    id = item
                    id_status = "FAILED"
                    id_reason = []
                    id_coverage = []
                    id_assert = []
                    id_mock = []
                    id_test_method_num = []
                    file_name = results_file
                    image = results[item]["image"]
                    filepairs_name = results[item]["file"]
                    for m in results[item]["results"].keys():
                        if m == "init":
                            if len(results[item]["results"]["init"]["1"]["init"]) > 1:
                                results[item]["results"]["init"]["1"]["init"] = merge_results_to_one(results[item]["results"]["init"]["1"]["init"])

                            init_status = results[item]["results"]["init"]["1"]["init"][0]["status"]
                            init_reason = results[item]["results"]["init"]["1"]["init"][0]["reason"]
                            # init_reason = ""
                        else:
                            model = m
                            sample_status_list = []
                            sample_reason_list = []
                            for s in results[item]["results"][m].keys():
                                sample_num = s
                                if len(results[item]["results"][m][s]["prompt_method_class_callee_test"]) > 1:
                                    results[item]["results"][m][s]["prompt_method_class_callee_test"] = merge_results_to_one(results[item]["results"][m][s]["prompt_method_class_callee_test"])

                                if results[item]["results"][m][s]["prompt_method_class_callee_test"][0] == "":
                                    sample_status = "FAILED"
                                    sample_reason = "Code not fully completed"
                                else:
                                    sample_status = results[item]["results"][m][s]["prompt_method_class_callee_test"][0]["status"]
                                    sample_reason = ""
                                    if sample_status == "FAILED":
                                        if isinstance(results[item]["results"][m][s]["prompt_method_class_callee_test"][0]["reason"], dict):
                                            if "compile" in results[item]["results"][m][s]["prompt_method_class_callee_test"][0]["reason"].keys():
                                                sample_reason = "compile"
                                            elif "test" in results[item]["results"][m][s]["prompt_method_class_callee_test"][0]["reason"].keys():
                                                sample_reason = "test"
                                            elif "coverage" in results[item]["results"][m][s]["prompt_method_class_callee_test"][0]["reason"].keys():
                                                sample_reason = "coverage"
                                        else:
                                            sample_reason = results[item]["results"][m][s]["prompt_method_class_callee_test"][0]["reason"]
                                    else:
                                        sample_reason = results[item]["results"][m][s]["prompt_method_class_callee_test"][0]["reason"]['line_coverage']
                                if sample_status == "SUCCESS":
                                    id_status = "SUCCESS"
                                    id_reason.append(sample_num)
                                    id_coverage.append(sample_reason)
                                    if language == "java":
                                        code = results[item]["LLM_answers_cleaned"][m][s]["prompt_method_class_callee_test"]
                                        id_assert.append(assert_for_java(code))
                                        id_mock.append(mock_for_java(code))
                                        id_test_method_num.append(test_method_num_for_java(code))
                                    elif language == "python":
                                        code = results[item]["LLM_answers_cleaned"][m][s]["prompt_method_class_callee_test"]
                                        id_assert.append(assert_for_python(code))
                                        id_mock.append(mock_for_python(code))
                                        id_test_method_num.append(test_method_num_for_python(code))


                                # sample_reason = results[item]["results"][m][s]["prompt_method_class_callee_test"][0]["reason"]
                                sample_status_list.append(sample_status)
                                sample_reason_list.append(sample_reason)
                                output_csv.append([file_name, model, id, init_status, init_reason, sample_num, sample_status, sample_reason, filepairs_name, image])
                                if "single" in file_name:
                                    output_json['single'].append({
                                        'model': model,
                                        'id': id,
                                        'init_status': init_status,
                                        'init_reason': init_reason,
                                        'sample_num': sample_num,
                                        'sample_status': sample_status,
                                        'sample_reason': sample_reason,
                                        'filepairs_name': filepairs_name,
                                        'image': image
                                    })
                                elif "multi" in file_name:
                                    output_json['multi'].append({
                                        'model': model,
                                        'id': id,
                                        'init_status': init_status,
                                        'init_reason': init_reason,
                                        'sample_num': sample_num,
                                        'sample_status': sample_status,
                                        'sample_reason': sample_reason,
                                        'filepairs_name': filepairs_name,
                                        'image': image
                                    })
                            summary_csv.append([file_name, model, id, id_status, id_reason, id_coverage, id_assert,id_mock,id_test_method_num,init_status, sample_status_list, sample_reason_list, filepairs_name, image])
                            if "single" in file_name:
                                summary_json['single'].append({
                                    'model': model,
                                    'id': id,
                                    'id_status': id_status,
                                    'id_reason': id_reason,
                                    'id_coverage': id_coverage,
                                    'id_assert': id_assert,
                                    'id_mock': id_mock,
                                    'id_test_method_num': id_test_method_num,
                                    'init_status': init_status,
                                    'sample_status': sample_status_list,
                                    'sample_reason': sample_reason_list,
                                    'filepairs_name': filepairs_name,
                                    'image': image
                                })
                            elif 'multi' in file_name:
                                summary_json['multi'].append({
                                    'model': model,
                                    'id': id,
                                    'id_status': id_status,
                                    'id_reason': id_reason,
                                    'id_coverage': id_coverage,
                                    'id_assert': id_assert,
                                    'id_mock': id_mock,
                                    'id_test_method_num': id_test_method_num,
                                    'init_status': init_status,
                                    'sample_status': sample_status_list,
                                    'sample_reason': sample_reason_list,
                                    'filepairs_name': filepairs_name,
                                    'image': image
                                })
        

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with open(output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerows(output_csv)

    with open(summary_file, "w") as f:
        writer = csv.writer(f)
        writer.writerows(summary_csv)
    
    with open(output_json_file, "w") as f:
        json.dump(output_json, f, indent=4)
    
    with open(summary_json_file, "w") as f:
        json.dump(summary_json, f, indent=4)



if __name__  == "__main__":
    results_path = sys.argv[1]
    output_path = sys.argv[2]
    language = sys.argv[3]
    
    main(results_path, output_path,language)