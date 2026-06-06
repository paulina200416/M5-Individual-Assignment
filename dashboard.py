
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="COVID Dashboard",
    layout="wide"
)

# We load the data base 
@st.cache_data
def load_data():
    df = pd.read_csv("WHO-COVID-19-global-data.csv")
    df["Date_reported"] = pd.to_datetime(df["Date_reported"])
    return df

df = load_data()

# Color correction from side bar 
st.markdown("""
<style>

/* Import font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

/* Apply font everywhere */
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Main background */
.stApp {
    background-color: #F4F8FB;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1E293B !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] strong {
    color: #F8FAFC !important;
}

</style>
""", unsafe_allow_html=True)


# We do the absoulute cumulative global totals for the KPI cards
latest = df.sort_values("Date_reported").groupby("Country").last()
total_cases = latest["Cumulative_cases"].sum()
total_deaths = latest["Cumulative_deaths"].sum()
countries_count = latest.shape[0]

# Global weekly deltas

latest_date = df["Date_reported"].max()
latest_week_data = df[df["Date_reported"] == latest_date]
total_new_cases_week = latest_week_data["New_cases"].sum()
total_new_deaths_week = latest_week_data["New_deaths"].sum()


# We add new color design in the side bar 

st.markdown("""
<style>

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #DCEFFD !important;
}

/* Sidebar text */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] strong {
    color: #0F4C81 !important;
}

/* Sidebar captions */
[data-testid="stSidebar"] .stCaption p {
    color: #475569 !important;
}

</style>
""", unsafe_allow_html=True)


# We do function to make number formats for KPI'S more readable
def format_number(num):
    if pd.isna(num):
        return "0"
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(int(num))


# We create sidebar 

with st.sidebar:
    st.image("https://img.icons8.com/color/96/coronavirus.png", width=70)
    st.title("Visualization framework")
    
    st.markdown("### Role & Stakeholders")
    st.markdown("**Role:** Public Health Analyst")
    st.markdown("**Stakeholders:** Public health officials")
    st.caption("Keeping and interpreting public health trends to understand the outbreak evolution.")
    
    st.divider()
    
    st.markdown("### Storyline")
    st.info(
        "\"Even if COVID-19 was a global crisis, its evolution, timing, and impact "
        "changed a lot across regions and countries. This highlights the "
        "importance of context-specifi public health responses.\""
    )


#We add title and navigation tabs  

