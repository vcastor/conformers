#!/usr/bin/python3
"""
Baseline run: every model with its out-of-the-box default hyperparameters.
No tuning, no search — just raw defaults on the same data and splits as main.py.
Compare the printed summary with the one from main.py to gauge how much tuning helps.
"""
import os
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor,
    ExtraTreesRegressor, HistGradientBoostingRegressor, StackingRegressor,
)
from sklearn.svm import SVR
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel as C, WhiteKernel
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from data_loader import load_data

Y_MIN, Y_MAX = 8, 20
N_OUTLIERS   = 5

hostname = os.popen("hostname").read().strip()
if hostname == 'Ada':
    N_SPLITS = 1
    db_path  = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db'
    features = ['electrofuge', 'q_qtaim_w', 'HOMO', 'sfplus', 'muplusfplus', 'mu', 'eigenchi']
elif hostname in ('rameau', 'aragorn'):
    N_SPLITS = 20
    db_path  = '/home/victoria/Documents/nucleo/nucleo_data.db'
    features = [
        'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
        'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
        'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
        'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
        'P', 'Pf2', 'HOMO', 'eigenchi', 'condensed_linear_response',
        'q_qtaim_w', 'condensed_linear_response_w',
    ]
else:
    quit(f"Unknown hostname '{hostname}'.")

X, y, _ = load_data(db_path, features=features)
mask = (y >= Y_MIN) & (y <= Y_MAX)
X = X[mask].reset_index(drop=True)
y = y[mask].reset_index(drop=True)
print(f'Filtered to N_Mayr in [{Y_MIN}, {Y_MAX}]: {len(y)} systems')


def remove_correlated_features(X, threshold=0.95):
    corr_matrix = X.corr().abs()
    upper = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )
    to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
    return set(to_drop)


corr_drop = remove_correlated_features(X, threshold=0.95)
if corr_drop:
    print(f'Removing {len(corr_drop)} highly correlated features: {sorted(corr_drop)}')
    X = X.drop(columns=list(corr_drop))
print(f'Active features ({X.shape[1]}): {list(X.columns)}')


def _default_stacking():
    base = [
        ('rf',   RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=10)),
        ('et',   ExtraTreesRegressor(n_estimators=100, random_state=42, n_jobs=10)),
        ('hgbr', HistGradientBoostingRegressor(random_state=42)),
        ('svr',  make_pipeline(StandardScaler(), SVR())),
    ]
    try:
        import xgboost as xgb
        base.append(('xgb', xgb.XGBRegressor(random_state=42, n_jobs=10, verbosity=0)))
    except ImportError:
        pass
    try:
        import lightgbm as lgb
        base.append(('lgbm', lgb.LGBMRegressor(random_state=42, n_jobs=10, verbose=-1)))
    except ImportError:
        pass
    return StackingRegressor(estimators=base, final_estimator=Ridge(), cv=5, n_jobs=10)


MODELS = [
    ('Random Forest', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=10)),
    ('GBR',           GradientBoostingRegressor(random_state=42)),
    ('SVR',           make_pipeline(StandardScaler(), SVR())),
    ('GPR',           make_pipeline(
                          StandardScaler(),
                          GaussianProcessRegressor(
                              kernel=C(1.0) * Matern(nu=2.5) + WhiteKernel(),
                              normalize_y=True, random_state=42,
                          ))),
    ('ExtraTrees',    ExtraTreesRegressor(n_estimators=100, random_state=42, n_jobs=10)),
    ('HistGBR',       HistGradientBoostingRegressor(random_state=42)),
]

try:
    import xgboost as xgb
    MODELS.append(('XGBoost', xgb.XGBRegressor(random_state=42, n_jobs=10, verbosity=0)))
except ImportError:
    pass

try:
    import lightgbm as lgb
    MODELS.append(('LightGBM', lgb.LGBMRegressor(random_state=42, n_jobs=10, verbose=-1)))
except ImportError:
    pass

MODELS.append(('Stacking', _default_stacking()))

COLORS = [
    'tab:blue', 'tab:orange', 'tab:green', 'tab:purple',
    'tab:red', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:cyan', 'tab:olive',
]


