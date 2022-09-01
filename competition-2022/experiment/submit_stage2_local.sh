if (($#==1)); #check if number of arguments is 1 
then
    mls="-ml ${1}"
else
    mls=''
fi

python3 analyze.py data/stage2/data/*train.csv -results ../results_stage2 --local -n_jobs 1 -n_threads 8 -m 16384 -n_trials 10 -stage 2 $mls

