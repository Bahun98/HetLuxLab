# plotting/spider_plot.py

import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from utils.street_table import update_street_detail_table
from utils.aggregate_values import show_aggregated_values


def plot_spider_web(criteria, values, title, filtered_df, target_frame):
    print(f"plot_spider_web called with target_frame: {target_frame}")
    # Clear previous canvas and missing data label if any
    for widget in target_frame.winfo_children():
        print(f"Destroying widget: {widget}")
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

    for i, angle in enumerate(angles[:-1]):  # Skip the duplicated last point
        value = values[i]
        # Adjust position slightly outward for readability
        x = angle
        y = value + 0.1
        ax.text(
            angle,
            value + 0.1,
            f"{value:.1f}",
            ha='center',
            va='center',
            fontsize=12,
            color='black',
            bbox=dict(
                facecolor='white',
                alpha=0.8,      # Transparency: 0.0 (fully transparent) to 1.0 (opaque)
                edgecolor='none',
                boxstyle='round,pad=0.2'
            )
        )

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


def on_edge_click(event, df_complete, detail_frame):
    line = event.artist
    Wijk_name = line.Wijk
    filtered = df_complete[df_complete["WIJK"] == Wijk_name]
    update_street_detail_table(filtered, detail_frame)

def on_wijk_selected(event, selected_wijk, df_complete, street_listbox, center_frame, plot_spider_web, aggregate_frame, street_list_frame):
    global current_filtered_data
    import utils.state as state
    state.suppress_next_listbox_select = True

    print(f"On_wijk_selected got called: {selected_wijk.get()}")
    wijk = selected_wijk.get()
    filtered = df_complete[df_complete["WIJK"] == wijk].copy()
    if filtered.empty:
        return

    # Update listbox
    street_listbox.delete(0, 'end')
    clean_streets = filtered["STRAATNAAM"].dropna().astype(str).str.strip()
    clean_streets = clean_streets[clean_streets != ""]

    for straat in sorted(clean_streets.unique()):
        street_listbox.insert('end', straat)

    wijk_averages = filtered[["nature_composite", "humans_composite", "efficiency_composite"]].mean().tolist()
    criteria = ["Nature", "Humans", "Efficiency"]
    plot_spider_web(criteria, wijk_averages, wijk, filtered, center_frame)

    
    show_aggregated_values(filtered, aggregate_frame)
    update_street_detail_table(filtered, street_list_frame)

def on_street_selected(
    straat,
    street_list_frame,
    center_frame,
    plot_spider_web,
    aggregate_frame,
    dataframe  # remove default None to force explicit data passing
):
    print(f"On_street_selected got called: {straat}")

    if dataframe is None:
        print("Error: dataframe must be provided to on_street_selected")
        return

    df = dataframe

    print(f"Columns in df: {df.columns}")
    print(f"Is 'STRAATNAAM' in df? {'STRAATNAAM' in df.columns}")
    print(f"Filtering for street: {straat}")

    if df.empty or "STRAATNAAM" not in df.columns:
        print("Dataframe empty or missing 'STRAATNAAM' column - aborting")
        return

    filtered = df[df["STRAATNAAM"] == straat].copy()
    if filtered.empty:
        print(f"No rows found for street: {straat}")
        return

    street_averages = filtered[["nature_composite", "humans_composite", "efficiency_composite"]].mean().tolist()
    criteria = ["Nature", "Humans", "Efficiency"]
    plot_spider_web(criteria, street_averages, straat, filtered, center_frame)

    show_aggregated_values(filtered, aggregate_frame)
    update_street_detail_table(filtered, street_list_frame)