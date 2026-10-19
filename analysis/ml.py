# -*- coding: UTF-8 -*-
# Regression models of an experimental target: RF, GBR, SVR and GPR, tuning, evaluation, outliers and PySR
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, DotProduct, RationalQuadratic, Matern, WhiteKernel, ConstantKernel as C
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, RepeatedKFold, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.base import clone
import plots

def kernels(n):
    """GPR kernels with anisotropic length scales over n features."""
    ls = np.ones(n)
    return {
        'rbf':              C(1.0)*RBF(length_scale=ls),
        'rbfwhite':         C(1.0)*RBF(length_scale=ls) + WhiteKernel(),
        'matern32':         C(1.0)*Matern(length_scale=ls, nu=1.5),
        'matern52':         C(1.0)*Matern(length_scale=ls, nu=2.5),
        'matern32white':    C(1.0)*Matern(length_scale=ls, nu=1.5) + WhiteKernel(),
        'matern52white':    C(1.0)*Matern(length_scale=ls, nu=2.5) + WhiteKernel(),
        'rq':               C(1.0)*RationalQuadratic(alpha=1.0, length_scale=1.0),
        'rqwhite':          C(1.0)*RationalQuadratic(alpha=1.0, length_scale=1.0) + WhiteKernel(),
        'dot':              C(1.0)*DotProduct(sigma_0=1.0),
        'rbfdot':           C(1.0)*RBF(length_scale=ls)*DotProduct(sigma_0=1.0),
        'matern52dotwhite': C(1.0)*Matern(length_scale=ls, nu=2.5)*DotProduct(sigma_0=1.0) + WhiteKernel(),
        'rbfmatern52':      C(1.0)*RBF(length_scale=ls) + C(1.0)*Matern(length_scale=ls, nu=2.5),
    }

def estimator(name, params, n):
    """RF, GBR, SVR or GPR over n features: the defaults of the final scripts when params is None, the tuned model otherwise."""
    if name == 'RF':
        if params is None:
            return RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        return RandomForestRegressor(random_state=42, n_jobs=-1, **params)
    if name == 'GBR':
        return GradientBoostingRegressor(random_state=42, **(params or {}))
    if name == 'SVR':
        if params is None:
            return make_pipeline(StandardScaler(), SVR())
        return make_pipeline(StandardScaler(), SVR(cache_size=500, **params))
    if name == 'GPR':
        if params is None:
            return make_pipeline(StandardScaler(), GaussianProcessRegressor(
                kernel=C(1.0)*Matern(nu=2.5) + WhiteKernel(), normalize_y=True, random_state=42))
        return make_pipeline(StandardScaler(), GaussianProcessRegressor(
            kernel=kernels(n)[params['kernel']], alpha=1e-6, normalize_y=True,
            n_restarts_optimizer=params['restarts'], random_state=42))
    raise ValueError(f'unknown model {name}')

