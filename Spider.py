import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the Excel file
file_path = 'data_quality_kleurtemperatuur1.xlsm'
data = pd.read_excel(file_path, sheet_name='Main_data')

# Average per WIJK
average_data = data.groupby('WIJK')[["Nature", "Human", "Efficiency"]].mean().reset_index()
wijken = list(average_data["WIJK"].unique())

# GUI root
root = tk.Tk()
root.title("Wijk Spider Web Tool")
root.geometry("300x150")

label = tk.Label(root, text="Select a WIJK:")
label.pack(pady=10)

selected_Wijk = tk.StringVar()
dropdown = ttk.Combobox(root, textvariable=selected_Wijk, values=wijken, state="readonly")
dropdown.pack()


def show_detail_table(Wijk, _):
    filtered = data[data["WIJK"] == Wijk].copy()

    if filtered.empty:
        return

    # Compute derived metrics
    filtered["Lumen_per_m2"] = filtered["LUMEN_LAMP"] / (filtered["LPH_ARMATUUR"] * 16)
    filtered["Composite_Score"] = (
        filtered["CK_IN_KELVIN"] + filtered["LPH_ARMATUUR"] + filtered["Lumen_per_m2"]
    ) / 3

    # Group by street and aggregate
    grouped = filtered.groupby("STRAATNAAM").agg({
        "CK_IN_KELVIN": ["median", "var"],
        "LPH_ARMATUUR": ["median", "var"],
        "Lumen_per_m2": "mean",
        "Composite_Score": "mean"
    }).reset_index()

    # Rename and flatten columns
    grouped.columns = [
        "Street",
        "Color Temperature Median",
        "Variance CT",
        "Pole Height Median",
        "Variance PH",
        "Lumen per m²",
        "Composite Score"
    ]

    grouped = grouped.round(2)
    grouped = grouped.fillna(0)  # Replace NaNs with 0

    # Create popup window
    win = tk.Toplevel()
    
    # Dynamic sizing
    row_height = 25
    num_rows = len(grouped)
    height = min(600, max(200, row_height * (num_rows + 2)))
    width = 180 * len(grouped.columns)
    win.geometry(f"{width}x{height}")

    win.title(f"{Wijk} - Per Street Summary")

    columns = list(grouped.columns)
    tree = ttk.Treeview(win, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')

    for _, row in grouped.iterrows():
        tree.insert("", "end", values=list(row))

    # Vertical scrollbar
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    tree.pack(fill='both', expand=True, padx=10, pady=10)



# Handle click on radar chart
def on_edge_click(event):
    line = event.artist
    ind = event.ind[0] % len(line.criteria)
    clicked_criteria = line.criteria[ind]
    Wijk_name = line.Wijk
    show_detail_table(Wijk_name, clicked_criteria)

# Plot radar chart
def plot_spider_web(criteria, values, Wijk_name):
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(criteria), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw={'polar': True})
    line, = ax.plot(angles, values, 'o-', label=Wijk_name, picker=True)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria)
    ax.set_title(f"{Wijk_name} - Criteria Overview")

    # Attach metadata
    line.criteria = criteria
    line.raw_values = values[:-1]
    line.Wijk = Wijk_name

    fig.canvas.mpl_connect('pick_event', on_edge_click)
    plt.show()

# When user selects a WIJK from dropdown
def on_Wijk_selected(event):
    Wijk = selected_Wijk.get()
    df = average_data[average_data["WIJK"] == Wijk]
    if df.empty:
        return
    values = df[["Nature", "Human", "Efficiency"]].values.flatten().tolist()
    criteria = ["Nature", "Human", "Efficiency"]
    plot_spider_web(criteria, values, Wijk)

dropdown.bind("<<ComboboxSelected>>", on_Wijk_selected)

# Run GUI
root.mainloop()
