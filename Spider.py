import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

# TODO add real data sheet.

file_path = 'data_quality_kleurtemperatuur1.xlsm'
# file_path = 'data_quality_kleurtemperatuur2.xlsx'
data = pd.read_excel(file_path, sheet_name='Main_data')

# Average per WIJK
average_data = data.groupby('WIJK')[["Nature", "Human", "Efficiency"]].mean().reset_index()

# At startup
wijken = sorted(data["WIJK"].dropna().unique())

# GUI root
root = tk.Tk()
root.title("Wijk Spider Web Tool")
root.geometry("800x600")
# root.resizable(False, False) # Uncomment this to force the app to be unresizable

# Main container
main_frame = tk.Frame(root, width=800, height=600)
main_frame.pack(fill="both", expand=True)
main_frame.pack_propagate(False)

# Left frame for dropdown
left_frame = tk.Frame(main_frame, width=200, height=600, bg="lightgray")
left_frame.pack(side="left", fill="y")
left_frame.pack_propagate(False)

# Right frame for graphs
right_frame = tk.Frame(main_frame, width=600, height=600)
right_frame.pack(side="right", fill="both", expand=True)


# Label for wijk selectiion
label = tk.Label(
    left_frame,
    text="Select a wijk:",
    bg="lightgray",          # Match left_frame background
    font=("Helvetica", 12, "bold"),  # Customize font and size
    anchor="w"             # Align text to the left (optional)
)
label.pack(side="top", anchor="n", fill="x", padx=10, pady=(10, 0))


# Dropdown for wijk selection and some styling

style = ttk.Style()
style.theme_use("clam")  # Use a better-looking theme

style.configure("TCombobox",
    fieldbackground="white",     # Background of the entry
    background="white",          # Background when clicked
    foreground="black",          # Text color
    padding=5,
    relief="flat",               # Flat like modern web menus
    borderwidth=1
)

selected_Wijk = tk.StringVar()
dropdown = ttk.Combobox(left_frame, textvariable=selected_Wijk, values=wijken, state="readonly")
dropdown.pack(side="top", anchor="n", fill="x", padx=10, pady=10)

# Scrollbar + Listbox for streets
street_scrollbar = ttk.Scrollbar(left_frame, orient="vertical")
street_listbox = tk.Listbox(left_frame, yscrollcommand=street_scrollbar.set, height=20)

street_scrollbar.config(command=street_listbox.yview)

# Pack both so scrollbar is beside listbox
street_listbox.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
street_scrollbar.pack(side="right", fill="y", pady=(0, 10))

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

# Keep a global canvas reference so we can destroy previous plot
current_canvas = None

# Plot radar chart
def plot_spider_web(criteria, values, title):
    global current_canvas

    # Clear previous plot widget (if any)
    for widget in right_frame.winfo_children():
        widget.destroy()


    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(criteria), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw={'polar': True})
    line, = ax.plot(angles, values, 'o-', label=title, picker=True)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria)
    ax.set_title(f"{title} - Criteria Overview")

    # Attach metadata
    line.criteria = criteria
    line.raw_values = values[:-1]
    line.Wijk = title


    # Embed in right frame
    current_canvas = FigureCanvasTkAgg(fig, master=right_frame)
    current_canvas.draw()
    current_canvas.get_tk_widget().pack(expand=True, fill='both')

def extract_street_name(full_str):
    return re.sub(r'\d+$', '', full_str).strip()

# When user selects a WIJK from dropdown
def on_Wijk_selected(event):
    Wijk = selected_Wijk.get()
    filtered = data[data["WIJK"] == Wijk].copy()

    if filtered.empty:
        return

    df = average_data[average_data["WIJK"] == Wijk]
    if df.empty:
        return
    
    values = df[["Nature", "Human", "Efficiency"]].values.flatten().tolist()
    criteria = ["Nature", "Human", "Efficiency"]
    plot_spider_web(criteria, values, Wijk)

    streets_raw = data [data["WIJK"] == Wijk]["straatnaam+identificatie_mast"].dropna().unique()
    # We extract the unique ID from the streetname to group by streets.
    streets = sorted([extract_street_name(s) for s in streets_raw])
    street_listbox.delete(0, tk.END)  
    for street in streets:
        street_listbox.insert(tk.END, street)

def on_street_selected(event):
    selection = street_listbox.curselection()
    if not selection:
        return
    street = street_listbox.get(selection[0])

    # Filter original data for that street (ignoring unique ID)
    filtered_street_data = data[data["straatnaam+identificatie_mast"].str.contains(street)]

    if filtered_street_data.empty:
        return

    avg_values = filtered_street_data[["Nature", "Human", "Efficiency"]].mean().tolist()
    criteria = ["Nature", "Human", "Efficiency"]

    plot_spider_web(criteria, avg_values, f"Street: {street}")

dropdown.bind("<<ComboboxSelected>>", on_Wijk_selected)
street_listbox.bind("<<ListboxSelect>>", on_street_selected)

# Run GUI
root.mainloop()
