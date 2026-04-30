#!/usr/bin/python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.svm import SVC
from scipy.optimize import minimize
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def read_react(filename):

    data = {
        "natoms": [],
        "expN": [],
        "expSn": [],
        "distances": [],
        "q_qtaim": [],
        "clr": [],
        "electrostatic_potential": [],
        "electrofuge": []
    }

    with open(filename, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            data["natoms"].append(int(lines[i].strip()))
            i += 1

            expN, expSn = map(float, lines[i].split())
            data["expN"].append(expN)
            data["expSn"].append(expSn)
            i += 1

            data["distances"].append(list(map(float, lines[i].split())))
            i += 1

            data["q_qtaim"].append(list(map(float, lines[i].split())))
            i += 1

            data["clr"].append(list(map(float, lines[i].split())))
            i += 1

            data["electrostatic_potential"].append(list(map(float, lines[i].split())))
            i += 2

            data["electrofuge"].append(float(lines[i].strip()))
            i += 1

    return data

def read_noreact(filename):

    data = {
        "natoms": [],
        "expN": [],
        "expSn": [],
        "distances": [],
        "q_qtaim": [],
        "clr": []
    }

    with open(filename, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            data["natoms"].append(int(lines[i].strip()))
            i += 1

            expN, expSn = map(float, lines[i].split())
            data["expN"].append(expN)
            data["expSn"].append(expSn)
            i += 1

            data["distances"].append(list(map(float, lines[i].split())))
            i += 1

            data["q_qtaim"].append(list(map(float, lines[i].split())))
            i += 1

            data["clr"].append(list(map(float, lines[i].split())))
            i += 1

    return data

react_data = read_react('reactive.pout')
noreact_data = read_noreact('no_reactive.pout')

def prepare_data(react_data, noreact_data):
    """
    Combine reactive and non-reactive data and create labels
    """
    combined_data = {
        "natoms": react_data["natoms"] + noreact_data["natoms"],
        "expN": react_data["expN"] + noreact_data["expN"],
        "expSn": react_data["expSn"] + noreact_data["expSn"],
        "distances": react_data["distances"] + noreact_data["distances"],
        "q_qtaim": react_data["q_qtaim"] + noreact_data["q_qtaim"],
        "clr": react_data["clr"] + noreact_data["clr"]
    }
    
    n_react = len(react_data["natoms"])
    n_noreact = len(noreact_data["natoms"])
    labels = np.array([1]*n_react + [0]*n_noreact)
    
    return combined_data, labels

def compute_weighted_features(data, alpha, beta, gamma, delta):
    """
    Compute exponentially weighted features for each molecule
    
    q_weighted   = γ*Σ exp(-α*distance)*q_atom
    clr_weighted = δ*Σ exp(-β*distance)*clr_atom
    """
    n_molecules = len(data["natoms"])
    features = []
    
    for i in range(n_molecules):
        distances = np.array(data["distances"][i])
        q_qtaim = np.array(data["q_qtaim"][i])
        clr = np.array(data["clr"][i])
        
        # Compute exponential weights with numerical stability
        weights_q = np.exp(-alpha*distances)
        weights_clr = np.exp(-beta*distances)
        
        # Compute weighted sums
        q_weighted = gamma*np.sum(weights_q*q_qtaim)
        clr_weighted = delta*np.sum(weights_clr*clr)
        
        features.append([
            q_weighted,
            clr_weighted,
            data["expN"][i],
            data["expSn"][i]
        ])
    
    return np.array(features)

def objective_function(params, data, labels):
    """
    Objective function to minimize (negative accuracy)
    
    params: [alpha, beta, gamma, delta] - decay and scaling parameters
    """
    alpha, beta, gamma, delta = params
    
    # Add penalty for extreme values to avoid numerical issues
    if alpha > 10 or beta > 10:
        return 1.0  # Return worst possible score
    
    X = compute_weighted_features(data, alpha, beta, gamma, delta)
    
    # Check for numerical issues
    if np.any(np.isnan(X)) or np.any(np.isinf(X)):
        return 1.0
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Use probability estimates for better optimization landscape
    model = SVC(kernel='rbf', random_state=42, probability=True, C=1.0)
    model.fit(X_scaled, labels)
    
    # Use cross-entropy-like loss for smoother optimization
    pred_proba = model.predict_proba(X_scaled)
    epsilon = 1e-15
    pred_proba = np.clip(pred_proba, epsilon, 1 - epsilon)
    
    # Calculate log loss (more sensitive to probability changes)
    loss = -np.mean(labels*np.log(pred_proba[:, 1]) + (1 - labels)*np.log(pred_proba[:, 0]))
    
    return loss

def optimize_decay_parameters(react_data, noreact_data):
    """
    Find optimal alpha, beta, gamma, and delta parameters that maximize classification accuracy
    """
    print("Starting optimization...")
    print("-"*50)
    
    data, labels = prepare_data(react_data, noreact_data)
    
    # Wider bounds for better exploration
    bounds = [(0.01, 5.0), (0.01, 5.0), (0.1, 10.0), (0.1, 10.0)]
    
    best_accuracy = -np.inf
    best_params = None
    all_results = []
    
    # More diverse initial guesses for better global optimization
    initial_guesses = [
        [3.0, 3.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [0.5, 0.5, 1.0, 1.0],
        [1.0, 1.0, 2.0, 2.0],
        [0.1, 0.1, 0.5, 0.5],
        [2.0, 2.0, 5.0, 5.0],
        [0.3, 1.5, 3.0, 1.5],
        [1.5, 0.3, 1.5, 3.0],
        [0.05, 2.0, 4.0, 0.5]
    ]
    
    # Callback to monitor progress
    iteration_count = [0]
    def callback(xk):
        iteration_count[0] += 1
        if iteration_count[0] % 10 == 0:
            print(f"  Iteration {iteration_count[0]}: α={xk[0]:.4f}, β={xk[1]:.4f}, γ={xk[2]:.4f}, δ={xk[3]:.4f}")
    
    for i, init_guess in enumerate(initial_guesses):
        print(f"\nTrying initial guess {i + 1}/{len(initial_guesses)}: {init_guess}")
        iteration_count[0] = 0
        
        # Try different optimization methods
        for method in ['L-BFGS-B', 'TNC']:
            result = minimize(
                objective_function,
                init_guess,
                args=(data, labels),
                method=method,
                bounds=bounds,
                options={'maxiter': 200, 'disp': False},
                callback=callback if method == 'L-BFGS-B' else None
            )
            
            # Evaluate with actual accuracy
            alpha, beta, gamma, delta = result.x
            X_test = compute_weighted_features(data, alpha, beta, gamma, delta)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_test)
            model = SVC(kernel='rbf', random_state=42)
            model.fit(X_scaled, labels)
            pred = model.predict(X_scaled)
            accuracy = accuracy_score(labels, pred)
            
            all_results.append({
                'params': result.x,
                'accuracy': accuracy,
                'method': method,
                'success': result.success
            })
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_params = result.x
                best_result = result
                best_method = method
    
    # Sort all results by accuracy
    all_results.sort(key=lambda x: x['accuracy'], reverse=True)
    
    print("\n" + "="*50)
    print("TOP 5 RESULTS:")
    print("="*50)
    for i, res in enumerate(all_results[:5]):
        print(f"{i + 1}. Accuracy: {res['accuracy']:.4f}, Method: {res['method']}")
        print(f"   α={res['params'][0]:.4f}, β={res['params'][1]:.4f}, γ={res['params'][2]:.4f}, δ={res['params'][3]:.4f}")
    
    # Final evaluation with best parameters
    alpha_opt, beta_opt, gamma_opt, delta_opt = best_params
    X_final = compute_weighted_features(data, alpha_opt, beta_opt, gamma_opt, delta_opt)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_final)
    
    model = SVC(kernel='rbf', random_state=42)
    model.fit(X_scaled, labels)
    pred = model.predict(X_scaled)
    
    from sklearn.metrics import classification_report, confusion_matrix
    
    print("\n" + "="*50)
    print("BEST OPTIMIZATION RESULTS")
    print("="*50)
    print(f"\nOptimal Parameters (Method: {best_method}):")
    print(f"  α (alpha) = {alpha_opt:.6f}")
    print(f"  β (beta)  = {beta_opt:.6f}")
    print(f"  γ (gamma) = {gamma_opt:.6f}")
    print(f"  δ (delta) = {delta_opt:.6f}")
    print(f"\nBest Accuracy: {best_accuracy:.4f}")
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(labels, pred)
    print(f"  True Negative:  {cm[0,0]:3d}  False Positive: {cm[0,1]:3d}")
    print(f"  False Negative: {cm[1,0]:3d}  True Positive:  {cm[1,1]:3d}")
    
    print("\nClassification Report:")
    print(classification_report(labels, pred, 
                              target_names=['Non-Reactive', 'Reactive'],
                              digits=4))
    
    # Parameter sensitivity analysis
    print("\n" + "="*50)
    print("PARAMETER SENSITIVITY CHECK")
    print("="*50)
    
    perturbations = [0.9, 0.95, 1.0, 1.05, 1.1]
    for pert in perturbations:
        if pert == 1.0:
            continue
        test_params = best_params*pert
        X_test = compute_weighted_features(data, *test_params)
        X_test_scaled = scaler.fit_transform(X_test)
        test_model = SVC(kernel='rbf', random_state=42)
        test_model.fit(X_test_scaled, labels)
        test_pred = test_model.predict(X_test_scaled)
        test_acc = accuracy_score(labels, test_pred)
        print(f"  {(pert - 1)*100:+.0f}% perturbation: Accuracy = {test_acc:.4f} (Δ = {(test_acc - best_accuracy)*100:+.2f}%)")
    
    return {
        'alpha': alpha_opt,
        'beta': beta_opt,
        'gamma': gamma_opt,
        'delta': delta_opt,
        'accuracy': best_accuracy,
        'model': model,
        'data': data,
        'labels': labels,
        'scaler': scaler,
        'all_results': all_results
    }

def plot_best_classification(results, save_fig=False, fig_name='best_classification.png'):
    """
    Plot the 2D classification results using the optimal alpha and beta parameters
    """
    alpha_opt = results['alpha']
    beta_opt = results['beta']
    gamma_opt = results['gamma']
    delta_opt = results['delta']
    data = results['data']
    labels = results['labels']
    
    X = compute_weighted_features(data, alpha_opt, beta_opt, gamma_opt, delta_opt)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    q_weighted = X_scaled[:, 0]
    clr_weighted = X_scaled[:, 1]
    
    labels_text = ['Non-Reactive', 'Reactive']
    
    plt.figure(figsize=(12, 8))
    
    model = SVC(kernel='rbf', random_state=42)
    model.fit(X_scaled[:, :2], labels)
    
    h = 0.02
    x_min, x_max = q_weighted.min() - 0.5, q_weighted.max() + 0.5
    y_min, y_max = clr_weighted.min() - 0.5, clr_weighted.max() + 0.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    x_factor = (X[:, 0].max() - X[:, 0].min())/(X_scaled[:, 0].max() - X_scaled[:, 0].min())
    y_factor = (X[:, 1].max() - X[:, 1].min())/(X_scaled[:, 1].max() - X_scaled[:, 1].min())
    x_offset = X[:, 0].min() - x_factor*X_scaled[:, 0].min()
    y_offset = X[:, 1].min() - y_factor*X_scaled[:, 1].min()
    x_start = x_min*x_factor + x_offset
    y_start = y_min*y_factor + y_offset
    x_end = x_max*x_factor + x_offset
    y_end = y_max*y_factor + y_offset
    xtickslables = [f'{val:.2f}' for val in np.linspace(x_start, x_end, num=5)]
    ytickslables = [f'{val:.2f}' for val in np.linspace(y_start, y_end, num=5)]
    plt.xticks(np.linspace(x_min, x_max, num=5), xtickslables, fontsize=22)
    plt.yticks(np.linspace(y_min, y_max, num=5), ytickslables, fontsize=22)

    colors = ["yellow", "purple"]
    cmap = ListedColormap(colors)
    
    plt.contourf(xx, yy, Z, alpha=0.3, levels=[0, 0.5, 1], cmap='viridis')
    plt.contour(xx, yy, Z, linewidths=1, alpha=0.4)
    
    for i in range(2):
        mask = labels == i
        plt.scatter(q_weighted[mask], clr_weighted[mask], 
                   cmap=cmap, c=colors[i],
                   edgecolor='k',
                   alpha=0.7, linewidth=0.5, s=50)
    
    predictions = model.predict(X_scaled[:, :2])
    misclassified = predictions != labels
    if np.any(misclassified):
        plt.scatter(q_weighted[misclassified], clr_weighted[misclassified],
                   label='Misclassified',
                   marker='x', s=150, c='black', linewidth=3)
    
    plt.xlabel(r'$q(N)$', fontsize=26)
    plt.ylabel(r'$\chi (N)$', fontsize=26)
    plt.title('Neighbour Weighted Clustering', fontsize=30, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    accuracy = accuracy_score(labels, predictions)
    
    label_text = f'$\\times$ Misclassified\nAccuracy: {accuracy*100:.1f}%'
    plt.text(
        x_min + 0.5, y_max - 0.7,
        label_text,
        fontsize=20,
        color='black',
        bbox=dict(
            facecolor='white',
            edgecolor='black',
            boxstyle='round,pad=0.4',
            alpha=0.8
        )
    )

    plt.tight_layout()
    
    if save_fig:
        plt.savefig(fig_name, dpi=300, bbox_inches='tight')
        print(f"\nFigure saved as '{fig_name}'")
    
    plt.show()

# Main execution
if __name__ == "__main__":
    react_data = read_react('reactive.pout')
    noreact_data = read_noreact('no_reactive.pout')
    
    results = optimize_decay_parameters(react_data, noreact_data)

    plot_best_classification(results, save_fig=True, fig_name='optimized_classification.png')
    
    print("\n" + "="*50)
    print("OPTIMAL PARAMETERS FOR FUTURE USE:")
    print("="*50)
    print(f"q_weighted   = {results['gamma']:.6f}*Σ(exp(-{results['alpha']:.6f}*distance)*q_atom)")
    print(f"clr_weighted = {results['delta']:.6f}*Σ(exp(-{results['beta']:.6f}*distance)*clr_atom)")

