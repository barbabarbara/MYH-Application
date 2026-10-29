# MYH Application Explorer

**Interactive Streamlit dashboard for Swedish higher vocational education applications (2020–2025).**

## Live Application

[Open MYH Application Explorer](https://myh-application.streamlit.app/)

Explore how applications to provide *yrkeshögskola* (YH) programmes were approved or rejected, compare application rounds and education areas, search for programme names, and download filtered records.

> **Live dashboard:** Add your `.streamlit.app` URL here after deployment.
>
> **Project status:** A descriptive data exploration tool. No machine-learning model is trained or used for predictions.

## At a glance

| Metric | Value |
| --- | ---: |
| Application rounds | 2020–2025 (6 years) |
| Application records | **7,641** |
| Dataset columns | **33** |
| Approved applications (`Beviljad`) | **2,613** |
| Rejected applications (`Ej beviljad`) | **5,027** |
| Withdrawn applications (`Återkallad`) | **1** |
| Overall approval rate | **34.20%** |

The approval rate uses only approved and rejected decisions: `2,613 / (2,613 + 5,027) × 100`. The withdrawn application stays in the dataset but is excluded from that rate.

## What you can explore

- **Filter** by application year, education area, and decision using sidebar multiselects.
- **Search** education programme names without distinguishing uppercase/lowercase letters.
- **Compare** approval rates by application year in a chart and table.
- **Compare** education areas, showing the top ten by approval rate among areas with at least **30 decided applications** in the active filter selection.
- **Inspect** matching applications in an eight-column overview or all 33 dataset columns.
- **Download** the filtered applications as a UTF-8 CSV file.

All charts and statistics update when the filters change. When only approved decisions are selected, the displayed approval rate is 100% **for that filtered subset**, not for all applications.

## Data source and preparation

**Original source:** [Myndigheten för yrkeshögskolan (MYH) — Resultat för program](https://www.myh.se/yrkeshogskolan/resultat-ansokningsomgangar/resultat-for-program).

The dataset was prepared from worksheet **`Tabell 3`** in six official MYH Excel workbooks, one per application round (2020–2025). **One row represents one application**, not one student or school enrolment. The application-round year is stored in `ansokningsar`; it is not necessarily the year a programme starts.

The original data-preparation work was performed separately in a Jupyter notebook using Python and pandas. It included:

1. Finding the correct table/header rows in year-specific Excel files.
2. Harmonising equivalent column names and decision labels across years.
3. Combining the six datasets, checking application identifiers and duplicates, and validating selected numeric fields.
4. Preserving source missing values rather than inventing numbers.
5. Creating three descriptive Boolean features: `Minst 400 YH-poäng`, `Heltidsstudier`, and `Flera kommuner (beräknad)`.
6. Exporting the cleaned application-level data as the CSV included in this repository.

The original Excel workbooks, Jupyter notebook, classroom material, and private assignment repository are **not included** in this public dashboard repository. The app only *reads* the already-prepared CSV; it does not repeat the cleaning steps.

## Repository structure

```text
MYH-Application-Explorer/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── processed/
        └── myh_applications_2020_2025.csv
```

`app.py` finds the CSV relative to its own location, so it works when executed from the repository root on Windows or on Streamlit Community Cloud.


## Run locally

You need Python and `pip` installed. Open a terminal in the repository folder.

### Windows PowerShell

```powershell
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt

# Start the Streamlit application
python -m streamlit run app.py
```

### Windows Git Bash

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/Scripts/activate

# Install dependencies
python -m pip install -r requirements.txt

# Start the Streamlit application
python -m streamlit run app.py
```

### macOS / Linux

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt

# Start the Streamlit application
python -m streamlit run app.py
```

### Open the dashboard

After starting Streamlit, open:

http://localhost:8501

To stop the application, press `Ctrl + C` in the terminal.

To deactivate the virtual environment, run:

```bash
deactivate
```

**Note:** The `venv/` folder is excluded from Git using `.gitignore`.


Open [http://localhost:8501](http://localhost:8501) if the browser doesn't open automatically. Press **Ctrl+C** in the terminal to stop the server.

`requirements.txt` lists only what this standalone dashboard needs: **Streamlit** and **pandas**. Excel-reading libraries are not needed because the app reads a CSV, not the original Excel files.

## Deploy to Streamlit Community Cloud

1. Create a **new public GitHub repository** in your own GitHub account and upload the contents of this folder (not the folder as an extra nested directory).
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
3. Select **Create app** → **Yup, I have an app**.
4. Choose your public repository and its default branch (usually `main`).
5. Set **Main file path** to **`app.py`** (the file is in the repository root).
6. Deploy, then open the generated `.streamlit.app` URL and test the sidebar filters and CSV download.
7. Replace the placeholder at the top of this README with your real deployed link and commit the change.

**Important:** The CSV must be committed to the public repository at `data/processed/myh_applications_2020_2025.csv`. Streamlit Cloud cannot read files stored only on your computer. You need sufficient permissions on the GitHub repository you deploy from; a new repository you own avoids many GitHub Classroom permission problems.

[Streamlit documentation: deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

## Data interpretation and limitations

- **Missing values:** The dataset contains **53,580 missing cells**. Many arise because source columns were absent in particular application years. The app leaves those cells missing instead of replacing them with zeros.
- **Programme names:** Slightly different spelling, punctuation, or wording is preserved. Searching is case-insensitive, but does not automatically merge similar programme names.
- **Year-to-year comparisons:** Column coverage and definitions can vary across MYH workbooks; compare years with care.
- **Approval rates:** Withdrawn applications are excluded from the approved/rejected denominator. Results depend on the selected filters.
- **Not an ML prediction app:** `Beslut` is a possible future prediction target. Outcome-based fields, such as approved places and approved rounds, must not be used as predictive input features without avoiding **target leakage**.
- **Public data disclosure:** Publishing this repository makes the included cleaned CSV and its application-level records publicly downloadable. Review the data and the source publisher's reuse terms before publishing.

## Quick verification

With all years, areas, and decisions selected, the top of the app should show:

| Applications | Approved | Rejected | Approval rate |
| ---: | ---: | ---: | ---: |
| 7,641 | 2,613 | 5,027 | 34.20% |

You should also be able to search for a programme, compare the two charts, switch between 8 and 33 visible columns, and download the filtered CSV.

## Attribution

Data: **Myndigheten för yrkeshögskolan (MYH)**, *Resultat för program* (application rounds 2020–2025). The downloaded public source workbooks were transformed into the CSV provided here. This is an independent educational dashboard and is **not** an official MYH service.

The repository intentionally does not declare a licence for the source data. Do not assume that a licence for the app code automatically governs MYH's underlying material; consult the publisher's applicable reuse terms.
