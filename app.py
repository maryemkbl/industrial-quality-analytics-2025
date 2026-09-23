import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Industrial Quality Analytics 2025",
    page_icon="🏭",
    layout="wide"
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #F5F7FA;
}

.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    text-align: center;
}

.metric-title {
    font-size: 14px;
    color: #6B7280;
}

.metric-value {
    font-size: 30px;
    font-weight: bold;
    color: #1F2937;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("Qualite_industrielle.csv")

    # Date
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Colonnes numériques
    numeric_columns = [
        "Units_Produced",
        "Defective_Units",
        "Quality_Rate"
    ]

    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        df[col] = df[col].fillna(
            df[col].median()
        )

    df = df.dropna(
        subset=["Date"]
    )

    return df


df = load_data()

# ============================================================
# HEADER
# ============================================================

st.title("🏭 Industrial Quality Analytics")

st.markdown(
    """
    ### 2025 Machine Performance Dashboard

    Interactive analysis of industrial quality,
    production performance, machine stability and anomalies.
    """
)

st.divider()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Dashboard Filters")

machines = ["All Machines"] + sorted(
    df["Machine"].unique().tolist()
)

selected_machine = st.sidebar.selectbox(
    "Select a machine",
    machines
)

# ============================================================
# FILTER DATA
# ============================================================

if selected_machine == "All Machines":

    filtered_df = df.copy()

else:

    filtered_df = df[
        df["Machine"] == selected_machine
    ].copy()

# ============================================================
# KPIs
# ============================================================

global_quality = filtered_df["Quality_Rate"].mean()

total_units = filtered_df["Units_Produced"].sum()

total_defective = filtered_df["Defective_Units"].sum()

if total_units > 0:

    defect_rate = (
        total_defective /
        total_units
    ) * 100

else:

    defect_rate = 0

number_machines = filtered_df["Machine"].nunique()

# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "✅ Quality Rate",
        f"{global_quality:.2f}%"
    )

with col2:

    st.metric(
        "📦 Total Production",
        f"{total_units:,.0f}"
    )

with col3:

    st.metric(
        "❌ Defective Units",
        f"{total_defective:,.0f}"
    )

with col4:

    st.metric(
        "🏭 Machines",
        number_machines
    )

st.divider()

# ============================================================
# QUALITY EVOLUTION
# ============================================================

st.subheader("📈 Quality Rate Evolution")

daily_quality = (
    filtered_df
    .groupby("Date")["Quality_Rate"]
    .mean()
    .reset_index()
)

fig_quality = px.line(
    daily_quality,
    x="Date",
    y="Quality_Rate",
    title="Industrial Quality Rate — 2025",
    markers=False
)

fig_quality.update_layout(
    xaxis_title="Date",
    yaxis_title="Quality Rate (%)",
    hovermode="x unified"
)

fig_quality.add_hline(
    y=global_quality,
    line_dash="dash",
    annotation_text=f"Average: {global_quality:.2f}%"
)

st.plotly_chart(
    fig_quality,
    use_container_width=True
)

# ============================================================
# MACHINE PERFORMANCE
# ============================================================

st.subheader("🏭 Machine Performance")

machine_analysis = (
    filtered_df
    .groupby("Machine")
    .agg(
        Average_Quality=("Quality_Rate", "mean"),
        Minimum_Quality=("Quality_Rate", "min"),
        Maximum_Quality=("Quality_Rate", "max"),
        Total_Production=("Units_Produced", "sum"),
        Total_Defective=("Defective_Units", "sum")
    )
    .reset_index()
)

machine_analysis["Defect_Rate"] = (
    machine_analysis["Total_Defective"]
    /
    machine_analysis["Total_Production"].replace(
        0,
        np.nan
    )
) * 100

machine_analysis["Quality_Std"] = (
    filtered_df
    .groupby("Machine")["Quality_Rate"]
    .std()
    .values
)

machine_analysis = machine_analysis.sort_values(
    "Average_Quality",
    ascending=False
)

# ============================================================
# MACHINE QUALITY CHART
# ============================================================

fig_machine = px.bar(
    machine_analysis,
    x="Average_Quality",
    y="Machine",
    orientation="h",
    title="Average Quality Rate by Machine",
    text="Average_Quality"
)

fig_machine.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_machine.update_layout(
    xaxis_title="Average Quality Rate (%)",
    yaxis_title="Machine"
)

st.plotly_chart(
    fig_machine,
    use_container_width=True
)

# ============================================================
# TWO COLUMNS
# ============================================================

col_left, col_right = st.columns(2)

# ============================================================
# QUALITY VS STABILITY
# ============================================================

with col_left:

    st.subheader("📊 Quality vs Stability")

    fig_stability = px.scatter(
        machine_analysis,
        x="Quality_Std",
        y="Average_Quality",
        text="Machine",
        size="Total_Production",
        hover_data=[
            "Defect_Rate",
            "Minimum_Quality",
            "Maximum_Quality"
        ],
        title="Machine Quality vs Stability"
    )

    fig_stability.update_traces(
        textposition="top center"
    )

    fig_stability.update_layout(
        xaxis_title="Quality Variability",
        yaxis_title="Average Quality (%)"
    )

    st.plotly_chart(
        fig_stability,
        use_container_width=True
    )

# ============================================================
# PRODUCTION VS DEFECTS
# ============================================================

with col_right:

    st.subheader("📦 Production vs Defects")

    fig_defects = px.scatter(
        machine_analysis,
        x="Total_Production",
        y="Total_Defective",
        text="Machine",
        size="Total_Production",
        title="Production vs Defective Units"
    )

    fig_defects.update_traces(
        textposition="top center"
    )

    fig_defects.update_layout(
        xaxis_title="Total Units Produced",
        yaxis_title="Total Defective Units"
    )

    st.plotly_chart(
        fig_defects,
        use_container_width=True
    )

# ============================================================
# ANOMALY DETECTION
# ============================================================

st.subheader("⚠️ Low Quality Periods")

daily_quality_all = (
    filtered_df
    .groupby("Date")["Quality_Rate"]
    .mean()
)

threshold = (
    daily_quality_all.mean()
    -
    daily_quality_all.std()
)

low_quality_days = (
    daily_quality_all[
        daily_quality_all < threshold
    ]
    .sort_values()
)

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Detection Threshold",
        f"{threshold:.2f}%"
    )

with col2:

    st.metric(
        "Low Quality Days",
        len(low_quality_days)
    )

if len(low_quality_days) > 0:

    anomaly_df = (
        low_quality_days
        .reset_index()
    )

    anomaly_df.columns = [
        "Date",
        "Quality_Rate"
    ]

    st.dataframe(
        anomaly_df.head(15),
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No low-quality periods detected."
    )

# ============================================================
# MACHINE TABLE
# ============================================================

st.subheader("📋 Machine Performance Details")

display_table = machine_analysis.copy()

display_table.columns = [
    "Machine",
    "Average Quality (%)",
    "Minimum Quality (%)",
    "Maximum Quality (%)",
    "Total Production",
    "Total Defective",
    "Defect Rate (%)",
    "Quality Std"
]

st.dataframe(
    display_table,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Industrial Quality Analytics 2025 • "
    "Python • Pandas • Plotly • Streamlit"
)
