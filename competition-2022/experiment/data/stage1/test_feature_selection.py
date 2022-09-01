import pandas as pd
from pathlib import Path
from sklearn.metrics import r2_score
import os

dir = os.path.dirname(os.path.realpath(__file__))
dir += '/data'

expr1 = '0.11 * x1**3 + 0.91 * x3*x5 + 0.68 * x7 * x9 + 0.26 * x11**2 * x13 + 0.13 * x15*x17*x19'
expr2 = '0.11 * x1**3 + 0.91 * x2*x3 + 0.68 * x4 * x5 + 0.26 * x6**2 * x7 + 0.13 * x8*x9*x10'

i = 0
score1 = 0.0
score2 = 0.0
for f in Path(dir).rglob('*.csv'):
    if str(f).find('featureselection') < 0:
        continue
    data = pd.read_csv(f)
    Y = data["y"].to_frame()
    Y1 = data.eval(expr1)
    Y2 = data.eval(expr2)

    score1 += r2_score(Y1, Y)
    score2 += r2_score(Y2, Y)

    i += 1

print(f'processed {i} files')
print(f'average r2= {score1/i} expr= {expr1}')
print(f'average r2= {score2/i} expr= {expr2}')
print(f'true expression= {expr1 if score1 > score2 else expr2}')
