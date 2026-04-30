#!/usr/bin/python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.svm import SVC
from scipy.optimize import minimize
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold
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
    Objective function using cross-validation to avoid overfitting
    Returns negative F1 score (we want to minimize)
    """
    alpha, beta, gamma, delta = params
    
    # Bounds check for numerical stability
    if alpha <= 0 or beta <= 0 or gamma <= 0 or delta <= 0:
        return 1.0
    if alpha > 10 or beta > 10 or gamma > 20 or delta > 20:
        return 1.0
    
    X = compute_weighted_features(data, alpha, beta, gamma, delta)
    
    # Check for numerical issues
    if np.any(np.isnan(X)) or np.any(np.isinf(X)):
        return 1.0
    
    # Use 5-fold cross-validation to get realistic performance
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    f1_scores = []
    
    for train_idx, val_idx in skf.split(X, labels):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = labels[train_idx], labels[val_idx]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        # Train model
        model = SVC(kernel='rbf', random_state=42, C=1.0)
        model.fit(X_train_scaled, y_train)
        
        # Predict on validation set
        y_pred = model.predict(X_val_scaled)
        
        # Calculate F1 score (harmonic mean of precision and recall)
        f1 = f1_score(y_val, y_pred)
        f1_scores.append(f1)
    
    # Return negative mean F1 score (we minimize)
    mean_f1 = np.mean(f1_scores)
    return -mean_f1

def optimize_decay_parameters(react_data, noreact_data):
    """
    Find optimal parameters using cross-validation to avoid overfitting
    """
    print("Starting optimization with cross-validation...")
    print("-"*50)
    
    data, labels = prepare_data(react_data, noreact_data)
    
    # Parameter bounds: [alpha, beta, gamma, delta]
    bounds = [(0.01, 5.0), (0.01, 5.0), (0.1, 10.0), (0.1, 10.0)]
    
    best_score = -np.inf
    best_params = None
    all_results = []
    
    # Diverse initial guesses
    initial_guesses = [
        [1.0, 1.0, 1.0, 1.0],
        [0.5, 0.5, 1.0, 1.0],
        [1.0, 1.0, 2.0, 2.0],
        [0.1, 0.1, 0.5, 0.5],
        [2.0, 2.0, 5.0, 5.0],
        [0.3, 1.5, 3.0, 1.5],
        [1.5, 0.3, 1.5, 3.0],
        [3.0, 3.0, 1.0, 1.0],
        [1.0, 0.5, 3.0, 2.0],
        [0.05, 2.0, 4.0, 0.5],
        [0.8, 1.2, 1.8, 2.5]
    ]
    
    print(f"Testing {len(initial_guesses)} initial guesses with 5-fold cross-validation...\n")
    
    for i, init_guess in enumerate(initial_guesses):
        # Optimize
        result = minimize(
            objective_function,
            init_guess,
            args=(data, labels),
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 200, 'disp': False}
        )
        
        # Get cross-validation score for optimized parameters
        print(40*"-")
        print(result.fun)
        cv_score = -result.fun
        
        # Also calculate full training set metrics for comparison
        alpha, beta, gamma, delta = result.x
        X_full = compute_weighted_features(data, alpha, beta, gamma, delta)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_full)
        model = SVC(kernel='rbf', random_state=42)
        model.fit(X_scaled, labels)
        pred = model.predict(X_scaled)
        
        train_accuracy = accuracy_score(labels, pred)
        train_precision = precision_score(labels, pred)
        train_recall = recall_score(labels, pred)
        train_f1 = f1_score(labels, pred)
        
        print(f"  → Optimized: α={alpha:.3f}, β={beta:.3f}, γ={gamma:.3f}, δ={delta:.3f}")
        print(f"     CV F1: {cv_score:.3f}, Train Acc: {train_accuracy:.3f}, Train F1: {train_f1:.3f}")
        
        all_results.append({
            'params': result.x,
            'cv_f1': cv_score,
            'train_accuracy': train_accuracy,
            'train_f1': train_f1,
            'train_precision': train_precision,
            'train_recall': train_recall,
            'success': result.success
        })
        
        if cv_score > best_score:
            best_score = cv_score
            best_params = result.x
            best_result = result
    
    # Sort by cross-validation F1 score
    all_results.sort(key=lambda x: x['cv_f1'], reverse=True)
    
    print("\n" + "="*50)
    print("TOP 5 RESULTS (sorted by CV F1 score):")
    print("="*50)
    for i, res in enumerate(all_results[:5]):
        print(f"{i + 1}. CV F1: {res['cv_f1']:.4f}, Train Acc: {res['train_accuracy']:.4f}, Train F1: {res['train_f1']:.4f}")
        print(f"   α={res['params'][0]:.4f}, β={res['params'][1]:.4f}, γ={res['params'][2]:.4f}, δ={res['params'][3]:.4f}")
        print(f"   Precision: {res['train_precision']:.4f}, Recall: {res['train_recall']:.4f}")
    
    # Final evaluation with best parameters
    alpha_opt, beta_opt, gamma_opt, delta_opt = best_params
    X_final = compute_weighted_features(data, alpha_opt, beta_opt, gamma_opt, delta_opt)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_final)
    
    model = SVC(kernel='rbf', random_state=42)
    model.fit(X_scaled, labels)
    pred = model.predict(X_scaled)
    
    # Calculate all metrics
    final_accuracy = accuracy_score(labels, pred)
    final_precision = precision_score(labels, pred)
    final_recall = recall_score(labels, pred)
    final_f1 = f1_score(labels, pred)
    
    from sklearn.metrics import classification_report, confusion_matrix
    
    print("\n" + "="*50)
    print("BEST OPTIMIZATION RESULTS")
    print("="*50)
    print(f"\nOptimal Parameters (based on CV F1 score):")
    print(f"  α (alpha) = {alpha_opt:.6f}")
    print(f"  β (beta)  = {beta_opt:.6f}")
    print(f"  γ (gamma) = {gamma_opt:.6f}")
    print(f"  δ (delta) = {delta_opt:.6f}")
    print(f"\nCross-Validation F1 Score: {best_score:.4f}")
    print(f"\nFull Training Set Metrics:")
    print(f"  Accuracy:  {final_accuracy:.4f}")
    print(f"  Precision: {final_precision:.4f}")
    print(f"  Recall:    {final_recall:.4f}")
    print(f"  F1 Score:  {final_f1:.4f}")
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(labels, pred)
    print(f"  True Negative:  {cm[0,0]:3d}  False Positive: {cm[0,1]:3d}")
    print(f"  False Negative: {cm[1,0]:3d}  True Positive:  {cm[1,1]:3d}")
    
    print("\nClassification Report:")
    print(classification_report(labels, pred, 
                              target_names=['Non-Reactive', 'Reactive'],
                              digits=4))
    
    # Perform cross-validation with final parameters for verification
    print("\n" + "="*50)
    print("CROSS-VALIDATION VERIFICATION (5-fold)")
    print("="*50)
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_accuracies = []
    cv_f1_scores = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X_final, labels), 1):
        X_train, X_val = X_final[train_idx], X_final[val_idx]
        y_train, y_val = labels[train_idx], labels[val_idx]
        
        scaler_cv = StandardScaler()
        X_train_scaled = scaler_cv.fit_transform(X_train)
        X_val_scaled = scaler_cv.transform(X_val)
        
        model_cv = SVC(kernel='rbf', random_state=42)
        model_cv.fit(X_train_scaled, y_train)
        y_pred = model_cv.predict(X_val_scaled)
        
        fold_acc = accuracy_score(y_val, y_pred)
        fold_f1 = f1_score(y_val, y_pred)
        cv_accuracies.append(fold_acc)
        cv_f1_scores.append(fold_f1)
        
        print(f"  Fold {fold}: Accuracy = {fold_acc:.4f}, F1 = {fold_f1:.4f}")
    
    print(f"\nMean CV Accuracy: {np.mean(cv_accuracies):.4f} ± {np.std(cv_accuracies):.4f}")
    print(f"Mean CV F1 Score: {np.mean(cv_f1_scores):.4f} ± {np.std(cv_f1_scores):.4f}")
    
    return {
        'alpha': alpha_opt,
        'beta': beta_opt,
        'gamma': gamma_opt,
        'delta': delta_opt,
        'accuracy': final_accuracy,
        'precision': final_precision,
        'recall': final_recall,
        'f1': final_f1,
        'cv_f1': best_score,
        'model': model,
        'data': data,
        'labels': labels,
        'scaler': scaler,
        'all_results': all_results
    }

def plot_best_classification(results, save_fig=False, fig_name='best_classification.png'):
    """
    Plot the 2D classification results using the optimal parameters
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
    
    plt.figure(figsize=(12, 8))
    
    # Train on 2D features only
    model = SVC(kernel='rbf', random_state=42)
    model.fit(X_scaled[:, :2], labels)
    
    h = 0.02
    x_min, x_max = q_weighted.min() - 0.5, q_weighted.max() + 0.5
    y_min, y_max = clr_weighted.min() - 0.5, clr_weighted.max() + 0.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Scale axes to original values
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
    
    # Show actual 2D accuracy
    accuracy_2d = accuracy_score(labels, predictions)
    precision_2d = precision_score(labels, predictions)
    recall_2d = recall_score(labels, predictions)
    f1_2d = f1_score(labels, predictions)
    
    label_text = (f'$\\times$ Misclassified\n'
                 f'2D Accuracy: {accuracy_2d*100:.1f}%\n'
                 f'F1: {f1_2d:.3f}')
    plt.text(
        x_min + 0.5, y_max - 0.9,
        label_text,
        fontsize=18,
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
    
    print(f"\n2D Classification Metrics (using only q_weighted and clr_weighted):")
    print(f"  Accuracy:  {accuracy_2d:.4f}")
    print(f"  Precision: {precision_2d:.4f}")
    print(f"  Recall:    {recall_2d:.4f}")
    print(f"  F1 Score:  {f1_2d:.4f}")

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
    print(f"\nExpected CV F1 Score: {results['cv_f1']:.4f}")
    print(f"Expected Accuracy: {results['accuracy']:.4f}")

