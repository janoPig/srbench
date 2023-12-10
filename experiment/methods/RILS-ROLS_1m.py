from rils_rols.rils_rols import RILSROLSRegressor as RILSROLSRegressor_1m
from symbolic_utils import complexity as cplx
import sympy as sp


# Create the pipeline for the model
eval_kwargs = {'scale_x': False, 'scale_y': False}
est = RILSROLSRegressor_1m(max_seconds=60, max_fit_calls=1000000000, max_complexity=50, sample_size=1.0)


def model(est):
    return str(est.model_string())


def complexity(est):
    return cplx(sp.parse_expr(str(est.model_string())))
