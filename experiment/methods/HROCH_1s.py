from HROCH import SymbolicRegressor as HROCH_1s
from symbolic_utils import complexity as cplx
import sympy as sp


# Create the pipeline for the model
eval_kwargs = {'scale_x': False, 'scale_y': False}
est = HROCH_1s(time_limit=1.0,num_threads=1)


def model(est):
    return str(est.sexpr)


def complexity(est):
    return cplx(sp.parse_expr(est.sexpr))
