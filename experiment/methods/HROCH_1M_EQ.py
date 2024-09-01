from HROCH import SymbolicRegressor as HROCH_1M_EQ
from symbolic_utils import complexity as cplx
import sympy as sp


# Create the pipeline for the model
eval_kwargs = {'scale_x': False, 'scale_y': False}
# evaluate 1M equations(each iteration try 15 mutations)
est = HROCH_1M_EQ(time_limit=0, iter_limit=1000000//15, num_threads=1)


def model(est):
    return str(est.sexpr_)


def complexity(est):
    return cplx(sp.parse_expr(est.sexpr_))
