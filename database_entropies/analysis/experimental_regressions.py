#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
# from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

# Load the data
def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S FROM molecules', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def fixed_models(X):
    return {
        'gas_model': [X['rot_S'] + X['trans_S'] + X['vib_S']],
        'model_23' : [(2/3)*X['rot_S'] + (2/3)*X['trans_S'] + X['vib_S']]
    }

def define_models(X):
    gas_model = [X['rot_S'] + X['trans_S'] + X['vib_S']]
    model_3   = [X['rot_S'] + X['trans_S'], X['vib_S'], X['rot_S']*X['vib_S']/gas_model + X['trans_S']*X['vib_S']/gas_model]
    model_4   = [X['rot_S'], X['trans_S'], X['vib_S'], X['rot_S']*X['vib_S']/gas_model, X['trans_S']*X['vib_S']/gas_model]
    prexp     = np.exp(X['epsilon'])
    model_5   = [prexp*X['rot_S'], prexp*X['trans_S'], X['vib_S'], X['rot_S']*X['vib_S']/gas_model, X['trans_S']*X['vib_S']/gas_model]
    return {
        'model_1': [X['rot_S'] + X['trans_S'], X['vib_S']],
        'model_2': [X['rot_S'], X['trans_S'], X['vib_S']],
        'model_3': model_3,
        'model_4': model_4,
        'model_5': model_5
    }

def objective(coeffs, *args):
    X, y = args
    predictions = np.dot(X, coeffs)
    return np.sum((y - predictions) ** 2)

