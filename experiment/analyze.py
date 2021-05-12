import pandas as pd
import subprocess
import numpy as np
from glob import glob
import argparse
import os, errno, sys
from joblib import Parallel, delayed
from seeds import SEEDS
from yaml import load, Loader

#TODO make this script smarter about running jobs. 
# have it check to see whethe results for that job exist before
# resubmitting. That way the same command can be run multiple times.

if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(
            description="An analyst for quick ML applications.", add_help=False)
    parser.add_argument('DATASET_DIR', type=str,
                        help='Dataset directory like (pmlb/datasets)')    
    parser.add_argument('-h', '--help', action='help',
                        help='Show this help message and exit.')
    parser.add_argument('-ml', action='store', dest='LEARNERS',default=None,
            type=str, help='Comma-separated list of ML methods to use (should '
            'correspond to a py file name in methods/)')
    parser.add_argument('--local', action='store_true', dest='LOCAL', default=False, 
            help='Run locally as opposed to on LPC')
    parser.add_argument('--slurm', action='store_true', dest='SLURM', default=False, 
            help='Run on a SLURM scheduler as opposed to on LPC')
    parser.add_argument('--noskips', action='store_true', dest='NOSKIPS', default=False, 
            help='Overwite existing results if found')
    parser.add_argument('-A', action='store', dest='A', default='plgsrbench', 
            help='SLURM account')
    parser.add_argument('-sym_data',action='store_true', dest='SYM_DATA', default=False, 
            help='Specify a symbolic dataset')
    parser.add_argument('-n_jobs',action='store',dest='N_JOBS',default=1,type=int,
            help='Number of parallel jobs')
    parser.add_argument('-seed',action='store',dest='SEED',default=None,
            type=int, help='A specific random seed')
    parser.add_argument('-n_trials',action='store',dest='N_TRIALS',default=1,
            type=int, help='Number of parallel jobs')
    parser.add_argument('-label',action='store',dest='LABEL',default='class',
            type=str,help='Name of class label column')
    parser.add_argument('-results',action='store',dest='RDIR',default='results',
            type=str,help='Results directory')
    parser.add_argument('-q',action='store',dest='QUEUE',
                        default='epistasis_long',
                        type=str,help='LSF queue')
    parser.add_argument('-m',action='store',dest='M',default=8192,type=int,
            help='LSF memory request and limit (MB)')
    parser.add_argument('-starting_seed',action='store',dest='START_SEED',
                        default=0,type=int, help='seed position to start with')
    parser.add_argument('-test',action='store_true', dest='TEST', 
                       help='Used for testing a minimal version')
    parser.add_argument('-target_noise',action='store',dest='Y_NOISE',
                        default=0.0, type=float, help='Gaussian noise to add'
                        'to the target')
    parser.add_argument('-feature_noise',action='store',dest='X_NOISE',
                        default=0.0, type=float, help='Gaussian noise to add'
                        'to the target')

    args = parser.parse_args()
     
    if args.SLURM and args.QUEUE == 'epistasis_long':
        print('setting queue to plgrid')
        args.QUEUE = 'plgrid'

    if args.LEARNERS == None:
        learners = [ml.split('/')[-1][:-3] for ml in glob('methods/*.py') 
                if not ml.split('/')[-1].startswith('_')]
    else:
        learners = [ml for ml in args.LEARNERS.split(',')]  # learners
    print('learners:',learners)

    print('dataset directory:',args.DATASET_DIR)

    if args.DATASET_DIR.endswith('.tsv.gz'):
        datasets = [args.DATASET_DIR]
    elif args.DATASET_DIR.endswith('*'):
        print('capturing glob',args.DATASET_DIR+'/*.tsv.gz')
        datasets = glob(args.DATASET_DIR+'*/*.tsv.gz')
    else:
        datasets = glob(args.DATASET_DIR+'/*/*.tsv.gz')
    print('found',len(datasets),'datasets:',datasets)
    # write run commands
    all_commands = []
    job_info=[]
    for t in range(args.START_SEED, args.START_SEED+args.N_TRIALS):
        # random_state = np.random.randint(2**15-1)
        if args.SEED and args.N_TRIALS==1:
            random_state = args.SEED
        else:
            random_state = SEEDS[t]
        # print('random_seed:',random_state)
        for dataset in datasets:
            # grab regression datasets
            metadata = load(
                open('/'.join(dataset.split('/')[:-1])+'/metadata.yaml','r'),
                    Loader=Loader)
            if metadata['task'] != 'regression':
                continue
            
            dataname = dataset.split('/')[-1].split('.tsv.gz')[0]
            results_path = '/'.join([args.RDIR, dataname]) + '/'
            if not os.path.exists(results_path):
                os.makedirs(results_path)
                
            for ml in learners:
                save_file = (results_path + '/' + dataname + '_' + ml + '_' 
                             + str(random_state))
                if args.Y_NOISE > 0:
                    save_file += '_target-noise'+str(args.Y_NOISE)
                if feature_noise > 0:
                    save_file += '_feature-noise'+str(args.X_NOISE)

                if os.path.exists(save_file+'.json') and not args.NOSKIPS:
                    print(save_file,'already exists, skipping. Override with --noskips.')
                    continue
                
                all_commands.append('python evaluate_model.py '
                                    '{DATASET}'
                                    ' -ml {ML}'
                                    ' -results_path {RDIR}'
                                    ' -seed {RS} '
                                    ' -target_noise {TN} '
                                    ' -feature_noise {FN} '
                                    '{TEST} {SYM_DATA}'.format(
                                        ML=ml,
                                        DATASET=dataset,
                                        RDIR=results_path,
                                        RS=random_state,
                                        TN=args.Y_NOISE,
                                        FN=args.X_NOISE,
                                        TEST=('-test' if args.TEST
                                                else ''),
                                        SYM_DATA='-sym_data' if args.SYM_DATA else ''
                                        )
                                    )
                job_info.append({'ml':ml,
                                 'dataset':dataname,
                                 'seed':str(random_state),
                                 'results_path':results_path})

    if args.LOCAL:
        # run locally  
        for run_cmd in all_commands: 
            print(run_cmd)
            Parallel(n_jobs=args.N_JOBS)(delayed(os.system)(run_cmd) 
                                     for run_cmd in all_commands)
    elif args.SLURM:
        # sbatch
        #SBATCH -J scikit
        #SBATCH -N 1
        #SBATCH --ntasks-per-node=1
        #SBATCH --time=168:00:00
        #SBATCH --mem-per-cpu=20GB
        #SBATCH -A  plgbicl1
        #SBATCH -p plgrid-long
        for i,run_cmd in enumerate(all_commands):
            job_name = '_'.join([
                                 job_info[i]['dataset'],
                                 job_info[i]['ml'],
                                 job_info[i]['seed']
                                ])
            out_file = job_info[i]['results_path'] + job_name + '_%J.out'
            error_file = out_file[:-4] + '.err'
            
            batch_script = \