st.markdown("""
<h1 style='color:#0F4C81;'>
One Pandemic, Many Realities
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<h4 style='color:#64748B; font-style:bold;'>
Was COVID-19 experienced the same across the world?
</h4>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    "Global Evolution",
    "Regional & Country impact",
])


#KPI design change 
st.markdown("""
<style>

/* KPI Number */
[data-testid="stMetricValue"] {
    font-size: 50px !important;
    font-weight: 700 !important;
    color: #0F4C81 !important;
}

/* KPI Label */
[data-testid="stMetricLabel"] p {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #334155 !important;
}

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# TAB 1: GLOBAL EVOLUTION (The Problem Introduction)
# ==============================================================================

with tab1:
    # Card 1: Narrative Intro
    with st.container(border=True):

        st.markdown("""
        <h2 style='
            color:#0F4C81;
            font-size:38px;
            font-weight:700;
            margin-bottom:10px;
        '>
        Global Evolution
        </h2>
        """, unsafe_allow_html=True)


    start_date = df["Date_reported"].min()
    end_date = df["Date_reported"].max()
    period = f"{start_date.year}-{end_date.year}"


    # View the scale of the Pandemic
    with st.container(border=True):

     st.markdown("### The Scale of the pandemic")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            label="Cases reported",
            value=format_number(total_cases)
        )
        st.caption("Confirmed worldwide")

    with k2:
        st.metric(
            label="Lives lost",
            value=format_number(total_deaths)
        )
        st.caption("Reported COVID-related deaths")

    with k3:
        st.metric(
            label="Countries & territories",
            value=countries_count
        )
        st.caption("WHO reporting locations")

    with k4:
        st.metric(
            label="Years covered",
            value="2020–2025"
        )
        st.caption("Pandemic timeline")

   

    # Chart one: Hero timeline (show pandemic evolution through years. Interactive feature)

    with st.container(border=True):
        st.subheader("The pandemic came in waves")
        st.write(
            "COVID-19 did not unfold as a single continuous outbreak. "
            "Instead, the world experienced multiple waves of infection. Use the chart "
            "below to explore how global cases changed over time."
        )

        # Global cases by date
        global_cases = df.groupby("Date_reported")["New_cases"].sum().reset_index()

        # Create 7-day average
        global_cases["Cases_7Day_Avg"] = global_cases["New_cases"].rolling(window=7, min_periods=1).mean()

        # We build the Interactive selector of time periods
        selected_period = st.selectbox(
            "Focus on:",
            ["Entire pandemic", "2020", "2021", "2022", "2023+"]
        )

        # We build a filter according to the selection
        filtered_data = global_cases.copy()
        if selected_period == "2020":
            filtered_data = global_cases[global_cases["Date_reported"].dt.year == 2020]
        elif selected_period == "2021":
            filtered_data = [global_cases["Date_reported"].dt.year == 2021]
        elif selected_period == "2022":
            filtered_data = global_cases[global_cases["Date_reported"].dt.year == 2022]
        elif selected_period == "2023+":
            filtered_data = global_cases[global_cases["Date_reported"].dt.year >= 2023]

        #We build the graph 

        fig = px.line(
            filtered_data,
            x="Date_reported",
            y="Cases_7Day_Avg",
            title="Global COVID-19 evolution",
            color_discrete_sequence=["#1D4ED8"] 
        )

        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="7-Day Average of new cases"
        )

        #Remove line background and leave it blank

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)


        #Chart 2 - The highest waves arent the deadliest

        with st.container(border=True):
               st.subheader("The Highest Waves Aren't the Deadliest")
               st.markdown("""
        Select one of the largest infection waves and compare the number of cases
        and deaths reported at that time. Notice how the largest transmission
        waves did not always correspond to the highest 
        mortality levels.
        """)
               
        # We build a global timeline

               global_timeline = (
        df.groupby("Date_reported")
        .agg({
            "New_cases": "sum",
            "New_deaths": "sum"
        })
        .reset_index()
        .sort_values("Date_reported")
        )
               
        # We find the 7-day averages

        global_timeline["Cases_7Day_Avg"] = (
         global_timeline["New_cases"]
        .rolling(window=7, min_periods=1)
        .mean()
        )

        global_timeline["Deaths_7Day_Avg"] = (
        global_timeline["New_deaths"]
        .rolling(window=7, min_periods=1)
        .mean()
        )

        # We find major peaks

        candidate_peaks = (
        global_timeline
        .sort_values("Cases_7Day_Avg", ascending=False)
        .head(30)
        )

        selected_peaks = []

        for _, row in candidate_peaks.iterrows():

         if len(selected_peaks) == 0:
            selected_peaks.append(row)

        else:
            keep_peak = True

            for exsisting_peak in selected_peaks:

                days_apart = abs(
                    (row["Date_reported"] - exsisting_peak["Date_reported"]).days
                )

                if days_apart < 90:
                    keep_peak = False
                    break

                if keep_peak:
                   selected_peaks.append(row)

                if len(selected_peaks) == 5:
                      break

        peak_df = pd.DataFrame(selected_peaks)

        peak_df = peak_df.sort_values(
        "Cases_7Day_Avg",
        ascending=False
       ).reset_index(drop=True)
        
        # Build the interactive selector

        peak_labels = [
        f"#{i+1} Peak — {row['Date_reported'].strftime('%b %Y')}"
        for i, row in peak_df.iterrows()
        ]

        selected_label = st.radio(
        "Choose a wave to investigate:",
        peak_labels
       )

        selected_idx = peak_labels.index(selected_label)

        selected_peak = peak_df.iloc[selected_idx]

        # Do Percent of Peak Comparison

        max_cases_peak = global_timeline["Cases_7Day_Avg"].max()
        max_deaths_peak = global_timeline["Deaths_7Day_Avg"].max()

        cases_pct = (
        selected_peak["Cases_7Day_Avg"] /
         max_cases_peak
         ) * 100
        
        deaths_pct = (
            selected_peak["Deaths_7Day_Avg"] /
            max_deaths_peak
            ) * 100
        comparison_df = pd.DataFrame({
            "Metric": [
                "Cases",
                "Deaths"
         ],
         "Percent of Peak": [
         cases_pct,
         deaths_pct
         ]
        })

        
        fig_compare = px.bar(
            comparison_df,
            x="Metric",
            y="Percent of Peak",
            color="Metric",
            text="Percent of Peak",
            color_discrete_map={
               "Cases": "#102868",
               "Deaths": "#404040"
             }
        )

        
        fig_compare.update_traces(
         texttemplate="%{text:.0f}%",
         textposition="outside"
        )

        fig_compare.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="",
        yaxis_title="Percent of All-Time Peak",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20)
        )

        fig_compare.update_xaxes(showgrid=False)

        fig_compare.update_yaxes(
          range=[0, 110],
          showgrid=False
        )

        st.plotly_chart(
           fig_compare,
           use_container_width=True
        )

        #Do dynamic insight

        st.info(
           f"""
        📌 **Selected wave:** {selected_peak['Date_reported'].strftime('%B %Y')}
        This wave reached **{cases_pct:.0f}%** of the pandemic's highest case peak.
        However, deaths reached only **{deaths_pct:.0f}%** of the pandemic's highest death peak.
         """
        )

        # Chart 3 - Cases and deaths gradually moved apart
        with st.container(border=True):
         st.subheader("Cases and deaths gradually moved apart")
         st.write(
            "The relationship between infections and mortality changed over time. " \
            "This reflects the impact of vaccination, improved treatments and " 
            "growing population immunity"
        )

        import plotly.graph_objects as go

        # We build Monthly aggregation
        monthly = (
            df.groupby(pd.Grouper(key="Date_reported", freq="ME"))
            [["New_cases", "New_deaths"]]
             .sum()
             .reset_index()
             )
        
        # Normalize each series to its own peak
        monthly["Cases_PctPeak"] = (
            monthly["New_cases"] /
            monthly["New_cases"].max()
        ) * 100

        monthly["Deaths_PctPeak"] = (
            monthly["New_deaths"] /
            monthly["New_deaths"].max()
        ) * 100

        # We plot the graph
        fig = go.Figure()

        fig.add_trace(
           go.Scatter(
               x=monthly["Date_reported"],
               y=monthly["Cases_PctPeak"],
               mode="lines",
               name="Cases",
               line=dict(width=3)

              )
            )
        
        fig.add_trace(
            go.Scatter(
                x=monthly["Date_reported"],
                y=monthly["Deaths_PctPeak"],
                mode="lines",
                name="Deaths",
                line=dict(width=3, dash="dash")

              )
            )
        
        fig.update_layout(
            title="Cases and deaths gradually moved apart",
            xaxis_title="Date",
            yaxis_title="Percent of peak (%)",
            height=500,
            template="plotly_white",
            legend_title=""
            
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

        st.plotly_chart(fig, use_container_width=True)


#===================
# TAB 2: REGIONAL PATTERNS 
# =============================================================================

with tab2:
    # Card 2: Who was affacted the most? region impact and its countries 
    with st.container(border=True):

        st.markdown("""
        <h2 style='
            color:#0F4C81;
            font-size:38px;
            font-weight:700;
            margin-bottom:10px;
        '>
        Region and countries impact
        </h2>
        """, unsafe_allow_html=True)

        # Did every region face the same intensity during the pandemic?
    with st.container(border=True):
     st.markdown("### Selected region snapshot")
     st.markdown("Even if COVID-19 was a global crisis, "
                "its intensity varied across regions. " 
                "Explore how each WHO region contributed to the overall " 
                "impact and compare their share of cases, deaths,"
                " and mortality.")

     #We build the region selector 

     region_options = {
         "Africa":  "AFRO",
         "Americas": "AMRO",
         "Eastern Mediterranean": "EMRO",
         "Europe": "EURO",
         "South-East Asia": "SEARO",
         "Western Pacific": "WPRO"

         }
     
     selected_region_label = st.radio(
         "Select a WHO Region",
         list(region_options.keys()),
         horizontal=True

         )
     
     selected_region = region_options[selected_region_label]


     #We filter the data 

     region_df = df[df["WHO_region"] == selected_region]

     #We calculate KPIS

     # Totals
     total_cases = region_df["New_cases"].sum()
     total_deaths = region_df["New_deaths"].sum()

     # CFR
     cfr = (
          (total_deaths / total_cases) * 100
          if total_cases > 0
          else 0
        )
     
     # Global deaths share
     global_deaths = df["New_deaths"].sum()

     death_share = (
         (total_deaths / global_deaths) * 100
             if global_deaths > 0
             else 0
        )
     
     #We correct the format of the numbers for better visualization

     def format_number(num):
         if pd.isna(num):
             return "0"
         if num >= 1_000_000_000:
             return f"{num / 1_000_000_000:.1f}B"
         elif num >= 1_000_000:
             return f"{num / 1_000_000:.1f}M"
         elif num >= 1_000:
             return f"{num / 1_000:.1f}K"
         
         else:
             return f"{num:.0f}"


     #We create the KPI cards 

     col1, col2, col3, col4 = st.columns(4)

     with col1:
         st.metric(
            "Total Cases",
            format_number(total_cases)

        )
         
     with col2:
         st.metric(
             "Total Deaths",
             format_number(total_deaths)
        )
         
    with col3:
        st.metric(
            "Case fatality rate",
             f"{cfr:.2f}%"

         )
        
    with col4:
        st.metric(
          "Share of Global deaths",
          f"{death_share:.1f}%"

         )


    # Ensure data is clean (fill NaN with 0)
    df['New_cases'] = df['New_cases'].fillna(0)
    df['New_deaths'] = df['New_deaths'].fillna(0)


    #Build a TOP 10 Country ranking


    with st.container(border=True):
     st.markdown("###  Which countries were the most affected?")
     st.markdown("Regional totals were often driven by a small number of countries. "
                "Use the ranking below to recognize the nations that contributed the " 
                "most to the selected region's reported cases and deaths.")

    metric_choice = st.radio(
        "Rank countries by:",
        ["Total Cases", "Total Deaths"],
        horizontal=True
    
    )

    country_summary = (
        region_df.groupby("Country")
        .agg(
            Total_Cases=("New_cases", "sum"),
            Total_Deaths=("New_deaths", "sum")
        )

        .reset_index()

        )
    
    if metric_choice == "Total Cases":
        metric_col = "Total_Cases"

    else:
        metric_col = "Total_Deaths"

    top_countries = (
        country_summary
        .sort_values(metric_col, ascending=False)
        .head(10)

    )

    #Highlight countries that are the most affected 

    top_countries["Color"] = "Other"
    top3_idx = top_countries.nlargest(3, metric_col).index
    top_countries.loc[top3_idx, "Color"] = "Top 3"

    top_countries["Label"] = top_countries[metric_col].apply(format_number)


    fig = px.bar(
        top_countries.sort_values(metric_col),
        x=metric_col,
        y="Country",
        orientation="h",
        text=metric_col,
        color="Color",
        color_discrete_map={
          "Top 3": "#0B3C6D",
          "Other": "#FAF1F1"    
          },
        title=f"Which countries were most affected? {metric_choice}"

    )

    fig.update_traces(
        textposition="outside"

    )

    fig.update_layout(
        height=500,
        template="plotly_white",
        yaxis_title="",
        xaxis_title="",
        showlegend=False

    )

    st.plotly_chart(fig, use_container_width=True)

    #World map chart - explore a country 


    st.subheader(f"🌍 Explore Countries in {selected_region_label}")
    st.markdown("Behind every regional trend is a unique national story." \
                " Each country had its own movement in the pandemic which brings different types of " 
                "responses to take action to address the issue.    " 
                 "If you want to explore another region, change your region "
                "selection in the snapshot")

    #Build a regional map 

    country_map = (
         region_df.groupby("Country")
         .agg(
             Total_Cases=("New_cases", "sum")
        )
         .reset_index()

        )
    
    fig_map = px.choropleth(
        country_map,
        locations="Country",
        locationmode="country names",
        color="Total_Cases",
        hover_name="Country",
        projection="natural earth",
        color_continuous_scale="Blues"
    )

    fig_map.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    st.plotly_chart(fig_map, use_container_width=True)

    #Build country selector

    selected_country = st.selectbox(
        "Select a country to explore",
        sorted(region_df["Country"].unique())
    )

    country_df = region_df[
        region_df["Country"] == selected_country
    ]

    #Show and build country selected snapshot 

    st.markdown("### Country snapshot")

    country_cases = country_df["New_cases"].sum()
    country_deaths = country_df["New_deaths"].sum()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Cases",
            format_number(country_cases)
        )

    with col2:
        st.metric(
            "Total Deaths",
            format_number(country_deaths)
        )

    #Show and build the worst wave

    peak_case_row = country_df.loc[
        country_df["New_cases"].idxmax()
    ]

    peak_death_row = country_df.loc[
        country_df["New_deaths"].idxmax()
    ]

    st.markdown("### When Did This Country Face Its Worst Wave?")
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Peak Cases",
            format_number(peak_case_row["New_cases"])
        )

        st.caption(
        f"Occurred on {peak_case_row['Date_reported'].strftime('%b %Y')}"
        )

    with col2:
        st.metric(
            "Peak Deaths",
            format_number(peak_death_row["New_deaths"])
        )

        st.caption(
             f"Occurred on {peak_death_row['Date_reported'].strftime('%b %Y')}"
        )

    #Show and build country journey

    st.markdown("### Country Journey")

    fig_country = px.line(
        country_df,
        x="Date_reported",
        y="New_cases",
        title=f"{selected_country}: COVID-19 Journey"
    )

    fig_country.update_layout(
        template="plotly_white",
        xaxis_title="",
        yaxis_title="New Cases",
        height=450
    )

    #Remove background from graph 

    fig_country.update_xaxes(showgrid=False)
    fig_country.update_yaxes(showgrid=False)

    st.plotly_chart(fig_country, use_container_width=True)