def optimize_model(X, y, num_params, model_exp=0):
    bounds = [(0, 1)] * num_params
    if model_exp:
        bounds.append((-np.inf, 0)*model_exp)
    best_score, best_result = np.inf, None
    for _ in range(20):
        initial_guess = np.random.rand(num_params)
        result = minimize(objective, initial_guess, args=(X, y), bounds=bounds, method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    if result.success:
        return result.x, np.mean(np.abs(y - np.dot(X, result.x)))
    return None, None

def main():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    X = data[['rot_S', 'trans_S', 'vib_S', 'epsilon']]
    y = data['experimental_S']
    models = define_models(X)
    for name, predictors in models.items():
        predictors = np.vstack(predictors).T
        coeffs, mae = optimize_model(predictors, y, predictors.shape[1])
        if coeffs is not None:
            print(f'Model: {name}')
            print(f'Optimization coefficients: {coeffs}')
            print(f'MAE: {mae:.4f}')

if __name__ == '__main__':
    main()

quit()


# quit()

#
# Objective function: sum of squared residuals
def objective_mod1(coeffs):
    alpha, beta = coeffs
    predictions = alpha*(strans + srot) + beta*svib
    return np.sum((s_exp - predictions) ** 2)

def objective_mod2(coeffs):
    alpha, beta, gamma = coeffs
    predictions = alpha * strans + beta * srot + gamma * svib
    return np.sum((s_exp - predictions) ** 2)

def objective_mod3(coeffs):
    alpha, beta, gamma = coeffs
    predictions = alpha * (strans + srot) + beta * svib + gamma * (stransvib + srotvib)
    return np.sum((s_exp - predictions) ** 2)

def objective_mod4(coeffs):
    alpha, beta, gamma, delta, epsilon = coeffs
    predictions = alpha * strans + beta * srot + gamma * svib + delta * stransvib + epsilon * srotvib
    return np.sum((s_exp - predictions) ** 2)

#
# Not compleated data!
data = fetch_data('entropiesCOSMO.db')
data = prepare_data(data)
# filtered_valdata = [val for val in valdata if None not in val]
strans, srot, svib = data['trans_S'], data['rot_S'], data['vib_S']
eps = data['epsilon']

s_exp = data['experimental_S']

# # Data for linear regression
# s_exp = np.array([val[3] for val in filtered_valdata])
# X = np.array([[val[0], val[1], val[2]] for val in filtered_valdata])
# strans, srot, svib = X[:,0], X[:,1], X[:,2] # Editable variables

# Just the addition (gas phase)
s_gas = strans + srot + svib
mae_gas = np.mean(np.abs(s_exp - s_gas))
print(f'MAE for gas phase: {mae_gas:.4f}')

# 2/3 model
s_23 = (2 * strans + srot) / 3 + svib
mae_23 = np.mean(np.abs(s_exp - s_23))
print(f'MAE for 2/3 model: {mae_23:.4f}')

# model 1
bounds = [(0, 1), (0, 1)]
best_score, best_result = np.inf, None
for _ in range(20):
    # Random initial guess for the coefficients
    initial_guess = np.random.rand(2)
    # Constraint: no intercept, coefficients between 0 and 1
    result = minimize(objective_mod1, initial_guess, bounds=bounds, method='SLSQP')
    # Check if this result is better
    if result.success and result.fun < best_score:
        best_score = result.fun
        best_result = result
if best_result is not None:
    alpha, beta = best_result.x
    predictions = alpha * (strans + srot) + beta * svib
    mae_mod1 = np.mean(np.abs(s_exp - predictions))
    print(f'MAE for model 1: {mae_mod1:.4f}')

# model 2
bounds = [(0, 1), (0, 1), (0, 1)]
best_score, best_result = np.inf, None
for _ in range(20):
    # Random initial guess for the coefficients
    initial_guess = np.random.rand(3)
    # Constraint: no intercept, coefficients between 0 and 1
    result = minimize(objective_mod2, initial_guess, bounds=bounds, method='SLSQP')
    # Check if this result is better
    if result.success and result.fun < best_score:
        best_score = result.fun
        best_result = result
if best_result is not None:
    alpha, beta, gamma = best_result.x
    predictions = alpha * strans + beta * srot + gamma * svib
    mae_mod2 = np.mean(np.abs(s_exp - predictions))
    print(f'MAE for model 2: {mae_mod2:.4f}')
    print(alpha, beta, gamma)

# pa lambda
iwant = 0.5972811403825273
iwant = [iwant] * len(strans)
bounds = [(-np.inf,0)]
def lambda_obj(coeffs):
    lambd = coeffs
    predictions = np.exp(lambd * eps)
    return np.sum((iwant - predictions) ** 2)
for _ in range(20):
    initial_guess = np.random.rand()
    result = minimize(lambda_obj, initial_guess, bounds=bounds, method='SLSQP')
    if result.success and result.fun < best_score:
        best_score = result.fun
        best_result = result
lambd = best_result.x
print(lambd)
print(np.mean(np.abs(iwant - lambd)))


# Add cross terms
sums = strans + srot + svib
stransrot = (strans * srot) / sums
stransvib = (strans * svib) / sums
srotvib = (srot * svib) / sums

# model 3
bounds = [(0, 1), (0, 1), (0, 1)]
best_score, best_result = np.inf, None
for _ in range(20):
    # Random initial guess for the coefficients
    initial_guess = np.random.rand(3)
    # Constraint: no intercept, coefficients between 0 and 1
    result = minimize(objective_mod3, initial_guess, bounds=bounds, method='SLSQP')
    # Check if this result is better
    if result.success and result.fun < best_score:
        best_score = result.fun
        best_result = result
if best_result is not None:
    alpha, beta, gamma = best_result.x
    predictions = alpha * (strans + srot) + beta * svib + gamma * (stransvib + srotvib)
    mae_mod3 = np.mean(np.abs(s_exp - predictions))
    print(f'MAE for model 3: {mae_mod3:.4f}')

# model 4
bounds = [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1)]
best_score, best_result = np.inf, None
for _ in range(20):
    # Random initial guess for the coefficients
    initial_guess = np.random.rand(5)
    # Constraint: no intercept, coefficients between 0 and 1
    result = minimize(objective_mod4, initial_guess, bounds=bounds, method='SLSQP')
    # Check if this result is better
    if result.success and result.fun < best_score:
        best_score = result.fun
        best_result = result
if best_result is not None:
    alpha, beta, gamma, delta, epsilon = best_result.x
    predictions = alpha * strans + beta * srot + gamma * svib + delta * stransvib + epsilon * srotvib
    mae_mod4 = np.mean(np.abs(s_exp - predictions))
    print(f'MAE for model 4: {mae_mod4:.4f}')

#
# Model with eps
#
def obj_mod5(coeffs):
    alpha, beta, lamd1, lambd2 = coeffs
    predictions = alpha*np.exp(-lamd1*eps)*strans + beta*np.exp(-lambd2*eps)*srot + svib
    return np.sum((s_exp - predictions) ** 2)
bounds = [(0,1), (0,1), (-9999,9999), (-9999,9999)]
# bounds = [(0,1), (0,1), (-np.inf,0), (-np.inf,0)]
best_score, best_result = np.inf, None
for _ in range(20):
    initial_guess = np.random.rand(4)
    result = minimize(obj_mod5, initial_guess, bounds=bounds, method='SLSQP')
    if result.success and result.fun < best_score:
        best_score = result.fun
        best_result = result
