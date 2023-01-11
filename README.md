# Branch for testing SRBench on local computer

This branch is primarily intended for testing the PHCRegressor from [HROCH](https://github.com/janoPig/HROCH) on local computer, but can be used for any SR method if it is fast enough.

SRBench test 120 black-box and 133 ground-truth datasets(119 feynman + 14 strogatz). Every dataset is tested for 10 random seeds, ground-truth datasets are testes for 4 values of noise[0, 0.001, 0.01, 0.1]. That's together (120+133*4)*10 = 6520 runs of symbolic regressor. Therefore the resources for the PHCRegressor are limited to 1 second and 1 thread per sample. However, the parallel hill climb is a pretty fast method that is comparable to other methods even under these conditions.

Changes:

- Added PHCRegressor limited to run 1 second and thread.
- Removed unused dependencies from enviroment not related to PHCRegressor for faster instalation.
- Added timeout for sympy parsing.
- Results from the run are merged with previous results.

How to run:

Run this script [srbench.sh](https://github.com/janoPig/HROCH/blob/main/benchmarks/srbench.sh) in an empty directory, wait about 2 hours, when finished run the workbooks blackbox_results.ipynb and groundtruth_results.ipynb from the postprocessing folder. The -n_jobs parameter controls the number of parallel jobs, so it must respect the number of cores of the machine. The script requires miniconda.

```bash
#clone pmlb
git clone https://github.com/EpistasisLab/pmlb/
cd pmlb
git lfs pull
cd ..

mkdir srbench
cd srbench

#clone srbench
git clone https://github.com/janoPig/srbench.git
cd srbench
git checkout local_test

# install enviroment
source ~/miniconda3/etc/profile.d/conda.sh
conda env create -f environment.yml
conda activate srbench

cd experiment
python analyze.py ../../../pmlb/datasets -n_trials 10 -ml PHCRegressor -results ../results_blackbox -skip_tuning --noskips --local -n_jobs 10 -job_limit 100000

# submit the ground-truth dataset experiment. 
for data in "../../../pmlb/datasets/strogatz_" "../../../pmlb/datasets/feynman_" ; do # feynman and strogatz datasets
    for TN in 0 0.001 0.01 0.1; do # noise levels
        python analyze.py \
            $data"*" \
            -results ../results_sym_data \
            -ml PHCRegressor \
            --noskips \
            --local \
            -target_noise $TN \
            -sym_data \
            -n_trials 10 \
            -m 16384 \
            -job_limit 100000 \
            -skip_tuning \
            -n_jobs 10
        if [ $? -gt 0 ] ; then
            break
        fi
    done
done

# assess the ground-truth models that were produced using sympy
for data in "../../../pmlb/datasets/strogatz_" "../../../pmlb/datasets/feynman_" ; do # feynman and strogatz datasets
    for TN in 0 0.001 0.01 0.1; do # noise levels
        python analyze.py \
            -script assess_symbolic_model \
            $data"*" \
            -results ../results_sym_data \
            -target_noise $TN \
            -ml PHCRegressor \
            --local \
            -sym_data \
            -n_trials 10 \
            -m 8192 \
            -time_limit 0:01 \
            -job_limit 100000 \
            -n_jobs 10
        if [ $? -gt 0 ] ; then
            break
        fi
    done
done

cd ../postprocessing
python collate_blackbox_results.py ../results_blackbox
python collate_groundtruth_results.py ../results_sym_data
```

---

# SRBench: A Living Benchmark for Symbolic Regression

The methods for symbolic regression (SR) have come a long way since the days of Koza-style genetic programming (GP).
Our goal with this project is to keep a living benchmark of modern symbolic regression, in the context of state-of-the-art ML methods.

Currently these are the challenges, as we see it:

- Lack of cross-pollination between the GP community and the ML community (different conferences, journals, societies etc)
- Lack of strong benchmarks in SR literature (small problems, toy datasets, weak comparator methods)
- Lack of a unified framework for SR, or GP

We are addressing the lack of pollination by making these comparisons open source, reproduceable and public, and hoping to share them widely with the entire ML research community.
We are trying to address the lack of strong benchmarks by providing open source benchmarking of many SR methods on large sets of problems, with strong baselines for comparison.
To handle the lack of a unified framework, we've specified minimal requirements for contributing a method to this benchmark: a scikit-learn compatible API.

# Benchmarked Methods

This benchmark currently consists of __14__ symbolic regression methods, __7__ other ML methods, and __252__ datasets from [PMLB](https://github.com/EpistasisLab/penn-ml-benchmarks), including real-world and synthetic datasets from processes with and without ground-truth models.

Methods currently benchmarked:

- Age-Fitness Pareto Optimization (Schmidt and Lipson 2009)
    [paper](https://dl.acm.org/doi/pdf/10.1145/1830483.1830584)
    ,
    [code](https://github.com/cavalab/ellyn)
- Age-Fitness Pareto Optimization with Co-evolved Fitness Predictors (Schmidt and Lipson 2009)
    [paper](https://dl.acm.org/doi/pdf/10.1145/1830483.1830584?casa_token=8fAFUrPlfuUAAAAA:u0QJvX-cC8rPtdZri-Jd4ZxcnRSIF_Fu2Vn5n-oXVNu_i71J6ZECx28ucLPOLQY628drsEbg4aFvTw)
    ,
    [code](https://github.com/cavalab/ellyn)
- AIFeynman 2.0 (Udrescu et al. 2020)
    [paper](https://arxiv.org/abs/2006.10782)
    ,
    [code](https://github.com/SJ001/AI-Feynman)
- Bayesian Symbolic Regression (Jin et al. 2020)
    [paper](https://arxiv.org/abs/1910.08892)
    ,
    [code](https://github.com/ying531/MCMC-SymReg)
- Deep Symbolic Regression (Petersen et al. 2020)
    [paper](https://arxiv.org/pdf/1912.04871)
    ,
    [code](https://github.com/brendenpetersen/deep-symbolic-optimization)
- Fast Function Extraction (McConaghy 2011)
    [paper](http://trent.st/content/2011-GPTP-FFX-paper.pdf)
    ,
    [code](https://github.com/natekupp/ffx)
- Feature Engineering Automation Tool (La Cava et al. 2017)
    [paper](https://arxiv.org/abs/1807.00981)
    ,
    [code](https://github.com/lacava/feat)
- epsilon-Lexicase Selection (La Cava et al. 2016)
    [paper](https://arxiv.org/abs/1905.13266)
    ,
    [code](https://github.com/cavalab/ellyn)
- GP-based Gene-pool Optimal Mixing Evolutionary Algorithm (Virgolin et al. 2017)
    [paper](https://dl.acm.org/doi/pdf/10.1145/3071178.3071287?casa_token=CHa8EK_ic5gAAAAA:mOAOCu6CL-jHobGWKD2wco4NbpCyS-XTY5thb1dPPsyUkTkLHzmLMF41MWMGWLyFv1G8n-VFaqmXSw)
    ,
    [code](https://github.com/marcovirgolin/GP-GOMEA/)
- gplearn (Stephens)
    [code](https://github.com/trevorstephens/gplearn)
- Interaction-Transformation Evolutionary Algorithm (de Franca and Aldeia, 2020)
    [paper](https://www.mitpressjournals.org/doi/abs/10.1162/evco_a_00285)
    ,
    [code](https://github.com/folivetti/ITEA/)
- Multiple Regression GP (Arnaldo et al. 2014)
    [paper](https://dl.acm.org/doi/pdf/10.1145/2576768.2598291?casa_token=Oh2e7jDBgl0AAAAA:YmYJhFniOrU0yIhsqrHGzUN_60veH56tfwizre94uImDpYyp9RcadUyv_VZf8gH7v3uo5SxjjIPPUA)
    ,
    [code](https://github.com/flexgp/gp-learners)
- Operon (Burlacu et al. 2020)
    [paper](https://dl.acm.org/doi/pdf/10.1145/3377929.3398099?casa_token=HJgFp342K0sAAAAA:3Xbelm-5YjcIgjMvqLcyoTYdB0wNR0S4bYcQBGUiwOuwqbFfV6YnE8YKGINija_V6wCi6dahvQ3Pxg)
    ,
    [code](https://github.com/heal-research/operon)

- Semantic Backpropagation GP (Virgolin et al. 2019)
    [paper](https://dl.acm.org/doi/pdf/10.1145/3321707.3321758?casa_token=v43VobsGalkAAAAA:Vj8S9mHAv-H4tLm_GCL4DJdfW3e5SVUtD6J3gIQh0vrNzM3s6psjl-bwO2NMnxLN0thRJ561OZ0sQA)
    ,
    [code](https://github.com/marcovirgolin/GP-GOMEA)

Methods Staged for Benchmarking:

- PySR (Cranmer 2020)
    [code](https://github.com/MilesCranmer/PySR)
- PSTree (Zhang 2021)
    [code](https://github.com/hengzhe-zhang/PS-Tree)

# Contribute

We are actively updating and expanding this benchmark.
Want to add your method?
See our [Contribution Guide.](https://cavalab.org/srbench/contributing/)

# References

A pre-print of the current version of the benchmark is available:
[v2.0](https://github.com/EpistasisLab/regression-benchmark/releases/tag/v2.0) was reported in our Neurips 2021 paper:

La Cava, W., Orzechowski, P., Burlacu, B., de França, F. O., Virgolin, M., Jin, Y., Kommenda, M., & Moore, J. H. (2021).
Contemporary Symbolic Regression Methods and their Relative Performance.
_Neurips Track on Datasets and Benchmarks._
[arXiv](https://arxiv.org/abs/2107.14351),
[neurips.cc](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/c0c7c76d30bd3dcaefc96f40275bdc0a-Abstract-round1.html)

[v1.0](https://github.com/EpistasisLab/regression-benchmark/releases/tag/v1.0) was reported in our GECCO 2018 paper:

Orzechowski, P., La Cava, W., & Moore, J. H. (2018).
Where are we now? A large benchmark study of recent symbolic regression methods.
GECCO 2018. [DOI](https://doi.org/10.1145/3205455.3205539), [Preprint](https://www.researchgate.net/profile/Patryk_Orzechowski/publication/324769381_Where_are_we_now_A_large_benchmark_study_of_recent_symbolic_regression_methods/links/5ae779b70f7e9b837d392dc9/Where-are-we-now-A-large-benchmark-study-of-recent-symbolic-regression-methods.pdf)

# Contact

William La Cava ([@lacava](https://github.com/lacava)), william dot lacava at childrens dot harvard dot edu
