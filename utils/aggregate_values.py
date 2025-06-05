import tkinter as tk
from tkinter import ttk
import pandas as pd

def show_aggregated_values(filtered_df: pd.DataFrame, aggregate_frame: tk.Frame):
    # Remove existing aggregated summary if it exists
    for widget in aggregate_frame.winfo_children():
        if getattr(widget, "is_aggregate_summary", False):
            widget.destroy()

    # Define which columns and their display names
    columns = {
        "LUMEN_LAMP": "Lumen", 
        "LUMEN_SQM": "Lumen in square meter",
        "LPH_ARMATUUR": "Pole height",
        "CK_IN_KELVIN": "Colour temperature",
    }

    # Compute averages
    averages = {}
    for col in columns:
        valid_vals = filtered_df[col].replace(0, pd.NA).dropna()
        averages[col] = valid_vals.mean() if not valid_vals.empty else None

    # Create a frame to hold the summary
    summary_frame = ttk.Frame(aggregate_frame)
    summary_frame.is_aggregate_summary = True  # Custom attribute to identify it
    summary_frame.pack(anchor="w", fill="x", pady=(5, 10))

    header = ttk.Label(summary_frame, text="Average aggregate values:", font=("Segoe UI", 9, "bold"))
    header.pack(anchor="w")

    for col, label in columns.items():
        val = averages[col]
        text = f"- {label}: {val:.2f}" if val is not None else f"- {label}: onbekend"
        label_widget = ttk.Label(summary_frame, text=text, font=("Segoe UI", 9), foreground="black")
        label_widget.pack(anchor="w")
