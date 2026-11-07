# Sri Lankan Port Activity Analytics

An interactive Streamlit dashboard for exploring vessel activity, imports, exports, and cargo patterns across Sri Lankan ports. The repository also includes Jupyter notebooks for data exploration, cleaning, and analysis.

## Requirements

- Python 3.10 or later
- Java 17 or later to run the PySpark workflows in the notebooks

The dashboard itself reads prepared CSV files and does not require Java. Python packages for the dashboard and notebooks are listed in [`requirements.txt`](requirements.txt).

## Set up the environment

Run these commands from the project root.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Activate the virtual environment again whenever you open a new terminal to work on the project.

## Run the dashboard

From the project root, with the virtual environment activated, run:

```bash
python -m streamlit run dashboard/app.py
```

Streamlit will print a local URL (usually <http://localhost:8501>) to open in your browser. Stop the app with `Ctrl+C`.

The dashboard expects the following data files in the repository:

- `data/processed/dashboard/annual_analysis.csv`
- `data/processed/dashboard/import_analysis_by_type.csv`
- `data/processed/dashboard/colombo_monthly_imports.csv`
- `data/raw/lk-port-activity.csv`

## Run the notebooks

With the same environment activated, start Jupyter:

```bash
python -m jupyter lab
```

Open the notebooks in the `notebooks/` directory. They cover data exploration, data cleaning, and exploratory data analysis. The data-cleaning and analysis workflows use PySpark, so ensure Java 17 or later is installed and available on your `PATH` before running those notebook cells.