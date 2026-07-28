#!/usr/bin/python3
"""
React/no-react classification with neighbour-weighted q_qtaim and the
*eigenchi* descriptor.

The .pout files only carry per-atom lists for distances, q_qtaim, clr and
electrostatic_potential — no eigenchi.  Eigenchi is fetched from the SQLite
database (one value per analysed atom) and matched to each .pout entry via
(experimental_N, experimental_Sn) plus the analysed-atom q_qtaim used as a
tie-breaker.  Entries whose eigenchi is missing or NaN in the database are
skipped, the same way `connect_db` drops NaN rows in the clustering pipeline.
"""
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.svm import SVC
from scipy.optimize import minimize
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, classification_report, confusion_matrix)
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
import warnings
warnings.filterwarnings('ignore')

DB_PATH = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db'

# ---------------------------------------------------------------------------
# .pout readers (same layout as opt4.py)
# ---------------------------------------------------------------------------
def read_react(filename):
    data = {"natoms": [], "expN": [], "expSn": [], "distances": [],
            "q_qtaim": [], "clr": [], "electrostatic_potential": [],
            "electrofuge": []}
    with open(filename, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            data["natoms"].append(int(lines[i].strip())); i += 1
            expN, expSn = map(float, lines[i].split())
            data["expN"].append(expN); data["expSn"].append(expSn); i += 1
            data["distances"].append(list(map(float, lines[i].split()))); i += 1
            data["q_qtaim"].append(list(map(float, lines[i].split()))); i += 1
            data["clr"].append(list(map(float, lines[i].split()))); i += 1
            data["electrostatic_potential"].append(list(map(float, lines[i].split())))
            i += 2
            data["electrofuge"].append(float(lines[i].strip())); i += 1
    return data

def read_noreact(filename):
    data = {"natoms": [], "expN": [], "expSn": [], "distances": [],
            "q_qtaim": [], "clr": []}
    with open(filename, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            data["natoms"].append(int(lines[i].strip())); i += 1
            expN, expSn = map(float, lines[i].split())
            data["expN"].append(expN); data["expSn"].append(expSn); i += 1
            data["distances"].append(list(map(float, lines[i].split()))); i += 1
            data["q_qtaim"].append(list(map(float, lines[i].split()))); i += 1
            data["clr"].append(list(map(float, lines[i].split()))); i += 1
    return data

# ---------------------------------------------------------------------------
# Database lookup for eigenchi
# ---------------------------------------------------------------------------
def fetch_eigenchi(data, table_name):
    """
    For every entry in `data`, return the eigenchi of the analysed atom from
    the SQLite database.  Missing rows or NaN values come back as None — the
    caller drops them.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if table_name == 'reactive':
        cur.execute("""
            SELECT p.experimental_N, p.experimental_Sn, t.q_qtaim, t.eigenchi
            FROM reactive t
            JOIN parameters p
              ON t.smiles = p.smiles
             AND t.solvent = p.solvent
             AND t.atom_analysed = p.atom_analysed
        """)
    elif table_name == 'no_reactive':
        cur.execute("SELECT q_qtaim, eigenchi FROM no_reactive")
    else:
        raise ValueError(f"Unknown table_name: {table_name}")

    rows = cur.fetchall()
    conn.close()

    eigenchis = []
    for i in range(len(data["natoms"])):
        q_analysed = data["q_qtaim"][i][0]   # first atom = analysed (distance 0.0)

        if table_name == 'reactive':
            expN, expSn = data["expN"][i], data["expSn"][i]
            candidates = [(q, e) for (eN, eSn, q, e) in rows
                          if eN == expN and eSn == expSn]
        else:
            candidates = rows

        if not candidates:
            eigenchis.append(None)
            continue

        # Pick the row whose stored q_qtaim is closest to the analysed atom's
        # q_qtaim from the .pout — disambiguates molecules with several
        # reactive sites that share (expN, expSn).
        q_db, eig = min(candidates, key=lambda r: abs(r[0] - q_analysed))
        eigenchis.append(eig if eig is not None and not np.isnan(eig) else None)

    return eigenchis

def drop_missing(data, eigenchis):
    """Filter out entries whose eigenchi is None/NaN."""
    keep = [j for j, e in enumerate(eigenchis) if e is not None]
    dropped = len(eigenchis) - len(keep)
    if dropped:
        print(f"  → dropped {dropped} entr{'y' if dropped == 1 else 'ies'} "
              f"with missing/NaN eigenchi")

    filtered = {k: [v[j] for j in keep] for k, v in data.items()}
    eig_filtered = [eigenchis[j] for j in keep]
    return filtered, eig_filtered

# ---------------------------------------------------------------------------
# Feature construction
# ---------------------------------------------------------------------------
def prepare_data(react_data, react_eig, noreact_data, noreact_eig):
    combined = {
        "natoms":    react_data["natoms"]    + noreact_data["natoms"],
        "expN":      react_data["expN"]      + noreact_data["expN"],
        "expSn":     react_data["expSn"]     + noreact_data["expSn"],
        "distances": react_data["distances"] + noreact_data["distances"],
        "q_qtaim":   react_data["q_qtaim"]   + noreact_data["q_qtaim"],
    }
    eigenchis = np.array(react_eig + noreact_eig, dtype=float)
    labels = np.array([1] * len(react_data["natoms"]) +
                      [0] * len(noreact_data["natoms"]))
    return combined, eigenchis, labels

def compute_weighted_features(data, eigenchis, alpha, gamma):
    """
    q_weighted = γ * Σ exp(-α·d_i) · q_i        (sum over all atoms in molecule)
    eigenchi   = scalar from the database (analysed atom)
    """
    n = len(data["natoms"])
    feats = np.empty((n, 4))
    for i in range(n):
        d = np.array(data["distances"][i])
        q = np.array(data["q_qtaim"][i])
        feats[i, 0] = gamma * np.sum(np.exp(-alpha * d) * q)
        feats[i, 1] = eigenchis[i]
        feats[i, 2] = data["expN"][i]
        feats[i, 3] = data["expSn"][i]
    return feats

# ---------------------------------------------------------------------------
# Optimization (CV F1)
# ---------------------------------------------------------------------------
def objective_function(params, data, eigenchis, labels):
    alpha, gamma = params
    if alpha <= 0 or gamma <= 0 or alpha > 10 or gamma > 20:
        return 1.0

    X = compute_weighted_features(data, eigenchis, alpha, gamma)
    if np.any(np.isnan(X)) or np.any(np.isinf(X)):
        return 1.0

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    f1s = []
    for train_idx, val_idx in skf.split(X, labels):
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X[train_idx])
        X_va = scaler.transform(X[val_idx])
        model = SVC(kernel='rbf', random_state=42, C=1.0)
        model.fit(X_tr, labels[train_idx])
        f1s.append(f1_score(labels[val_idx], model.predict(X_va)))
    return -np.mean(f1s)

def optimize_decay_parameters(react_data, react_eig, noreact_data, noreact_eig):
    print("Starting optimization with cross-validation...")
    print("-" * 50)

    data, eigenchis, labels = prepare_data(react_data, react_eig,
                                           noreact_data, noreact_eig)
    bounds = [(0.01, 5.0), (0.1, 10.0)]   # alpha, gamma
    initial_guesses = [
        [1.0, 1.0], [0.5, 1.0], [1.0, 2.0], [0.1, 0.5],
        [2.0, 5.0], [0.3, 3.0], [1.5, 1.5], [3.0, 1.0],
        [0.05, 4.0], [0.8, 1.8],
    ]

    print(f"Testing {len(initial_guesses)} initial guesses with 5-fold CV...\n")
    all_results = []
    best_score, best_params = -np.inf, None
    for init_guess in initial_guesses:
        result = minimize(objective_function, init_guess,
                          args=(data, eigenchis, labels),
                          method='L-BFGS-B', bounds=bounds,
                          options={'maxiter': 200, 'disp': False})
        cv_score = -result.fun
        alpha, gamma = result.x

        X_full = compute_weighted_features(data, eigenchis, alpha, gamma)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_full)
        model = SVC(kernel='rbf', random_state=42).fit(X_scaled, labels)
        pred = model.predict(X_scaled)

        train_acc = accuracy_score(labels, pred)
        train_f1 = f1_score(labels, pred)
        train_prec = precision_score(labels, pred)
        train_rec = recall_score(labels, pred)

        print(40 * "-")
        print(f"  → Optimized: α={alpha:.3f}, γ={gamma:.3f}")
        print(f"     CV F1: {cv_score:.3f}, Train Acc: {train_acc:.3f}, "
              f"Train F1: {train_f1:.3f}")
        all_results.append({'params': result.x, 'cv_f1': cv_score,
                            'train_accuracy': train_acc, 'train_f1': train_f1,
                            'train_precision': train_prec,
                            'train_recall': train_rec,
                            'success': result.success})
        if cv_score > best_score:
            best_score, best_params = cv_score, result.x

    all_results.sort(key=lambda x: x['cv_f1'], reverse=True)
    print("\n" + "=" * 50)
    print("TOP 5 RESULTS (sorted by CV F1 score):")
    print("=" * 50)
    for i, res in enumerate(all_results[:5]):
        print(f"{i + 1}. CV F1: {res['cv_f1']:.4f}, "
              f"Train Acc: {res['train_accuracy']:.4f}, "
              f"Train F1: {res['train_f1']:.4f}")
        print(f"   α={res['params'][0]:.4f}, γ={res['params'][1]:.4f}")
        print(f"   Precision: {res['train_precision']:.4f}, "
              f"Recall: {res['train_recall']:.4f}")

    alpha_opt, gamma_opt = best_params
    X_final = compute_weighted_features(data, eigenchis, alpha_opt, gamma_opt)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_final)
    model = SVC(kernel='rbf', random_state=42).fit(X_scaled, labels)
    pred = model.predict(X_scaled)

    print("\n" + "=" * 50)
    print("BEST OPTIMIZATION RESULTS")
    print("=" * 50)
    print(f"\nOptimal Parameters (based on CV F1 score):")
    print(f"  α (alpha) = {alpha_opt:.6f}")
    print(f"  γ (gamma) = {gamma_opt:.6f}")
    print(f"\nCross-Validation F1 Score: {best_score:.4f}")
    print(f"\nFull Training Set Metrics:")
    print(f"  Accuracy:  {accuracy_score(labels, pred):.4f}")
    print(f"  Precision: {precision_score(labels, pred):.4f}")
    print(f"  Recall:    {recall_score(labels, pred):.4f}")
    print(f"  F1 Score:  {f1_score(labels, pred):.4f}")

    cm = confusion_matrix(labels, pred)
    print("\nConfusion Matrix:")
    print(f"  True Negative:  {cm[0,0]:3d}  False Positive: {cm[0,1]:3d}")
    print(f"  False Negative: {cm[1,0]:3d}  True Positive:  {cm[1,1]:3d}")

    print("\nClassification Report:")
    print(classification_report(labels, pred,
                                target_names=['Non-Reactive', 'Reactive'],
                                digits=4))

    return {'alpha': alpha_opt, 'gamma': gamma_opt,
            'cv_f1': best_score,
            'data': data, 'eigenchis': eigenchis, 'labels': labels,
            'model': model, 'scaler': scaler,
            'all_results': all_results}

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
def plot_best_classification(results, save_fig=False,
                             fig_name='best_classification_eigenchi.png'):
    alpha = results['alpha']; gamma = results['gamma']
    data = results['data']; eigenchis = results['eigenchis']
    labels = results['labels']

    X = compute_weighted_features(data, eigenchis, alpha, gamma)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    qw, eg = X_scaled[:, 0], X_scaled[:, 1]

    plt.figure(figsize=(12, 8))
    model = SVC(kernel='rbf', random_state=42).fit(X_scaled[:, :2], labels)

    h = 0.02
    x_min, x_max = qw.min() - 0.5, qw.max() + 0.5
    y_min, y_max = eg.min() - 0.5, eg.max() + 0.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    # Re-scale ticks to the original (unstandardized) feature values
    x_factor = (X[:, 0].max() - X[:, 0].min()) / (qw.max() - qw.min())
    y_factor = (X[:, 1].max() - X[:, 1].min()) / (eg.max() - eg.min())
    x_offset = X[:, 0].min() - x_factor * qw.min()
    y_offset = X[:, 1].min() - y_factor * eg.min()
    xtl = [f'{x_min*x_factor + x_offset + i*(x_max-x_min)*x_factor/4:.2f}'
           for i in range(5)]
    ytl = [f'{y_min*y_factor + y_offset + i*(y_max-y_min)*y_factor/4:.2f}'
           for i in range(5)]
    plt.xticks(np.linspace(x_min, x_max, num=5), xtl, fontsize=22)
    plt.yticks(np.linspace(y_min, y_max, num=5), ytl, fontsize=22)

    colors = ["yellow", "purple"]
    cmap = ListedColormap(colors)
    plt.contourf(xx, yy, Z, alpha=0.3, levels=[0, 0.5, 1], cmap='viridis')
    plt.contour(xx, yy, Z, linewidths=1, alpha=0.4)
    for i in range(2):
        mask = labels == i
        plt.scatter(qw[mask], eg[mask], cmap=cmap, c=colors[i],
                    edgecolor='k', alpha=0.7, linewidth=0.5, s=50)

    pred = model.predict(X_scaled[:, :2])
    miscl = pred != labels
    if np.any(miscl):
        plt.scatter(qw[miscl], eg[miscl], label='Misclassified',
                    marker='x', s=150, c='black', linewidth=3)

    plt.xlabel(r'$q(N)$ weighted', fontsize=26)
    plt.ylabel(r'$\chi_{\mathrm{eig}}$', fontsize=26)
    plt.title('Neighbour Weighted Clustering (eigenchi)',
              fontsize=28, fontweight='bold')
    plt.grid(True, alpha=0.3)

    acc_2d = accuracy_score(labels, pred); f1_2d = f1_score(labels, pred)
    label_text = (f'$\\times$ Misclassified\n'
                  f'2D Accuracy: {acc_2d * 100:.1f}%\nF1: {f1_2d:.3f}')
    plt.text(x_min + 0.5, y_max - 0.9, label_text, fontsize=18, color='black',
             bbox=dict(facecolor='white', edgecolor='black',
                       boxstyle='round,pad=0.4', alpha=0.8))
    plt.tight_layout()
    if save_fig:
        plt.savefig(fig_name, dpi=300, bbox_inches='tight')
        print(f"\nFigure saved as '{fig_name}'")
    plt.show()

    print("\n2D Classification Metrics (q_weighted vs eigenchi):")
    print(f"  Accuracy:  {acc_2d:.4f}")
    print(f"  Precision: {precision_score(labels, pred):.4f}")
    print(f"  Recall:    {recall_score(labels, pred):.4f}")
    print(f"  F1 Score:  {f1_2d:.4f}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    react_data = read_react('reactive.pout')
    noreact_data = read_noreact('no_reactive.pout')

    print("Fetching eigenchi from database…")
    react_eig = fetch_eigenchi(react_data, 'reactive')
    react_data, react_eig = drop_missing(react_data, react_eig)
    noreact_eig = fetch_eigenchi(noreact_data, 'no_reactive')
    noreact_data, noreact_eig = drop_missing(noreact_data, noreact_eig)
    print(f"Kept {len(react_eig)} reactive and {len(noreact_eig)} non-reactive entries\n")

    results = optimize_decay_parameters(react_data, react_eig,
                                        noreact_data, noreact_eig)
    plot_best_classification(results, save_fig=True,
                             fig_name='optimized_classification_eigenchi.png')

    print("\n" + "=" * 50)
    print("OPTIMAL PARAMETERS FOR FUTURE USE:")
    print("=" * 50)
    print(f"q_weighted = {results['gamma']:.6f} * Σ(exp(-{results['alpha']:.6f}*distance)*q_atom)")
    print(f"eigenchi   = scalar from database (analysed atom)")
    print(f"\nExpected CV F1 Score: {results['cv_f1']:.4f}")
