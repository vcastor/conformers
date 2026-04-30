#!/usr/bin/python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.svm import SVC
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

def prepare_data(react_data, noreact_data):
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
    labels = np.array([1] * n_react + [0] * n_noreact)
    
    return combined_data, labels

def compute_weighted_features(data, alpha, beta):
    """
    Simplified version without gamma and delta scaling
    q_weighted   = Σ exp(-α*distance)*q_atom
    clr_weighted = Σ exp(-β*distance)*clr_atom
    """
    n_molecules = len(data["natoms"])
    features = []
    
    for i in range(n_molecules):
        distances = np.array(data["distances"][i])
        q_qtaim = np.array(data["q_qtaim"][i])
        clr = np.array(data["clr"][i])
        
        weights_q   = np.exp(-alpha*distances)
        weights_clr = np.exp(-beta*distances)
        
        q_weighted   = np.sum(weights_q*q_qtaim)
        clr_weighted = np.sum(weights_clr*clr)
        
        features.append([
            q_weighted,
            clr_weighted,
            data["expN"][i],
            data["expSn"][i]
        ])
    
    return np.array(features)

def evaluate_parameters(alpha, beta, data, labels):
    """
    Evaluate classification accuracy for given alpha and beta
    """
    X = compute_weighted_features(data, alpha, beta)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = SVC(kernel='rbf', random_state=42)
    model.fit(X_scaled, labels)
    
    pred = model.predict(X_scaled)
    accuracy = accuracy_score(labels, pred)
    
    return accuracy

def grid_scan_analysis(react_data, noreact_data, alpha_range=None, beta_range=None, n_points=20):
    """
    Perform grid scan over alpha and beta parameters
    """
    print("Starting grid scan analysis...")
    print("-" * 50)
    
    data, labels = prepare_data(react_data, noreact_data)
    
    # Default ranges if not provided
    if alpha_range is None:
        alpha_range = (0.01, 4.0)
    if beta_range is None:
        beta_range = (0.01, 4.0)
    
    # Create grid
    alphas = np.linspace(alpha_range[0], alpha_range[1], n_points)
    betas = np.linspace(beta_range[0], beta_range[1], n_points)
    
    # Initialize accuracy matrix
    accuracy_matrix = np.zeros((n_points, n_points))
    
    # Compute accuracy for each combination
    best_acc = 0
    best_alpha = None
    best_beta = None
    
    print(f"Scanning {n_points}x{n_points} = {n_points**2} parameter combinations...")
    
    for i, alpha in enumerate(alphas):
        for j, beta in enumerate(betas):
            acc = evaluate_parameters(alpha, beta, data, labels)
            accuracy_matrix[i, j] = acc
            
            if acc > best_acc:
                best_acc = acc
                best_alpha = alpha
                best_beta = beta
        
        # Progress indicator
        if (i+1) % 5 == 0:
            print(f"  Completed {i+1}/{n_points} alpha values...")
    
    print("\nBest parameters found:")
    print(f"  α = {best_alpha:.4f}")
    print(f"  β = {best_beta:.4f}")
    print(f"  Accuracy = {best_acc:.4f}")
    
    return {
        'alphas': alphas,
        'betas': betas,
        'accuracy_matrix': accuracy_matrix,
        'best_alpha': best_alpha,
        'best_beta': best_beta,
        'best_accuracy': best_acc,
        'data': data,
        'labels': labels
    }

