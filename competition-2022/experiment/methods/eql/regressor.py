#!/usr/bin/env python3
from .eql.est import EQL
import pandas as pd
from sklearn.model_selection import GridSearchCV


base = EQL(n_iter=10_000)

hp = {
    "reg": (1e-4, 1e-3, 1e-2, 5e-2),
    "n_layers": (1, 2),
    "functions": (
        "id;mul;cos;sin;exp;square;sqrt;id;mul;cos;sin;exp;square;sqrt;log",
        "id;mul;cos;div;sqrt;cos;sin;div;mul;mul;cos;id;log",
    ),
}

est = GridSearchCV(estimator=base, param_grid=hp, cv=2, refit=True, n_jobs=4,
                   verbose=2)
# est = base


def model(est, X=None):
    try:
        model_str = str(est.best_estimator_.get_eqn())
    except AttributeError:
        return ""

    if isinstance(X, pd.DataFrame):
        mapping = {"x" + str(i): k for i, k in enumerate(X.columns)}
        for k, v in reversed(mapping.items()):
            model_str = model_str.replace(k, v)

    return model_str


eval_kwargs = {
    'test_params': {'param_grid': {'n_iter': [10], **hp}},
    'DataFrame':False
}
