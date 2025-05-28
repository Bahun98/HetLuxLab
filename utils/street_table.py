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

    # Group data by TYPE_LAMP
    grouped = filtered.groupby("TYPE_LAMP")

    for lamp_type, group in grouped:
        count = len(group)
        first_row = group.iloc[0]

        # Lamp type header with count
        header_label = ttk.Label(parent_frame, text=f"{lamp_type} {count}x", font=("Segoe UI", 10, "bold"))
        header_label.pack(anchor="w", pady=(5, 0))

        # Column name → Display label mapping
        details = {
            "LUMEN_SQM": "Lumen in square meter",
            "LPH_ARMATUUR": "Pole height",
            "CK_IN_KELVIN": "Colour temperature",
            "TYPE_ARMATUUR": "Armature",
        }

        details_frame = ttk.Frame(parent_frame)
        details_frame.pack(anchor="w", padx=20)

        for col, label_text in details.items():
            if col == "LPH_ARMATUUR":
                # Get counts of unique pole heights in this group
                height_counts = group["LPH_ARMATUUR"].value_counts(dropna=True).sort_index()
                height_list = [f"{int(height)} cm ({count}x)" for height, count in height_counts.items()]
                display_val = ", ".join(height_list) if height_list else "N/A"
            elif col == "LUMEN_SQM":
                val = first_row[col]
                display_val = f"{val:.2f}" if not pd.isna(val) else "N/A"
            elif col == "CK_IN_KELVIN":
                val = first_row[col]
                display_val = f"{val} kelvin" if not pd.isna(val) else "N/A"
            else:
                display_val = first_row[col]

            # Default label formatting
            label_style = {"wraplength": 300, "justify": "left"}

            # Create label text with the value styled if missing
            if display_val in ("N/A", None, ""):
                label = ttk.Label(
                    details_frame,
                    text=f"- {label_text}: {display_val}",
                    foreground="red",
                    font=("Segoe UI", 10, "bold"),
                    **label_style
                )
            else:
                label = ttk.Label(
                    details_frame,
                    text=f"- {label_text}: {display_val}",
                    **label_style
                )

            label.pack(anchor="w")
