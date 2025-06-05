from tkinter import ttk
import pandas as pd

def update_street_detail_table(filtered, parent_frame):
    # Clear existing widgets in the frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    total_lamps = len(filtered)
    missing_percent = filtered['missing_zero_flag'].mean() * 100

    stats_label = ttk.Label(
        parent_frame,
        text=f"Total Lamps: {total_lamps} — Missing/Zero: {missing_percent:.1f}%",
        foreground="red",
        font=("Segoe UI", 10, "italic")
    )
    stats_label.pack(anchor="w", padx=10, pady=(5, 10))

    # Group data by TYPE_LAMP and sort by # of lamps
    grouped = filtered.groupby("TYPE_LAMP")
    sorted_groups = sorted(grouped, key=lambda g: len(g[1]), reverse=True)

    for lamp_type, group in sorted_groups:
        count = len(group)
        first_row = group.iloc[0]

        # Lamp type header with count
        header_label = ttk.Label(parent_frame, text=f"{lamp_type} {count}x", font=("Segoe UI", 10, "bold"))
        header_label.pack(anchor="w", pady=(5, 0))

        # Column name → Display label mapping
        details = {
            "LUMEN_LAMP": "Lumen", 
            "LUMEN_SQM": "Lumen in square meter",
            "LPH_ARMATUUR": "Pole height",
            "CK_IN_KELVIN": "Colour temperature",
            "TYPE_ARMATUUR": "Armature",
        }

        details_frame = ttk.Frame(parent_frame)
        details_frame.pack(anchor="w", padx=20)
        missing_message = "nan"

        for col, label_text in details.items():
            val = first_row[col]

            # Treat 0 as missing_message for specific columns
            is_missing = pd.isna(val) or (
                col in ("LUMEN_SQM", "LUMEN") and val == 0
            )

            # Format values based on column
            if col in ("LUMEN_SQM", "LUMEN"):
                display_val = f"{val:.2f}" if not is_missing else missing_message
            elif col in ("LPH_ARMATUUR", "CK_IN_KELVIN"):
                if pd.isna(val):
                    display_val = missing_message
                else:
                    unit = "cm" if col == "LPH_ARMATUUR" else "kelvin"
                    display_val = f"{val} {unit}"
            else:
                display_val = val if not is_missing else missing_message

            # Style missing_message values
            font = ("Segoe UI", 9, "bold") if is_missing else ("Segoe UI", 9)
            color = "red" if is_missing else "black"

            label = ttk.Label(
                details_frame,
                text=f"- {label_text}: {display_val}",
                wraplength=300,
                justify="left",
                font=font,
                foreground=color
            )
            label.pack(anchor="w")