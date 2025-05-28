import tkinter as tk
from tkinter import ttk
import platform

def create_scrollable_frame(root):
    canvas = tk.Canvas(root, bg="lightgray", highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_configure)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack scrollbar first so it appears on right
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Mouse wheel support
    def _on_mousewheel(event):
        if platform.system() == 'Windows':
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            canvas.yview_scroll(int(-1*event.delta), "units")

    # For Windows and MacOS
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    # For Linux scroll up/down events
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    return canvas, scrollable_frame