def tune(df, features, target, name):
    """Hyperparameters of one model, searched on the 80 % training part of a seed-42 split; prints and returns them.
    RF, GBR and SVR: optuna TPE, 300 trials, MAE of a repeated 5-fold; GPR: the kernel with the lowest held-out MAE."""
    warnings.filterwarnings('ignore')
    n                  = len(features)
    Xtr, Xte, ytr, yte = train_test_split(df[features], df[target], test_size=0.2, random_state=42)
    if name == 'GPR':
        best, low = None, np.inf
        for kernel in kernels(n):
            params = {'kernel': kernel, 'restarts': 15}
            mae    = mean_absolute_error(yte, estimator(name, params, n).fit(Xtr, ytr).predict(Xte))
            if mae < low:
                best, low = params, mae
        print(f'{name} best params: {best}')
        return best
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def objective(trial):
        if name == 'RF':
            params = {
                'max_depth':         trial.suggest_categorical('max_depth', [None, 5, 10, 20, 40, 80]),
                'max_features':      trial.suggest_categorical('max_features', ['sqrt', 'log2', 0.3, 0.5, 0.7, None]),
                'criterion':         trial.suggest_categorical('criterion', ['squared_error', 'absolute_error', 'friedman_mse']),
                'n_estimators':      trial.suggest_int('n_estimators', 100, 4000),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf':  trial.suggest_int('min_samples_leaf', 1, 15),
                'bootstrap':         trial.suggest_categorical('bootstrap', [True, False]),
            }
        elif name == 'GBR':
            params = {
                'n_estimators':      trial.suggest_int('n_estimators', 50, 5000),
                'learning_rate':     trial.suggest_float('learning_rate', 1e-3, 0.5, log=True),
                'max_depth':         trial.suggest_int('max_depth', 2, 15),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 25),
                'min_samples_leaf':  trial.suggest_int('min_samples_leaf', 1, 15),
                'subsample':         trial.suggest_float('subsample', 0.4, 1.0),
                'max_features':      trial.suggest_categorical('max_features', ['sqrt', 'log2', 0.5, 0.7, None]),
                'loss':              trial.suggest_categorical('loss', ['squared_error', 'huber', 'absolute_error']),
            }
        else:
            kernel = trial.suggest_categorical('kernel', ['rbf', 'poly', 'sigmoid'])
            params = {
                'C':       trial.suggest_float('C', 1e-2, 3000.0, log=True),
                'epsilon': trial.suggest_float('epsilon', 1e-4, 2.0, log=True),
                'kernel':  kernel,
                'gamma':   trial.suggest_categorical('gamma', ['scale', 'auto', 1e-4, 1e-3, 1e-2, 0.1, 1.0]),
            }
            if kernel == 'poly':
                params['degree'] = trial.suggest_int('degree', 2, 5)
                params['coef0']  = trial.suggest_float('coef0', 0.0, 2.0)
        model = estimator(name, params, n)
        if name == 'RF':
            model.set_params(n_jobs=1)
        cv = RepeatedKFold(n_splits=5, n_repeats=3, random_state=42)
        return -cross_val_score(model, Xtr, ytr, cv=cv, scoring='neg_mean_absolute_error', n_jobs=-1).mean()

    study = optuna.create_study(direction='minimize', sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=300, n_jobs=4, show_progress_bar=False)
    print(f'{name} best params: {study.best_params}')
    return study.best_params

def evaluate(df, features, target, models, splits=None, ensembles=()):
    """Fits each model on every split (default 20 train_test_split, seeds 0..19); each ensemble averages its members.
    Prints n, MAE and R² ± std, MAE per family and stars, the 10 largest errors; returns {name: {'maes', 'r2s', 'x', 'y'}}."""
    warnings.filterwarnings('ignore')
    X, y   = df[features], df[target]
    splits = list(splits) if splits is not None else [
        train_test_split(np.arange(len(y)), test_size=0.2, random_state=seed) for seed in range(20)]
    raw    = {}
    for name, params in models.items():
        model     = estimator(name, params, len(features))
        raw[name] = [(te, clone(model).fit(X.iloc[tr], y.iloc[tr]).predict(X.iloc[te])) for tr, te in splits]
    for members in ensembles:
        raw['+'.join(members)] = [(raw[members[0]][s][0], np.mean([raw[m][s][1] for m in members], axis=0))
                                  for s in range(len(splits))]
    out = {}
    for name, rows in raw.items():
        preds     = [[] for _ in range(len(y))]
        maes, r2s = [], []
        for te, yp in rows:
            for i, p in zip(te, yp):
                preds[i].append(p)
            maes.append(mean_absolute_error(y.iloc[te], yp))
            r2s.append(r2_score(y.iloc[te], yp))
        mean      = np.array([np.mean(p) if p else np.nan for p in preds])
        err       = np.abs(mean - y.values)
        out[name] = {'maes': maes, 'r2s': r2s, 'x': y.values, 'y': mean}
        line      = (f'{name:10s} n {len(y):3d}  MAE {np.mean(maes):.3f} ± {np.std(maes):.3f}   '
                     f'R2 {np.mean(r2s):.3f} ± {np.std(r2s):.3f}')
        if 'family' in df:
            line += '   per family:' + ''.join(f'  {f[:9]} ({k}) {np.nanmean(err[(df["family"] == f).values]):.2f}'
                                               for f, k in df['family'].value_counts().items())
        if 'stars' in df:
            line += '   per stars:' + ''.join(f'  {s}-star ({(df["stars"] == s).sum()}) '
                                              f'{np.nanmean(err[(df["stars"] == s).values]):.2f}'
                                              for s in sorted(df['stars'].unique()))
        print(line)
        worst = np.argsort(np.nan_to_num(err, nan=-1.0))[::-1][:10]
        print('     10 largest errors: ' + '; '.join(f'{y.iloc[j]:.2f} {str(df["name"].iloc[j]).strip()} {err[j]:.2f}'
                                                    for j in worst))
    return out

