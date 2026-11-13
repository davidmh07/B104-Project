import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import pyodbc
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

DB_FILE = "XXH2025_YRBS_Data.mdb"   # must be in the same folder as this script
QUERY = "B104_project"
ORDER = ["Never", "Before 13", "13 or older"]

# Each option: (starting substance, other substance)
ANALYSES = {
    "Alcohol start age vs. marijuana": ("Alcohol", "Marijuana"),
    "Marijuana start age vs. alcohol": ("Marijuana", "Alcohol"),
}


def load_data():
    """Load Q40 and Q45 from the saved Access query."""
    folder = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(folder, DB_FILE)
    conn = pyodbc.connect(
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + db_path + ";"
    )
    try:
        return pd.read_sql(f"SELECT Q40, Q45 FROM [{QUERY}]", conn)
    finally:
        conn.close()


def age_group(code):
    """1 = never tried, 2-4 = before 13, 5-7 = 13 or older."""
    if code == 1:
        return "Never"
    return "Before 13" if code <= 4 else "13 or older"


def prepare(df):
    """Clean the data and label each student's start-age group."""
    d = df.apply(pd.to_numeric, errors="coerce").dropna()
    d["Alcohol"] = d["Q40"].apply(age_group)
    d["Marijuana"] = d["Q45"].apply(age_group)
    return d


def run_test(d, first, other):
    """Row percentages and chi-square p-value for first vs. other."""
    counts = pd.crosstab(d[first], d[other]).reindex(index=ORDER, columns=ORDER, fill_value=0)
    pct = (counts.div(counts.sum(axis=1), axis=0) * 100).round(1)
    p = chi2_contingency(counts)[1]
    return pct, p


def plot_bar(d, first, other):
    """Graphic 1: % who ever tried the other substance, by start-age group."""
    pct, p = run_test(d, first, other)
    ever = 100 - pct["Never"]
    ever.plot(kind="bar", color=["tab:gray", "tab:red", "tab:blue"])
    plt.ylabel(f"% who have tried {other.lower()}")
    plt.xlabel(f"When they first tried {first.lower()}")
    plt.title(f"{first} start age vs. ever trying {other.lower()} (p = {p:.4g})")
    plt.xticks(rotation=0)
    plt.show()


def plot_heatmap(d, first, other):
    """Graphic 2: heatmap of start-age groups for both substances."""
    pct, p = run_test(d, first, other)
    plt.imshow(pct, cmap="Blues")
    plt.colorbar(label="% of row")
    plt.xticks(range(3), ORDER)
    plt.yticks(range(3), ORDER)
    for i in range(3):
        for j in range(3):
            plt.text(j, i, f"{pct.iloc[i, j]:.0f}%", ha="center", va="center")
    plt.xlabel(f"{other} start")
    plt.ylabel(f"{first} start")
    plt.title(f"{first} vs. {other} start age")
    plt.show()


def run_analysis():
    """Called by the Run button; window stays open so users can repeat."""
    try:
        first, other = ANALYSES[analysis_box.get()]
        d = prepare(data)
        pct, p = run_test(d, first, other)
        result_label.config(
            text=f"Rows = {first} start, columns = {other} start (% of row)\n"
                 f"{pct.to_string()}\nchi-square p = {p:.4g}\nStudents: {len(d)}"
        )
        if graphic_box.get() == "Bar chart":
            plot_bar(d, first, other)
        else:
            plot_heatmap(d, first, other)
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


try:
    data = load_data()
except Exception as e:
    print("Could not load the database:", e)
    raise SystemExit

root = tk.Tk()
root.title("YRBS: Age of first alcohol and marijuana use")

ttk.Label(root, text="Analysis:").pack(pady=2)
analysis_box = ttk.Combobox(root, values=list(ANALYSES), state="readonly", width=35)
analysis_box.current(0)
analysis_box.pack()

ttk.Label(root, text="Graphic:").pack(pady=2)
graphic_box = ttk.Combobox(root, values=["Bar chart", "Heatmap"], state="readonly", width=35)
graphic_box.current(0)
graphic_box.pack()

ttk.Button(root, text="Run", command=run_analysis).pack(pady=8)
result_label = ttk.Label(root, text="", justify="left")
result_label.pack(padx=10, pady=5)

root.mainloop()