import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Industrial Quality Analytics 2025",
    page_icon="🏭",
    layout="wide"
)


# ============================================================
# CUSTOM STYLE
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #F5F7FA;
}

h1 {
    color: #1F2937;
    font-weight: 700;
}

h2, h3 {
    color: #374151;
}

[data-testid="stMetric"] {
    background-color: white;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    border: 1px solid #E5E7EB;
}

[data-testid="stMetricLabel"] {
    font-size: 15px;
}

[data-testid="stMetricValue"] {
    font-size: 30px;
    font-weight: 700;
}

.insight-card {
    background-color: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
    min-height: 150px;
}

.insight-title {
    font-size: 18px;
    font-weight: 700;
    color: #1F2937;
    margin-bottom: 10px;
}

.insight-text {
    font-size: 15px;
    color: #4B5563;
    line-height: 1.6;
}

.footer {
    text-align: center;
    color: #9CA3AF;
    font-size: 14px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD AND CLEAN DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("Qualite_industrielle.csv")

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Normalize possible column names
    column_mapping = {}

    for col in df.columns:

        clean_col = col.lower()

        if clean_col == "date":
            column_mapping[col] = "Date"

        elif clean_col in ["machine", "machines"]:
            column_mapping[col] = "Machine"

        elif clean_col in [
            "units_produced",
            "unit_produced",
            "produced_units",
            "production"
        ]:
            column_mapping[col] = "Units_Produced"

        elif clean_col in [
            "defective_units",
            "defective_unit",
            "defects",
            "defective"
        ]:
            column_mapping[col] = "Defective_Units"

        elif clean_col in [
            "quality_rate",
            "qualityrate",
            "quality",
            "quality_percentage"
        ]:
            column_mapping[col] = "Quality_Rate"

    df = df.rename(columns=column_mapping)

    # Required columns
    required_columns = [
        "Date",
        "Machine",
        "Units_Produced",
        "Defective_Units",
        "Quality_Rate"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        st.error(
            "❌ Some required columns are missing from the CSV."
        )

        st.write(
            "Columns detected:"
        )

        st.write(
            df.columns.tolist()
        )

        st.write(
            "Missing columns:"
        )

        st.write(
            missing_columns
        )

        st.stop()

    # Convert date
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Convert numerical columns
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

    # Remove invalid dates
    df = df.dropna(
        subset=["Date"]
    )

    # Sort
    df = df.sort_values(
        "Date"
    )

    return df


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()


# ============================================================
# TITLE
# ============================================================

st.title(
    "🏭 Industrial Quality Analytics"
)

st.markdown(
    """
    ### 2025 Machine Performance Dashboard

    Interactive analysis of industrial quality,
    production performance, machine stability
    and quality anomalies.
    """
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚙️ Dashboard Filters"
)

machines = [
    "All Machines"
] + sorted(
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
# GLOBAL KPIs
# ============================================================

global_quality = (
    filtered_df["Quality_Rate"].mean()
)

total_units = (
    filtered_df["Units_Produced"].sum()
)

total_defective = (
    filtered_df["Defective_Units"].sum()
)

if total_units > 0:

    defect_rate = (
        total_defective /
        total_units
    ) * 100

else:

    defect_rate = 0

number_machines = (
    filtered_df["Machine"].nunique()
)


# ============================================================
# FORMAT PRODUCTION
# ============================================================

def format_number(value):

    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"

    else:
        return f"{value:,.0f}"


production_display = format_number(
    total_units
)


# ============================================================
# KPI SECTION
# ============================================================

st.subheader(
    "📊 Executive Overview"
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "✅ Quality Rate",
        f"{global_quality:.2f}%"
    )


with col2:

    st.metric(
        "📦 Total Production",
        production_display
    )


with col3:

    st.metric(
        "❌ Defect Rate",
        f"{defect_rate:.2f}%"
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

st.subheader(
    "📈 Quality Rate Evolution"
)

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
    title="Industrial Quality Rate — 2025"
)


fig_quality.update_layout(
    xaxis_title="Date",
    yaxis_title="Quality Rate (%)",
    hovermode="x unified",
    template="plotly_white"
)


fig_quality.update_traces(
    line_width=2
)


fig_quality.add_hline(
    y=global_quality,
    line_dash="dash",
    annotation_text=(
        f"Average: {global_quality:.2f}%"
    )
)


st.plotly_chart(
    fig_quality,
    use_container_width=True
)


# ============================================================
# MACHINE PERFORMANCE
# ============================================================

st.subheader(
    "🏭 Machine Performance"
)


machine_analysis = (
    filtered_df
    .groupby("Machine")
    .agg(
        Average_Quality=(
            "Quality_Rate",
            "mean"
        ),

        Minimum_Quality=(
            "Quality_Rate",
            "min"
        ),

        Maximum_Quality=(
            "Quality_Rate",
            "max"
        ),

        Total_Production=(
            "Units_Produced",
            "sum"
        ),

        Total_Defective=(
            "Defective_Units",
            "sum"
        )
    )
    .reset_index()
)


# ============================================================
# DEFECT RATE
# ============================================================

machine_analysis[
    "Defect_Rate"
] = (

    machine_analysis[
        "Total_Defective"
    ]

    /

    machine_analysis[
        "Total_Production"
    ].replace(
        0,
        np.nan
    )

) * 100


# ============================================================
# QUALITY STABILITY
# ============================================================

quality_std = (
    filtered_df
    .groupby("Machine")[
        "Quality_Rate"
    ]
    .std()
    .reset_index()
)


quality_std.columns = [
    "Machine",
    "Quality_Std"
]


machine_analysis = machine_analysis.merge(
    quality_std,
    on="Machine",
    how="left"
)


machine_analysis[
    "Quality_Std"
] = machine_analysis[
    "Quality_Std"
].fillna(0)


# ============================================================
# SORT
# ============================================================

machine_analysis = (
    machine_analysis
    .sort_values(
        "Average_Quality",
        ascending=False
    )
)


# ============================================================
# MACHINE BAR CHART
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
    yaxis_title="Machine",
    template="plotly_white",
    xaxis=dict(
        range=[
            max(
                0,
                machine_analysis[
                    "Average_Quality"
                ].min() - 2
            ),
            100
        ]
    )
)


st.plotly_chart(
    fig_machine,
    use_container_width=True
)


# ============================================================
# QUALITY VS STABILITY
# ============================================================

col_left, col_right = st.columns(2)


with col_left:

    st.subheader(
        "📊 Quality vs Stability"
    )

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
        yaxis_title="Average Quality (%)",
        template="plotly_white"
    )


    st.plotly_chart(
        fig_stability,
        use_container_width=True
    )


# ============================================================
# PRODUCTION VS DEFECTS
# ============================================================

with col_right:

    st.subheader(
        "📦 Production vs Defects"
    )


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
        yaxis_title="Total Defective Units",
        template="plotly_white"
    )


    st.plotly_chart(
        fig_defects,
        use_container_width=True
    )


