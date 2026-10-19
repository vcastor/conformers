# -*- coding: UTF-8 -*-
# Closed-form regressions: model registry, bounded multistart fit, neighbour damping, least-squares baseline
import itertools
import numpy as np
from scipy.optimize import minimize
from sklearn.model_selection import KFold

# c[i] is the i-th Greek letter of the formula in alphabetical order; the dielectric constant is written epsilon
MODELS = {
    'linear':       ('α*Sr + β*St + γ*Sv',
                     lambda c, d: c[0]*d.Sr + c[1]*d.St + c[2]*d.Sv,
                     [(0, 1)]*3),
    'crossterms':   ('α*(Sr + St) + β*Sv + γ*Sv*(Sr + St)/Sgas',
                     lambda c, d: c[0]*(d.Sr + d.St) + c[1]*d.Sv + c[2]*d.Sv*(d.Sr + d.St)/(d.Sr + d.St + d.Sv),
                     [(0, 1)]*3),
    'expgrouped':   ('e^(-λ*epsilon)[α*(Sr + St) + β*Sv + γ*Sv*(Sr + St)/Sgas]',
                     lambda c, d: np.exp(-c[3]*d.epsilon)*(c[0]*(d.Sr + d.St) + c[1]*d.Sv + c[2]*d.Sv*(d.Sr + d.St)/(d.Sr + d.St + d.Sv)),
                     [(0, 1)]*3 + [(0, 0.05)]),
    'expseparated': ('e^(-λ*epsilon)[α*Sr + β*St + γ*Sv + δ*Sv*Sr/Sgas + ζ*Sv*St/Sgas]',
                     lambda c, d: np.exp(-c[5]*d.epsilon)*(c[0]*d.Sr + c[1]*d.St + c[2]*d.Sv + c[3]*d.Sv*d.Sr/(d.Sr + d.St + d.Sv)
                                                           + c[4]*d.Sv*d.St/(d.Sr + d.St + d.Sv)),
                     [(0, 1)]*5 + [(0, 0.05)]),
    'splited':      ('e^(-λ*epsilon)[α*Sr + β*St + γ*Sv*Sr/Sgas + δ*Sv*St/Sgas] + ζ*Sv',
                     lambda c, d: np.exp(-c[5]*d.epsilon)*(c[0]*d.Sr + c[1]*d.St + c[2]*d.Sv*d.Sr/(d.Sr + d.St + d.Sv)
                                                           + c[3]*d.Sv*d.St/(d.Sr + d.St + d.Sv)) + c[4]*d.Sv,
                     [(0, 1)]*5 + [(0, 0.05)]),
    'cdft1':        ('α*Sr + β*St + (γ*Sv + δ*epsilon)*e^(-ζ*gamma)',
                     lambda c, d: c[0]*d.Sr + c[1]*d.St + (c[2]*d.Sv + c[3]*d.epsilon)*np.exp(-c[4]*d.gamma),
                     [(0, 1), (0, 1), (0, 1), (-1, 1), (-np.inf, np.inf)]),
    'cdft2':        ('α*(Sr + St)*e^(-γ*eta) + β*Sv*e^(δ*gamma)',
                     lambda c, d: c[0]*(d.Sr + d.St)*np.exp(-c[2]*d.eta) + c[1]*d.Sv*np.exp(c[3]*d.gamma),
                     [(0, 1), (0, 1), (0, np.inf), (-np.inf, np.inf)]),
    'cdft3':        ('(α*Sr + β*St)*e^(-γ*epsilon) + (δ*Sv + ζ*epsilon)*e^(η*gamma)',
                     lambda c, d: (c[0]*d.Sr + c[1]*d.St)*np.exp(-c[2]*d.epsilon) + (c[3]*d.Sv + c[4]*d.epsilon)*np.exp(c[5]*d.gamma),
                     [(0, 1), (0, 1), (0, 0.5), (-1, 1), (-100, 100), (-np.inf, np.inf)]),
    'inverse':      ('α/electrofuge',
                     lambda c, d: c[0]/d.electrofuge,
                     [(50, 150)]),
    'charge':       ('α/electrofuge + β*nucleofuge + γ*q + δ',
                     lambda c, d: c[0]/d.electrofuge + c[1]*d.nucleofuge + c[2]*d.q + c[3],
                     [(50, 150), (-10, 10), (-50, 50), (-30, 30)]),
    'betap':        ('(α + β*P)/electrofuge + γ',
                     lambda c, d: (c[0] + c[1]*d.P)/d.electrofuge + c[2],
                     [(50, 150), (-10, 10), (-50, 50)]),
    'mult':         ('α/(electrofuge*q) + β',
                     lambda c, d: c[0]/(d.electrofuge*d.q) + c[1],
                     [(50, 150), (-20, 20)]),
    'log':          ('(-log|α*electrofuge + β| + γ)/(δ*q)',
                     lambda c, d: (-np.log(np.abs(c[0]*d.electrofuge + c[1])) + c[2])/(c[3]*d.q),
                     [(-10, 10), (-20, 20), (-50, 50), (-30, 30)]),
    'homo':         ('α/nucleofuge + β/HOMO + γ*q + δ',
                     lambda c, d: c[0]/(d.nucleofuge + 1e-8) + c[1]/d.HOMO + c[2]*d.q + c[3],
                     [(-80, 80), (-200, 200), (-50, 59), (-30, 30)]),
    'homoq':        ('α*HOMO + β*q + γ',
                     lambda c, d: c[0]*d.HOMO + c[1]*d.q + c[2],
                     [(-200, 200)]*3),
    'damped':       ('α/electrofuge - β*nucleofuge - γ*Σe^(-δ*d²)*q + ε',
                     lambda c, d: c[0]/d.electrofuge - c[1]*d.nucleofuge - c[2]*damped(d, 'q', c[3], 2) + c[4],
                     [(-200, 200), (0, 10), (0, 2000), (0, 3.99), (-2000, 2000)]),
    'dampedall':    ('α/electrofuge - β*nucleofuge - γ*Σe^(-δ*d²)*q + ε*Σe^(-ζ*d²)*chi + η*Σe^(-θ*d²)*esp/N + ι + κ*HOMO',
                     lambda c, d: (c[0]/d.electrofuge - c[1]*d.nucleofuge - c[2]*damped(d, 'q', c[3], 2) + c[4]*damped(d, 'chi', c[5], 2)
                                   + c[6]*damped(d, 'esp/N', c[7], 2) + c[8] + c[9]*d.HOMO),
                     [(-200, 200), (0, 10), (0, 2000), (0, 3.99), (-2000, 2000), (0, 3.99), (-2000, 2000), (0, 3.99), (-2000, 2000), (-200, 200)]),
    'snlog':        ('(log(α/nucleofuge)²)^(-β) + γ',
                     lambda c, d: (np.log(c[0]/d.nucleofuge)**2)**(-c[1]) + c[2],
                     [(0, 5), (0, 5), (-5, 5)]),
    'sninverse':    ('α/electrofuge + β',
                     lambda c, d: c[0]/d.electrofuge + c[1],
                     [(-10, 10), (-10, 10)]),
    'snP':          ('α/P + β',
                     lambda c, d: c[0]/d.P + c[1],
                     [(-10, 10), (-10, 10)]),
    'snpower':      ('α/nucleofuge^β + γ',
                     lambda c, d: c[0]/d.nucleofuge**c[1] + c[2],
                     [(0, 30), (0, 10), (-20, 20)]),
}

