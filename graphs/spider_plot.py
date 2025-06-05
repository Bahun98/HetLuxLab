# plotting/spider_plot.py

import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from utils.street_table import update_street_detail_table

def plot_spider_web(criteria, values, title, filtered_df, target_frame):
    # Clear previous canvas and missing data label if any
    for widget in target_frame.winfo_children():
        widget.destroy()

    # Calculate missing percentage
    missing_percent = filtered_df['missing_zero_flag'].mean() * 100 
    total_lamps = len(filtered_df)
    info_str = f"Total Lamps: {total_lamps} - Missing or Zero Data: {missing_percent:.1f}%"

    # Add label above the plot
    missing_label = tk.Label(target_frame, text=info_str, foreground="black", font=("Segoe UI", 10, "italic"), bg="white")
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
    canvas = FigureCanvasTkAgg(fig, master=target_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill='both')

    plt.close()



# Global for currently filtered data
current_filtered_data = pd.DataFrame()


def on_edge_click(event, df_complete):
    line = event.artist
    ind = event.ind[0] % len(line.criteria)
    Wijk_name = line.Wijk
    update_street_detail_table(Wijk_name, df_complete)


def on_wijk_selected(event, selected_wijk, df_complete, street_listbox, center_frame, plot_spider_web):
    global current_filtered_data

    wijk = selected_wijk.get()
    filtered = df_complete[df_complete["WIJK"] == wijk].copy()
    if filtered.empty:
        return

    filtered["Cleaned_Straat"] = (
        filtered["straatnaam+identificatie_mast"]
        .str.extract(r"^([A-Za-zÀ-ÿ'\- ]+)", expand=False)
        .str.strip()
    )
    current_filtered_data = filtered

    # Update listbox
    street_listbox.delete(0, 'end')
    clean_streets = filtered["Cleaned_Straat"].dropna().astype(str).str.strip()
    clean_streets = clean_streets[clean_streets != ""]

    for straat in sorted(clean_streets.unique()):
        street_listbox.insert('end', straat)

    wijk_averages = filtered[["nature_composite", "humans_composite", "efficiency_composite"]].mean().tolist()
    criteria = ["Nature", "Humans", "Efficiency"]
    plot_spider_web(criteria, wijk_averages, wijk, filtered, center_frame)


def on_street_selected(event, street_listbox, right_inner_frame, center_frame, plot_spider_web):
    selection = street_listbox.curselection()
    if not selection:
        return

    straat = street_listbox.get(selection[0])
    filtered = current_filtered_data[current_filtered_data["Cleaned_Straat"] == straat].copy()
    if filtered.empty:
        return

    street_averages = filtered[["nature_composite", "humans_composite", "efficiency_composite"]].mean().tolist()
    criteria = ["Nature", "Humans", "Efficiency"]
    plot_spider_web(criteria, street_averages, straat, filtered, center_frame)

    update_street_detail_table(filtered, right_inner_frame)