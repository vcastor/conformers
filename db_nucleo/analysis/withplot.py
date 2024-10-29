#!/opt/homebrew/bin/python3.9
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from pysr import PySRRegressor

# Function to create PySR model
def create_pysr_model():
    binaryOp = ["plus", "mult", "-", "/", "pow"]
    unitaryOp = ["square", "inv(x)=1/x", "exp", "log", "sqrt", "abs"]
    return PySRRegressor(
        niterations=500,  # Increased iterations
        maxdepth=15,  # Allowing deeper equations for more complexity
        binary_operators=binaryOp,
        unary_operators=unitaryOp,
        extra_sympy_mappings={"inv": lambda x: 1/x},
        populations=50,  # Increased populations for more diversity in candidates
        model_selection='best'
    )

# Load data from SQLite database

db_file_path = '../nucleo_data.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute('''SELECT DISTINCT family FROM main WHERE atom_analysed > 0 AND nconformers not null''')
families = cursor.fetchall()
cursor.execute('''SELECT 
                    experimental_N, experimental_Sn,
                    mu, eta, softness, hyperhardness, omega, nucleofuge, electrofuge, electrodonating, electroaccepting,
                    fplus, fminus, fzero, f2, sfplus, sfminus, sfzero, s2,
                    muplusfplus, muminusfminus, wfplus, wf2, Sf2, s2f2, electro, nucleo,
                    q_qtaim, q_hirshfeld,
                    family
                  FROM main WHERE atom_analysed > 0 AND nconformers not null''')
rawdata = cursor.fetchall()
rawdata = [val for val in rawdata if None not in val]
# Commit the changes and close the connection
conn.commit()
conn.close()

# Converte families to a list
families = [f[0] for f in families]

# Split
data_f = {}
for family in families:
    data_f[family] = [row for row in rawdata if row[-1] == family]

# Model for apliphatic amines and pyridines quinine
ali_py = [data_f['aliphatic_amines'], data_f['pyridines_quinolines_etc']]
n_exp = np.array([val[0] for val in ali_py[0]])
sn_exp = np.array([val[1] for val in ali_py[0]])
X = np.array([val[2:-1] for val in ali_py[0]])
nsn = n_exp*sn_exp
# Targets
targets = {'N': n_exp, 'Sn': sn_exp, 'N*Sn': nsn}
fig, ax = plt.subplots(1, 3, figsize=(15, 5))
for i, (target, y) in enumerate(targets.items()):
    print(f'Predicting {target}:\n')
    model = create_pysr_model()
    model.fit(X, y)
    # Display best three equations
    print('Top 3 equations:')
    top_eqs = model.equations_.sort_values('score', ascending=False).head(3)
    for j, eq in top_eqs.iterrows():
        print(f'{j+1}. {eq["equation"]}')
    # Predictions and MAE calculation
    pred = model.predict(X)
    mae = np.absolute(pred - y).mean()
    print(f'MAE: {mae}\n')
    # Plot Experimental vs. Predicted values
    ax[i].scatter(y, pred, label="Predicted vs. Experimental", color="blue")
    ax[i].plot([min(y), max(y)], [min(y), max(y)], color='red', label="y=x")
    ax[i].set_xlabel(f'Experimental {target}')
    ax[i].set_ylabel(f'Predicted {target}')
    ax[i].legend()
    ax[i].set_title(f'Experimental vs. Predicted {target}')
    plt.tight_layout()
    plt.show()

quit()# Stop here FOR NOW

# Model for every family
for family in families:
    print(f'Family: {family}')
    filtered_data = data_f[family]

    # Prepare data for regression
    n_exp = np.array([val[0] for val in filtered_data])
    sn_exp = np.array([val[1] for val in filtered_data])
    X = np.array([val[2:-1] for val in filtered_data])
    nsn = n_exp*sn_exp
    # Targets
    targets = {'N': n_exp, 'Sn': sn_exp, 'N*Sn': nsn}

    # Create plot for every family
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))

    # Loop over targets
    for i, (target, y) in enumerate(targets.items()):
        print(f'Predicting {target}:\n')
        model = create_pysr_model()
        # model = PySRRegressor()
        model.fit(X, y)

        # Display best three equations
        print('Top 3 equations:')
        top_eqs = model.equations_.sort_values('score', ascending=False).head(3)
        for j, eq in top_eqs.iterrows():
            print(f'{j+1}. {eq["equation"]}')

        # Predictions and MAE calculation
        pred = model.predict(X)
        mae = np.absolute(pred - y).mean()
        print(f'MAE: {mae}\n')

        # Plot Experimental vs. Predicted values
        ax[i].scatter(y, pred, label="Predicted vs. Experimental", color="blue")
        ax[i].plot([min(y), max(y)], [min(y), max(y)], color='red', label="y=x")
        ax[i].set_xlabel(f'Experimental {target}')
        ax[i].set_ylabel(f'Predicted {target}')
        ax[i].legend()
        ax[i].set_title(f'Experimental vs. Predicted {target}')
    plt.tight_layout()
    # plt.savefig(f'{family}_plot.pdf')

