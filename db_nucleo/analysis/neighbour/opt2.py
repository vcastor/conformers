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
    # Combine data
    combined_data = {
        "natoms": react_data["natoms"] + noreact_data["natoms"],
        "expN": react_data["expN"] + noreact_data["expN"],
        "expSn": react_data["expSn"] + noreact_data["expSn"],
        "distances": react_data["distances"] + noreact_data["distances"],
        "q_qtaim": react_data["q_qtaim"] + noreact_data["q_qtaim"],
        "clr": react_data["clr"] + noreact_data["clr"]
    }
    
    # Create labels: 1 for reactive, 0 for non-reactive
    n_react = len(react_data["natoms"])
    n_noreact = len(noreact_data["natoms"])
    labels = np.array([1] * n_react + [0] * n_noreact)
    
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
        # Get data for this molecule
        distances = np.array(data["distances"][i])
        q_qtaim = np.array(data["q_qtaim"][i])
        clr = np.array(data["clr"][i])
        
        # Compute exponential weights
        weights_q   = np.exp(-alpha*distances)
        weights_clr = np.exp(-beta*distances)
        
        # Compute weighted sums
        q_weighted   = gamma*np.sum(weights_q*q_qtaim)
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

    # Compute weighted features
    X = compute_weighted_features(data, alpha, beta, gamma, delta)
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train SVM model
    model = SVC(kernel='rbf', random_state=42, probability=True, C=1.0)
    model.fit(X_scaled, labels)
    
    # Predict and calculate accuracy
    pred_proba = model.predict_proba(X_scaled)
    epsilon = 1e-15
    pred_proba = np.clip(pred_proba, epsilon, 1 - epsilon)

    loss = -np.mean(labels*np.log(pred_proba[:,1]) + (1 - labels)*np.log(pred_proba[:,0]))
    
    return loss
    
