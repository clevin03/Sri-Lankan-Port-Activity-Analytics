
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Sri Lankan Port Analytics",
    page_icon="🚢",
    layout="wide"
)

# ==========================================
# 2. LOAD ANALYTICAL DATA
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed" / "dashboard"


@st.cache_data
def load_data():

    annual = pd.read_csv(DATA_DIR / "annual_analysis.csv")

    cargo = pd.read_csv(
        DATA_DIR / "import_analysis_by_type.csv"
    )

    colombo = pd.read_csv(
        DATA_DIR / "colombo_monthly_imports.csv"
    )

    export_columns = [
        "export_container",
        "export_dry_bulk",
        "export_general_cargo",
        "export_roro",
        "export_tanker",
        "export_cargo",
    ]
    daily_colombo_exports = pd.read_csv(
        PROJECT_DIR / "data" / "raw" / "lk-port-activity.csv",
        usecols=["date", "portname", *export_columns],
    )
    daily_colombo_exports = daily_colombo_exports.loc[
        daily_colombo_exports["portname"]
        .astype("string")
        .str.strip()
        .str.casefold()
        .eq("colombo")
    ].copy()
    daily_colombo_exports["date"] = pd.to_datetime(
        daily_colombo_exports["date"], utc=True
    )
    daily_colombo_exports["year"] = daily_colombo_exports["date"].dt.year
    daily_colombo_exports["month"] = daily_colombo_exports["date"].dt.month
    colombo_exports = (
        daily_colombo_exports.groupby(["year", "month"], as_index=False)[
            export_columns
        ]
        .sum()
        .rename(
            columns={
                **{
                    column: f"total_{column}"
                    for column in export_columns
                },
            }
        )
    )

    # Ensure numeric data types
    annual["year"] = pd.to_numeric(annual["year"])
    cargo["year"] = pd.to_numeric(cargo["year"])
    colombo["year"] = pd.to_numeric(colombo["year"])
    colombo_exports["year"] = pd.to_numeric(colombo_exports["year"])

    numeric_annual = [
        "total_port_calls",
        "total_imports",
        "total_exports"
    ]

    for c in numeric_annual:
        annual[c] = pd.to_numeric(
            annual[c], errors="coerce"
        ).fillna(0)

    return annual, cargo, colombo, colombo_exports


annual, cargo, colombo, colombo_exports = load_data()

# ==========================================
# 3. DASHBOARD HEADER
# ==========================================

st.title("🚢 Sri Lankan Port Activity Analytics")

st.markdown(
    """
    An interactive dashboard exploring vessel activity,
    imports, exports and cargo patterns across
    Sri Lankan ports.
    """
)

st.divider()

# ==========================================
# 4. SIDEBAR FILTERS
# ==========================================

st.sidebar.title("Dashboard Filters")

available_years = sorted(
    annual["year"].dropna().unique().tolist()
)

selected_years = st.sidebar.multiselect(
    "Select Years",
    available_years,
    default=available_years
)

available_ports = sorted(
    annual["portname"].dropna().unique().tolist()
)

selected_ports = st.sidebar.multiselect(
    "Select Ports",
    available_ports,
    default=available_ports
)

annual_filtered = annual[
    annual["year"].isin(selected_years) &
    annual["portname"].isin(selected_ports)
]

cargo_filtered = cargo[
    cargo["year"].isin(selected_years) &
    cargo["portname"].isin(selected_ports)
]

colombo_filtered = colombo[
    colombo["year"].isin(selected_years)
].copy()

colombo_exports_filtered = colombo_exports[
    colombo_exports["year"].isin(selected_years)
].copy()

# ==========================================
# 5. KPI CARDS
# ==========================================

st.subheader("Port Activity Overview")

total_calls = annual_filtered["total_port_calls"].sum()
total_imports = annual_filtered["total_imports"].sum()
total_exports = annual_filtered["total_exports"].sum()
port_count = annual_filtered["portname"].nunique()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Vessel Calls", f"{total_calls:,.0f}")
c2.metric("Total Imports", f"{total_imports:,.0f}")
c3.metric("Total Exports", f"{total_exports:,.0f}")
c4.metric("Ports Selected", port_count)

st.divider()

# ==========================================
# 6. DASHBOARD TABS
# ==========================================

overview_tab, trade_tab, colombo_tab = st.tabs([
    "Port Overview",
    "Trade Analysis",
    "Colombo Import & Export Analysis"
])

# ==========================================
# TAB 1 - PORT OVERVIEW
# ==========================================

