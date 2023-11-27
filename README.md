# mlatnan_mixed_gambles_project

Current state: 

preprocess.py contains functions to split larger nifti files into smaller volumes spanning shorter time and bind those volumes to events described in events.csv

preprocessed_ica.ipynb - notebook which contains analysis of nifti volumes corresponding to subjective attractiveness of gamble of 4 and 2. It has been done for run 1 for subject 1.

Naming convention of preprocessed files: 

merged_run{id of run}\_slices{ids of 2 second long slices}\_onset{onset which contains those 2 second long intervals}.nii.gz

Preprocessed files: https://drive.google.com/drive/folders/1Gt9Ns52l3VH99njDZcIuoCxjtpMVSN-j?usp=drive_link

To run preprocess.py:

'''
python preprocess.py --input sub-01_task-mixedgamblestask_run-1_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz --events_csv sub-01_task-mixedgamblestask_run-01_events.tsv --task 1
'''
