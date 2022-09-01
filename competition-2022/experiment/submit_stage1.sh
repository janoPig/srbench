if (($#==1)); #check if number of arguments is 1 
then
    mls="-ml ${1}"
else
    mls=''
fi

python3 analyze.py data/stage1/data/*data.csv -results ../results_stage1 --local -n_jobs 1 -n_threads 8 -m 16384 -n_trials 1 -stage 1 -time_limit "01:05" $mls

