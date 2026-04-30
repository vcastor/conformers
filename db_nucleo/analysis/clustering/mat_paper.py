#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from castor_functions import *

# ----------------------------
# Config
# ----------------------------
exp  = ['experimental_N', 'experimental_Sn']
cols = [ 
    'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
    'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
    'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
    'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
    'condensed_linear_response', 'P', 'Pf2'
]

# Preferred (manual) labels — these take precedence
label_map = {
    'mu':       r'$\mu$',
    'eta':      r'$\eta$',
    'softness': r'$S$',
    'hyperhardness': r'$\gamma$',
    'omega':         r'$\omega$',
    'nucleofuge':    'nucleofuge',
    'electrofuge':   'e fuge',
    'electrodonating': 'e donating',
    'electroaccepting': 'e accepting',
    'fplus': r'$f^+$',
    'fminus': r'$f^-$',
    'fzero': r'$f^0$',
    'f2': r'$f^2$',
    'sfplus': r'$sf^+$',
    'sfminus': r'$sf^-$',
    'sfzero': r'$sf^0$',
    's2': r'$s^2$',
    'muplusfplus': r'$\mu^+ f^+$',
    'muminusfminus': r'$\mu^- f^-$',
    'wfplus': r'$w^+$',
    'wf2': r'$w^2$',
    'Sf2': r'$S^2$',
    's2f2': r'$S^2 f^2$',
    'nucleo': 'nucleophilicity',
    'q_qtaim': r'$q_{QTAIM}$',
    'q_hirshfeld': r'$q_{Hirshfeld}$',
    'electrostatic_potential': 'ESP',
    'condensed_linear_response': r'$\chi(N)$',
    'P': r'$P$',
    'Pf2': r'$Pf^2$',
    'experimental_N': r'$N_{Mayr}$',
    'experimental_Sn': r'$Sn_{Mayr}$'
}

# ----------------------------
# Helper: auto-short labels
# ----------------------------
def auto_shorten(name: str) -> str:
    """Shorten a snake_case/camel name conservatively for axis labels.
    Rules:
      - If in label_map: keep it (handled outside).
      - If name is long (>12 chars), use acronym of parts (uppercased).
      - Else, use a neat title-case with spaces.
    """
    # already math/latex → keep as is
    if name.startswith('$') and name.endswith('$'):
        return name

    base = name.replace('-', '_')
    parts = [p for p in base.split('_') if p]

    # If very long or many parts → acronym
    if len(name) > 12 or len(parts) >= 3:
        # keep digits and first letter of each part
        acronym = ''.join(''.join(ch for ch in p if ch.isalpha())[:1].upper() + ''.join(ch for ch in p if ch.isdigit()) for p in parts)
        # fallback if acronym too short
        if len(acronym) < 2:
            acronym = name[:3].upper()
        return acronym

    # Otherwise a clean title
    return ' '.join(parts).title() if parts else name

def build_display_labels(columns, label_map):
    disp = {}
    for c in columns:
        if c in label_map:
            disp[c] = label_map[c]
        else:
            disp[c] = auto_shorten(c)
    return disp

# ----------------------------
# Data
# ----------------------------
df = connect_db(exp, cols)
for drop_col in ('smiles', 'solvent', 'atom_analysed', 'source'):
    if drop_col in df.columns:
        df = df.drop(drop_col, axis=1)

# Keep only the columns we want (and present)
want = [c for c in exp + cols if c in df.columns]
df = df[want]

# Correlation matrix (ensure same order on both axes)
corr_matrix = df.corr().loc[want, want]

# ----------------------------
# Report top correlations with experimental targets
# ----------------------------
for expval in exp:
    if expval in corr_matrix.columns:
        top_correlations = (
            corr_matrix[expval]
            .dropna()
            .sort_values(ascending=False)
            .head(5)
        )
        print(f"Top 5 most positively correlated with {expval}:")
        print(top_correlations, "\n")

# ----------------------------
# Heatmap with alternating ticks (complementary X/Y)
# ----------------------------
display_labels = build_display_labels(corr_matrix.columns.tolist(), label_map)

# Relabel the matrix for plotting (copy to avoid mutating original)
plot_matrix = corr_matrix.rename(index=display_labels, columns=display_labels)

plt.figure(figsize=(14, 12))
ax = sns.heatmap(
    plot_matrix,
    annot=False,
    cmap='coolwarm',
    center=0,
    linewidths=0.5,
    square=True
)
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(labelsize=22)

# Pull the labels seaborn placed
x_orig = [t.get_text() for t in ax.get_xticklabels()]
y_orig = [t.get_text() for t in ax.get_yticklabels()]

# Alternate: even indices on X, odd indices on Y (complementary)
x_labels = [lab if i % 2 == 0 else "" for i, lab in enumerate(x_orig)]
y_labels = [lab if i % 2 == 1 else "" for i, lab in enumerate(y_orig)]

# Apply labels (rotate X for space)
ax.set_xticklabels(x_labels, rotation=90, ha='center', fontsize=28)
ax.set_yticklabels(y_labels, rotation=0, va='center', fontsize=28)

plt.title("Correlation Matrix Heatmap", fontsize=34, pad=12)
plt.tight_layout()
# plt.savefig('heatmap.pdf', bbox_inches='tight')
plt.show()

# ----------------------------
# If you want to flip which side shows more labels, swap parity:
# x_labels = [lab if i % 2 == 1 else "" for i, lab in enumerate(x_orig)]
# y_labels = [lab if i % 2 == 0 else "" for i, lab in enumerate(y_orig)]

