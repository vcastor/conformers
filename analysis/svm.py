# -*- coding: UTF-8 -*-
# Support vector classification of sites on standardised descriptor combinations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import label, binary_fill_holes
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from plots import LABELS

def scan(df, combos, y, kernel='rbf', C=1.0, gamma='scale'):
    """
    In-sample and 20-split test accuracy of an SVC on every combination of columns.
    Returns [(mean, std, in-sample, combination)], best first.
    """
    rows = []
    for combo in combos:
        combo = tuple(combo)
        d     = df.dropna(subset=list(combo))
        yv    = y.loc[d.index].astype(int).values
        X     = StandardScaler().fit_transform(d[list(combo)])
        ins   = np.mean(SVC(kernel=kernel, C=C, gamma=gamma, random_state=42).fit(X, yv).predict(X) == yv)
        accs  = []
        for seed in range(20):
            Xtr, Xte, ytr, yte = train_test_split(X, yv, test_size=0.2, random_state=seed)
            accs.append(np.mean(SVC(kernel=kernel, C=C, gamma=gamma, random_state=seed).fit(Xtr, ytr).predict(Xte) == yte))
        rows.append((np.mean(accs), np.std(accs), ins, combo, yv.sum(), len(yv) - yv.sum()))

    rows.sort(key=lambda r: r[0], reverse=True)
    for mean, std, ins, combo, n1, n0 in rows:
        names = ' '.join(f'{c:10s}' for c in combo)
        print(f'{names} {n1:3d} / {n0:3d}  in-sample {100*ins:5.1f} %  test {100*mean:5.1f} ± {100*std:4.1f} %')

    return [r[:4] for r in rows]

