# -*- coding: UTF-8 -*-
# Shared figures (parity, correlation heat map, histogram, two-column correlation) and the LaTeX label of every column
import itertools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import to_hex
from scipy.stats import pearsonr

LABELS = {
    'mu':               r'$\mu$',
    'eta':              r'$\eta$',
    'softness':         r'$S$',
    'gamma':            r'$\gamma$',
    'omega':            r'$\omega$',
    'nucleofuge':       'nucleofuge',
    'electrofuge':      'electrofuge',
    'electrodonating':  r'$\omega^-$',
    'electroaccepting': r'$\omega^+$',
    'fplus':            r'$f^+$',
    'fminus':           r'$f^{-}(N)$',
    'fzero':            r'$f^0$',
    'f2':               r'$f^{(2)}$',
    'sfplus':           r'$s^+$',
    'sfminus':          r'$s^-$',
    'sfzero':           r'$s^0$',
    's2':               r'$s^{(2)}$',
    'muplusfplus':      r'$\mu^+f^+$',
    'muminusfminus':    r'$\mu^-f^-$',
    'wfplus':           r'$\omega f^+$',
    'wf2':              r'$\omega f^{(2)}$',
    'Sf2':              r'$Sf^{(2)}$',
    's2f2':             r'$S^2f^{(2)}$',
    'nucleo':           'nucleophilicity',
    'q':                r'$q(N)$',
    'hirshfeld':        r'$q_{Hirshfeld}$',
    'esp':              'ESP',
    'P':                r'$P$',
    'Pf2':              r'$Pf^{(2)}$',
    'HOMO':             'HOMO',
    'eigenchi':         r'$\chi^\lambda(N)$',
    'chi':              r'$\chi(N)$',
    'qw':               r'$q_w(N)$',
    'chiw':             r'$\chi_w(N)$',
    'Nexp':             r'$N_{Mayr}$',
    'sN':               r'$s_N$',
    'Sexp':             r'$S$',
    'St':               r'$S_t$',
    'Sr':               r'$S_r$',
    'Sv':               r'$S_v^h$',
    'dSv':              r'$\Delta S_v^G$',
    'epsilon':          r'$\varepsilon_r$',
}

COLORS = {'RF': 'tab:blue', 'SVR': 'tab:orange', 'GBR': 'tab:green', 'GPR': 'tab:purple'}

def parity(out, target, figure=None, fraction=1.0, removed=None):
    """
    Experimental against predicted target for every entry of out ({name: {'x', 'y'[, 'maes', 'r2s']}}).
    removed = {name: {'x', 'y'}} (ml.outliers) is drawn as crosses of the series colour.
    """
    removed = {m: r for m, r in (removed or {}).items() if m in out}
    names   = [m for m in COLORS if m in out] + [m for m in out if m not in COLORS]
    used    = {to_hex(COLORS[m]) for m in names if m in COLORS}
    free    = itertools.cycle([c for c in plt.rcParams['axes.prop_cycle'].by_key()['color'] if to_hex(c) not in used])
    colors  = {m: COLORS[m] if m in COLORS else next(free) for m in names}
    values  = np.concatenate([np.ravel(np.asarray(o[k], dtype=float))
                              for o in [*out.values(), *removed.values()] for k in ('x', 'y')])
    lo, hi  = np.floor(np.nanmin(values)), np.ceil(np.nanmax(values))
    rng     = np.random.default_rng(42)
    plt.figure(figsize=(8, 8))
    plt.plot([lo, hi], [lo, hi], 'k--', linewidth=1.5, label='Ideal')
    for m in names:
        x     = np.asarray(out[m]['x'], dtype=float)
        y     = np.asarray(out[m]['y'], dtype=float)
        valid = np.where(~np.isnan(y))[0]
        idx   = rng.choice(valid, size=int(fraction*len(valid)), replace=False)
        if 'maes' in out[m]:
            maes, r2s = out[m]['maes'], out[m]['r2s']
            label     = (f'{m} (MAE {np.mean(maes):.2f} $\\pm$ {np.std(maes):.2f}, '
                         f'$R^2$ {np.mean(r2s):.2f} $\\pm$ {np.std(r2s):.2f})')
        else:
            err   = y[valid] - x[valid]
            label = (f'{m} (MAE {np.mean(np.abs(err)):.2f}, '
                     f'$R^2$ {1 - np.sum(err**2)/np.sum((x[valid] - np.mean(x[valid]))**2):.2f})')
        plt.scatter(x[idx], y[idx], s=45, alpha=0.8, color=colors[m], edgecolor='k', linewidths=0.4, label=label)
        if m in removed:
            plt.scatter(removed[m]['x'], removed[m]['y'], s=70, marker='x', color=colors[m], linewidths=1.5)
    if removed:
        plt.scatter([], [], s=70, marker='x', color='k', linewidths=1.5, label='removed outliers')
    plt.xlim(lo, hi)
    plt.ylim(lo, hi)
    plt.xlabel(f'Experimental {LABELS.get(target, target)}', fontsize=22)
    plt.ylabel(f'Predicted {LABELS.get(target, target)}', fontsize=22)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.legend(fontsize=12, loc='upper left')
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    if figure:
        plt.savefig(figure)
        plt.close()
    else:
        plt.show()

