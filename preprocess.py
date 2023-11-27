import subprocess
import sys
import argparse, sys
import os
import re
import pandas as pd
import json


TIMESTAMP_COL = 'onset'
SPLIT_INTERVAL = 2
PATTERN = r'vol\d+'
# def split_into_bins(timestamps, interval=2):
#     bins = {}

#     for timestamp in timestamps:
#         bin_index = int(timestamp // interval)

#         if bin_index not in bins:
#             bins[bin_index] = [timestamp]
#         else:
#             bins[bin_index].append(timestamp)

#     result = [(bin_start * interval, bins[bin_start]) for bin_start in sorted(bins.keys())]
#     return result

# if i*2 not in binned:
#     timestamp = 'empty'
# else: timestamp = bins
# '{original_name}_{timestamps}'


def merge_slices_with_timeframes(timeframes, slices):
    merged_slices = []
    current_timeframe_index = 0
    current_start = timeframes[current_timeframe_index]
    current_end = timeframes[current_timeframe_index + 1]

    for time_slice in slices:
        if current_start <= time_slice < current_end:
            # Slice belongs to the current timeframe, merge it
            merged_slices.append((current_start, current_end))
        else:
            # Move to the next timeframe
            
            current_timeframe_index += 1
            
            try:
                current_start = timeframes[current_timeframe_index]
                current_end = timeframes[current_timeframe_index + 1]
            except IndexError:
                current_end = current_start
            merged_slices.append((current_start, current_end))

    # Add the last merged timeframe
    merged_slices.append((current_start, current_end))

    return merged_slices

def single_task_preprocess(input_filename, events, TASK_ID=''):
    """
    function which requires .tsv file with events corresponding to TASK_ID run, and input filename with preprocessed fmri .nii.gz file.
    1. nii.gz file is split using fsl_split
    2. onsets are mapped to ids of files which are created in 1.
    3. nii.gz files belonging to the same onset are merged using fslmaths -add command.
    4. timestamp_filename.json is saved, which 
    """
    onsets = events[TIMESTAMP_COL].values.tolist()
    command = ['fslsplit', str(input_filename),'-t', str(SPLIT_INTERVAL) ]
    subprocess.run(command)
    ids = []
    slice_id_filename = dict()
    for filename in os.listdir('./'):
        if ''.join(([input_filename] + ['vol0'])) in filename or ('vol0' in filename):
            match = re.search(PATTERN, filename)
            split_id = match.group().lstrip('vol')
            split_id = int(split_id)
            ids.append(split_id)
            slice_id_filename[split_id] = filename

    slices = [id*SPLIT_INTERVAL for id in ids]
    slices.sort()
    merged = merge_slices_with_timeframes(onsets, slices)
    ids.sort()
    merged_dict = dict(zip(ids, merged))
    timestamp_slice_dict = dict()
    for slice_id, timestamp in merged_dict.items():
        if timestamp not in timestamp_slice_dict:
            timestamp_slice_dict[timestamp] = [slice_id]
        else:
            # If the value is already a key, append the current key to the list
            timestamp_slice_dict[timestamp].append(slice_id)
    timestamp_slice_dict_filenames = dict()
    timestamp_filename = dict()

    for timestamp, slices_list in timestamp_slice_dict.items():
        timestamp_slice_dict_filenames[timestamp] = [slice_id_filename[slice_id] for slice_id in slices_list]
        slice_ids = '_'.join([str(s) for s in slices_list])
        first_input_file = timestamp_slice_dict_filenames[timestamp][0]
        output_name = f'merged_run{TASK_ID}_slices_{slice_ids}_onset_{int(timestamp[0])}.nii.gz'
        command = ['fslmaths', first_input_file, '-add', timestamp_slice_dict_filenames[timestamp][1], output_name]
        print(command)
        subprocess.run(command)
        for n in range(2, len(slices_list)):
            command = ['fslmaths', output_name, '-add', timestamp_slice_dict_filenames[timestamp][n], output_name]
            # remove previously created files
            print(command)
            subprocess.run(command) #TODO merging produces too noisy results
        timestamp_filename[timestamp[0]] = output_name
    with open('timestamp_filename.json', 'w') as fp:
        json.dump(timestamp_filename, fp) 


def merge_files_based_on_timestamps(timestamp_list, output_prefix=''):
    with open('timestamp_filename.json', 'r') as fp:
        timestamp_filename = json.load(fp)
    first_input_file = timestamp_filename[str(timestamp_list[0])]
    output_name = f'{output_prefix}_merged.nii.gz'
    command = ['fslmaths', first_input_file, '-add', timestamp_filename[str(timestamp_list[1])], output_name]
    print(command)
    subprocess.run(command)
    for n, t in enumerate(timestamp_list[2:]):
            command = ['fslmaths', output_name, '-add', timestamp_filename[str(timestamp_list[n])], output_name]
            # remove previously created files
            print(command)
            subprocess.run(command)
        
        
def main():
    """
    Function to run splitting FMRI nifti file and merging based on timestamp
    Takes command line arguments: input and events.csv
    """
    parser=argparse.ArgumentParser()

    parser.add_argument("--input", help=".nii.gz input filename")
    parser.add_argument("--events_csv", help=".csv file with dataset description")
    parser.add_argument("--task", help="run id")
    args=parser.parse_args()

    input_filename = args.input
    events = pd.read_csv(args.events_csv, sep='\t')
    #input_filename = ['']
    #events = pd.read_csv('sub-01_task-mixedgamblestask_run-01_events.tsv', sep='\t')
    single_task_preprocess(input_filename, events, TASK_ID=args.task)

def run_merging_for_all_subjects():
    """
    to be implemented
    """
    pass
    # DOWNLOAD_ROOT = './ds000005-download/'
    # FMRIPREP_ROOT = './ds000005-fmriprep/'
    # subjects = [n for n in range(1, 17)]
    # task_ids = [1, 2, 3]
    # for SUB_ID in subjects:
    #     for TASK_ID in task_ids:
            
    #         EVENTS_CSV = pd.read_csv(f'{DOWNLOAD_ROOT}/sub-0{SUB_ID}/sub-0{SUB_ID}_task-mixedgamblestask_run-0{TASK_ID}_events.tsv', sep='\t')
    #         INPUT = f'{FMRIPREP_ROOT}/sub-0{SUB_ID}sub-0{SUB_ID}_task-mixedgamblestask_run-{TASK_ID}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz'
    #         single_task_preprocess(INPUT, EVENTS_CSV, TASK_ID=TASK_ID)



if __name__ == '__main__':
    #run_merging_for_all_subjects()
    main()

    


    

    

    