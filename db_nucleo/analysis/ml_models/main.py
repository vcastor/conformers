#!/usr/bin/python3
import os
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import matplotlib.pyplot as plt
import models_dv.random_forest as rf
import models_dv.neural_network as nnet
import models_dv.svr as svr
import models_dv.gbr as gbr
import models_dv.gpr as gpr
from data_loader import load_data

N_SPLITS = 30
hostname = os.popen("hostname").read().strip()
if hostname == 'Ada':
    ROBUST = False
    db_path = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db'
    features = ['electrofuge', 'q_qtaim_w', 'HOMO', 'sfplus', 'muplusfplus', 'mu', 'eigenchi']
elif hostname == 'rameau':
    ROBUST = True
    db_path = '/home/victoria/Documents/nucleo/nucleo_data.db'
    features = [
        'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
        'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
        'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
        'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
        'P', 'Pf2', 'HOMO', 'eigenchi'
    ]
else:
    quit(f"Unknown hostname '{hostname}'. Please set ROBUST manually.")

X, y, _ = load_data(db_path, features=features)

model_funcs = [rf.run_model, svr.run_model, gbr.run_model, nnet.run_model, gpr.run_model]
colors      = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']

plt.figure(figsize=(8, 8))
plt.plot([min(y), max(y)], [min(y), max(y)], 'k--', label='Ideal', linewidth=2)

summary = []
for func, color in zip(model_funcs, colors):
    y_tests, y_preds, maes, r2s, label = func(
        X, y, n_splits=N_SPLITS, robust=ROBUST, feature_names=features
    )
    mae_m, mae_s = np.mean(maes), np.std(maes)
    r2_m, r2_s   = np.mean(r2s),  np.std(r2s)
    summary.append((label, mae_m, mae_s, r2_m, r2_s))

    full_label = f'{label} (MAE {mae_m:.2f}±{mae_s:.2f}, R² {r2_m:.2f}±{r2_s:.2f})'
    yt_all = np.concatenate(y_tests)
    yp_all = np.concatenate(y_preds)
    plt.scatter(yt_all, yp_all, alpha=0.25, label=full_label,
                edgecolor='k', linewidths=0.3, s=35, color=color)

plt.xlabel(r'Experimental $N_{Mayr}$', fontsize=20)
plt.ylabel(r'Predicted $N_{Mayr}$', fontsize=20)
plt.title(f'Model Comparison ({N_SPLITS} splits, {"robust" if ROBUST else "light"})', fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=14)
plt.legend(fontsize=11, loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.savefig(f'ml_models_{"robust" if ROBUST else "light"}_{N_SPLITS}.pdf')

print('\n=== Summary (mean ± std over splits) ===')
print(f'{"model":20s}  {"MAE":>16s}   {"R²":>16s}')
for name, mm, ms, rm, rs in summary:
    print(f'{name:20s}  {mm:7.3f} ± {ms:5.3f}   {rm:7.3f} ± {rs:5.3f}')

