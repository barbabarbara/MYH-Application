"""Explore MYH programme applications from 2020–2025 in Streamlit.

Run from the repository root:
    python -m streamlit run app.py

The repository includes the cleaned CSV exported by the original notebook.
"""

from pathlib import Path

import pandas as pd
import streamlit as st


# --- Data source and decision categories ---

# Build the CSV path relative to this script, independent of the terminal folder.
DATA_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "processed"
    / "myh_applications_2020_2025.csv"
)

APPROVED = "Beviljad"
REJECTED = "Ej beviljad"
WITHDRAWN = "Återkallad"


# --- Load and filter data ---

# Cache the loaded dataset so changing filters does not reread the CSV.
@st.cache_data(show_spinner=False)
def load_data(csv_path: str) -> pd.DataFrame:
    """Read the cleaned MYH dataset without changing its values.

    Args:
        csv_path (str): Path to the exported CSV file.

    Returns:
        pd.DataFrame: Application data with Diarienummer stored as text.

    Raises:
        FileNotFoundError: If the CSV does not exist.
        pd.errors.EmptyDataError: If the CSV has no data columns.
        pd.errors.ParserError: If the CSV cannot be parsed.
    """
    return pd.read_csv(
        csv_path,
        encoding="utf-8-sig",  # Support UTF-8 and an optional BOM.
        dtype={"Diarienummer": "string"},  # Keep application IDs as text.
        low_memory=False,  # Help pandas infer column types consistently.
    )


def filter_data(
    data: pd.DataFrame,
    years: list[int],
    areas: list[str],
    decisions: list[str],
    programme_search: str,
) -> pd.DataFrame:
    """Return applications matching all selected sidebar filters.

    Args:
        data (pd.DataFrame): All MYH applications.
        years (list[int]): Selected years.
        areas (list[str]): Selected education areas.
        decisions (list[str]): Selected decision categories.
        programme_search (str): Optional programme-name search text.

    Returns:
        pd.DataFrame: Matching rows in a copy; input data is unchanged.
    """
    # Create a True/False mask: each row must match all three selections.
    matches = (
        data["ansokningsar"].isin(years)
        & data["Utbildningsområde"].isin(areas)
        & data["Beslut"].isin(decisions)
    )

    # Add a case-insensitive text search only when the user enters text.
    if programme_search.strip():
        matches &= data["Utbildningsnamn"].fillna("").str.contains(
            programme_search.strip(), case=False, regex=False
        )

    # Select matching rows without modifying the original DataFrame.
    return data.loc[matches].copy()


def decided_applications(data: pd.DataFrame) -> pd.DataFrame:
    """Exclude withdrawn cases and label approvals with 1 and rejections with 0.

    Args:
        data (pd.DataFrame): Applications after optional filtering.

    Returns:
        pd.DataFrame: Decided applications with a numeric Approved column.
    """
    # Approval rates include approved and rejected applications only.
    decided = data.loc[data["Beslut"].isin([APPROVED, REJECTED])].copy()
    decided["Approved"] = decided["Beslut"].eq(APPROVED).astype(int)
    return decided


# --- Calculate approval statistics ---

def year_statistics(decided: pd.DataFrame) -> pd.DataFrame:
    """Summarise approved, rejected and total applications by year.

    Args:
        decided (pd.DataFrame): Decided applications with Approved = 1 or 0.

    Returns:
        pd.DataFrame: Yearly counts and approval percentages.
    """
    result = decided.groupby("ansokningsar").agg(
        Applications=("Approved", "size"),  # Count applications.
        Approved=("Approved", "sum"),  # Sum the 1s to count approvals.
    )
    result["Rejected"] = result["Applications"] - result["Approved"]
    result["Approval rate (%)"] = (
        100 * result["Approved"] / result["Applications"]
    ).round(2)
    return result.reset_index().rename(columns={"ansokningsar": "Year"})


def area_statistics(decided: pd.DataFrame) -> pd.DataFrame:
    """Summarise applications and approval rates by education area.

    Args:
        decided (pd.DataFrame): Decided applications with Approved = 1 or 0.

    Returns:
        pd.DataFrame: Area totals and approval rates, highest rate first.
    """
    result = decided.groupby("Utbildningsområde").agg(
        Applications=("Approved", "size"),  # Count applications.
        Approved=("Approved", "sum"),  # Count approvals.
    )
    result["Rejected"] = result["Applications"] - result["Approved"]
    result["Approval rate (%)"] = (
        100 * result["Approved"] / result["Applications"]
    ).round(2)
    return result.reset_index().sort_values("Approval rate (%)", ascending=False)


# --- Build the Streamlit dashboard ---