def optimize_decay_parameters(react_data, noreact_data):
    """
    Find optimal alpha, beta, gamma, and delta parameters that maximize classification accuracy
    """
    print("Starting optimization...")
    print("-" * 50)
    
    data, labels = prepare_data(react_data, noreact_data)
    bounds = [(0.005, 4.0), (0.005, 4.0), (0.005, 4.0), (0.005, 4.0)]
    
    # Store best results
    best_accuracy = -np.inf
    best_params = None
    all_results = []
    
    # More diverse initial guesses for better global optimization
    initial_guesses = [
        [1.0, 1.0, 1.0, 1.0],
        [3.0, 3.0, 1.0, 1.0],
        [1.0, 1.0, 2.0, 2.0],
        [0.1, 0.1, 0.5, 0.5],
        [2.0, 2.0, 3.7, 3.8],
        [0.3, 1.5, 3.0, 1.5],
        [1.5, 0.3, 1.5, 3.0],
        [0.05, 2.0, 4.0, 0.5]
    ]
    
    for i, init_guess in enumerate(initial_guesses):
        # Optimize
        result = minimize(
            objective_function,
            init_guess,
            args=(data, labels),
            method='TNC',
            bounds=bounds,
            options={'maxiter': 200, 'disp': False}
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
            'sucess': result.success
        })
        
        # Get accuracy for this solution
        # accuracy = -result.fun
        
        # Update best if better
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_params = result.x
            best_result = result
    
    # Sort all results by accuracy
    all_results.sort(key=lambda x: x['accuracy'], reverse=True)
    print(50*"-")
    print("TOP FIVE RESULTS:")
    for res in all_results[:5]:
        alpha, beta, gamma, delta = res['params']
        print(f"  α={alpha:.6f}, β={beta:.6f}, γ={gamma:.6f}, δ={delta:.6f} | Accuracy: {res['accuracy']:.4f} | Success: {res['sucess']}")

    # Final evaluation with best parameters
    alpha_opt, beta_opt, gamma_opt, delta_opt = best_params
    X_final = compute_weighted_features(data, alpha_opt, beta_opt, gamma_opt, delta_opt)
    
    # Standardize and train final model
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_final)
    
    model = SVC(kernel='rbf', random_state=42)
    model.fit(X_scaled, labels)
    pred = model.predict(X_scaled)
    
    # Calculate final metrics
    from sklearn.metrics import classification_report, confusion_matrix
    
    print("\n" + "=" * 50)
    print("OPTIMIZATION RESULTS")
    print("=" * 50)
    print(f"\nOptimal Parameters:")
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
    
    return {
        'alpha': alpha_opt,
        'beta': beta_opt,
        'gamma': gamma_opt,
        'delta': delta_opt,
        'accuracy': best_accuracy,
        'model': model,
        'data': data,
        'labels': labels,
        'scaler': scaler
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
    
    q_weighted = X_scaled[:, 0]  # Standardized q_weighted
    clr_weighted = X_scaled[:, 1]  # Standardized clr_weighted
    
    # Define colors for classes
    labels_text = ['Non-Reactive', 'Reactive']
    
    # ========== Plot 1: Raw Weighted Features ==========
    plt.figure(figsize=(12, 8))
    
    # Train SVM with optimal parameters
    model = SVC(kernel='rbf', random_state=42)
    model.fit(X_scaled[:, :2], labels)
    
    # Create mesh for decision boundary
    h = 0.02  # step size in the mesh
    x_min, x_max = q_weighted.min() - 0.5, q_weighted.max() + 0.5
    y_min, y_max = clr_weighted.min() - 0.5, clr_weighted.max() + 0.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    
    # Predict on mesh
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Set the tiks in the original scale
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

    # colors = ["purple", "yellow"]
    colors = ["yellow", "purple"]
    cmap = ListedColormap(colors)
    
    # Plot decision boundary
    # plt.contourf(xx, yy, Z, alpha=0.3, extend='both', cmap=cmap)
    plt.contourf(xx, yy, Z, alpha=0.3, levels=[0, 0.5, 1], cmap='viridis')
    plt.contour(xx, yy, Z, linewidths=1, alpha=0.4)
    
    # Plot points
    for i in range(2):
        mask = labels == i
        plt.scatter(q_weighted[mask], clr_weighted[mask], 
                    cmap=cmap, c=colors[i],
                    edgecolor='k',
                    # label=labels_text[i], edgecolor='k',
                    alpha=0.7, linewidth=0.5, s=50)
    
    # Mark misclassified points
    predictions = model.predict(X_scaled[:, :2])
    misclassified = predictions != labels
    if np.any(misclassified):
        plt.scatter(q_weighted[misclassified], clr_weighted[misclassified],
                   label='Misclassified',
                   marker='x', s=150, c='black', linewidth=3)
    
    plt.xlabel(r'$q(N)$', fontsize=26)
    plt.ylabel(r'$\chi (N)$', fontsize=26)
    plt.title('Neighbour Weighted Clustering', fontsize=30, fontweight='bold')
    # plt.legend(loc='best', fontsize=18)
    plt.grid(True, alpha=0.3)
    
    # Calculate metrics
    accuracy = accuracy_score(labels, predictions)
    from sklearn.metrics import precision_score, recall_score, f1_score
    
    precision = precision_score(labels, predictions)
    recall = recall_score(labels, predictions)
    f1 = f1_score(labels, predictions)
    
    accuracy = accuracy_score(labels, predictions)
    handles, labels_legend = plt.gca().get_legend_handles_labels()

    # Create text with marker symbols
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
    
    # if save_fig:
    #     plt.savefig(fig_name, dpi=300, bbox_inches='tight')
    #     print(f"\nFigure saved as '{fig_name}'")
    
    plt.show()

# Main execution
if __name__ == "__main__":
    # Read your data
    react_data = read_react('reactive.pout')
    noreact_data = read_noreact('no_reactive.pout')
    
    # Run optimization
    results = optimize_decay_parameters(react_data, noreact_data)

    plot_best_classification(results)
    
    # You can now use the optimal parameters for predictions on new data
    print("\n" + "=" * 50)
    print("You can now use these optimal parameters:")
    print(f"  q_weighted   = {results['gamma']:.6f} * Σ exp(-{results['alpha']:.6f} * distance) * q_atom")
    print(f"  clr_weighted = {results['delta']:.6f} * Σ exp(-{results['beta']:.6f} * distance) * clr_atom")

