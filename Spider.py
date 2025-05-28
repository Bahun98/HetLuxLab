import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
from utils.street_table import update_street_detail_table
from calc.calculations import generate_data_frames
from utils.scrollable_frame import create_scrollable_frame

df_complete, df_clean, df_missing = generate_data_frames()

wijk_options = sorted(df_complete["WIJK"].dropna().unique())

# GUI root
root = tk.Tk()
root.title("Wijk Spider Web Tool")
# root.geometry("800x600")
root.state('zoomed')
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)

# Main container
main_frame = tk.Frame(root, width=800, height=600)
main_frame.pack(fill="both", expand=True)
main_frame.pack_propagate(False)

# Left frame for dropdown
left_frame = tk.Frame(main_frame, width=200, height=600, bg="lightgray")
left_frame.pack(side="left", fill="y")
left_frame.pack_propagate(False)

# Center frame for spider graph
center_frame = tk.Frame(main_frame, width=400, height=600)
center_frame.pack(side="left", fill="both", expand=True)

# Right frame container (fixed size, no scroll yet)
right_frame_container = tk.Frame(main_frame, width=300, height=600, bg="lightgray")
right_frame_container.pack(side="left", fill="y")
right_frame_container.pack_propagate(False)

# Scrollable frame inside right_frame_container
right_scrollable_frame, right_inner_frame = create_scrollable_frame(right_frame_container)

# Label for wijk selection
label = tk.Label(
    left_frame,
    text="Select a wijk:",
    bg="lightgray",
    font=("Helvetica", 12, "bold"),
    anchor="w"
)
label.pack(side="top", anchor="n", fill="x", padx=10, pady=(10, 0))

# Combobox style
style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox",
    fieldbackground="white",
    background="white",
    foreground="black",
    padding=5,
    relief="flat",
    borderwidth=1
)

# Wijk dropdown
selected_Wijk = tk.StringVar()
dropdown = ttk.Combobox(left_frame, textvariable=selected_Wijk, values=wijk_options, state="readonly")
dropdown.pack(side="top", anchor="n", fill="x", padx=10, pady=10)

# Street listbox with scrollbar
street_scrollbar = ttk.Scrollbar(left_frame, orient="vertical")
street_listbox = tk.Listbox(left_frame, yscrollcommand=street_scrollbar.set, height=20)
street_scrollbar.config(command=street_listbox.yview)

street_listbox.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
street_scrollbar.pack(side="right", fill="y", pady=(0, 10))

# Handle click on radar chart
def on_edge_click(event):
    line = event.artist
    ind = event.ind[0] % len(line.criteria)
    clicked_criteria = line.criteria[ind]
    Wijk_name = line.Wijk
    update_street_detail_table(Wijk_name, df_complete)

# Keep a global canvas reference so we can destroy previous plot
current_canvas = None

def plot_spider_web(criteria, values, title, filtered_df):
    global current_canvas

    # Clear previous canvas and missing data label if any
    for widget in center_frame.winfo_children():
        widget.destroy()

    # Calculate missing percentage
    missing_percent = filtered_df['missing_zero_flag'].mean() * 100 
    total_lamps = len(filtered_df)
    info_str = f"Total Lamps: {total_lamps} - Missing or Zero Data: {missing_percent:.1f}%"

    # Add label above the plot
    missing_label = tk.Label(center_frame, text=info_str, foreground="black", font=("Segoe UI", 10, "italic"), bg="white")
    missing_label.pack(anchor="w", padx=10, pady=(5, 0))

    # Prepare radar chart
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(criteria), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw={'polar': True})
    ax.set_ylim(1, 5)
    line, = ax.plot(angles, values, 'o-', label=title, picker=True)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria)
    ax.set_title(f"{title}")

    # Attach metadata
    line.criteria = criteria
    line.raw_values = values[:-1]
    line.Wijk = title

    # Embed in Tkinter
    current_canvas = FigureCanvasTkAgg(fig, master=center_frame)
    current_canvas.draw()
    current_canvas.get_tk_widget().pack(expand=True, fill='both')

    plt.close()


# When user selects a WIJK from dropdown
def on_Wijk_selected(event):
    wijk = selected_Wijk.get()
    filtered = df_complete[df_complete["WIJK"] == wijk].copy()

    if filtered.empty:
        return

    filtered["Cleaned_Straat"] = (
        filtered["straatnaam+identificatie_mast"]
        .str.extract(r"^([A-Za-zÀ-ÿ'\- ]+)", expand=False)
        .str.strip()
    )
    
    # Store filtered data globally for use by street selection
    global current_filtered_data
    current_filtered_data = filtered

    # Update listbox with cleaned street names
    street_listbox.delete(0, tk.END)
    clean_streets = (
        filtered["Cleaned_Straat"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    clean_streets = clean_streets[clean_streets != ""]

    for straat in sorted(clean_streets.unique()):
        street_listbox.insert(tk.END, straat)

    # Compute WIJK averages
    wijk_averages = filtered[["nature_composite", "humans_composite", "efficiency_composite"]].mean().tolist()
    criteria = ["Nature", "Humans", "Efficiency"]
    plot_spider_web(criteria, wijk_averages, wijk, filtered)

def on_street_selected(event, right_inner_frame):
    selection = street_listbox.curselection()
    if not selection:
        return

    straat = street_listbox.get(selection[0])
    filtered = current_filtered_data[
        current_filtered_data["Cleaned_Straat"] == straat
    ].copy()

    if filtered.empty:
        return

    # Compute spider plot values
    street_averages = filtered[["nature_composite", "humans_composite", "efficiency_composite"]].mean().tolist()
    criteria = ["Nature", "Humans", "Efficiency"]
    plot_spider_web(criteria, street_averages, straat, filtered)

    update_street_detail_table(filtered, right_inner_frame)

dropdown.bind("<<ComboboxSelected>>", on_Wijk_selected)
street_listbox.bind("<<ListboxSelect>>", lambda event: on_street_selected(event, right_inner_frame))

selected_Wijk.set(wijk_options[0])
on_Wijk_selected(None)


def on_closing():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
