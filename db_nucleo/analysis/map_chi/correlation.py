#!/usr/bin/python3
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr

conn = sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db')

# Query data where both columns are not null
query = """
SELECT eigenchi, condensed_linear_response 
FROM reactive 
WHERE eigenchi IS NOT NULL AND condensed_linear_response IS NOT NULL
"""

df = pd.read_sql_query(query, conn)
conn.close()

# Extract data
x = df['eigenchi'].values
y = df['condensed_linear_response'].values

# Compute correlation and R^2
r, p_value = pearsonr(x, y)
r_squared = r**2

# Plot
plt.figure(figsize=(8, 6))
plt.scatter(x, y, alpha=0.6)
plt.xlabel(r'$\chi$ eigenvalue')
plt.ylabel(r'$\chi$')
plt.title(f'Correlation: r = {r:.4f}, R² = {r_squared:.4f}')

# Add trend line
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x, p(x), "r--", alpha=0.8)

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print(f"Sample size: {len(x)}")
print(f"Correlation coefficient: {r:.6f}")
print(f"R-squared: {r_squared:.6f}")
print(f"P-value: {p_value:.6e}")

