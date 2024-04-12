import os
import sys
import time
import traceback

import csv
import json
import pandas as pd
from utils import get_all_file_paths, get_code_test_file_mapping, remove_non_pl_files

# map files
METADATA_COLUMNS = ('organization', 'project', 'total_num_files', 'total_pl_files', 'total_file_pairs', 'filename', 'file_type')
FILEPAIR_COLUMNS = ( 'code_filename', 'test_filename')


def main(repo_dir, file_pairs_dir, org, project, pl):
    project_path = os.path.join(repo_dir, org, project)
    metadata_path = os.path.join(output_dir, 'MetaData', 'metadata_' + org + '__' + project + '.json')
    filepairs_path = os.path.join(output_dir, 'FilePairs', 'filepairs_' + org + '__' + project + '.json')

    #if os.path.exists(metadata_path):
    #    print(f"Extracted files already!!!")
    #    return

    metadata = {key: [] for key in METADATA_COLUMNS}
    filepairs = {key: [] for key in FILEPAIR_COLUMNS}

    start = time.time()
    timers = {'meta': 0, 'file_paths': 0, 'file_map': 0, 'process_metadata': 0, 'process_file_map': 0, 'remove_files': 0}

    try:
        # get all files
        file_paths_start = time.time()
        pl_file_paths, all_file_paths = get_all_file_paths(project_path, pl)
        file_paths_end = time.time()
        timers['file_paths'] += file_paths_end - file_paths_start
        # get file pairs 
        file_map_start = time.time()
        code_test_file_mapping, code_file_paths, test_file_paths = get_code_test_file_mapping(pl_file_paths, pl)
        file_map_end = time.time()
        timers['file_map'] += file_map_end - file_map_start
    

        # update meta data
        process_metadata_start = time.time()
        for code_file in code_file_paths:
            metadata['organization'].append(org)
            metadata['project'].append(project)
            metadata['total_num_files'].append(len(all_file_paths))
            metadata['total_pl_files'].append(len(pl_file_paths))
            metadata['total_file_pairs'].append(len(code_test_file_mapping))
            metadata['filename'].append(code_file)
            metadata['file_type'].append('code')
        for test_file in test_file_paths:
            metadata['organization'].append(org)
            metadata['project'].append(project)
            metadata['total_num_files'].append(len(all_file_paths))
            metadata['total_pl_files'].append(len(pl_file_paths))
            metadata['total_file_pairs'].append(len(code_test_file_mapping))
            metadata['filename'].append(test_file)
            metadata['file_type'].append('test')
        process_metadata_end = time.time()
        timers['process_metadata'] += process_metadata_end - process_metadata_start 

        # update mapping data
        file_map_process_start = time.time()
        for code_file, test_file in code_test_file_mapping.items():
            filepairs['code_filename'].append(code_file)
            filepairs['test_filename'].append(test_file)
        file_map_process_end = time.time()
        timers['process_file_map'] += file_map_process_end - file_map_process_start 
    
        print(f'meta data for {org}, {project} => total_file_pairs: {len(code_test_file_mapping)}')
                
    except Exception as e:
        print("Exception extracting file pairs", org, project, e)
        traceback.print_exc()

    try:
        remove_files_start = time.time()
        #total_files_removed = remove_non_pl_files(all_file_paths, pl)
        remove_files_end = time.time()
        timers['remove_files'] += remove_files_end - remove_files_start
                
    except Exception as e:
        print("Exception removing non {pl} files", org, project, e)
        traceback.print_exc()

    # store metadata 
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)

    # store file pairs 
    with open(filepairs_path, 'w') as f:
        json.dump(filepairs, f)

    end = time.time()
    print(f'time meta {org}, {project}, {timers["meta"]:.3f}s')
    print(f'time file paths {org}, {project}, {timers["file_paths"]:.3f}s')
    print(f'time file map {org}, {project}, {timers["file_map"]:.3f}s')
    print(f'time process file map {org}, {project}, {timers["process_file_map"]:.3f}s')
    print(f'time overall {org}, {project}, {end - start:.3f}s')


if __name__ == '__main__':
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else '/data/GitHubMining/RawTestData/java'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '/data/GitHubMining/TestDataOutput/java/'
    project_path = sys.argv[3] if len(sys.argv) > 3 else '/data/GitHubMining/RawTestData/java/sunysen/naivechain/'
    pl = sys.argv[4] if len(sys.argv) > 4 else 'java'
    
    if project_path.endswith('/'):
        project_path = project_path[:-1]
    *_, org, project = project_path.split('/')

    print(f"Processing {pl}/{org}/{project}")
    main(repo_dir, output_dir, org, project, pl)
    