def damped(df, column, k, power=1):
    """Σ_conformers w Σ_atoms exp(-k*d^power)*x of every site, from the nb column of nucleophilicity.neighbours.
    power 1 is the decay of qw/chiw, power 2 the Gaussian of the damped forms; column 'esp/N' divides per atom."""
    top, _, bottom = column.partition('/')

    def site(nb):
        x = np.asarray(nb[top], float)/(np.asarray(nb[bottom], float) if bottom else 1)
        return np.dot(nb['w'], (np.exp(-k*np.asarray(nb['d'], float)**power)*x).sum(1))

    return df.nb.apply(site)

def fit(df, target, model, folds=None):
    """Bounded L-BFGS-B fit of a MODELS name or (formula, f, bounds) on target, best of 50 starts (rng 42).
    folds=k first prints the shuffled k-fold test MAE. Returns {'c', 'x', 'y'} for plots.parity."""
    formula, f, bounds = MODELS[model] if isinstance(model, str) else model

    def best(d):
        box  = np.array([b if np.isfinite(b).all() else (0, 1) for b in bounds], float)
        rng  = np.random.default_rng(42)
        y    = d[target].to_numpy(float)
        sse  = lambda c: np.sum((y - np.asarray(f(c, d), float))**2)
        runs = [minimize(sse, rng.uniform(*box.T), bounds=bounds, method='L-BFGS-B') for _ in range(50)]
        return min((r for r in runs if r.success and r.fun < np.inf), key=lambda r: r.fun).x

    print(f'{target} = {formula}')
    print('n', len(df))
    if folds:
        maes = []
        for train, test in KFold(n_splits=folds, shuffle=True, random_state=42).split(df):
            c, t = best(df.iloc[train]), df.iloc[test]
            maes.append(np.mean(np.abs(t[target].to_numpy(float) - np.asarray(f(c, t), float))))
        print(f'{folds}-fold MAE {np.mean(maes):.4f} ± {np.std(maes):.4f}')
    c     = best(df)
    x     = df[target].to_numpy(float)
    y     = np.asarray(f(c, df), float)
    names = [g for g in 'αβγδεζηθικλμνξοπρστυφχψω' if g in formula]
    print(', '.join(f'{g}: {v:.4f}' for g, v in zip(names, c)))
    print(f'MAE {np.mean(np.abs(x - y)):.4f}')
    print(f'R² {1 - np.sum((x - y)**2)/np.sum((x - x.mean())**2):.4f}')
    labels = [col for col in ('name', 'solvent') if col in df]
    for i in np.argsort(-np.abs(x - y))[:5]:
        print(*df.iloc[i][labels], f'{x[i]:.2f}', f'{y[i]:.2f}')
    return {'c': c, 'x': x, 'y': y}

def baseline(df, features, target, sets=()):
    """In-sample MAE of least squares with intercept for each column set in sets
    and for the best 2- and 3-column subsets of features."""
    y = df[target].to_numpy(float)

    def mae(cols):
        A = np.c_[df[list(cols)].to_numpy(float), np.ones(len(y))]
        b = np.linalg.lstsq(A, y, rcond=None)[0]
        return np.mean(np.abs(y - A@b))

    print('n', len(y))
    for cols in sets:
        print('+'.join(cols), mae(cols))
    for k in (2, 3):
        best = min(itertools.combinations(features, k), key=mae)
        print(k, best, mae(best))