def plot_accuracy_heatmap(results, save_fig=False, fig_name='accuracy_heatmap.png'):
    """
    Create heatmap and contour plot of accuracy vs alpha and beta
    """
    alphas = results['alphas']
    betas = results['betas']
    accuracy_matrix = results['accuracy_matrix']
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Heatmap
    ax1 = axes[0]
    im = ax1.imshow(accuracy_matrix.T, origin='lower', aspect='auto', 
                    extent=[alphas[0], alphas[-1], betas[0], betas[-1]],
                    cmap='viridis', interpolation='bilinear')
    
    # Mark best point
    ax1.plot(results['best_alpha'], results['best_beta'], 'r*', 
             markersize=15, markeredgecolor='white', markeredgewidth=1)
    
    ax1.set_xlabel(r'$\alpha$ (q decay)', fontsize=14)
    ax1.set_ylabel(r'$\beta$ (CLR decay)', fontsize=14)
    ax1.set_title('Accuracy Heatmap', fontsize=16, fontweight='bold')
    
    cbar = plt.colorbar(im, ax=ax1)
    cbar.set_label('Accuracy', fontsize=12)
    
    # Contour plot
    ax2 = axes[1]
    X, Y = np.meshgrid(alphas, betas)
    contour = ax2.contour(X, Y, accuracy_matrix.T, levels=15, colors='black', alpha=0.4, linewidths=0.5)
    contourf = ax2.contourf(X, Y, accuracy_matrix.T, levels=20, cmap='viridis')
    
    ax2.clabel(contour, inline=True, fontsize=8, fmt='%.3f')
    ax2.plot(results['best_alpha'], results['best_beta'], 'r*', 
             markersize=15, markeredgecolor='white', markeredgewidth=1)
    
    ax2.set_xlabel(r'$\alpha$ (q decay)', fontsize=14)
    ax2.set_ylabel(r'$\beta$ (CLR decay)', fontsize=14)
    ax2.set_title('Accuracy Contours', fontsize=16, fontweight='bold')
    
    plt.colorbar(contourf, ax=ax2, label='Accuracy')
    
    # Add best point annotation
    for ax in axes:
        ax.annotate(f'Best: ({results["best_alpha"]:.3f}, {results["best_beta"]:.3f})\nAcc: {results["best_accuracy"]:.4f}',
                   xy=(results['best_alpha'], results['best_beta']),
                   xytext=(results['best_alpha'] + 0.3, results['best_beta'] + 0.3),
                   arrowprops=dict(arrowstyle='->', color='red', lw=2),
                   fontsize=10, color='red',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    if save_fig:
        plt.savefig(fig_name, dpi=300, bbox_inches='tight')
        print(f"\nFigure saved as '{fig_name}'")
    
    plt.show()

def plot_1d_scans(results, save_fig=False, fig_name='1d_scans.png'):
    """
    Plot 1D scans: accuracy vs alpha (at best beta) and accuracy vs beta (at best alpha)
    """
    alphas = results['alphas']
    betas = results['betas']
    accuracy_matrix = results['accuracy_matrix']
    
    # Find indices of best parameters
    best_alpha_idx = np.argmin(np.abs(alphas - results['best_alpha']))
    best_beta_idx = np.argmin(np.abs(betas - results['best_beta']))
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Alpha scan at best beta
    ax1 = axes[0]
    ax1.plot(alphas, accuracy_matrix[:, best_beta_idx], 'b-', linewidth=2, label=f'β = {results["best_beta"]:.3f}')
    ax1.axvline(results['best_alpha'], color='r', linestyle='--', alpha=0.7, label='Optimal α')
    ax1.set_xlabel(r'$\alpha$ (q decay)', fontsize=14)
    ax1.set_ylabel('Accuracy', fontsize=14)
    ax1.set_title(r'Accuracy vs $\alpha$ (at optimal $\beta$)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Beta scan at best alpha
    ax2 = axes[1]
    ax2.plot(betas, accuracy_matrix[best_alpha_idx, :], 'g-', linewidth=2, label=f'α = {results["best_alpha"]:.3f}')
    ax2.axvline(results['best_beta'], color='r', linestyle='--', alpha=0.7, label='Optimal β')
    ax2.set_xlabel(r'$\beta$ (CLR decay)', fontsize=14)
    ax2.set_ylabel('Accuracy', fontsize=14)
    ax2.set_title(r'Accuracy vs $\beta$ (at optimal $\alpha$)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    
    if save_fig:
        plt.savefig(fig_name, dpi=300, bbox_inches='tight')
        print(f"Figure saved as '{fig_name}'")
    
    plt.show()

def analyze_parameter_sensitivity(results):
    """
    Analyze sensitivity of accuracy to parameter changes
    """
    accuracy_matrix = results['accuracy_matrix']
    alphas = results['alphas']
    betas = results['betas']
    
    # Calculate gradients
    grad_alpha, grad_beta = np.gradient(accuracy_matrix, alphas[1]-alphas[0], betas[1]-betas[0])
    
    # Find regions of high sensitivity
    sensitivity = np.sqrt(grad_alpha**2 + grad_beta**2)
    
    print("\n" + "="*50)
    print("PARAMETER SENSITIVITY ANALYSIS")
    print("="*50)
    
    print(f"\nAccuracy range: [{accuracy_matrix.min():.4f}, {accuracy_matrix.max():.4f}]")
    print(f"Mean accuracy: {accuracy_matrix.mean():.4f} ± {accuracy_matrix.std():.4f}")
    
    # Find robust region (low sensitivity, high accuracy)
    high_acc_threshold = results['best_accuracy'] - 0.01  # Within 1% of best
    high_acc_mask = accuracy_matrix > high_acc_threshold
    
    if np.any(high_acc_mask):
        robust_alphas = []
        robust_betas = []
        for i in range(len(alphas)):
            for j in range(len(betas)):
                if high_acc_mask[i, j]:
                    robust_alphas.append(alphas[i])
                    robust_betas.append(betas[j])
        
        print(f"\nRobust parameter region (accuracy > {high_acc_threshold:.4f}):")
        print(f"  α range: [{min(robust_alphas):.3f}, {max(robust_alphas):.3f}]")
        print(f"  β range: [{min(robust_betas):.3f}, {max(robust_betas):.3f}]")
    
    # Find most sensitive point
    max_sens_idx = np.unravel_index(np.argmax(sensitivity), sensitivity.shape)
    print(f"\nMost sensitive point:")
    print(f"  α = {alphas[max_sens_idx[0]]:.3f}, β = {betas[max_sens_idx[1]]:.3f}")
    print(f"  Sensitivity = {sensitivity[max_sens_idx]:.6f}")

# Main execution
if __name__ == "__main__":
    # Read data
    react_data = read_react('reactive.pout')
    noreact_data = read_noreact('no_reactive.pout')
    
    # Perform grid scan
    results = grid_scan_analysis(
        react_data, 
        noreact_data,
        alpha_range=(0.01, 4.0),
        beta_range=(0.01, 4.0),
        n_points=50  # Increase for finer resolution
    )
    
    # Visualize results
    plot_accuracy_heatmap(results, save_fig=True)
    plot_1d_scans(results, save_fig=True)
    
    # Analyze sensitivity
    analyze_parameter_sensitivity(results)
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    print(f"Optimal parameters for classification:")
    print(f"  q_weighted   = Σ exp(-{results['best_alpha']:.4f} * distance) * q_atom")
    print(f"  clr_weighted = Σ exp(-{results['best_beta']:.4f} * distance) * clr_atom")
    print(f"  Best accuracy: {results['best_accuracy']:.4f}")

