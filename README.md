# Het Lux Lab Lighting Analysis Tool

## Overview

This application provides an interactive GUI tool to analyze street lighting data by neighborhood ("wijk") and lamp types. It helps users explore lamp counts, missing or zero data flags, and detailed lamp specifications grouped by street and lamp type.

Key features include filtering by wijk, cleaning and grouping street names, displaying statistics and detailed lamp attributes, and visualizing wijk-level composite criteria using spider/radar charts.

---

## Features

- Load and filter lighting data by wijk (neighborhood).
- Clean street names to remove numeric and alphanumeric suffixes (e.g., "Zandeiland 003A" → "Zandeiland").
- Display total lamp counts and percentage of missing/zero flagged lamps.
- Group lamps by type and show detailed attributes like lumen output, pole height, color temperature, and armature type.
- Highlight missing attribute values in red and bold for easy identification.
- Interactive spider graphs visualizing wijk composite scores for nature, humans, and efficiency criteria.
- Scrollable lamp details with proper mouse wheel support scoped to the detail pane.

---

## Limitations

- Data depends on accurate and consistent input CSV or database files.
- Lamp attribute completeness varies; some data fields may be missing or inconsistent, namely colour temperature in Kelvin.
- Currently designed for single-user desktop use; no multi-user or web version yet.
- Some GUI behaviors (e.g., mouse wheel scrolling) depend on OS specifics.
- Initial dataset loading and filtering may be slow with very large datasets.
- Limited error handling and data validation in the current version.

---

## Backlog / Future Improvements

- Add data import wizards and support for multiple data sources/formats.
- Enable export of filtered data and reports in CSV or PDF formats, this capability exists in calculations.py but is commented out.
- Implement more advanced filtering and searching capabilities.
- Add more visualization options beyond spider charts (e.g., histograms, maps).
- Improve responsiveness and UX of the GUI for large datasets.
- Integrate with external APIs or databases for live data updates.
- Add user preferences and theme support for better accessibility.
- Implement automated data quality checks and cleaning routines.

---

## Getting Started

Follow these steps to set up and run the Het Lux Lab Lighting Analysis Tool on Windows using Visual Studio Code.

### 1. Install Python and Visual Studio Code

- Make sure Python 3.x is installed on your system. Download from [python.org](https://www.python.org/downloads/windows/).
- Install Visual Studio Code from [code.visualstudio.com](https://code.visualstudio.com/).

### 2. Create and Activate a Virtual Environment

A virtual environment helps isolate your project dependencies from other Python projects on your machine, avoiding version conflicts.

Open a terminal (in VS Code: `Terminal > New Terminal`) and run:

```bash
python -m venv .venv
```
This creates a .venv folder in your project directory.

Activate the virtual environment:

For PowerShell (default in VS Code on Windows):
.\.venv\Scripts\Activate.ps1

For Command Prompt:
.\.venv\Scripts\activate.bat

### 3. Install Dependencies
With the virtual environment activated, install required Python packages from the requirements.txt file:

pip install -r requirements.txt
This installs all necessary libraries (like pandas, tkinter, Pillow, etc.).

### 4. Place Your Dataset
Make sure your dataset file named real_data.xlsx is placed in the root folder of the project (the same folder as your main Python script).

### 5. Dataset Requirements
The dataset must include a column for colour temperature, named exactly as CK_IN_KELVIN. This column is used to analyze the colour temperature of the lamps.

Once these steps are complete, you can run the main Python script, Spider.py to start the GUI application.
---

## License

Owned by Het Lux Lab and Fontys
---