def outliers(df, features, target, name, params, threshold=5):
    """Removes, round after round, the sites whose out-of-fold mean error (5-fold CV repeated 4 times) exceeds threshold.
    Prints every round and the removed (smiles, target) pairs; returns {'drop', 'x', 'y'} at the prediction of removal."""
    warnings.filterwarnings('ignore')
    X, y  = df[features], df[target]
    model = estimator(name, params, len(features))
    who   = df['solvent'].astype(str).str.ljust(6) + ' ' + df['name'].astype(str).str.strip()
    if 'stars' in df:
        who = df['stars'].astype(str) + '-star  ' + who
    mask    = np.ones(len(y), dtype=bool)
    removed = []
    for rnd in range(1, 30):
        idx   = np.where(mask)[0]
        preds = [[] for _ in idx]
        for tr, te in RepeatedKFold(n_splits=5, n_repeats=4, random_state=42).split(idx):
            for i, p in zip(te, clone(model).fit(X.iloc[idx[tr]], y.iloc[idx[tr]]).predict(X.iloc[idx[te]])):
                preds[i].append(p)
        mean = np.array([np.mean(p) for p in preds])
        err  = np.abs(mean - y.values[idx])
        drop = np.where(err > threshold)[0]
        print(f'--- {name} round {rnd}: {len(idx)} points, MAE of the out-of-fold means {np.mean(err):.3f}, '
              f'{len(drop)} above {threshold:g}')
        for j in drop[np.argsort(err[drop])[::-1]]:
            print(f'      {target} {y.iloc[idx[j]]:6.2f}  {who.iloc[idx[j]]}  error {err[j]:5.2f}')
            removed.append((idx[j], rnd, err[j], mean[j]))
        if not len(drop):
            break
        mask[idx[drop]] = False
    print(f'{name}: {len(removed)} sites removed, converged at round {rnd}, {mask.sum()} kept')
    print(f"    '{name}': [")
    for j, rnd, e, _ in removed:
        print(f'        ({df["smiles"].iloc[j]!r}, {y.iloc[j]:.2f}),  # round {rnd}, error {e:.2f}')
    print('    ],')
    rows = [j for j, *_ in removed]
    return {'drop': [(df['smiles'].iloc[j], y.iloc[j]) for j in rows], 'x': y.values[rows],
            'y': np.array([p for *_, p in removed])}

def perfamily(df, features, target, models):
    """Pooled model, family one-hot columns, and one model per family (pooled below 15 training rows) on 20 random splits.
    Prints MAE ± std and R² ± std of each scheme and the MAE of each family."""
    warnings.filterwarnings('ignore')
    X, y, fam = df[features], df[target].values, df['family']
    Xf        = pd.concat([X, pd.get_dummies(fam, prefix='fam', prefix_sep='').astype(int)], axis=1)
    indices   = np.arange(len(y))
    print(f'{target}: {len(y)} points, 20 splits')
    print(fam.value_counts().to_string())
    for name, params in models.items():
        model  = estimator(name, params, len(features))
        modelf = estimator(name, params, Xf.shape[1])
        preds  = {k: np.full((20, len(y)), np.nan) for k in ('pooled', 'onehot', 'family')}
        for seed in range(20):
            tr, te                    = train_test_split(indices, test_size=0.2, random_state=seed)
            pooled                    = clone(model).fit(X.iloc[tr], y[tr])
            preds['pooled'][seed, te] = pooled.predict(X.iloc[te])
            preds['onehot'][seed, te] = clone(modelf).fit(Xf.iloc[tr], y[tr]).predict(Xf.iloc[te])
            for f in fam.unique():
                trf = tr[fam.iloc[tr].values == f]
                tef = te[fam.iloc[te].values == f]
                if len(tef) == 0:
                    continue
                preds['family'][seed, tef] = (clone(model).fit(X.iloc[trf], y[trf]) if len(trf) >= 15
                                              else pooled).predict(X.iloc[tef])
        print(f'== {name}')
        for scheme, P in preds.items():
            ok   = ~np.isnan(P)
            maes = [mean_absolute_error(y[ok[s]], P[s][ok[s]]) for s in range(20)]
            r2s  = [r2_score(y[ok[s]], P[s][ok[s]]) for s in range(20)]
            line = (f'{scheme:7s} MAE {np.mean(maes):.2f} ± {np.std(maes):.2f}  '
                    f'R2 {np.mean(r2s):.2f} ± {np.std(r2s):.2f}  per family:')
            for f in fam.value_counts().index:
                mask  = (fam == f).values
                line += f'  {f[:9]} {np.nanmean(np.abs(P[:, mask] - y[mask])):.2f}'
            print(line)

