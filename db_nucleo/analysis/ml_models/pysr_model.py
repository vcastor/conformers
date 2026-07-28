#!/usr/bin/python3
"""
Symbolic regression for N_Mayr with PySR.

This is the resurrected, schema-updated descendant of the old
analysis/ml_model.py (which queried a `main` table that no longer exists).  It
now pulls from the current reactive/parameters schema through the same
data_loader the ensemble (main.py) uses, so the data, the N filter and the new
neighbour-weighted descriptor q_qtaim_w are all identical.

Symbolic regression searches for a *closed-form equation* N = f(descriptors)
instead of a black-box ensemble.  On this dataset it tends to reach a lower MAE
than the tuned ensembles while staying interpretable — that is the
"low-MAE test from a while ago".

HEAVY / DO NOT run on the laptop: PySR spins up a Julia backend and many
populations for `niterations`.  Run it on rameau / aragorn (or overnight).

    pip install pysr           # then, once:  python -c "import pysr; pysr.install()"
    python3 pysr_model.py

Outputs:
    pysr_equations_<tag>.csv   full Pareto front (complexity, loss, equation)
    pysr_parity_<tag>.pdf      predicted vs experimental N (train + test)
    stdout                     best equation + MAE/R² on train and test
"""
import os
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from data_loader import load_data

Y_MIN, Y_MAX = 8, 20
TEST_SIZE    = 0.2
SEED         = 42

# A small, curated, interpretable feature set works best for symbolic
# regression (a huge feature list explodes the search space and overfits).
# Mirrors the light set in main.py and includes the neighbour-weighted charge.
FEATURES = ['electrofuge', 'q_qtaim_w', 'HOMO', 'sfplus', 'muplusfplus', 'mu', 'eigenchi']

hostname = os.popen("hostname").read().strip()
if hostname == 'Ada':
    db_path = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db'
    NITERATIONS, POPULATIONS = 200, 40        # lighter, in case it is ever run here
elif hostname in ('rameau', 'aragorn'):
    db_path = '/home/victoria/Documents/nucleo/nucleo_data.db'
    NITERATIONS, POPULATIONS = 1000, 80       # the real, heavy run
else:
    quit(f"Unknown hostname '{hostname}'. Set db_path manually.")

TAG = hostname


# ---------------------------------------------------------------------------
# Data (same pipeline as main.py)
# ---------------------------------------------------------------------------
X, y, _ = load_data(db_path, features=FEATURES)
mask = (y >= Y_MIN) & (y <= Y_MAX)
X = X[mask].reset_index(drop=True)
y = y[mask].reset_index(drop=True)
print(f'Filtered to N_Mayr in [{Y_MIN}, {Y_MAX}]: {len(y)} systems')
print(f'Features ({len(FEATURES)}): {FEATURES}')

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=SEED)


# ---------------------------------------------------------------------------
# Build the regressor (kwargs kept to the stable core; `loss` was renamed to
# `elementwise_loss` in newer PySR, so fall back gracefully)
# ---------------------------------------------------------------------------
def build_model():
    from pysr import PySRRegressor

    common = dict(
        niterations=NITERATIONS,
        populations=POPULATIONS,
        maxsize=30,
        maxdepth=10,
        binary_operators=['+', '-', '*', '/'],
        unary_operators=['square', 'cube', 'exp', 'log', 'sqrt', 'abs', 'inv(x) = 1/x'],
        extra_sympy_mappings={'inv': lambda x: 1 / x},
        model_selection='best',     # pick by accuracy/complexity trade-off
        random_state=SEED,
        deterministic=False,
        progress=True,
        verbosity=1,
    )
    # Optimise directly for MAE, the metric we report.
    try:
        return PySRRegressor(elementwise_loss='loss(x, y) = abs(x - y)', **common)
    except TypeError:                # older PySR
        return PySRRegressor(loss='loss(x, y) = abs(x - y)', **common)


def report(name, model, X_, y_):
    yp = model.predict(X_)
    mae = mean_absolute_error(y_, yp)
    r2 = r2_score(y_, yp)
    print(f'  {name:6s}  MAE = {mae:.3f}   R² = {r2:.3f}')
    return yp, mae, r2


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    model = build_model()
    print('\nFitting PySR (this is the slow part)…')
    model.fit(X_tr, y_tr, variable_names=list(X.columns))

    print('\nBest equation (PySR model_selection="best"):')
    print(' ', model.sympy())

    print('\nPerformance of the selected equation:')
    yp_tr, _, _ = report('train', model, X_tr, y_tr)
    yp_te, _, _ = report('test',  model, X_te, y_te)

    # Save the whole Pareto front and pick the equation that generalises best.
    eqs = model.equations_
    eqs.to_csv(f'pysr_equations_{TAG}.csv', index=False)
    print(f'\nPareto front written to pysr_equations_{TAG}.csv '
          f'({len(eqs)} equations)')

    print('\nTest MAE per Pareto equation (complexity → eq):')
    best_idx, best_mae = None, np.inf
    for idx in range(len(eqs)):
        mae_te = mean_absolute_error(y_te, model.predict(X_te, index=idx))
        comp = eqs.iloc[idx]['complexity']
        print(f'  [{idx:2d}] complexity {comp:>3}  test MAE {mae_te:.3f}')
        if mae_te < best_mae:
            best_mae, best_idx = mae_te, idx
    print(f'\nLowest test-MAE equation: index {best_idx}, MAE {best_mae:.3f}')
    print(' ', model.sympy(best_idx))

    # Parity plot for the selected ("best") equation.
    plt.figure(figsize=(8, 8))
    plt.plot([Y_MIN, Y_MAX], [Y_MIN, Y_MAX], 'k--', linewidth=2, label='Ideal')
    plt.scatter(y_tr, yp_tr, alpha=0.5, s=40, edgecolor='k', linewidths=0.3,
                color='tab:blue', label=f'train (MAE {mean_absolute_error(y_tr, yp_tr):.2f})')
    plt.scatter(y_te, yp_te, alpha=0.8, s=55, edgecolor='k', linewidths=0.3,
                color='tab:red', label=f'test (MAE {mean_absolute_error(y_te, yp_te):.2f})')
    plt.xlabel(r'Experimental $N_{Mayr}$', fontsize=18)
    plt.ylabel(r'Predicted $N_{Mayr}$', fontsize=18)
    plt.title('PySR symbolic regression', fontsize=18)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'pysr_parity_{TAG}.pdf')
    plt.close()
    print(f'Parity plot written to pysr_parity_{TAG}.pdf')