def svmplot(df, pair, y, kernel='rbf', C=1.0, gamma='scale', xlim=None, ylim=None, title=None, badge=None, regions=False, figure=None):
    """
    Decision surface of an SVC on the z-scored pair, drawn in original units.
    Prints the misclassified sites.
    """
    d      = df.dropna(subset=list(pair))
    yv     = y.loc[d.index].astype(int).values
    X      = d[list(pair)].values
    mean   = X.mean(axis=0)
    std    = X.std(axis=0)
    model  = SVC(kernel=kernel, C=C, gamma=gamma, random_state=42).fit((X - mean)/std, yv)
    pred   = model.predict((X - mean)/std)
    wrong  = np.where(pred != yv)[0]
    lo, hi = X.min(axis=0), X.max(axis=0)
    pad    = 0.1*(hi - lo)
    x0, x1 = xlim if xlim is not None else (lo[0] - pad[0], hi[0] + pad[0])
    y0, y1 = ylim if ylim is not None else (lo[1] - pad[1], hi[1] + pad[1])
    xx, yy = np.meshgrid(np.linspace(x0, x1, 600), np.linspace(y0, y1, 600))
    Z      = model.predict(np.c_[(xx.ravel() - mean[0])/std[0], (yy.ravel() - mean[1])/std[1]]).reshape(xx.shape)

    print(f'{yv.sum()} of {len(yv)} sites in class 1, in-sample accuracy {100*np.mean(pred == yv):.1f} %')
    for i in wrong:
        site = '  '.join(str(d[c].iloc[i]).strip() for c in ('family', 'solvent', 'smiles', 'name') if c in d)
        print(f'true {yv[i]} pred {pred[i]}  {pair[0]} {X[i, 0]:.3f}  {pair[1]} {X[i, 1]:.3f}  {site}')

    plt.figure(figsize=(12, 8))
    plt.contourf(xx, yy, Z, alpha=0.4, extend='both', cmap='viridis')
    plt.scatter(X[:, 0], X[:, 1], c=yv, s=60, edgecolor='k')
    plt.scatter(X[wrong, 0], X[wrong, 1], c='black', marker='x', s=150, label='Misclassified', linewidth=3)
    plt.xlabel(LABELS.get(pair[0], pair[0]), fontsize=36)
    plt.ylabel(LABELS.get(pair[1], pair[1]), fontsize=36)
    if title is not None:
        plt.title(title, fontsize=40)
    plt.xticks(fontsize=26)
    plt.yticks(fontsize=26)
    plt.xlim(x0, x1)
    plt.ylim(y0, y1)

    if regions:
        labelled, n = label(Z, structure=np.ones((3, 3)))
        for k in range(1, n + 1):
            mask = labelled == k
            plt.text(xx[mask].mean(), yy[mask].mean(), f'Region {k}', fontsize=22, color='black',
                     weight='bold', ha='center', va='center',
                     bbox=dict(facecolor='yellow', edgecolor='black', boxstyle='round,pad=0.3', alpha=0.6))

    if badge is None:
        badge = f'{100*np.mean(pred == yv):.1f}%'
    plt.text(x0 + 0.03*(x1 - x0), y1 - 0.03*(y1 - y0), f'$\\times$ Misclassified\nAccuracy: {badge}',
             fontsize=22, color='black', ha='left', va='top',
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.4', alpha=0.8))

    plt.tight_layout()
    if figure:
        plt.savefig(figure)
        plt.close()
    else:
        plt.show()

def regions(df, pair, y, kernel='rbf', C=1.0, gamma='scale'):
    """
    Id of the connected class-1 decision area that holds each site, 0 outside.
    Same mesh as svmplot without limits, so the ids match its 'Region n' tags.
    """
    d        = df.dropna(subset=list(pair))
    yv       = y.loc[d.index].astype(int).values
    X        = d[list(pair)].values
    mean     = X.mean(axis=0)
    std      = X.std(axis=0)
    model    = SVC(kernel=kernel, C=C, gamma=gamma, random_state=42).fit((X - mean)/std, yv)
    lo, hi   = X.min(axis=0), X.max(axis=0)
    pad      = 0.1*(hi - lo)
    xx, yy   = np.meshgrid(np.linspace(lo[0] - pad[0], hi[0] + pad[0], 600), np.linspace(lo[1] - pad[1], hi[1] + pad[1], 600))
    Z        = model.predict(np.c_[(xx.ravel() - mean[0])/std[0], (yy.ravel() - mean[1])/std[1]]).reshape(xx.shape)
    labelled = label(Z, structure=np.ones((3, 3)))[0]
    ix       = np.abs(xx[0][:, None] - X[:, 0]).argmin(axis=0)
    iy       = np.abs(yy[:, 0][:, None] - X[:, 1]).argmin(axis=0)

    return pd.Series(labelled[iy, ix], index=d.index, name='region')

def connected(df, pair, y, Cs, gammas):
    """
    RBF classifiers of a C × gamma grid whose class-1 area is one connected, hole-free region.
    Ranked by misclassified count, then 20-split test accuracy; returns the best (C, gamma) or None.
    """
    d      = df.dropna(subset=list(pair))
    yv     = y.loc[d.index].astype(int).values
    X      = d[list(pair)].values
    mean   = X.mean(axis=0)
    std    = X.std(axis=0)
    Xs     = (X - mean)/std
    lo, hi = X.min(axis=0), X.max(axis=0)
    pad    = 0.2*(hi - lo)
    xx, yy = np.meshgrid(np.linspace(lo[0] - pad[0], hi[0] + pad[0], 400), np.linspace(lo[1] - pad[1], hi[1] + pad[1], 400))
    grid   = np.c_[(xx.ravel() - mean[0])/std[0], (yy.ravel() - mean[1])/std[1]]
    eight  = np.ones((3, 3))

    candidates = []
    for gamma in gammas:
        for C in Cs:
            model = SVC(kernel='rbf', C=C, gamma=gamma, random_state=42).fit(Xs, yv)
            Z     = model.predict(grid).reshape(xx.shape).astype(bool)
            if label(Z, eight)[1] != 1 or binary_fill_holes(Z).sum() != Z.sum():
                continue
            pred  = model.predict(Xs)
            wrong = np.where(pred != yv)[0]
            accs  = []
            for seed in range(20):
                Xtr, Xte, ytr, yte = train_test_split(Xs, yv, test_size=0.2, random_state=seed)
                accs.append(np.mean(SVC(kernel='rbf', C=C, gamma=gamma, random_state=seed).fit(Xtr, ytr).predict(Xte) == yte))
            candidates.append((len(wrong), -np.mean(accs), C, gamma, 100*np.mean(pred == yv), 100*np.mean(accs), 100*np.std(accs), wrong))

    candidates.sort(key=lambda t: t[:2])
    for n, _, C, gamma, ins, acc, sd, wrong in candidates:
        print(f'C {C:5.2f}  gamma {gamma:4.2f}  in-sample {ins:5.1f} %  test {acc:5.1f} ± {sd:4.1f} %  '
              f'misclassified {n}: ' + ', '.join(d.smiles.iloc[i] for i in wrong))

    if not candidates:
        return None
    return candidates[0][2], candidates[0][3]