if best_result is not None:
    alpha, beta, lamd1, lambd2 = best_result.x
    predictions = alpha*np.exp(-lamd1*eps)*strans + beta*np.exp(-lambd2*eps)*srot + svib
    mae_mod5 = np.mean(np.abs(s_exp - predictions))
    print(alpha, beta, lamd1, lambd2)
    print(f'MAE for model 5: {mae_mod5:.4f}')


quit()

# Scipy optimization
bounds = [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)]
best_score, best_result = np.inf, None
for _ in range(20):
    # Random initial guess for the coefficients
    initial_guess = np.random.rand(6)
    # Constraint: no intercept, coefficients between 0 and 1
    result = minimize(objective, initial_guess, bounds=bounds, method='SLSQP')
    # Check if this result is better
    if result.success and result.fun < best_score:
        best_score = result.fun
        best_result = result
if best_result is not None:
    alpha, beta, gamma, delta, epsilon, zeta = best_result.x
    predictions = alpha * x0 + beta * x1 + gamma * x2 + delta * x3 + epsilon * x4 + zeta * x5
    mae = np.mean(np.abs(y - predictions))
    print(f'MAE for model 3: {mae:.4f}')

quit()


# Minimization result
print('Optimization result:')
if best_result is not None:
    alpha, beta, gamma, delta, epsilon, zeta = best_result.x
    predictions = alpha * x0 + beta * x1 + gamma * x2 + delta * x3 + epsilon * x4 + zeta * x5
    sum_contributions = np.sum(X, axis=1)
    print(f"Optimal coefficients found: alpha={alpha:.4f}, beta={beta:.4f}, gamma={gamma:.4f}")
    print(f"Optimal coefficients found: delta={delta:.4f}, epsilon={epsilon:.4f}, zeta={zeta:.4f}")
    print("for the equation: S_exp = alpha translational + beta rotational + gamma vibrational")
    print("for the equation:       + delta translational*rotational + epsilon translational*vibrational + zeta rotational*vibrational")
    # Calculate R^2
    r_squared = 1 - (np.sum((y - (alpha * x0 + beta * x1 + gamma * x2)) ** 2) / np.sum((y - np.mean(y)) ** 2))
    print(f"R^2: {r_squared:.4f}")
    # Text for the plot
    equation_text = r'$S_{\text{exp}} = \alpha S_{\text{trans}} + \beta S_{\text{rot}} + \gamma S_{\text{vib}} + \delta S_{\text{trans}} S_{\text{rot}} + \epsilon S_{\text{rot}}S_{\text{vib}} + \zeta S_{\text{trans}}S_{\text{vib}}$'
    alpha_text = r'$\alpha = {:.4f}$'.format(alpha)
    beta_text = r'$\beta = {:.1f}$'.format(beta)
    gamma_text = r'$\gamma = {:.1f}$'.format(gamma)
    r_squared_text = r'$r^2 = {:.4f}$'.format(r_squared)
else:
    print("No successful optimization found.")
    quit()

# Plotting
plt.figure(figsize=(12, 6))

# Plot for model predictions vs experimental
plt.subplot(1, 2, 1)
plt.scatter(y, predictions, alpha=0.5)
plt.title('Model Predictions vs. Experimental Entropy')
plt.xlabel('Experimental Entropy')
plt.ylabel('Model Predicted Entropy')
plt.text(0.05, 0.9, equation_text, fontsize=9, transform=plt.gca().transAxes)
plt.text(0.05, 0.85, alpha_text, fontsize=8, transform=plt.gca().transAxes)
plt.text(0.05, 0.8, beta_text, fontsize=8, transform=plt.gca().transAxes)
plt.text(0.05, 0.75, gamma_text, fontsize=8, transform=plt.gca().transAxes)
plt.text(0.05, 0.7, r_squared_text, fontsize=8, transform=plt.gca().transAxes)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)  # Line of perfect fit
plt.grid(True)

# Plot for sum of contributions vs experimental
plt.subplot(1, 2, 2)
plt.scatter(y, sum_contributions, alpha=0.5)
plt.scatter(y, X[:,0], alpha=0.5, label='Translational')
plt.scatter(y, X[:,1], alpha=0.5, label='Rotational')
plt.scatter(y, X[:,2], alpha=0.5, label='Vibrational')
plt.title('Sum of Contributions vs. Experimental Entropy')
plt.xlabel('Experimental Entropy')
plt.ylabel('Sum of Contributions')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)  # Line of perfect fit
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

