#!/usr/bin/python3
import os
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import matplotlib.pyplot as plt
import models_dv.random_forest as rf
import models_dv.svr as svr
import models_dv.gbr as gbr
import models_dv.gpr as gpr
import models_dv.extra_trees as et
import models_dv.histgbr as hgbr
import models_dv.xgb as xgb
import models_dv.lgbm as lgbm
import models_dv.stacking as stacking
from data_loader import load_data, load_keys

Y_MIN, Y_MAX = 8, 20
N_OUTLIERS   = 5

hostname = os.popen("hostname").read().strip()
if hostname == 'Ada':
    ROBUST   = False
    N_SPLITS = 1
    db_path  = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db'
    features = ['electrofuge', 'q_qtaim_w', 'HOMO', 'sfplus', 'muplusfplus', 'mu', 'eigenchi']
elif hostname in ('rameau', 'aragorn'):
    ROBUST   = True
    N_SPLITS = 20
    db_path  = '/home/victoria/Documents/nucleo/nucleo_data.db'
    features = [
        'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
        'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
        'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
        'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'electrostatic_potential',
        'P', 'Pf2', 'HOMO', 'eigenchi', 'condensed_linear_response',
        'q_qtaim_w', 'condensed_linear_response_w',
    ]
else:
    quit(f"Unknown hostname '{hostname}'. Please set ROBUST manually.")

X, y, _ = load_data(db_path, features=features)

mask = (y >= Y_MIN) & (y <= Y_MAX)
X = X[mask].reset_index(drop=True)
y = y[mask].reset_index(drop=True)
keys = load_keys(db_path, features=features)[mask].reset_index(drop=True)
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
active_features = list(X.columns)
print(f'Active features ({len(active_features)}): {active_features}')


model_funcs = [
    rf.run_model,
    svr.run_model,
    gbr.run_model,
    gpr.run_model,
    et.run_model,
    hgbr.run_model,
    xgb.run_model,
    lgbm.run_model,
    stacking.run_model,
]
colors = [
    'tab:blue', 'tab:orange', 'tab:green', 'tab:purple',
    'tab:red', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:cyan',
]

base_tag = "robust" if ROBUST else "light"


def run_pipeline(X, y, suffix=''):
    file_tag = f'{base_tag}{suffix}'
    plt.figure(figsize=(8, 8))
    plt.plot([Y_MIN, Y_MAX], [Y_MIN, Y_MAX], 'k--', label='Ideal', linewidth=2)

    summary = []
    per_model_per_point = {}
    for func, color in zip(model_funcs, colors):
        result = func(
            X, y,
            n_splits=N_SPLITS, robust=ROBUST,
            feature_names=active_features, tag=file_tag,
        )
        y_tests, y_preds, test_idxs, maes, r2s, label = result

        if not y_tests:
            print(f'[{label}] skipped (package missing)')
            continue

        mae_m, mae_s = np.mean(maes), np.std(maes)
        r2_m,  r2_s  = np.mean(r2s),  np.std(r2s)
        summary.append((label, mae_m, mae_s, r2_m, r2_s))

        full_label = f'{label} (MAE {mae_m:.2f}±{mae_s:.2f}, R² {r2_m:.2f}±{r2_s:.2f})'
        yt_all = np.concatenate(y_tests)
        yp_all = np.concatenate(y_preds)
        plt.scatter(yt_all, yp_all, alpha=0.25, label=full_label,
                    edgecolor='k', linewidths=0.3, s=35, color=color)

        mp = {}
        for te_idx, yp in zip(test_idxs, y_preds):
            for i, p in zip(te_idx, yp):
                mp.setdefault(int(i), []).append(float(p))
        per_model_per_point[label] = mp

    title_extra = ', no outliers' if suffix else ''
    plt.xlabel(r'Experimental $N_{Mayr}$', fontsize=20)
    plt.ylabel(r'Predicted $N_{Mayr}$', fontsize=20)
    plt.title(f'Model Comparison ({N_SPLITS} splits, {base_tag}{title_extra})', fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'ml_models_{base_tag}_{N_SPLITS}{suffix}.pdf')
    plt.close()

    print(f'\n=== Summary ({file_tag}, mean ± std over {N_SPLITS} splits) ===')
    print(f'{"model":20s}  {"MAE":>16s}   {"R²":>16s}')
    for name, mm, ms, rm, rs in sorted(summary, key=lambda x: x[1]):
        print(f'{name:20s}  {mm:7.3f} ± {ms:5.3f}   {rm:7.3f} ± {rs:5.3f}')

    return per_model_per_point


# First pass: full data
per_model_per_point = run_pipeline(X, y, suffix='')

y_arr  = np.asarray(y)
labels = list(per_model_per_point.keys())
err_matrix = np.full((len(labels), len(y)), np.nan)
for k, lab in enumerate(labels):
    for i, preds in per_model_per_point[lab].items():
        err_matrix[k, i] = abs(y_arr[i] - np.mean(preds))

all_nan = np.all(np.isnan(err_matrix), axis=0)
max_err = np.where(all_nan, -1.0, np.nanmax(err_matrix, axis=0))
outlier_idx = np.argsort(max_err)[-N_OUTLIERS:][::-1]

print(f'\n=== Top {N_OUTLIERS} outliers (worst per-model error) ===')
header = f'{"idx":>5}  {"y_true":>7}  {"worst_model":>20}  {"|err|":>6}  {"mean_err":>8}  smiles  name'
print(header)
for i in outlier_idx:
    j = int(i)
    col = err_matrix[:, j]
    finite = ~np.isnan(col)
    k_worst = int(np.argmax(np.where(finite, col, -np.inf)))
    print(f'{j:5d}  {y_arr[j]:7.2f}  {labels[k_worst]:>20}  '
          f'{col[k_worst]:6.2f}  {np.nanmean(col):8.2f}  {keys["smiles"][j]}  {keys["name"][j]}')

# Second pass: drop outliers, retrain
keep_mask = np.ones(len(y), dtype=bool)
keep_mask[outlier_idx] = False
X_clean = X[keep_mask].reset_index(drop=True)
y_clean = y[keep_mask].reset_index(drop=True)
print(f'\nDropped outliers: {len(y_clean)} systems remain (was {len(y)})')

run_pipeline(X_clean, y_clean, suffix='_without_outliers')

