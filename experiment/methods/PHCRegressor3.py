from HROCH import PHCRegressor as PHCRegressor3
from symbolic_utils import complexity as cplx
import sympy as sp


# Create the pipeline for the model
eval_kwargs = {'scale_x': False, 'scale_y': False}
est = PHCRegressor3(time_limit=5*60.0, num_threads=1)


def model(est):
    return str(est.sexpr)


def complexity(est):
    return cplx(sp.parse_expr(est.sexpr))