"""#!/usr/bin/bash 
#SBATCH -o {OUT_FILE} 
#SBATCH -N 1 
#SBATCH -n {N_CORES} 
#SBATCH -J {JOB_NAME} 
#SBATCH -A {A} -p {QUEUE} 
#SBATCH --ntasks-per-node=1 --time=48:00:00 
#SBATCH --mem-per-cpu={M} 

conda info 
source plg_modules

{cmd}
""".format(
           OUT_FILE=out_file,
           JOB_NAME=job_name,
           QUEUE=args.QUEUE,
           A=args.A,
           N_CORES=args.N_JOBS,
           M=args.M,
           cmd=run_cmd
        )
            with open('tmp_script','w') as f:
                f.write(batch_script)

            print(batch_script)
            sbatch_response = subprocess.check_output(['sbatch tmp_script'],shell=True)     # submit jobs 
            if not os.path.exists('job_scripts/success/'):
                os.makedirs('job_scripts/success/')
            with open('job_scripts/success/'+job_name+'.sh','w') as f:
                f.write(batch_script)

            os.remove('tmp_script')
    else: # LPC
        for i,run_cmd in enumerate(all_commands):
            job_name = '_'.join([
                                 job_info[i]['dataset'],
                                 job_info[i]['ml'],
                                 job_info[i]['seed']
                                ])
            out_file = job_info[i]['results_path'] + job_name + '_%J.out'
            error_file = out_file[:-4] + '.err'
            
            bsub_cmd = ('bsub -o {OUT_FILE} -n {N_CORES} -J {JOB_NAME} -q {QUEUE} '
                       '-R "span[hosts=1] rusage[mem={M}]" -M {M} ').format(
                               OUT_FILE=out_file,
                               JOB_NAME=job_name,
                               QUEUE=args.QUEUE,
                               N_CORES=args.N_JOBS,
                               M=args.M)
            
            bsub_cmd +=  '"' + run_cmd + '"'
            print(bsub_cmd)
            os.system(bsub_cmd)     # submit jobs 