with overview_tab:

    st.subheader("Annual Vessel Activity by Port")

    if not annual_filtered.empty:

        fig1 = px.bar(
            annual_filtered,
            x="year",
            y="total_port_calls",
            color="portname",
            barmode="group",
            title="Vessel Calls by Year and Port",
            labels={
                "year": "Year",
                "total_port_calls": "Vessel Calls",
                "portname": "Port"
            }
        )

        st.plotly_chart(fig1, use_container_width=True)

    else:
        st.info("Select at least one year and port.")

    st.subheader("Annual Import Activity by Port")

    if not annual_filtered.empty:

        fig2 = px.bar(
            annual_filtered,
            x="year",
            y="total_imports",
            color="portname",
            barmode="group",
            title="Annual Imports by Port",
            labels={
                "year": "Year",
                "total_imports": "Total Imports"
            }
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Annual Export Activity by Port")

    if not annual_filtered.empty:

        fig3 = px.bar(
            annual_filtered,
            x="year",
            y="total_exports",
            color="portname",
            barmode="group",
            title="Annual Exports by Port"
        )

        st.plotly_chart(fig3, use_container_width=True)


# ==========================================
# TAB 2 - TRADE ANALYSIS
# ==========================================

with trade_tab:

    st.subheader("Import vs Export Comparison")

    if not annual_filtered.empty:

        trade = annual_filtered.melt(
            id_vars=["year", "portname"],
            value_vars=[
                "total_imports",
                "total_exports"
            ],
            var_name="Trade Type",
            value_name="Volume"
        )

        trade["Trade Type"] = trade["Trade Type"].map({
            "total_imports": "Imports",
            "total_exports": "Exports"
        })

        fig4 = px.bar(
            trade,
            x="year",
            y="Volume",
            color="Trade Type",
            barmode="group",
            facet_col="portname",
            facet_col_wrap=2,
            title="Imports and Exports by Year and Port"
        )

        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Imports by Cargo Type")

    if not cargo_filtered.empty:

        cargo_columns = [
            "total_import_container",
            "total_import_dry_bulk",
            "total_import_general_cargo",
            "total_import_roro",
            "total_import_tanker"
        ]

        cargo_long = cargo_filtered.melt(
            id_vars=["year", "portname"],
            value_vars=cargo_columns,
            var_name="Cargo Type",
            value_name="Import Volume"
        )

        cargo_long["Cargo Type"] = (
            cargo_long["Cargo Type"]
            .str.replace("total_import_", "", regex=False)
            .str.replace("_", " ")
            .str.title()
        )

        fig5 = px.bar(
            cargo_long,
            x="year",
            y="Import Volume",
            color="Cargo Type",
            barmode="group",
            facet_col="portname",
            facet_col_wrap=2,
            title="Import Cargo Categories by Port and Year"
        )

        st.plotly_chart(fig5, use_container_width=True)

    else:
        st.info("No cargo data for the selected filters.")


# ==========================================
# TAB 3 - COLOMBO IMPORT ANALYSIS
# ==========================================

with colombo_tab:

    st.subheader("Monthly Import Patterns - Colombo Port")

    colombo_columns = [
        "total_import_container",
        "total_import_dry_bulk",
        "total_import_general_cargo",
        "total_import_roro",
        "total_import_tanker"
    ]

    if not colombo_filtered.empty:

        colombo_filtered["date"] = pd.to_datetime(
            colombo_filtered[["year", "month"]].assign(day=1)
        )

        colombo_filtered = colombo_filtered.sort_values("date")

        fig6 = px.line(
            colombo_filtered,
            x="date",
            y=colombo_columns,
            markers=True,
            title="Monthly Imports by Cargo Category",
            labels={
                "date": "Month",
                "value": "Import Volume",
                "variable": "Cargo Category"
            }
        )

        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("Colombo Monthly Import Data")

        st.dataframe(
            colombo_filtered,
            use_container_width=True
        )

    else:
        st.info("No Colombo import data for the selected years.")

    st.divider()
    st.subheader("Monthly Export Patterns - Colombo Port")

    export_chart_columns = [
        "total_export_container",
        "total_export_dry_bulk",
        "total_export_general_cargo",
        "total_export_roro",
        "total_export_tanker",
    ]

    if not colombo_exports_filtered.empty:
        colombo_exports_filtered["date"] = pd.to_datetime(
            colombo_exports_filtered[["year", "month"]].assign(day=1)
        )
        colombo_exports_filtered = colombo_exports_filtered.sort_values("date")

        fig7 = px.line(
            colombo_exports_filtered,
            x="date",
            y=export_chart_columns,
            markers=True,
            title="Monthly Exports by Cargo Category and Total",
            labels={
                "date": "Month",
                "value": "Export Volume",
                "variable": "Export Category",
            },
        )
        st.plotly_chart(fig7, use_container_width=True)

        st.subheader("Colombo Monthly Export Data")
        st.dataframe(
            colombo_exports_filtered,
            use_container_width=True,
        )
    else:
        st.info("No Colombo export data for the selected years.")

# ==========================================
# 7. FOOTER
# ==========================================

st.divider()

st.caption(
    "Sri Lankan Port Activity Analytics | "
    "Big Data Analytics Project"
)

st.caption(
    "Note: 2026 contains partial-year data. "
    "Annual comparisons should account for this."
)
