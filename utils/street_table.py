import tkinter as tk
from tkinter import ttk

def update_street_detail_table(filtered, parent_frame):
    # Clear existing widgets in the frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Group data by TYPE_LAMP
    grouped = filtered.groupby("TYPE_LAMP")

    for lamp_type, group in grouped:
        count = len(group)
        first_row = group.iloc[0]

        # Lamp type header with count
        header_label = ttk.Label(parent_frame, text=f"{lamp_type} {count}x", font=("Segoe UI", 10, "bold"))
        header_label.pack(anchor="w", pady=(5, 0))

        # Details to show for each lamp type
        details_cols = [
            "LUMEN_LAMP",
            "TYPE_ARMATUUR",
            "LPH_ARMATUUR",
            "CK_IN_KELVIN",
            # "Lumen_per_m2",
            # "Composite_Score",
        ]

        details_frame = ttk.Frame(parent_frame)
        details_frame.pack(anchor="w", padx=20)

        for col in details_cols:
            val = first_row[col]
            label = ttk.Label(details_frame, text=f"- {col}: {val}", wraplength=300, justify="left")
            label.pack(anchor="w")