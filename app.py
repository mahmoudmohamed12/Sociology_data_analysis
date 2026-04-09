import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ESS Life Satisfaction Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #1a1a2e;
    }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Playfair Display', serif !important;
        color: #1a1a2e !important;
    }
    .main, [data-testid="stAppViewContainer"] {
        background-color: #f4f6fb;
    }
    [data-testid="block-container"] {
        background-color: #f4f6fb;
    }
    p, span, label, div, li, td, th,
    .stMarkdown, .stText,
    [data-testid="stMarkdownContainer"] {
        color: #1a1a2e !important;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 18px 20px;
        border-radius: 14px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border-left: 4px solid #4f46e5;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: #1a1a2e !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #e2e5f0;
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 500;
        color: #374151 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        color: #1a1a2e !important;
    }
    [data-testid="stSidebar"] {
        background-color: #1e1b4b !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] {
        background-color: #312e81 !important;
        border-color: #6366f1 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #4f46e5 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSlider"] * {
        color: #ffffff !important;
    }
    [data-testid="stExpander"] summary {
        color: #1a1a2e !important;
        font-weight: 600;
    }
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {
        color: #374151 !important;
    }
    [data-testid="stDataFrame"] * {
        color: #1a1a2e !important;
    }
    hr { border-color: #d1d5db; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "df_final.csv")

    if not os.path.exists(file_path):
        st.error(f"⚠️ **File Not Found:** Please ensure 'df_final.csv' is in: `{base_path}`")
        st.stop()

    df = pd.read_csv(file_path)

    # Bins for heatmaps
    if 'religiosity' in df.columns:
        df['rel_bins'] = pd.cut(df['religiosity'], bins=5, labels=['Very Low', 'Low', 'Mid', 'High', 'Very High'])
    if 'stfeco' in df.columns:
        df['eco_bins'] = pd.cut(df['stfeco'], bins=5, labels=['Very Low', 'Low', 'Mid', 'High', 'Very High'])

    # Age groups
    if 'agea' in df.columns:
        df['age_group'] = pd.cut(
            df['agea'],
            bins=[0, 25, 40, 55, 70, 120],
            labels=['18-25', '26-40', '41-55', '56-70', '71+']
        )

    # ISO map — supports BOTH 2-letter codes AND full country names
    iso_map = {
        # 2-letter codes (original ESS format)
        "AT": "AUT", "BE": "BEL", "CH": "CHE", "CZ": "CZE", "DE": "DEU",
        "DK": "DNK", "EE": "EST", "ES": "ESP", "FI": "FIN", "FR": "FRA",
        "GB": "GBR", "GR": "GRC", "HU": "HUN", "IE": "IRL", "IT": "ITA",
        "LT": "LTU", "NL": "NLD", "NO": "NOR", "PL": "POL", "PT": "PRT",
        "SE": "SWE", "SI": "SVN", "SK": "SVK",
        # Full country names
        "Austria": "AUT", "Belgium": "BEL", "Switzerland": "CHE",
        "Czech Republic": "CZE", "Czechia": "CZE", "Germany": "DEU",
        "Denmark": "DNK", "Estonia": "EST", "Spain": "ESP",
        "Finland": "FIN", "France": "FRA", "United Kingdom": "GBR",
        "Great Britain": "GBR", "Greece": "GRC", "Hungary": "HUN",
        "Ireland": "IRL", "Italy": "ITA", "Lithuania": "LTU",
        "Netherlands": "NLD", "Norway": "NOR", "Poland": "POL",
        "Portugal": "PRT", "Sweden": "SWE", "Slovenia": "SVN",
        "Slovakia": "SVK",
    }

    df["iso3"] = df["cntry"].map(iso_map)

    # Fallback: case-insensitive match for any remaining NaNs
    if df["iso3"].isna().any():
        iso_map_lower = {k.lower().strip(): v for k, v in iso_map.items()}
        mask = df["iso3"].isna()
        df.loc[mask, "iso3"] = df.loc[mask, "cntry"].apply(
            lambda c: iso_map_lower.get(str(c).lower().strip(), None)
        )

    return df

df_raw = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.markdown("## Filters")
st.sidebar.markdown("---")

countries = st.sidebar.multiselect(
    "Countries",
    options=sorted(df_raw["cntry"].unique()),
    default=sorted(df_raw["cntry"].unique())
)

secular_options = ["All"]
if "secular_status" in df_raw.columns:
    secular_options += list(df_raw["secular_status"].dropna().unique())
secular_filter = st.sidebar.selectbox("Secular Status", options=secular_options)

age_options = ["All"]
if "age_group" in df_raw.columns:
    age_options += list(df_raw["age_group"].cat.categories)
age_filter = st.sidebar.multiselect("Age Group", options=age_options[1:], default=age_options[1:])

st.sidebar.markdown("**Life Satisfaction Range**")
sat_min, sat_max = int(df_raw["stflife"].min()), int(df_raw["stflife"].max())
sat_range = st.sidebar.slider("", min_value=sat_min, max_value=sat_max, value=(sat_min, sat_max))

st.sidebar.markdown("---")
st.sidebar.markdown("*Data: European Social Survey (ESS)*")

# --- APPLY FILTERS ---
df = df_raw[df_raw["cntry"].isin(countries)].copy()
if secular_filter != "All" and "secular_status" in df.columns:
    df = df[df["secular_status"] == secular_filter]
if age_filter and "age_group" in df.columns:
    df = df[df["age_group"].isin(age_filter)]
df = df[(df["stflife"] >= sat_range[0]) & (df["stflife"] <= sat_range[1])]

# --- HEADER ---
st.title("Life Satisfaction in Europe")
st.markdown("Exploring social, economic, and cultural drivers of well-being using the **European Social Survey (ESS)**.")
st.divider()

# --- TOP METRICS ---
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Avg. Satisfaction", f"{df['stflife'].mean():.2f}")
m2.metric("Respondents", f"{len(df):,}")
m3.metric("Happiest Country", df.groupby('cntry')['stflife'].mean().idxmax() if not df.empty else "-")
m4.metric("Avg. Social Trust", f"{df['social_trust'].mean():.2f}")
m5.metric("Lowest Country", df.groupby('cntry')['stflife'].mean().idxmin() if not df.empty else "-")

st.divider()

# --- TABS ---
tab_geo, tab_drivers, tab_correlations, tab_radar = st.tabs([
    "Geography & Trends",
    "Key Drivers",
    "Deep Relationships",
    "Country Profiles"
])

# TAB 1: Geography
with tab_geo:
    col_a, col_b = st.columns([1.2, 0.8])

    with col_a:
        st.subheader("Secularization Map")
        if "secular_status" in df.columns and df["iso3"].notna().any():
            secular_pct = df.groupby("iso3").apply(
                lambda x: (x["secular_status"] == "Secular").sum() / len(x),
                include_groups=False
            ).reset_index()
            secular_pct.columns = ["iso3", "Secular_Rate"]
            fig_map = px.choropleth(
                secular_pct, locations="iso3", color="Secular_Rate",
                color_continuous_scale="Viridis", scope="europe",
                title="Percentage of Secular Population by Country"
            )
            fig_map.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Could not render map: country names could not be matched to ISO codes. Check your `cntry` column values.")

    with col_b:
        st.subheader("Distribution by Country")
        fig_box = px.box(df, x="cntry", y="stflife", color="cntry",
                         title="Life Satisfaction Variance",
                         color_discrete_sequence=px.colors.qualitative.Vivid)
        fig_box.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
        st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("Country Ranking by Average Life Satisfaction")
    avg_by_country = df.groupby("cntry")["stflife"].mean().reset_index().sort_values("stflife", ascending=False)
    fig_bar = px.bar(
        avg_by_country, x="cntry", y="stflife", color="stflife",
        color_continuous_scale="RdYlGn", text_auto=".2f",
        title="Average Life Satisfaction per Country (Descending)"
    )
    fig_bar.update_layout(
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_family="DM Sans", yaxis_title="Avg. Life Satisfaction", xaxis_title="Country"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# TAB 2: Key Drivers
with tab_drivers:
    st.subheader("What Drives Happiness?")
    col_c, col_d = st.columns(2)

    with col_c:
        fig_eco = px.scatter(df, x="stfeco", y="stflife", trendline="ols",
                             opacity=0.2, title="Economic Satisfaction vs. Life Satisfaction",
                             color_discrete_sequence=['#10b981'])
        fig_eco.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
        st.plotly_chart(fig_eco, use_container_width=True)

    with col_d:
        fig_trust = px.scatter(df, x="social_trust", y="stflife", trendline="ols",
                               opacity=0.2, title="Social Trust vs. Life Satisfaction",
                               color_discrete_sequence=['#6366f1'])
        fig_trust.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
        st.plotly_chart(fig_trust, use_container_width=True)

    if "age_group" in df.columns:
        st.subheader("Life Satisfaction by Age Group")
        age_sat = df.groupby("age_group", observed=True)["stflife"].mean().reset_index()
        fig_age = px.bar(age_sat, x="age_group", y="stflife",
                         color="stflife", color_continuous_scale="Blues",
                         text_auto=".2f", title="Average Life Satisfaction Across Age Groups")
        fig_age.update_layout(
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_family="DM Sans", xaxis_title="Age Group", yaxis_title="Avg. Life Satisfaction"
        )
        st.plotly_chart(fig_age, use_container_width=True)

# TAB 3: Correlations
with tab_correlations:
    col_e, col_f = st.columns([1, 1])

    with col_e:
        st.subheader("The Interaction Matrix")
        corr_cols = ['stflife', 'social_trust', 'inst_trust', 'religiosity', 'stfeco', 'immigration_attitude']
        available_cols = [c for c in corr_cols if c in df.columns]
        if len(available_cols) >= 2:
            corr = df[available_cols].corr()
            fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale='RdBu_r',
                                 aspect="auto", title="Correlation Heatmap")
            fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
            st.plotly_chart(fig_corr, use_container_width=True)

    with col_f:
        st.subheader("Economy x Religiosity Interaction")
        if 'rel_bins' in df.columns and 'eco_bins' in df.columns:
            pivot_data = df.pivot_table(index="rel_bins", columns="eco_bins",
                                        values="stflife", aggfunc="mean")
            fig_heat = px.imshow(pivot_data, text_auto=".1f", color_continuous_scale="YlGnBu",
                                 labels=dict(x="Economic Satisfaction", y="Religiosity", color="Life Sat."))
            fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
            st.plotly_chart(fig_heat, use_container_width=True)

    if "secular_status" in df.columns:
        st.subheader("Life Satisfaction: Secular vs. Religious")
        fig_violin = px.violin(df, x="secular_status", y="stflife", color="secular_status",
                               box=True, points="outliers",
                               color_discrete_map={"Secular": "#6366f1", "Religious": "#f59e0b"},
                               title="Distribution of Life Satisfaction by Secular Status")
        fig_violin.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
        st.plotly_chart(fig_violin, use_container_width=True)

# TAB 4: Radar
with tab_radar:
    st.subheader("Multi-Dimensional Country Profile Radar")
    st.markdown("Compare countries across all key well-being dimensions simultaneously.")

    radar_cols = ['stflife', 'social_trust', 'inst_trust', 'stfeco', 'religiosity']
    available_radar = [c for c in radar_cols if c in df.columns]

    if available_radar:
        selected_countries_radar = st.multiselect(
            "Choose up to 6 countries to compare",
            options=sorted(df["cntry"].unique()),
            default=sorted(df["cntry"].unique())[:4],
            max_selections=6
        )

        if selected_countries_radar:
            radar_data = (
                df[df["cntry"].isin(selected_countries_radar)]
                .groupby("cntry")[available_radar]
                .mean()
                .reset_index()
            )

            for col in available_radar:
                col_min = df[col].min()
                col_max = df[col].max()
                radar_data[col + "_norm"] = (radar_data[col] - col_min) / (col_max - col_min + 1e-9)

            norm_cols = [c + "_norm" for c in available_radar]
            labels = [c.replace("_", " ").replace("stf", "Satisfaction: ").title() for c in available_radar]
            labels_closed = labels + [labels[0]]

            palette = px.colors.qualitative.Bold
            fig_radar = go.Figure()

            for i, row in radar_data.iterrows():
                values = [row[c] for c in norm_cols] + [row[norm_cols[0]]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=values, theta=labels_closed, fill='toself',
                    name=row["cntry"],
                    line_color=palette[i % len(palette)],
                    opacity=0.7
                ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1], tickformat=".0%")),
                showlegend=True,
                title="Normalized Country Profiles (0 = lowest, 1 = highest in dataset)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="DM Sans",
                height=520
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            with st.expander("View Raw Averages"):
                display_df = radar_data[["cntry"] + available_radar].set_index("cntry")
                display_df.columns = labels
                st.dataframe(display_df.style.format("{:.2f}").background_gradient(cmap="YlGn"),
                             use_container_width=True)
    else:
        st.warning("Radar chart requires at least one of: stflife, social_trust, inst_trust, stfeco, religiosity")

# --- FOOTER ---
st.divider()
with st.expander("Data Interpretation Guide"):
    st.markdown("""
    - **Economic Satisfaction (stfeco):** Scale 0-10 rating of the current national economy.
    - **Social Trust:** Composite score reflecting how much respondents believe people are fair and helpful.
    - **Institutional Trust (inst_trust):** Trust in parliament, police, and legal institutions.
    - **Secular Status:** Derived from religiosity scores; "Secular" = low religious practice.
    - **OLS Trendlines:** Indicate strength of linear relationship between variables.
    - **Radar Chart:** Values normalized 0-1 across the full dataset for cross-variable comparability.
    - **Age Groups:** Constructed from the agea (age in years) column.
    """)