# ============================================================
# LOW QUALITY PERIODS
# ============================================================

st.subheader(
    "⚠️ Low Quality Periods"
)


daily_quality_all = (
    filtered_df
    .groupby("Date")[
        "Quality_Rate"
    ]
    .mean()
)


quality_mean = (
    daily_quality_all.mean()
)


quality_std_daily = (
    daily_quality_all.std()
)


threshold = (
    quality_mean -
    quality_std_daily
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

    anomaly_df[
        "Quality_Rate"
    ] = anomaly_df[
        "Quality_Rate"
    ].round(2)

    st.dataframe(
        anomaly_df.head(15),
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "✅ No low-quality periods detected."
    )


# ============================================================
# INDUSTRIAL INSIGHTS
# ============================================================

st.divider()

st.subheader(
    "💡 Industrial Insights"
)


best_machine = (
    machine_analysis
    .iloc[0]
)


worst_machine = (
    machine_analysis
    .iloc[-1]
)


best_machine_name = (
    best_machine["Machine"]
)

best_machine_quality = (
    best_machine["Average_Quality"]
)

worst_machine_name = (
    worst_machine["Machine"]
)

worst_machine_quality = (
    worst_machine["Average_Quality"]
)


insight1, insight2 = st.columns(2)


with insight1:

    st.markdown(
        f"""
        <div class="insight-card">

        <div class="insight-title">
        🥇 Highest Quality Performance
        </div>

        <div class="insight-text">

        <b>{best_machine_name}</b>
        recorded the highest average quality
        rate among the analyzed machines.

        <br><br>

        Average Quality:
        <b>{best_machine_quality:.2f}%</b>

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with insight2:

    st.markdown(
        f"""
        <div class="insight-card">

        <div class="insight-title">
        ⚠️ Lowest Quality Performance
        </div>

        <div class="insight-text">

        <b>{worst_machine_name}</b>
        recorded the lowest average quality
        rate in the dataset.

        <br><br>

        Average Quality:
        <b>{worst_machine_quality:.2f}%</b>

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


insight3, insight4 = st.columns(2)


with insight3:

    st.markdown(
        f"""
        <div class="insight-card">

        <div class="insight-title">
        📉 Quality Monitoring
        </div>

        <div class="insight-text">

        The overall average quality rate is
        <b>{global_quality:.2f}%</b>.

        The statistical detection threshold
        is <b>{threshold:.2f}%</b>.

        <br><br>

        <b>{len(low_quality_days)}</b>
        low-quality days were detected.

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with insight4:

    st.markdown(
        f"""
        <div class="insight-card">

        <div class="insight-title">
        🏭 Production Quality
        </div>

        <div class="insight-text">

        The analyzed production volume is
        <b>{production_display}</b> units.

        <br><br>

        The overall defective-unit rate is
        <b>{defect_rate:.2f}%</b>.

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MACHINE PERFORMANCE TABLE
# ============================================================

st.divider()

st.subheader(
    "📋 Machine Performance Details"
)


display_table = (
    machine_analysis.copy()
)


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


display_table[
    "Average Quality (%)"
] = display_table[
    "Average Quality (%)"
].round(2)


display_table[
    "Minimum Quality (%)"
] = display_table[
    "Minimum Quality (%)"
].round(2)


display_table[
    "Maximum Quality (%)"
] = display_table[
    "Maximum Quality (%)"
].round(2)


display_table[
    "Defect Rate (%)"
] = display_table[
    "Defect Rate (%)"
].round(2)


display_table[
    "Quality Std"
] = display_table[
    "Quality Std"
].round(3)


st.dataframe(
    display_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# PERFORMANCE SUMMARY
# ============================================================

st.divider()

st.subheader(
    "🏆 Performance Summary"
)


col1, col2 = st.columns(2)


with col1:

    st.info(
        f"""
        **🥇 Highest Average Quality**

        {best_machine_name}

        **Quality Rate: {best_machine_quality:.2f}%**
        """
    )


with col2:

    st.warning(
        f"""
        **⚠️ Lowest Average Quality**

        {worst_machine_name}

        **Quality Rate: {worst_machine_quality:.2f}%**
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">

    <b>Industrial Quality Analytics 2025</b>
    <br>
    Python • Pandas • Plotly • Streamlit
    <br>
    Industrial Data Analysis & Machine Performance Monitoring

    </div>
    """,
    unsafe_allow_html=True
)