def heatmap(df, columns, targets=(), figure=None):
    """
    Correlation matrix of targets + columns, values in the cells up to 12 columns, alternating ticks beyond.
    Prints the five largest positive correlations of each target.
    """
    cols   = list(targets) + list(columns)
    corr   = df[cols].corr()
    labels = [LABELS.get(c, c) for c in cols]
    for t in targets:
        print(f'Top 5 most positively correlated with {t}:')
        print(corr[t].drop(t).dropna().sort_values(ascending=False).head(5).to_string())
    if len(cols) <= 12:
        plt.figure(figsize=(8, 7))
        ax = sns.heatmap(corr, annot=True, fmt='.2f', annot_kws={'fontsize': 8, 'color': 'k'}, cmap='coolwarm',
                         center=0, vmin=-1, vmax=1, square=True, xticklabels=labels, yticklabels=labels)
        ax.tick_params(axis='x', labelrotation=90, labelsize=14)
        ax.tick_params(axis='y', labelrotation=0, labelsize=14)
    else:
        plt.figure(figsize=(14, 12))
        ax = sns.heatmap(corr, cmap='coolwarm', center=0, linewidths=0.5, square=True,
                         xticklabels=[s if i % 2 == 0 else '' for i, s in enumerate(labels)],
                         yticklabels=[s if i % 2 == 1 else '' for i, s in enumerate(labels)])
        ax.collections[0].colorbar.ax.tick_params(labelsize=22)
        ax.tick_params(axis='x', labelrotation=90, labelsize=28)
        ax.tick_params(axis='y', labelrotation=0, labelsize=28)
        ax.set_title('Correlation Matrix Heatmap', fontsize=34, pad=12)
    plt.tight_layout()
    if figure:
        plt.savefig(figure)
        plt.close()
    else:
        plt.show()

def histogram(df, x, hue=None, figure=None):
    """Step histogram with KDE, 50 bins, one series per hue value."""
    label = LABELS.get(x, x)
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x=x, hue=hue, bins=50, kde=True, element='step', stat='count')
    plt.title(f'Distribution of {label} values' + (f' by {hue}' if hue else ''), fontsize=18)
    plt.xlabel(f'{label} value', fontsize=16)
    plt.ylabel('Count', fontsize=16)
    plt.tick_params(axis='both', labelsize=14)
    plt.tight_layout()
    if figure:
        plt.savefig(figure)
        plt.close()
    else:
        plt.show()

def correlate(df, x, y, figure=None):
    """Pearson correlation of two columns over the rows with both values, scatter and least-squares line."""
    d      = df[[x, y]].dropna()
    xv, yv = d[x].values, d[y].values
    r, p   = pearsonr(xv, yv)
    line   = np.poly1d(np.polyfit(xv, yv, 1))
    print(f'Sample size: {len(d)}')
    print(f'Correlation coefficient: {r:.6f}')
    print(f'R-squared: {r**2:.6f}')
    print(f'P-value: {p:.6e}')
    plt.figure(figsize=(8, 6))
    plt.scatter(xv, yv, alpha=0.6)
    plt.xlabel(LABELS.get(x, x))
    plt.ylabel(LABELS.get(y, y))
    plt.title(f'Correlation: r = {r:.4f}, R² = {r**2:.4f}')
    plt.plot(xv, line(xv), 'r--', alpha=0.8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if figure:
        plt.savefig(figure)
        plt.close()
    else:
        plt.show()
