import sympy as sp
import json
from pathlib import Path

import sys
import os
sys.path.append(os.path.join(os.path.dirname(
    __file__), '..', '..', 'metrics'))

from evaluation import feature_absence_score

def fix_feature_absence_score(path:str):
    i = 0
    for f in Path(path).rglob('*.json'):
        with open(f, 'r') as of:
            d = json.load(of)
        if d['dataset'].find('featureselection') >= 0:
            tot_num_features = 20
            features = [f'x{i+1}' for i in range(tot_num_features)]
            irrelevant_features = [f'x{i+1}' for i in range(10, 20)]
            local_dict = {f: sp.Symbol(f) for f in features}
            pred_model = d['symbolic_model']
            fas = feature_absence_score(pred_model,
                                        sp.symbols(irrelevant_features),
                                        local_dict
                                        )
            before = d['feature_absence_score']
            print(f'change score {before} -> {fas}')
            d['feature_absence_score'] = fas
            with open(f, 'w', encoding='utf-8') as of:
                json.dump(d, of, ensure_ascii=False, indent=4)
            i += 1

    print('fixed', i, 'results')


#target_dir = str(Path.home()) + '/Downloads/zenodo/results_stage1'
#fix_feature_absence_score(target_dir)
