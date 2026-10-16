import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor, export_text
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ζ', 'η', 'θ', 'ι', 'κ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f'          | {formatted_coeffs}')

def plot_subplot(position, title, ylabel, y, predictions, equation_text, params_texts, ybox=0.77):
    plt.subplot(2, 3, position)
    plt.scatter(y, predictions, alpha=0.5)
    plt.title(title)
    plt.xlabel('Experimental Entropy')
    plt.ylabel(ylabel)
    textstr = equation_text + '\n' + ', '.join(params_texts[:-1]) + '\n' + params_texts[-1]
    plt.text(0.05, ybox, textstr, fontsize=9, transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.grid(True)

def fetch_data_cross_validation(db_file_path, table_name='all_molecules'):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql(f'SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM {table_name} WHERE nconformers = 1', conn)

def obj_model(coeffs, srot, strans, svib, s_exp, epsilon, model_name):
    sgas = srot + strans + svib
    if model_name == 'linear':
        predictions = coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib
    elif model_name == 'cross_terms':
        predictions = coeffs[0]*(srot + strans) + coeffs[1]*svib + coeffs[2]*svib*(srot + strans)/sgas
    elif model_name == 'exp_agrouped':
        predictions = np.exp(-coeffs[-1]*epsilon)*(coeffs[0]*(srot + strans) +
                                                   coeffs[1]*svib +
                                                   coeffs[2]*svib*(srot + strans)/sgas)
    elif model_name == 'exp_separated':
        predictions = np.exp(-coeffs[-1]*epsilon)*(coeffs[0]*srot +
                                                   coeffs[1]*strans +
                                                   coeffs[2]*svib +
                                                   coeffs[3]*svib*srot/sgas +
                                                   coeffs[4]*svib*strans/sgas)
    elif model_name == 'splited':
        predictions = (np.exp(-coeffs[-1]*epsilon)*(coeffs[0]*srot +
                                                    coeffs[1]*strans +
                                                    coeffs[2]*svib*srot/sgas +
                                                    coeffs[3]*svib*strans/sgas) +
                       coeffs[4]*svib)
    return np.sum((s_exp - predictions)**2)

def opt_model(srot, strans, svib, s_exp, epsilon, model_name, nlin_coeffs, nexp_coeffs=0):
    bounds = [(0, 1)]*nlin_coeffs + [(0, 0.05)]*nexp_coeffs
    best_score, best_result = np.inf, None
    for _ in range(40):
        initial_guess = np.concatenate([np.random.uniform(0, 1, nlin_coeffs), np.random.uniform(0, 0.05, nexp_coeffs)])
        result = minimize(obj_model, initial_guess, args=(srot, strans, svib, s_exp, epsilon, model_name), bounds=bounds, method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def run_models(data):
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    epsilon, s_exp = data['epsilon'], data['experimental_S']
    models = {
        'linear': {'nlin_coeffs': 3, 'nexp_coeffs': 0,
                   'formula': 'α*S_r + β*S_t + γ*S_v'},
        'cross_terms': {'nlin_coeffs': 3, 'nexp_coeffs': 0,
                   'formula': 'α*(S_r + S_t) + β*S_v + γ*S_v(S_r + S_t)/S_gas'},
        'exp_agrouped': {'nlin_coeffs': 3, 'nexp_coeffs': 1,
                   'formula': 'e^(-λ*ε)[α*(S_r + S_t) + β*S_v + γ*S_v*(S_r + S_t)/S_gas]'},
        'exp_separated': {'nlin_coeffs': 5, 'nexp_coeffs': 1,
                   'formula': 'e^(-λ*ε)[α*S_r + β*S_t + γ*S_v + δ*S_v*S_r/S_gas + ζ*S_v*S_t/S_gas]'},
        'splited': {'nlin_coeffs': 5, 'nexp_coeffs': 1,
                   'formula': 'e^(-λ*ε)[α*S_r + β*S_t + γ*S_v*S_r/S_gas + δ*S_v*S_t/S_gas] + ζ*S_v'}
    }
    kf = KFold(n_splits=10, shuffle=True)
    for model_name, model_info in models.items():
        maes = []
        for train_index, test_index in kf.split(data):
            srot_train, strans_train, svib_train = srot[train_index], strans[train_index], svib[train_index]
            epsilon_train, s_exp_train = epsilon[train_index], s_exp[train_index]
            srot_test, strans_test, svib_test = srot[test_index], strans[test_index], svib[test_index]
            epsilon_test, s_exp_test = epsilon[test_index], s_exp[test_index]
            result = opt_model(srot_train, strans_train, svib_train, s_exp_train, epsilon_train, model_name, model_info['nlin_coeffs'], model_info['nexp_coeffs'])
            if result is not None:
                coeffs = result.x
                sgas = srot_test + strans_test + svib_test
                if model_name == 'linear':
                    predictions = coeffs[0]*srot_test + coeffs[1]*strans_test + coeffs[2]*svib_test
                elif model_name == 'cross_terms':
                    predictions = (coeffs[0]*(srot_test + strans_test) + coeffs[1]*svib_test +
                                   coeffs[2]*svib_test*(srot_test + strans_test)/sgas)
                elif model_name == 'exp_agrouped':
                    predictions = np.exp(-coeffs[-1]*epsilon_test)*(coeffs[0]*(srot_test + strans_test) +
                                                                    coeffs[1]*svib_test +
                                                                    coeffs[2]*svib_test*(srot_test + strans_test)/sgas)
                elif model_name == 'exp_separated':
                    predictions = np.exp(-coeffs[-1]*epsilon_test)*(coeffs[0]*srot_test +
                                                                    coeffs[1]*strans_test +
                                                                    coeffs[2]*svib_test +
                                                                    coeffs[3]*svib_test*srot_test/sgas +
                                                                    coeffs[4]*svib_test*strans_test/sgas)
                elif model_name == 'splited':
                    predictions = (np.exp(-coeffs[-1]*epsilon_test)*(coeffs[0]*srot_test +
                                                                     coeffs[1]*strans_test +
                                                                     coeffs[2]*svib_test*srot_test/sgas +
                                                                     coeffs[3]*svib_test*strans_test/sgas) +
                                   coeffs[4]*svib_test)
                maes.append(mean_absolute_error(s_exp_test, predictions))
        avg_mae = np.mean(maes)
        print(f'          |')
        print(f'  {avg_mae:6.4f} | S = {model_info["formula"]}')
        if model_info['nexp_coeffs'] > 0:
            print(f'          | λ: {coeffs[-1]:.4f}')
        print_coeffs(coeffs[:model_info['nlin_coeffs']])

def no_opt_models(data):
    gas_phase = data['rot_S'] + data['trans_S'] + data['vib_S']
    twothirds = 2/3*data['rot_S'] + 2/3*data['trans_S'] + data['vib_S']
    gas_phase_corr = gas_phase + data['correctionS']
    print(f"  {np.mean(np.abs(data['experimental_S'] - gas_phase)):6.2f}  | S = S_r + S_t + S_v")
    print(f'          |')
    print(f"  {np.mean(np.abs(data['experimental_S'] - gas_phase_corr)):6.2f}  | S = S_r + S_t + S_v + ΔS_corr")
    print(f'          |')
    print(f"  {np.mean(np.abs(data['experimental_S'] - twothirds)):6.2f}  | S = 2/3*(S_r + S_t) + S_v")
    print(f'          |')

def cross_validation(db):
    functionals = ['PBE', 'PBE0']
    for functional in functionals:
        data = fetch_data_cross_validation(db, table_name=functional)
        data = prepare_data(data)
        print(f'Functional: {functional}')
        print('    MAE   |  Model')
        print('----------+--------------------------')
        no_opt_models(data)
        run_models(data)

def fetch_data_highest_errors(db_file_path, table_name='all_molecules'):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql(f'SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM {table_name}', conn)

def worst_case_predictions(pred, exp):
    w_idx = np.argmax(np.abs(exp - pred))
    s_idx = np.argmin(exp.values)
    h_idx = np.argmax(exp.values)
    pw, ew = pred.values[w_idx], exp.values[w_idx]
    ps, es = pred.values[s_idx], exp.values[s_idx]
    ph, eh = pred.values[h_idx], exp.values[h_idx]
    dw, ds, dh = pw - ew, ps - es, ph - eh
    print(f'{pw:17.2f} & {ew:20.2f} & {dw:16.2f} & Worst Case')
    print(f'{ps:17.2f} & {es:20.2f} & {ds:16.2f} & Smallest Entropy')
    print(f'{ph:17.2f} & {eh:20.2f} & {dh:16.2f} & Highest Entropy')
    print(f'                  |                      |')

def models_highest_errors(data, functional):
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    s_exp, epsilon = data['experimental_S'], data['epsilon']
    sgas = srot + strans + svib
    model_dic = {
            'linear': {'PBE': [0.7009, 0.5327, 1.0000], 'PBE0': [1.0000, 0.3286, 0.9993]},
            'cross_terms': {'PBE': [0.5590, 0.3972, 1.0000], 'PBE0': [0.5666, 0.3880, 1.0000]},
            'exp_agrouped': {'PBE': [0.5974, 0.3085, 1.0000, 0.0025], 'PBE0': [0.6043, 0.3004, 1.0000, 0.0027]},
            'exp_separated': {'PBE': [0.8999, 0.4318, 0.5242, 0.0000, 1.0000, 0.0024], 'PBE0': [1.0000, 0.3690, 0.5271, 0.0000, 1.0000, 0.0020]},
            'splited': {'PBE': [0.4068, 0.7256, 0.0000, 1.0000, 0.6190, 0.0023], 'PBE0': [0.8178, 0.4699, 0.4721, 1.0000, 0.3978, 0.0016]}
            }
    for model, info in model_dic.items():
        if model == 'linear':
            predictions = info[functional][0]*srot + info[functional][1]*strans + info[functional][2]*svib
        elif model == 'cross_terms':
            predictions = info[functional][0]*(srot + strans) + info[functional][1]*svib + info[functional][2]*svib*(srot + strans)/sgas
        elif model == 'exp_agrouped':
            predictions = np.exp(-info[functional][-1]*epsilon)*(info[functional][0]*(srot + strans) +
                                                                 info[functional][1]*svib +
                                                                 info[functional][2]*svib*(srot + strans)/sgas)
        elif model == 'exp_separated':
            predictions = np.exp(-info[functional][-1]*epsilon)*(info[functional][0]*srot +
                                                                 info[functional][1]*strans +
                                                                 info[functional][2]*svib +
                                                                 info[functional][3]*svib*srot/sgas +
                                                                 info[functional][4]*svib*strans/sgas)
        elif model == 'splited':
            predictions = (np.exp(-info[functional][-1]*epsilon)*(info[functional][0]*srot +
                                                                 info[functional][1]*strans +
                                                                 info[functional][2]*svib*srot/sgas +
                                                                 info[functional][3]*svib*strans/sgas) +
                           info[functional][4]*svib)
        print(f' Functional: {functional:<4} | Model: {model:<13} |     MAE: {mean_absolute_error(s_exp, predictions):.2f}')
        worst_case_predictions(predictions, s_exp)

def highest_errors(db):
    functionals = ['PBE', 'PBE0']
    print(f'    Predictions   |      Experimental    |    Difference    |   Description')
    print(f'------------------+----------------------+------------------+-----------------')
    for functional in functionals:
        data = fetch_data_highest_errors(db, table_name=functional)
        data = prepare_data(data)
        models_highest_errors(data, functional)
        print(f'                  |                      |')

def fetch_data_final_regressions(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM PBE WHERE nconformers IS NOT NULL', conn)

def plot_subplot_final_regressions(position, title, ylabel, y, predictions, equation_text, params_texts, ybox=0.77):
    plt.subplot(1, 3, position)
    plt.scatter(y, predictions, alpha=0.5)
    plt.xlabel('Experimental Entropy', fontsize=14)
    plt.ylabel('Model Predictions', fontsize=14)
    textstr = equation_text + '\n' + ', '.join(params_texts[:-1]) + '\n' + params_texts[-1]
    plt.text(0.05, ybox, textstr, fontsize=9, transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.grid(True)

def final_regressions(db):
    plt.figure(figsize=(18, 6))
    data = fetch_data_final_regressions(db)
    data = prepare_data(data)
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    epsilon, y = data['epsilon'], data['experimental_S']
    s_gas = srot + strans + svib
    s_gas_corr = s_gas + data['correctionS']
    # Linear Model
    # 10.8598 | S = α*S_r + β*S_t + γ*S_v
    #         | α: 1.0000, β: 0.3286, γ: 0.9993
    alpha, beta, gamma = 1.0000, 0.3286, 0.9993
    mae = 10.8598
    predictions = alpha*srot + beta*strans + gamma*svib
    plot_subplot_final_regressions(1, 'Linear Model vs. Experimental Entropy',
                                   'Linear Model', y, predictions,
                                   r'$S = \alpha S_{\text{rot}} + \beta S_{\text{trans}} + \gamma S_{\text{vib}}$',
                                   [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                                    r'$\gamma = {:.2f}$'.format(gamma),
                                    r'$MAE = {:.4f}$'.format(mae)], ybox=0.82)
    # Exponential Separated Model
    # 10.5310 | S = e^(-λ*ε)[α*S_r + β*S_t + γ*S_v + δ*S_v*S_r/S_gas + ζ*S_v*S_t/S_gas]
    #         | λ: 0.0020
    #         | α: 1.0000, β: 0.3690, γ: 0.5271, δ: 0.0000, ζ: 1.0000
    lambd = 0.0020
    alpha, beta, gamma, delta, zeta = 1.0000, 0.3690, 0.5271, 0.0000, 1.0000
    mae = 10.5310
    predictions = np.exp(-lambd*epsilon)*(alpha*srot + beta*strans + gamma*svib + delta*svib*srot/s_gas + zeta*svib*strans/s_gas)
    plot_subplot_final_regressions(2, 'Model Predictions vs. Experimental Entropy',
                                   'Exponential Separated', y, predictions,
                                   r'$S = e^{-\lambda\varepsilon} [\alpha S_{\text{rot}} + \beta S_{\text{trans}} + \gamma S_{\text{vib}} + \delta\frac{S_{\text{vib}}S_{\text{rot}}}{S_{\text{gas}}} + \zeta\frac{S_{\text{vib}}S_{\text{trans}}}{S_{\text{gas}}}]$',
                                   [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                                    r'$\delta = {:.2f}$'.format(delta), r'$\zeta = {:.2f}$'.format(zeta),
                                    r'$\lambda = {:.4f}$'.format(lambd),
                                    r'$MAE = {:.4f}$'.format(mae)], ybox=0.82)
    # Exponential Split Model
    # 10.1949 | S = e^(-λ*ε)[α*S_r + β*S_t + γ*S_v*S_r/S_gas + δ*S_v*S_t/S_gas] + ζ*S_v
    #         | λ: 0.0016
    #         | α: 0.8178, β: 0.4699, γ: 0.4721, δ: 1.0000, ζ: 0.3978
    lambd = 0.0016
    alpha, beta, gamma, delta, zeta = 0.8178, 0.4699, 0.4721, 1.0000, 0.3978
    mae = 10.1949
    predictions = np.exp(-lambd*epsilon)*(alpha*srot + beta*strans + gamma*svib*srot/s_gas + delta*svib*strans/s_gas) + zeta*svib
    plot_subplot_final_regressions(3, 'Exponential Split vs. Experimental Entropy',
                                   'Exponential', y, predictions,
                                   r'$S = e^{-\lambda\varepsilon} [\alpha S_{\text{rot}} + \beta S_{\text{trans}} + \gamma\frac{S_{\text{vib}}S_{\text{rot}}}{S_{\text{gas}}} + \delta\frac{S_{\text{vib}}S_{\text{trans}}}{S_{\text{gas}}}] + \zeta S_{\text{vib}}$',
                                   [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                                    r'$\gamma = {:.2f}$'.format(gamma), r'$\delta = {:.2f}$'.format(delta),
                                    r'$\zeta = {:.2f}$'.format(zeta), r'$\lambda = {:.4f}$'.format(lambd),
                                    r'$MAE = {:.4f}$'.format(mae)], ybox=0.82)
    plt.tight_layout()
    # plt.savefig('final_regressions.pdf')
    plt.show()

def fetch_data_anharmonic_contributions(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM PBE0', conn)

def anharmonic_contributions(db):
    data = fetch_data_anharmonic_contributions(db)
    data = prepare_data(data)
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    epsilon, y, corr = data['epsilon'], data['experimental_S'], data['correctionS']
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 2)
    plt.scatter(y, strans, alpha=0.5, label='Translational')
    plt.scatter(y, srot, alpha=0.5, label='Rotational')
    plt.scatter(y, svib, alpha=0.5, label='Vibrational')
    plt.xlabel(r'Experimental Entropy $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'Average Contributions $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.subplot(1, 2, 1)
    plt.scatter(svib, corr, alpha=0.5)
    plt.xlabel(r'$\mathrm{S_{v}^{h}}$ $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'$\mathrm{\overline{\Delta S}_{v}^{G}}$ $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('anharmonic_contributions.pdf')
    # plt.show()

def fetch_data_anharmonic(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT vib_S, correctionS FROM PBE0', conn)

def anharmonic(db):
    data = fetch_data_anharmonic(db)
    data = prepare_data(data)
    vib, corr = data['vib_S'], data['correctionS']
    plt.scatter(vib,corr)
    plt.xlabel(r'$\mathrm{S_{v}^{h}}$ $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'$\mathrm{\Delta S_{v}^{G}}$ $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.grid(True)
    plt.tight_layout()
    # plt.savefig('final_regressions.pdf')
    plt.show()

def fetch_data_models_figure(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS, rad FROM PBE', conn)

def models_figure(db):
    data = fetch_data_models_figure(db)
    data = prepare_data(data)
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    epsilon, y, corr = data['epsilon'], data['experimental_S'], data['correctionS']
    rad = data['rad']
    plt.figure(figsize=(12, 6))
    s1 = srot + strans + svib
    s23 = (2/3)*(srot + strans) + svib
    s2nl =  0.578*(srot + strans) + svib + 0.403*(svib*srot/(srot+svib+strans) + svib*strans/(srot+svib+strans))
    s3nlv =  0.582*(srot + strans) + svib + 0.238*(svib*srot/(srot+svib+strans) + svib*strans/(srot+svib+strans))
    fgamma = 1 +0.4*np.arctan(np.tanh(0.131*rad))
    gdelta = 5.4*np.log(5.82/epsilon)
    s4nlv =  0.582*(srot + strans) + fgamma*svib + 0.238*(svib*srot/(srot+svib+strans) + svib*strans/(srot+svib+strans)) + gdelta
    s3eps = svib**1.05 - epsilon + 166
    plt.subplot(1, 2, 1)
    plt.scatter(y, s1, alpha=0.5, label=r'$S_1^l$ $\alpha=1$ ')
    plt.scatter(y, s23, alpha=0.5, label=r'$S_1^l$ $\alpha=2/3$ ')
    plt.scatter(y, s2nl, alpha=0.5, label=r'$S_2^{nl}$')
    plt.xlabel(r'Standard Exp. Entropy $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'S$^{\mathrm{pred}}$', size=16)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.subplot(1, 2, 2)
    plt.scatter(y, s3nlv, alpha=0.5, label=r'$S_3^{nl,v-only}$')
    plt.scatter(y, s4nlv, alpha=0.5, label=r'$S_4^{nlv}$')
    plt.scatter(y, s3eps, alpha=0.5, label=r'$S_3^{eps}$')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.xlabel(r'Standard Exp. Entropy $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'S$^{\mathrm{pred}}$', size=16)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('models.pdf')
    # plt.show()

def calculate_mae(model, data, casefrom):
    prediction = model(data, casefrom)
    return mean_absolute_error(data['experimental_S'], prediction)

def fetch_data_cdft_models(db_file_path, casedb):
    with sqlite3.connect(db_file_path) as conn:
        if casedb == 'pbe0':
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS, gamma, eta FROM pbe0', conn)
        elif casedb == 'training':
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS, gamma, eta FROM molecules', conn)
        elif casedb == 'testing':
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS, gamma, eta FROM test_molecules', conn)

def model1(data, case='training'):
    #  9.71  | α*Sr + β*St + (δ*Sv + ζ*epsilon)*e^(-θ*gamma)
    #        | α: 0.5425, β: 0.6639, δ: 0.7824, ζ: -0.3979, θ: -1.9725
    # 11.60  | α: 0.3901, β: 0.7498, δ: 1.0000, ζ: -0.5074, θ: -0.9118
    if case == 'training' or case == 'testing':
        α, β, δ, ζ, θ = 0.5425, 0.6639, 0.7824, -0.3979, -1.9725
    elif case == 'pbe0':
        α, β, δ, ζ, θ = 0.3901, 0.7498, 1.0000, -0.5074, -0.9118
    return α*data['rot_S'] + β*data['trans_S'] + (δ*data['vib_S'] + ζ*data['epsilon'])*np.exp(-θ*data['gamma'])

def modelNO(data):
    # MUY DEPENDIENTE DEL FUNCIONAL DFT (PBE, PBE0) CAMBIAN MUCHO LOS PARAMETROS
    # 9.87  | α*St + β*Sv*e^(γ*eta^3) + δ*eta*epsilon
    #       | α: 1.0000, β: 1.0000, γ: 18.2477, δ: -3.2656
    α, β, γ, δ = 1.0, 1.0, 18.2478, -3.2656
    return α*data['trans_S'] + β*data['vib_S']*np.exp(γ*data['eta']**3) + δ*data['eta']*data['epsilon']

def modelNO(data):
    # MUY DEPENDIENTE DEL FUNCIONAL DFT (PBE, PBE0) CAMBIAN MUCHO LOS PARAMETROS
    # 9.45  | α*Sr + β*St + γ*Sv*e^(δ*eta^3) + ζ*eta*epsilon
    #       | α: 0.4643, β: 0.7121, γ: 0.9138, δ: 20.8624, ζ: -2.7363
    α, β, γ, δ, ζ = 0.4643, 0.7121, 0.9138, 20.8624, -2.7363
    return α*data['rot_S'] + β*data['trans_S'] + γ*data['vib_S']*np.exp(δ*data['eta']**3) + ζ*data['eta']*data['epsilon']

def model2(data, case='training'):
    # 11.55  | α*(Sr + St)*exp(-δ*eta) + β*Sv*exp(ζ*gamma)
    #        | α: 0.5827, β: 0.9019, δ: 0.0965, ζ: 1.5777
    #        | α: 0.6404, β: 1.0000, δ: 0.4378, ζ: 1.0436
    if case == 'training' or case == 'testing':
        α, β, δ, ζ = 0.5827, 0.9019, 0.0965, 1.5777
    elif case == 'pbe0':
        α, β, δ, ζ = 0.6404, 1.0000, 0.4378, 1.0436
    return α*(data['rot_S'] + data['trans_S'])*np.exp(-δ*data['eta']) + β*data['vib_S']*np.exp(ζ*data['gamma'])

def model3(data, case='training'):
    # 9.50  | (α*Sr + β*St)*exp(-θ*epsilon) + (δ*Sv + ζ*epsilon)*exp(ι*gamma)
    #       | α: 0.2657, β: 0.8252, δ: 1.0709, ζ: -1.7112, θ: -0.0077, ι: 0.7422
    #       | α: 0.3507, β: 0.7623, θ: 0.0076, δ: 0.9216, ζ: 0.2847, ι: 1.2514
    if case == 'training' or case == 'testing':
        α, β, δ, ζ, θ, ι = 0.2657, 0.8252, 1.0709, -1.7112, -0.0077, 0.7422
    elif case == 'pbe0':
        α, β, δ, ζ, θ, ι = 0.3507, 0.7623, 0.9216, 0.2847, 0.0076, 1.2514
    return (α*data['rot_S'] + β*data['trans_S'])*np.exp(-θ*data['epsilon']) + (δ*data['vib_S'] + ζ*data['epsilon'])*np.exp(ι*data['gamma'])

def modelnocdft(data, case='training'):
    # 12.7529 | S = e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
    #         | λ: 0.0022
    #         | α: 0.4632, β: 0.5902, γ: 0.2493
    α, β, γ, λ = 0.4632, 0.5902, 0.2493, 0.0022
    sgas = data['rot_S'] + data['trans_S'] + data['vib_S']
    return np.exp(-λ*data['epsilon'])*(α*data['rot_S'] + β*data['trans_S'] + data['vib_S']*data['rot_S']/sgas + γ*data['vib_S']*data['trans_S']/sgas) + data['vib_S']

def print_mae(casefrom, db):
    cases  = ['training', 'testing', 'pbe0']
    models = [model1, model2, model3, modelnocdft]
    model_names = ['Model 1', 'Model 2', 'Model 3', 'Model No CDFT']
    maes = {name: [] for name in model_names}
    for case in cases:
        data = fetch_data_cdft_models(db, case)
        for model, name in zip(models, model_names):
            maes[name].append(calculate_mae(model, data, casefrom))
    mae_df = pd.DataFrame(maes, index=cases)
    print(mae_df)

def plot_subplot_cdft_models(position, title, model, db, ybox=0.77):
    plt.subplot(2, 2, position)
    for case in ['training', 'testing', 'pbe0']:
        d = fetch_data_cdft_models(db, casedb=case)
        for val in ['pbe0']:
            pred = model(d, val)
            plt.scatter(d['experimental_S'], pred, alpha=0.3, label=f'{case.capitalize()} data')
    plt.title(title, fontsize=9)
    plt.xlabel('Experimental S', fontsize=9, labelpad=-1)
    plt.ylabel('Predicted S', fontsize=9)
    plt.plot([d['experimental_S'].min(), d['experimental_S'].max()], [d['experimental_S'].min(), d['experimental_S'].max()], 'k--', lw=2)
    plt.tick_params(axis='both', which='major', labelsize=7)
    plt.legend()
    plt.grid(True)

def plotting(db):
    plt.figure(figsize=(8, 8))
    plot_subplot_cdft_models(1, r'$\alpha S_r + \beta S_t + (\delta S_v + \zeta\epsilon)*e^{-\theta\gamma}$', model1, db)
    plot_subplot_cdft_models(2, r'$\alpha(S_r + S_t)e^{-\delta\eta} + \beta S_v e^{\zeta\gamma}$', model2, db)
    plot_subplot_cdft_models(3, r'$(\alpha S_r + \beta S_t)e^{-\theta\epsilon} + (\delta S_v + \zeta\epsilon)e^{\iota\gamma}$', model3, db)
    plot_subplot_cdft_models(4, r'$e^{-\lambda\epsilon}[\alpha S_r + \beta S_t + S_vS^{-1}_{gas} + \gamma S_tS^{-1}_{gas}] + S_v$', modelnocdft, db)
    plt.savefig('cdft_models.pdf')
    plt.show()

def cdft_models(db):
    print('''
 Model 1 | α*Sr + β*St + (γ*Sv + δ*epsilon)*e^(-ζ*gamma)
 Model 2 | α*(Sr + St)*exp(-γ*eta) + β*Sv*exp(δ*gamma)
 Model 3 | (α*Sr + β*St)*exp(-ζ*epsilon) + (γ*Sv + δ*epsilon)*exp(η*gamma)
 No CDFT | e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
      ''')
    print_mae('training', db)
    print_mae('pbe0', db)
    plotting(db)

def fetch_data_cdft_regressions(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT mu, eta, gamma, epsilon, rot_S, trans_S, vib_S, experimental_S, correctionS FROM pbe0', conn)

def generate_bounds(num_coeffs):
    return [(0, 1)]*num_coeffs

def obj_linear_model(coeffs, sr, st, sv, mu, eta, gamma, epsilon, s_exp, model_name):
    if model_name == 'model0':
        predictions = coeffs[0]*st + (coeffs[1]*sv + coeffs[2]*epsilon)*np.exp(-coeffs[3]*gamma)
    elif model_name == 'model1':
        predictions = coeffs[0]*sr + coeffs[1]*st + (coeffs[2]*sv + coeffs[3]*epsilon)*np.exp(-coeffs[4]*gamma)
    elif model_name == 'model2':
        predictions = coeffs[0]*st + coeffs[1]*sv*np.exp(coeffs[2]*eta**3) + coeffs[3]*eta*epsilon
    elif model_name == 'model3':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*eta**3) + coeffs[4]*eta*epsilon
    elif model_name == 'model4':
        predictions = np.abs(coeffs[0]*sv + coeffs[1])/np.abs((coeffs[2]*gamma*epsilon**(np.sqrt(coeffs[3]*gamma)))**(coeffs[4]*eta))
    elif model_name == 'model5':
        predictions = np.abs(coeffs[0]*sv + coeffs[1])/np.abs((coeffs[2]*gamma*epsilon**(np.sqrt(np.abs(coeffs[3]*gamma))))**(coeffs[4]*eta))
    elif model_name == 'model6':
        predictions = (coeffs[0]*sr + coeffs[1]*sv)**np.cosh(coeffs[2]*gamma) + coeffs[3]
    elif model_name == 'model7':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*epsilon*np.exp(coeffs[3]*gamma) + coeffs[4]*sv*np.exp(coeffs[5]*gamma)
    elif model_name == 'model8':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*np.exp(coeffs[3]*gamma)*sv
    elif model_name == 'model9':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*gamma*sv*(1 + coeffs[3]*epsilon)
    elif model_name == 'model10':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv - coeffs[3]*epsilon*sv*np.exp(coeffs[4]*gamma)
    elif model_name == 'model11':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv + coeffs[3]*sv**(coeffs[4]*eta)
    elif model_name == 'model12':
        sgas = sr + st + sv
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*eta**3) + coeffs[4]*eta*epsilon*sv*sr/sgas
    elif model_name == 'model13':
        predictions = (coeffs[0]*sr + coeffs[1]*st)*np.exp(-coeffs[4]*epsilon) + coeffs[2]*sv + coeffs[3]*epsilon*np.exp(-coeffs[5]*gamma)
    elif model_name == 'model14':
        predictions = (coeffs[0]*sr + coeffs[1]*st)*np.exp(-coeffs[2]*epsilon) + (coeffs[3]*sv + coeffs[4]*epsilon)*np.exp(coeffs[5]*gamma)
    elif model_name == 'model15':
        predictions = coeffs[0]*(sr + st)*np.exp(-coeffs[2]*gamma) + coeffs[1]*sv*np.exp(coeffs[3]*epsilon)
    elif model_name == 'model16':
        predictions = coeffs[0]*(sr + st)*np.exp(-coeffs[2]*eta) + coeffs[1]*sv*np.exp(coeffs[3]*gamma)
    return np.sum((s_exp - predictions)**2)

def optimise_model(sr, st, sv, mu, eta, gamma, epsilon, s_exp, model_name, num_coeffs, bounds):
    best_score, best_result = np.inf, None
    for _ in range(40):
        initial_guess = np.random.rand(num_coeffs)
        result = minimize(obj_linear_model, initial_guess, bounds=bounds, args=(sr, st, sv, mu, eta, gamma, epsilon, s_exp, model_name), method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def models_cdft_regressions(data):
    mu, eta, gamma = data['mu'], data['eta'], data['gamma']
    s_exp, epsilon = data['experimental_S'], data['epsilon']
    sr, st, sv = data['rot_S'], data['trans_S'], data['vib_S']
    gas = sr + st + sv
    models = {
        'model0': {'num_coeffs': 4,
                   'bounds': [(0, 1), (0, 1), (-1, 1), (-2, 2)],
                   'formula': 'α*St + (β*Sv + γ*epsilon)*exp(-δ*gamma)'},
        'model1': {'num_coeffs': 5,
                   'bounds': [(0, 1), (0, 1), (0, 1), (-1, 1), (-np.inf, np.inf)],
                   'formula': 'α*Sr + β*St + (γ*Sv + δ*epsilon)*e^(-ζ*gamma)'},
        'model2': {'num_coeffs': 4,
                   'bounds': [(0, 1), (0, 1), (-20, 20), (-5, 5)],
                   'formula': 'α*St + β*Sv*e^(γ*eta^3) + δ*eta*epsilon'},
        'model3': {'num_coeffs': 5,
                   'bounds': [(0, 1), (0, 1), (0, 1), (-np.inf, np.inf), (-9, 9)],
                   'formula': 'α*Sr + β*St + γ*Sv*e^(δ*eta^3) + ζ*eta*epsilon'},
        'model4': {'num_coeffs': 5,
                   'bounds': [(0, 1), (0, 1000), (0.1, 1), (-9, 9), (-9, 9)],
                   'formula': '|α*Sv + β|/|(γ*gamma*epsilon^(sqrt(δ*gamma)))^(ζ*eta)|'},
        'model5': {'num_coeffs': 5,
                   'bounds': [(0, 1), (0, 1000), (0.01, 1), (0, np.inf), (-np.inf, np.inf)],
                   'formula': '|α*Sv + β|/|(γ*gamma*epsilon**(sqrt(|δ*gamma|)))**(δ*eta)|'},
        'model6' : {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (-np.inf, np.inf), (-300, 300)],
                    'formula': '(α*Sr + β*Sv)^cosh(γ*gamma) + δ'},
        'model7' : {'num_coeffs': 6,
                    'bounds': [(0, 1), (0, 1), (-np.inf, np.inf), (-5, 5), (0, 5), (-5, 5)],
                    'formula': 'α*Sr + β*St + γ*epsilon*exp(δ*gamma) + ζ*Sv*exp(η*gamma)'},
        'model8' : {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (0, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*Sr + β*St + γ*exp(δ*gamma)*Sv'},
        'model9' : {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (0, 9), (-9, 9)],
                    'formula': 'α*Sr + β*St + γ*gamma*Sv*(1+δ*epsilon)'},
        'model10' : {'num_coeffs': 5,
                    'bounds': [(0, 1), (0, 1), (0, 1), (-np.inf, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*Sr + β*St + γ*Sv - δ*epsilon*Sv*e^(ζ*gamma)'},
        'model11' : {'num_coeffs': 5,
                    'bounds': [(0, 1), (0, 1), (0, 1), (-np.inf, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*Sr + β*St + γ*Sv + δ*Sv^(ζ*eta)'},
        'model12': {'num_coeffs': 5,
                    'bounds': [(0, 1), (0, 1), (0, 1), (-20, 20), (-np.inf, np.inf)],
                    'formula': 'α*Sr β*St + γ*Sv*e^(δ*eta^3) + ζ*eta*epsilon*sv^2/sgas'},
        'model13': {'num_coeffs': 6,
                    'bounds': [(0, 1), (0, 1), (0, 1), (-3, 3), (0, np.inf), (0, np.inf)],
                    'formula': '(α*Sr + β*St)*exp(-ζ*epsilon) + γ*Sv + δ*epsilon*exp(-η*gamma)'},
        'model14': {'num_coeffs': 6,
                    'bounds': [(0, 1), (0, 1), (0, 0.5), (-1, 1), (-100, 100), (-np.inf, np.inf)],
                    'formula': '(α*Sr + β*St)*exp(-γ*epsilon) + (δ*Sv + ζ*epsilon)*exp(η*gamma)'},
        'model15': {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (0, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*(Sr + St)*exp(-γ*gamma) + β*Sv*exp(δ*epsilon)'},
        'model16': {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (0, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*(Sr + St)*exp(-γ*eta) + β*Sv*exp(δ*gamma)'},
    }
    for model_name, model_info in models.items():
        result = optimise_model(sr, st, sv, mu, eta, gamma, epsilon, s_exp, model_name, model_info['num_coeffs'], model_info['bounds'])
        if result is not None:
            coeffs = result.x
            if model_name == 'model0':
                predictions = coeffs[0]*st + (coeffs[1]*sv + coeffs[2]*epsilon)*np.exp(-coeffs[3]*gamma)
            elif model_name == 'model1':
                predictions = coeffs[0]*sr + coeffs[1]*st + (coeffs[2]*sv + coeffs[3]*epsilon)*np.exp(-coeffs[4]*gamma)
            elif model_name == 'model2':
                predictions = coeffs[0]*st + coeffs[1]*sv*np.exp(coeffs[2]*eta**3) + coeffs[3]*eta*epsilon
            elif model_name == 'model3':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*eta**3) + coeffs[4]*eta*epsilon
            elif model_name == 'model4':
                predictions = np.abs(coeffs[0]*sv + coeffs[1])/np.abs((coeffs[2]*gamma*epsilon**(np.sqrt(coeffs[3]*gamma)))**(coeffs[4]*eta))
            elif model_name == 'model5':
                predictions = np.abs(coeffs[0]*sv + coeffs[1])/np.abs((coeffs[2]*gamma*epsilon**(np.sqrt(np.abs(coeffs[3]*gamma))))**(coeffs[4]*eta))
            elif model_name == 'model6':
                predictions = (coeffs[0]*sr + coeffs[1]*sv)**np.cosh(coeffs[2]*gamma) + coeffs[3]
            elif model_name == 'model7':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*gamma) + coeffs[4]*sv*np.exp(coeffs[5]*gamma)
            elif model_name == 'model8':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*np.exp(coeffs[3]*gamma)*sv
            elif model_name == 'model9':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*gamma*sv*(1 + coeffs[3]*epsilon)
            elif model_name == 'model10':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv - coeffs[3]*epsilon*sv*np.exp(coeffs[4]*gamma)
            elif model_name == 'model11':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv + coeffs[3]*sv**(coeffs[4]*eta)
            elif model_name == 'model12':
                sgas = sr + st + sv
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*eta**3) + coeffs[4]*eta*epsilon*sv*sr/sgas
            elif model_name == 'model13':
                predictions = (coeffs[0]*sr + coeffs[1]*st)*np.exp(-coeffs[4]*epsilon) + coeffs[2]*sv + coeffs[3]*epsilon*np.exp(-coeffs[5]*gamma)
            elif model_name == 'model14':
                predictions = (coeffs[0]*sr + coeffs[1]*st)*np.exp(-coeffs[2]*epsilon) + (coeffs[3]*sv + coeffs[4]*epsilon)*np.exp(coeffs[5]*gamma)
            elif model_name == 'model15':
                predictions = coeffs[0]*(sr + st)*np.exp(-coeffs[2]*gamma) + coeffs[1]*sv*np.exp(coeffs[3]*epsilon)
            elif model_name == 'model16':
                predictions = coeffs[0]*(sr + st)*np.exp(-coeffs[2]*eta) + coeffs[1]*sv*np.exp(coeffs[3]*gamma)
            mae = np.mean(np.abs(s_exp - predictions))
            diff=np.abs(s_exp-predictions)
            max_diff=np.max(diff)
            max_idx=np.argmax(diff)
            print(f'  {mae:6.2f}  | {model_info["formula"]}')
            print_coeffs(coeffs)

def no_model(data):
    # Abs(x2 + 129.85002)/Abs((x5*x6**(sqrt(x5)))**x4)
    sr, st, sv = data['rot_S'], data['trans_S'], data['vib_S']
    mu, eta, gamma = data['mu'], data['eta'], data['gamma']
    s_exp, epsilon = data['experimental_S'], data['epsilon']
    pred = np.abs(sv + 129.85002)/np.abs((gamma*epsilon**(np.sqrt(gamma)))**eta)
    mae = np.mean(np.abs(s_exp - pred))
    print(f'  {mae:6.2f}  | Abs(Sv + 129.85002)/Abs((gamma*epsilon**(sqrt(gamma)))**eta)')
    # (x1 + x2)**cosh(x5) + 43.268063
    pred = (sr + sv)**np.cosh(gamma) + 43.268063
    mae = np.mean(np.abs(s_exp - pred))
    print(f'  {mae:6.2f}  | (Sr + Sv)**cosh(gamma) + 43.268063')

def cdft_regressions(db):
    data = fetch_data_cdft_regressions(db)
    data = prepare_data(data)
    print('    MAE   |  Model')
    print('----------+--------------------------')
    models_cdft_regressions(data)

def get_mae_values(interaction_type):
    print(f'{interaction_type}')
    mae1 = int(input('Extra equation 1: '))
    mae2 = int(input('Extra equation 2: '))

    mae1 = 1 if mae1 < 0 else mae1
    mae2 = 2 if mae2 < 0 else mae2

    return mae1, mae2

def create_pysr_model():
    from pysr import PySRRegressor
    binaryOp  = ["plus", "mult", "-", "/", "pow"]
    unitaryOp = ["square", "inv(x)=1/x", "exp", "log", "sqrt", "sin", "cos", "tan", "abs"]
    default_pysr_params = dict(
        populations=70,
        model_selection='best',
    )
    return PySRRegressor(
        niterations=300,
        maxdepth=9,
        binary_operators=binaryOp,
        unary_operators=unitaryOp,
        extra_sympy_mappings={"inv": lambda x: 1/x},
        **default_pysr_params
    )

def print_other_model_equations(model, description, num_equations=4):
    print(description)
    for i in range(1, num_equations + 1):
        print(i, model.sympy(i))
    print()

def print_and_return_mae(model, X, y, mae_indices, interaction_type):
    print(f'{interaction_type}\n')
    y_predict0 = model.predict(X)
    print("Best model:", np.absolute(y_predict0 - y).mean())

    y_predict1, y_predict2 = None, None

    if len(mae_indices) > 0 and mae_indices[0] > 0:
        y_predict1 = model.predict(X, mae_indices[0])
        print(f"Manual selection MAE for index {mae_indices[0]}:", np.absolute(y_predict1 - y).mean())

    if len(mae_indices) > 1 and mae_indices[1] > 0:
        y_predict2 = model.predict(X, mae_indices[1])
        print(f"Manual selection MAE for index {mae_indices[1]}:", np.absolute(y_predict2 - y).mean())

    return y_predict0, y_predict1, y_predict2

def pysr_model(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('SELECT trans_S, rot_S, vib_S, epsilon, rad, correctionS, mu, eta, gamma, omega, experimental_S FROM PBE WHERE nconformers = 1')
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    filtered_data = [val for val in data if None not in val]
    s_exp = np.array([val[-1] for val in filtered_data])
    # Best model for entropy without CDFT
    # 12.7529 | S = e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
    #         | λ: 0.0022
    #         | α: 0.4632, β: 0.5902, γ: 0.2493
    eps = np.array([val[6] for val in filtered_data])
    srot = np.array([val[0] for val in filtered_data])
    strans = np.array([val[1] for val in filtered_data])
    svib = np.array([val[2] for val in filtered_data])
    gas = srot + strans + svib
    s_vr = svib*srot/gas
    s_vt = svib*strans/gas
    pred = np.exp(-0.0022*eps)*(0.4632*srot + 0.5902*strans + s_vr + 0.2493*s_vt) + svib
    X = np.array([[val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7], val[8], val[9]] for val in filtered_data])
    model = create_pysr_model()
    model.fit(X, s_exp)
    print('Best model:\n')
    print(model.sympy())
    # The curent best model
    # x2**1.0574647 - x3 + 166.88306
    pred = model.predict(X)
    mae = np.absolute(pred - s_exp).mean()
    print(f'MAE: {mae}\n')

def pysr_figure(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('SELECT trans_S, rot_S, vib_S, epsilon, rad, correctionS, mu, eta, gamma, omega, experimental_S FROM PBE')
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    filtered_data = [val for val in data if None not in val]
    s_exp = np.array([val[-1] for val in filtered_data])
    X = np.array([[val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7], val[8], val[9]] for val in filtered_data])
    pred1 = X[:, 2]**1.0574647 - X[:, 3] + 166.88306
    pred2 = X[:,2] + X[:,5] - np.tan(0.4191836/X[:,9]) + 282.24756 - 386.79474/X[:,4]
    plt.figure(figsize=(8,6))
    plt.scatter(s_exp, pred1, c='blue', edgecolors='k', alpha=0.7)
    plt.plot([s_exp.min(), s_exp.max()], [s_exp.min(), s_exp.max()], 'k--')
    plt.text(0.95, 0.05, r'$S = S_v^{1.05} - \varepsilon + 166$'+f'\nMAE = 13.21', transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    pred2 = X[:,2] + X[:,5] - np.tan(0.4191836/X[:,9]) + 282.24756 - 386.79474/X[:,4]
    plt.scatter(s_exp, pred2, c='green', edgecolors='k', alpha=0.7)
    plt.text(0.05, 0.95, r'$S = S_v + \varepsilon - \tan(0.42/\omega) + 282 - 387/\epsilon$'+f'\nMAE = 13.21', transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    plt.xlabel('Experimental S', fontsize=12)
    plt.ylabel('Predicted S', fontsize=12)
    plt.title('Experimental vs Predicted S', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    # plt.show()
    plt.savefig('plot_no_physical_interpretation.pdf')

def ml_cdft(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('SELECT trans_S, rot_S, vib_S, epsilon, rad, correctionS, mu, eta, gamma, omega, experimental_S FROM PBE0 WHERE nconformers = 1')
    data = cursor.fetchall()
    conn.close()
    filtered_data = [val for val in data if None not in val]
    s_exp = np.array([val[-1] for val in filtered_data])
    X = np.array([[val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7], val[8], val[9]] for val in filtered_data])
    X_train, X_test, y_train, y_test = train_test_split(X, s_exp, test_size=0.2, random_state=42)
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=400, random_state=84)
    }
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        results[name] = {"model": model, "MAE": mae, "R2": r2}
    for name, result in results.items():
        print(f"{name}:")
        print(f"  Mean Absolute Error: {result['MAE']}")
        print(f"  R-squared: {result['R2']}")
        print()
    best_model_name = max(results, key=lambda name: results[name]["R2"])
    best_model = results[best_model_name]["model"]
    print(f"Best model: {best_model_name}")

def fetch_data_random_forest(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, rad, correctionS, mu, eta, gamma, omega, experimental_S FROM PBE', conn)

def random_forest(db):
    data = fetch_data_random_forest(db)
    data = prepare_data(data)
    X = data[['trans_S', 'rot_S', 'vib_S', 'epsilon', 'rad', 'correctionS', 'mu', 'eta', 'gamma', 'omega']]
    y = data['experimental_S']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    random_forest_model = RandomForestRegressor(n_estimators=200, random_state=42)
    random_forest_model.fit(X_train, y_train)
    y_pred = random_forest_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print("Root Mean Squared Error:", np.sqrt(mse))
    print("Feature Importances:", random_forest_model.feature_importances_)
    tree = random_forest_model.estimators_[0]
    tree_rules = export_text(tree, feature_names=['trans_S', 'rot_S', 'vib_S', 'epsilon', 'rad', 'correctionS', 'mu', 'eta', 'gamma', 'omega'])

def fig1(db):
    import seaborn as sns
    conn=sqlite3.connect(db)
    df=pd.read_sql_query('SELECT epsilon,experimental_S FROM PBE',conn)
    fig,ax = plt.subplots(1,2,figsize=(12,6))
    nbin = 80
    nsystems = len(df)
    sns.histplot(df['epsilon'], ax=ax[0], color='blue', fill=True,
                 stat='count', bins=nbin, alpha=0.5)
    ax[0].set_xlabel(r'$\varepsilon_r$',fontsize=18)
    ax[0].set_ylabel('Frequency',fontsize=18)
    ax[0].tick_params(which='major', labelsize=14)
    sns.histplot(df['experimental_S'], ax=ax[1], color='green', fill=True,
                 stat='count', bins=nbin, alpha=0.5)
    ax[1].set_xlabel(r'Experimental Entropy [$\mathrm{JK^{-1}mol^{-1}}$]',fontsize=18)
    ax[1].set_ylabel('Frequency',fontsize=18)
    ax[1].tick_params(axis='both', which='major', labelsize=14)
    plt.tight_layout()
    plt.savefig('fig1.pdf')

def entropy_model(St, Sr, Sv, epsilon):
    # S = e^(-λ*ε)[α*S_r + β*S_t + γ*S_v + δ*S_v*S_r/S_gas + ζ*S_v*S_t/S_gas]
    # λ: 0.0034
    # α: 0.3440, β: 0.7091, γ: 1.0000, δ: 1.0000, ζ: 0.3454
    lambd = 0.0034
    alpha, beta, gamma, delta, zeta = 0.3440, 0.7091, 1.0000, 1.0000, 0.3454
    S_gas = St + Sr + Sv
    return (np.exp(-lambd*epsilon)*(alpha*Sr + beta*St +
                                    gamma*Sv +
                                    delta*Sv*Sr/S_gas +
                                    zeta*Sv*St/S_gas))