def predict(train, test, features, target, models):
    """Fits each model on train and prints, for every row of test, its name, solvent, experimental target and predictions."""
    warnings.filterwarnings('ignore')
    preds = {name: estimator(name, params, len(features)).fit(train[features], train[target]).predict(test[features])
             for name, params in models.items()}
    for i in range(len(test)):
        print(f'{str(test["name"].iloc[i]).strip()} {test["solvent"].iloc[i]}  experimental {test[target].iloc[i]:.2f}'
              + ''.join(f'   {m} {p[i]:6.2f}' for m, p in preds.items()))

def importance(df, features, target, figure=None):
    """Random forest with out-of-bag predictions: errors, sorted importances, correlations of the ten most important
    columns and the ones kept at |r| <= 0.95; bar chart of the ten importances. Returns the ten columns."""
    X, y = df[features], df[target]
    rf   = RandomForestRegressor(random_state=42, oob_score=True, n_jobs=-1).fit(X, y)
    print('n', len(y))
    print('MAE insample', round(mean_absolute_error(y, rf.predict(X)), 3))
    print('MAE oob', round(mean_absolute_error(y, rf.oob_prediction_), 3))
    print('R2 oob', round(r2_score(y, rf.oob_prediction_), 3))
    imp = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
    for name, val in imp.items():
        print('importance', name, round(val, 4))
    top   = list(imp.index[:10])
    corr  = X[top].corr()
    ncorr = X[top].corrwith(y)
    for name in top:
        print('corr with', target, name, round(ncorr[name], 3))
    for i, a in enumerate(top):
        for b in top[i + 1:]:
            if abs(corr.loc[a, b]) > 0.5:
                print('corr', a, b, round(corr.loc[a, b], 3))
    drop = set()
    for i, a in enumerate(top):
        for b in top[i + 1:]:
            if abs(corr.loc[a, b]) > 0.95 and a not in drop:
                drop.add(b)
    print('keep', [f for f in top if f not in drop])
    plt.figure(figsize=(8, 5))
    plt.bar(range(len(top)), imp.values[:len(top)])
    plt.xticks(range(len(top)), [plots.LABELS.get(f, f) for f in top], rotation=90, fontsize=16)
    plt.yticks(fontsize=14)
    plt.ylabel('Importance', fontsize=16)
    plt.tight_layout()
    if figure:
        plt.savefig(figure)
        plt.close()
    else:
        plt.show()
    return top

def symbolic(df, features, target, figure=None):
    """PySR on an 80/20 split (random_state 42): the selected equation, its train/test MAE and R², the test MAE of every
    Pareto equation and the lowest one; train/test parity through plots.parity."""
    from pysr import PySRRegressor
    warnings.filterwarnings('ignore')
    model = PySRRegressor(
        niterations=1000,
        populations=80,
        maxsize=30,
        maxdepth=10,
        binary_operators=['+', '-', '*', '/'],
        unary_operators=['square', 'cube', 'exp', 'log', 'sqrt', 'abs', 'inv(x) = 1/x'],
        extra_sympy_mappings={'inv': lambda x: 1/x},
        elementwise_loss='loss(x, y) = abs(x - y)',
        model_selection='best',
        random_state=42,
        deterministic=False,
        progress=False,
        verbosity=0,
    )
    Xtr, Xte, ytr, yte = train_test_split(df[features], df[target], test_size=0.2, random_state=42)
    model.fit(Xtr, ytr, variable_names=list(features))
    ptr, pte = model.predict(Xtr), model.predict(Xte)
    print(model.sympy())
    print(f'train   MAE = {mean_absolute_error(ytr, ptr):.3f}   R² = {r2_score(ytr, ptr):.3f}')
    print(f'test    MAE = {mean_absolute_error(yte, pte):.3f}   R² = {r2_score(yte, pte):.3f}')
    eqs       = model.equations_
    best, low = None, np.inf
    for i in range(len(eqs)):
        mae = mean_absolute_error(yte, model.predict(Xte, index=i))
        print(f'[{i:2d}] complexity {eqs.iloc[i]["complexity"]:>3}  test MAE {mae:.3f}')
        if mae < low:
            best, low = i, mae
    print(f'lowest test MAE: index {best}, MAE {low:.3f}')
    print(model.sympy(best))
    plots.parity({'train': {'x': ytr.values, 'y': ptr}, 'test': {'x': yte.values, 'y': pte}}, target, figure)
