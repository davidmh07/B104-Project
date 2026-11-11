import os
import pandas as pd
import pyodbc

db_path = os.path.abspath(r"XXH2025_YRBS_Data.mdb")
conn = pyodbc.connect(
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + db_path + ";"
)
cursor = conn.cursor()

# List what's inside the database
table_names = [row.table_name for row in cursor.tables(tableType="TABLE")]
query_names = [row.table_name for row in cursor.tables(tableType="VIEW")]
print("Tables:", table_names)
print("Saved queries:", query_names)

# Load each table into a DataFrame, stored in a dictionary
dfs = {name: pd.read_sql(f"SELECT * FROM [{name}]", conn) for name in table_names}

# Load a saved query the same way (replace with the real query name)
# query_df = pd.read_sql("SELECT * FROM [YourQueryName]", conn)

# Preview the first table
first = table_names[0]
print(dfs[first].head())

conn.close()

import itertools
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, chi2_contingency

df = dfs["XXHq"]

qs = ["q40", "q45", "q62", "q83"]
missing = [q for q in qs if q not in df.columns]
print("Missing columns:", missing)

data = df[qs].apply(pd.to_numeric, errors="coerce").dropna()
print("Respondents with all four answered:", len(data))

# Correlation matrix
corr = data.corr(method="spearman")
print("\nSpearman correlation matrix:\n", corr.round(3))

plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar(label="Spearman rho")
plt.xticks(range(len(qs)), qs)
plt.yticks(range(len(qs)), qs)
for i in range(len(qs)):
    for j in range(len(qs)):
        plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
plt.title("Correlation between questions")
plt.show()

# Pairwise summary table
rows = []
for a, b in itertools.combinations(qs, 2):
    pair = df[[a, b]].apply(pd.to_numeric, errors="coerce").dropna()
    rho, p = spearmanr(pair[a], pair[b])
    chi_p = chi2_contingency(pd.crosstab(pair[a], pair[b]))[1]
    rows.append({"pair": f"{a} vs {b}", "n": len(pair),
                 "rho": round(rho, 3), "p_value": p, "chi2_p": chi_p})
summary = pd.DataFrame(rows).sort_values("rho", key=abs, ascending=False)
print("\nPairwise summary:\n", summary.to_string(index=False))

# Row-percentage crosstabs to see where the differences are
for a, b in itertools.combinations(qs, 2):
    pair = df[[a, b]].apply(pd.to_numeric, errors="coerce").dropna()
    print(f"\n=== {a} (rows) vs {b} (columns), row % ===")
    print((pd.crosstab(pair[a], pair[b], normalize="index") * 100).round(1))

# Average answers on the other questions, split by q40 response
print("\nMean of other questions by q40 answer:")
print(data.groupby("q40")[qs[1:]].mean().round(2))

summary.to_csv("pairwise_summary.csv", index=False)
corr.to_csv("correlation_matrix.csv")