def evaluate_defaults(X, y, suffix=''):
    indices = np.arange(len(X))
    plt.figure(figsize=(8, 8))
    plt.plot([Y_MIN, Y_MAX], [Y_MIN, Y_MAX], 'k--', label='Ideal', linewidth=2)

    summary = []
    per_model_per_point = {}

    for (label, model), color in zip(MODELS, COLORS):
        print(f'Running {label} (defaults)...')
        y_tests, y_preds, test_idxs, maes, r2s = [], [], [], [], []
        for seed in range(N_SPLITS):
            tr, te = train_test_split(indices, test_size=0.2, random_state=seed)
            import sklearn.base as _base
            m = _base.clone(model)
            m.fit(X.iloc[tr], y.iloc[tr])
            yp = m.predict(X.iloc[te])
            y_tests.append(np.asarray(y.iloc[te]))
            y_preds.append(yp)
            test_idxs.append(np.asarray(te))
            maes.append(mean_absolute_error(y.iloc[te], yp))
            r2s.append(r2_score(y.iloc[te], yp))

        mae_m, mae_s = np.mean(maes), np.std(maes)
        r2_m,  r2_s  = np.mean(r2s),  np.std(r2s)
        summary.append((label, mae_m, mae_s, r2_m, r2_s))

        full_label = f'{label} (MAE {mae_m:.2f}±{mae_s:.2f}, R² {r2_m:.2f}±{r2_s:.2f})'
        plt.scatter(np.concatenate(y_tests), np.concatenate(y_preds),
                    alpha=0.25, label=full_label,
                    edgecolor='k', linewidths=0.3, s=35, color=color)

        mp = {}
        for te_idx, yp in zip(test_idxs, y_preds):
            for i, p in zip(te_idx, yp):
                mp.setdefault(int(i), []).append(float(p))
        per_model_per_point[label] = mp

    title_extra = ', no outliers' if suffix else ''
    plt.xlabel(r'Experimental $N_{Mayr}$', fontsize=20)
    plt.ylabel(r'Predicted $N_{Mayr}$', fontsize=20)
    plt.title(f'Defaults Comparison ({N_SPLITS} splits{title_extra})', fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'ml_defaults_{N_SPLITS}{suffix}.pdf')
    plt.close()

    print(f'\n=== Summary defaults{suffix} — mean ± std over {N_SPLITS} splits ===')
    print(f'{"model":20s}  {"MAE":>16s}   {"R²":>16s}')
    for name, mm, ms, rm, rs in sorted(summary, key=lambda x: x[1]):
        print(f'{name:20s}  {mm:7.3f} ± {ms:5.3f}   {rm:7.3f} ± {rs:5.3f}')

    return per_model_per_point


# First pass: full data
per_model_per_point = evaluate_defaults(X, y)

# Outlier detection (same logic as main.py)
y_arr  = np.asarray(y)
labels = list(per_model_per_point.keys())
err_matrix = np.full((len(labels), len(y)), np.nan)
for k, lab in enumerate(labels):
    for i, preds in per_model_per_point[lab].items():
        err_matrix[k, i] = abs(y_arr[i] - np.mean(preds))

all_nan = np.all(np.isnan(err_matrix), axis=0)
max_err = np.where(all_nan, -1.0, np.nanmax(err_matrix, axis=0))
outlier_idx = np.argsort(max_err)[-N_OUTLIERS:][::-1]

print(f'\n=== Top {N_OUTLIERS} outliers ===')
print(f'{"idx":>5}  {"y_true":>7}  {"worst_model":>20}  {"|err|":>6}  {"mean_err":>8}')
for i in outlier_idx:
    j = int(i)
    col = err_matrix[:, j]
    finite = ~np.isnan(col)
    k_worst = int(np.argmax(np.where(finite, col, -np.inf)))
    print(f'{j:5d}  {y_arr[j]:7.2f}  {labels[k_worst]:>20}  '
          f'{col[k_worst]:6.2f}  {np.nanmean(col):8.2f}')

# Second pass: drop outliers
keep_mask = np.ones(len(y), dtype=bool)
keep_mask[outlier_idx] = False
X_clean = X[keep_mask].reset_index(drop=True)
y_clean = y[keep_mask].reset_index(drop=True)
print(f'\nDropped outliers: {len(y_clean)} systems remain (was {len(y)})')

evaluate_defaults(X_clean, y_clean, suffix='_without_outliers')