def main() -> None:
    """Display sidebar filters, approval statistics, charts and records."""
    st.set_page_config(page_title="MYH Application Explorer", page_icon="📊", layout="wide")

    st.title("MYH Application Explorer")
    st.write(
        "Explore applications for Swedish higher vocational education "
        "(yrkeshögskolan), **2020–2025**."
    )

    # Stop with a useful message if the cleaned CSV is missing.
    if not DATA_FILE.is_file():
        st.error("The cleaned CSV file was not found.")
        st.code(str(DATA_FILE))
        st.info("Check that the processed CSV is present in data/processed/.")
        st.stop()

    data = load_data(str(DATA_FILE))

    # Check the columns required for filtering and statistics.
    needed_columns = {
        "ansokningsar", "Utbildningsområde", "Utbildningsnamn", "Beslut"
    }
    if not needed_columns.issubset(data.columns):
        st.error(f"Missing required columns: {sorted(needed_columns - set(data.columns))}")
        st.stop()

    # --- Sidebar filters ---
    st.sidebar.header("Filter applications")

    # List available options without duplicates or missing values.
    all_years = sorted(data["ansokningsar"].dropna().unique().tolist())
    all_areas = sorted(data["Utbildningsområde"].dropna().unique().tolist())
    all_decisions = [
        value for value in [APPROVED, REJECTED, WITHDRAWN]
        if value in data["Beslut"].unique()
    ]

    selected_years = st.sidebar.multiselect(
        "Application years", all_years, default=all_years
    )
    selected_areas = st.sidebar.multiselect(
        "Education areas", all_areas, default=all_areas
    )
    selected_decisions = st.sidebar.multiselect(
        "Decisions", all_decisions, default=all_decisions
    )
    programme_search = st.sidebar.text_input(
        "Search education programme", placeholder="e.g. Python"
    )

    filtered = filter_data(
        data, selected_years, selected_areas,
        selected_decisions, programme_search,
    )
    if filtered.empty:
        st.warning("No applications match these filters. Try widening your selection.")
        st.stop()

    # --- Summary metrics ---
    decided = decided_applications(filtered)
    approved_count = int(decided["Approved"].sum())
    rejected_count = len(decided) - approved_count
    withdrawn_count = int(filtered["Beslut"].eq(WITHDRAWN).sum())
    approval_rate = 100 * approved_count / len(decided) if len(decided) else None

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Applications (all decisions)", f"{len(filtered):,}")
    metric2.metric("Approved", f"{approved_count:,}")
    metric3.metric("Rejected", f"{rejected_count:,}")
    metric4.metric(
        "Approval rate", f"{approval_rate:.2f}%" if approval_rate is not None else "N/A"
    )
    st.caption(
        f"Withdrawn applications in this selection: {withdrawn_count}. "
        "Approval rate = approved / (approved + rejected); "
        "withdrawn cases are excluded only from this calculation."
    )

    # --- Charts and application records ---
    tab_year, tab_area, tab_records = st.tabs(
        ["By year", "By education area", "Explore records"]
    )

    with tab_year:
        st.subheader("Approval rates by application year")
        if decided.empty:
            st.info("Select approved and/or rejected decisions to calculate rates.")
        else:
            yearly = year_statistics(decided)
            st.bar_chart(yearly.set_index("Year")["Approval rate (%)"])
            st.dataframe(yearly, use_container_width=True, hide_index=True)

    with tab_area:
        st.subheader("Approval rates by education area")
        st.caption(
            "Ranking includes only areas with at least 30 decided applications "
            "in the current filter selection."
        )
        if decided.empty:
            st.info("Select approved and/or rejected decisions to compare areas.")
        else:
            areas = area_statistics(decided)
            ranked = areas.loc[areas["Applications"] >= 30].head(10)
            if ranked.empty:
                st.info("No education areas have 30 decided applications with these filters.")
            else:
                st.bar_chart(
                    ranked.set_index("Utbildningsområde")["Approval rate (%)"]
                )
                st.dataframe(ranked, use_container_width=True, hide_index=True)

    with tab_records:
        st.subheader("Filtered applications")
        show_all = st.checkbox("Show all 33 columns", value=False)
        overview_columns = [
            "ansokningsar", "Utbildningsområde", "Utbildningsnamn",
            "Län", "Kommun", "YH-poäng", "Studieform", "Beslut"
        ]
        displayed = filtered if show_all else filtered[overview_columns]
        st.dataframe(displayed, use_container_width=True, hide_index=True)
        st.download_button(
            "Download filtered applications as CSV",
            data=filtered.to_csv(index=False).encode("utf-8-sig"),
            file_name="myh_filtered_applications.csv",
            mime="text/csv",
        )

    # --- Dataset context and source ---
    with st.expander("About the dataset and missing values"):
        st.write(
            "Source: MYH application-round results, `Tabell 3` in the six "
            "Excel workbooks for 2020–2025. Each row is one application, "
            "not one student. The unfiltered dataset has **7,641 rows "
            "and 33 columns**."
        )
        st.write(
            "The full dataset contains **53,580 missing cells**. "
            "Many result from columns being unavailable in earlier years. "
            "Missing values were preserved, not automatically replaced by zero."
        )
        st.write(
            "This dashboard is for descriptive exploration only. "
            "`Beslut` remains in the source file for future ML training; "
            "approved-round and approved-place columns must not be used as "
            "prediction inputs when predicting that decision."
        )

    st.markdown(
        "**Data source:** "
        "[Myndigheten för yrkeshögskolan (MYH) — "
        "Results of programme application rounds (2020–2025)]"
        "(https://www.myh.se/yrkeshogskolan/resultat-ansokningsomgangar/resultat-for-program)"
    )
    st.caption(
        "Data preparation: Python and pandas. "
        "The original Excel files were harmonised into a single dataset. "
        "This dashboard is for descriptive exploration, not ML predictions."
    )


# Run main() once so Streamlit widgets are not duplicated.
if __name__ == "__main__":
    main()
