from HROCH import PHCRegressor as PHCRegressor4
from symbolic_utils import complexity as cplx
import sympy as sp


# Create the pipeline for the model
eval_kwargs = {'scale_x': False, 'scale_y': False}
# fixed iter limit 500'000
est = PHCRegressor4(iter_limit=500000*64, time_limit=0.0, num_threads=1)


def model(est):
    return str(est.sexpr)


def complexity(est):
    return cplx(sp.parse_expr(est.sexpr))
