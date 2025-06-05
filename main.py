import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from calc.calculations import generate_data_frames
from utils.scrollable_frame import create_scrollable_frame
from graphs.spider_plot import (
    on_wijk_selected,
    on_street_selected,
    plot_spider_web
)

# df_complete, df_clean, df_missing = generate_data_frames()
df_complete = generate_data_frames()

wijk_options = sorted(df_complete["WIJK"].dropna().unique())

# GUI root
root = tk.Tk()
root.title("Het Lux Lab lighting analysis tool")
root.iconphoto(False, tk.PhotoImage(file="icons\luxlabicon.png"))
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
# right_frame_container.pack_propagate(False)
# Scrollable frame inside right_frame_container (MUST come first)
right_scrollable_frame, right_inner_frame = create_scrollable_frame(right_frame_container)

# Create two subframes INSIDE the scrollable right_inner_frame
aggregate_frame = ttk.Frame(right_inner_frame)
aggregate_frame.pack(fill="x", padx=5, pady=(5, 0))

street_list_frame = ttk.Frame(right_inner_frame)
street_list_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

# Scrollable frame inside right_frame_container

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

dropdown.bind(
    "<<ComboboxSelected>>",
    lambda event: on_wijk_selected(event, selected_Wijk, df_complete, street_listbox, center_frame, plot_spider_web, aggregate_frame, street_list_frame)
)

street_listbox.bind(
    "<<ListboxSelect>>",
    lambda event: on_street_selected(event, street_listbox, street_list_frame, center_frame, plot_spider_web, aggregate_frame)
)

selected_Wijk.set(wijk_options[0])
on_wijk_selected(None, selected_Wijk, df_complete, street_listbox, center_frame, plot_spider_web, aggregate_frame, street_list_frame)

def on_closing():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
