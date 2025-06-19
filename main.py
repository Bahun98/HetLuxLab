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
from difflib import get_close_matches
from utils.street_table import update_street_detail_table

# df_complete, df_clean, df_missing = generate_data_frames()
df_complete = generate_data_frames()

df_complete["Cleaned_Straat"] = (
    df_complete["straatnaam+identificatie_mast"]
    .str.extract(r"^([A-Za-zÀ-ÿ'\- ]+)", expand=False)
    .str.strip()
)

wijk_options = sorted(df_complete["WIJK"].dropna().unique())

search_popup = None

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

# Inside left_frame
label = tk.Label(
    left_frame,
    text="Search for a street:",
    bg="lightgray",
    font=("Helvetica", 10, "bold"),
    anchor="w"
)

label.pack(side="top", anchor="n", fill="x", padx=10, pady=(10, 0))
search_frame = ttk.Frame(left_frame)
search_frame.pack(fill="x", padx=5, pady=(5, 0))

search_var = tk.StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var)
search_entry.pack(side="left", fill="x", expand=True)

# Frame to hold search results (under search_entry)
search_results_frame = ttk.Frame(left_frame)
search_results_frame.pack(fill="x", padx=5, pady=(0, 10))

search_results_listbox = tk.Listbox(search_results_frame, height=5)
search_results_listbox.pack_forget()

def search_streets(event, street_listbox):
    global search_popup

    query = search_var.get().strip()
    if not query:
        if search_popup:
            search_popup.destroy()
            search_popup = None
        return

    all_streets = df_complete["Cleaned_Straat"].dropna().unique().tolist()
    matches = get_close_matches(query, all_streets, n=5, cutoff=0.3)

    if not matches:
        if search_popup:
            search_popup.destroy()
            search_popup = None
        return

    # Destroy old popup if it exists
    if search_popup:
        search_popup.destroy()

    # Create new popup
    search_popup = tk.Toplevel(root)
    search_popup.wm_overrideredirect(True)  # Removes window decorations
    search_popup.lift()
    
    # Position just under the search_entry
    x = search_entry.winfo_rootx()
    y = search_entry.winfo_rooty() + search_entry.winfo_height()
    search_popup.geometry(f"+{x}+{y}")

    # Fill with Listbox
    popup_listbox = tk.Listbox(search_popup, height=len(matches), borderwidth=1, relief="solid")
    popup_listbox.pack()

    for match in matches:
        popup_listbox.insert("end", match)

    def on_select(event):
        selection = popup_listbox.curselection()
        if selection:
            street_name = popup_listbox.get(selection[0])
            # Find index in listbox
            streets = list(street_listbox.get(0, tk.END))
            if street_name in streets:
                idx = streets.index(street_name)
                street_listbox.selection_clear(0, tk.END)
                street_listbox.selection_set(idx)
                street_listbox.event_generate("<<ListboxSelect>>")
        search_popup.destroy()

    popup_listbox.bind("<<ListboxSelect>>", on_select)


def on_search_result_selected(event):
    selection = search_results_listbox.curselection()
    if not selection:
        return

    straat = search_results_listbox.get(selection[0])
    search_results_listbox.pack_forget()
    search_var.set("")  # Clear search box

    # Create cleaned street column if not already done
    if "Cleaned_Straat" not in df_complete.columns:
        df_complete["Cleaned_Straat"] = (
            df_complete["straatnaam+identificatie_mast"]
            .str.extract(r"^([A-Za-zÀ-ÿ'\- ]+)", expand=False)
            .str.strip()
        )

    # Filter by street name globally
    filtered = df_complete[df_complete["Cleaned_Straat"] == straat].copy()
    if filtered.empty:
        return

    street_averages = filtered[["nature_composite", "humans_composite", "efficiency_composite"]].mean().tolist()
    criteria = ["Nature", "Humans", "Efficiency"]

    plot_spider_web(criteria, street_averages, straat, filtered, center_frame)

    from utils.aggregate_values import show_aggregated_values

    show_aggregated_values(filtered, aggregate_frame)
    update_street_detail_table(filtered, street_list_frame)

search_results_listbox.bind("<<ListboxSelect>>", on_search_result_selected)


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

search_entry.bind("<KeyRelease>", lambda e: search_streets(e, street_listbox))

def on_click_outside(event):
    global search_popup
    if search_popup and not str(event.widget).startswith(str(search_popup)):
        search_popup.destroy()
        search_popup = None

root.bind("<Button-1>", on_click_outside)


selected_Wijk.set(wijk_options[0])
on_wijk_selected(None, selected_Wijk, df_complete, street_listbox, center_frame, plot_spider_web, aggregate_frame, street_list_frame)

def on_closing():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
