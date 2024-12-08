import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import warnings
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

warnings.simplefilter(action='ignore', category=FutureWarning)

st.title("🕵️ Analysis")
# st.markdown("This interactive dashboard supports the exploration of the mental health data of the people from different countries. You can filter by the country of the person.")
df = pd.read_csv("data/processed/mental_health_country.csv")

tmp_df = df.copy()
tmp_df.drop(columns=['User_ID'], inplace=True)
tmp_df['Gender'] = LabelEncoder().fit_transform(df['Gender'])
tmp_df['Occupation'] = LabelEncoder().fit_transform(df['Occupation'])
tmp_df['Country'] = LabelEncoder().fit_transform(df['Country'])
tmp_df['Mental_Health_Issue'] = LabelEncoder().fit_transform(df['Mental_Health_Issue'])
tmp_df['Consultation_History'] = LabelEncoder().fit_transform(df['Consultation_History'])
tmp_df['Stress_Level'] = LabelEncoder().fit_transform(df['Stress_Level'])

st.write("## Feature Correlation Heatmap:")

correlation_matrix = tmp_df.corr()

correlation_data = correlation_matrix.reset_index().melt(
    id_vars="index", 
    var_name="FeatureX", 
    value_name="Correlation"
)
correlation_data.rename(columns={"index": "FeatureY"}, inplace=True)

correlation_data["FeatureX"] = correlation_data["FeatureX"].str.replace("_", " ")
correlation_data["FeatureY"] = correlation_data["FeatureY"].str.replace("_", " ")

heatmap = alt.Chart(correlation_data).mark_rect().encode(
    x=alt.X(
        "FeatureX:N",
        title=None,
        sort=list(correlation_matrix.columns.str.replace("_", " ")),
        axis=alt.Axis(
            labelAngle=-90, 
            labelAlign="right",
            labelBaseline="middle" 
        )
    ),
    y=alt.Y(
        "FeatureY:N",
        title=None,
        axis=None,
        sort=list(correlation_matrix.index.str.replace("_", " "))
    ),
    color=alt.Color("Correlation:Q", scale=alt.Scale(scheme="blues")),
    tooltip=["FeatureX", "FeatureY", alt.Tooltip("Correlation:Q", format=".2f")]
).properties(
    width=700,
    height=700
)

text = heatmap.mark_text(baseline="middle", fontSize=10).encode(
    text=alt.Text("Correlation:Q", format=".2f"),
    color=alt.condition(
        "datum.Correlation > 0.5 || datum.Correlation < -0.5",
        alt.value("white"),
        alt.value("black")
    )
)

final_chart = heatmap + text

st.altair_chart(final_chart, use_container_width=False)

st.markdown("""
            The heatmap shows that there is no significant correlation between “Mental_Health_Issue” and the other columns. 
            This suggests that a single feature is not effective in predicting whether a person has a mental health issue, and that a more complex and non-linear analysis or modeling is needed that combines multiple factors.
            """)

st.markdown(f"## Socioeconomic Factors Analysis:")

st.markdown("In this section, we will analyze the mental health issues based on socioeconomic factors such as GDP, and happiness score.")

st.markdown(f"### Mental Health Issue Cases by Country")

tmp_df = df.groupby(["Country", "Mental_Health_Issue"]).size().reset_index(name="count")

count_hist = alt.Chart(tmp_df).mark_bar().encode(
    alt.X("Mental_Health_Issue:N", title=None, axis=None),
    alt.Y("count:Q", title="Count"),
    alt.Color("Mental_Health_Issue:N", title="Mental Health Issue", scale=alt.Scale(range=['#1f77b4', '#ff7f0e'])),
    alt.Column("Country:N", title="Country", header=alt.Header(orient='bottom')),
    tooltip=["Country", "Mental_Health_Issue", "count"]
).properties(
    width=60
)

st.altair_chart(count_hist)


st.markdown(f"### Socioeconomic indicators by Country")

country_df = pd.read_csv("data/processed/country_mean.csv")


normalized_df = country_df.copy()
scaler = MinMaxScaler()
normalized_df["Happiness score"] = scaler.fit_transform(country_df[["Happiness score"]])
normalized_df = normalized_df.rename(columns={"Happiness score": "Happiness score (normalized)"})

normalized_df = normalized_df.melt(
    id_vars=["Country"],
    value_vars=["Happiness score (normalized)", "GDP", "Corruption", "Healthy life expectancy"],
    var_name="Metric",
    value_name="Value"
)

line_chart = alt.Chart(normalized_df).mark_line(point=True).encode(
    x=alt.X("Country:N", title="Country", sort=None, axis=alt.Axis(labelAngle=0, labelFontSize=12)),
    y=alt.Y("Value:Q", title="Value", axis=alt.Axis(labelFontSize=12)),
    color=alt.Color("Metric:N", title="Metric"),
    tooltip=["Country", "Metric", alt.Tooltip("Value:Q", format=".2f")]
).properties(
    width=900,
    height=500
).configure_legend(
    titleFontSize=14,
    labelFontSize=12,
    orient="bottom-left",
    legendX=10,          
    legendY=10           
)

# Render the chart in Streamlit
st.altair_chart(line_chart, use_container_width=True)

st.markdown("""
            There is no clear pattern in the relationship between the presence of mental health issues and the socioeconomic conditions of the country. 
            As we can see from the plots above, although Australia and Canada have similarly high indicators, Australia has significantly more people without mental health issues than with mental health issues (87 compared to 73), while the opposite is true for Canada (59 compared to 79). 
            In addition, India, which is the individual country with the lowest indicators, has a higher number of people with mental health issues (85/155), but the United States, which has higher indicators, has a higher percentage of people with mental health issues (86/152).
            """)

st.markdown(f"### Boxplot of Selected Feature by Country")

selected_variable = st.selectbox("Choose the variable to compare: ", ['Sleep_Hours', 'Work_Hours', 'Physical_Activity_Hours'])

if selected_variable == 'Sleep_Hours':
    text = "Sleep Hours"
    range = [4, 10]
elif selected_variable == 'Work_Hours':
    text = "Work Hours"
    range = [30, 80]
else:
    text = "Physical Activity Hours"
    range = [0, 10]

chart = alt.Chart(df).mark_boxplot().encode(
    y=alt.Y(f'{selected_variable}:Q', title='Hours', scale=alt.Scale(domain=range)),
    x=alt.X('Country:N', title='Country', axis=alt.Axis(labelAngle=0)),
    xOffset='Mental_Health_Issue:N',
    color=alt.Color('Mental_Health_Issue:N', title='Mental Health Issue', scale=alt.Scale(range=['#1f77b4', '#ff7f0e'])),
    tooltip=['Country', 'Mental_Health_Issue', selected_variable]
).properties(
    width=800,
    height=400
)

st.altair_chart(chart)


st.markdown(f"##### Selected feature: {text} ")
st.markdown(f"The distribution of {text} varies across countries, but we cannot see a clear pattern of mental health issues from the boxplot.")


st.markdown(f"## Individual Factors Analysis:")
st.markdown("In this section, we will analyze the mental health issues based on individual factors such as daily habits and occupations.")


count_hist = alt.Chart(df).mark_bar().encode(
    alt.X("Mental_Health_Issue:N", title=None, axis=None),
    alt.Y("count():Q", axis=alt.Axis(title="Count of People")),
    alt.Color("Mental_Health_Issue:N", title="Mental Health Issue"),
    alt.Column("Occupation:N", title="Occupation", header=alt.Header(orient='bottom')),
    tooltip=['Mental_Health_Issue:N', alt.Tooltip('count():Q', title='Count')]
).properties(
    width=67
)

st.markdown('### Mental Health Issue Distribution by Occupation')

st.altair_chart(count_hist, theme=None)

st.markdown("""
    We can see that the number of people with mental health issues varies across occupations, but not much overall.
    In every occupation, except education, there are slightly more people with mental health issues than those without.
""")

st.markdown('### Different Factors affecting Mental Health')

sleep_bins = [0, 5.5, 7, 8.5, float('inf')]
sleep_labels = ['4.0-5.4', '5.5-6.9', '7.0-8.4', '8.5-10.0']
df['Sleep_Bin'] = pd.cut(df['Sleep_Hours'], bins=sleep_bins, labels=sleep_labels, right=False)

work_bins = [0, 42.5, 55, 67.5, float('inf')]
work_labels = ['30.0-42.4', '42.5-54.9', '55.0-67.4', '67.5-80.0']
df['Work_Bin'] = pd.cut(df['Work_Hours'], bins=work_bins, labels=work_labels, right=False)

activity_bins = [0, 2.5, 5, 7.5, float('inf')]
activity_labels = ['0.0-2.4', '2.5-4.9', '5.0-7.4', '7.5-10.0']
df['Activity_Bin'] = pd.cut(df['Physical_Activity_Hours'], bins=activity_bins, labels=activity_labels, right=False)

job_selected = st.multiselect("Filter by Job", df["Occupation"].unique(), default=df["Occupation"].unique())
df_filtered = df[df["Occupation"].isin(job_selected)]

df_grouped_sleep = df_filtered.groupby(['Sleep_Bin', 'Mental_Health_Issue']).size().reset_index(name='Count')
df_grouped_sleep["Percentage"] = df_grouped_sleep.groupby('Sleep_Bin')['Count'].transform(lambda x: x / x.sum() * 100)

df_grouped_work = df_filtered.groupby(['Work_Bin', 'Mental_Health_Issue']).size().reset_index(name='Count')
df_grouped_work["Percentage"] = df_grouped_work.groupby('Work_Bin')['Count'].transform(lambda x: x / x.sum() * 100)

df_grouped_activity = df_filtered.groupby(['Activity_Bin', 'Mental_Health_Issue']).size().reset_index(name='Count')
df_grouped_activity["Percentage"] = df_grouped_activity.groupby('Activity_Bin')['Count'].transform(
    lambda x: x / x.sum() * 100)

sleep_hist = alt.Chart(df_grouped_sleep).mark_bar().encode(
    alt.X("Mental_Health_Issue:N", title=None, axis=None),
    alt.Y("Count:Q", axis=alt.Axis(title="Count of People"), scale=alt.Scale(domain=[0, 200])),
    alt.Color("Mental_Health_Issue:N", title="Mental Health Issue"),
    alt.Column("Sleep_Bin:N", title="Sleep Time (Hours/Day)", header=alt.Header(orient='bottom'), sort=sleep_labels),
    tooltip=['Mental_Health_Issue:N', "Count:Q", alt.Tooltip("Percentage:Q", format=".2f")]
).properties(
    width=130
)

work_hist = alt.Chart(df_grouped_work).mark_bar().encode(
    alt.X("Mental_Health_Issue:N", title=None, axis=None),
    alt.Y("Count:Q", axis=alt.Axis(title="Count of People"), scale=alt.Scale(domain=[0, 200])),
    alt.Color("Mental_Health_Issue:N", title="Mental Health Issue"),
    column=alt.Column("Work_Bin:N", title="Work Time (Hours/Week)", header=alt.Header(orient='bottom'),
                      sort=work_labels),
    tooltip=['Mental_Health_Issue:N', "Count:Q", alt.Tooltip("Percentage:Q", format=".2f")]
).properties(
    width=130
)

activity_hist = alt.Chart(df_grouped_activity).mark_bar().encode(
    alt.X("Mental_Health_Issue:N", title=None, axis=None),
    alt.Y("Count:Q", axis=alt.Axis(title="Count of People"), scale=alt.Scale(domain=[0, 200])),
    alt.Color("Mental_Health_Issue:N", title="Mental Health Issue"),
    column=alt.Column("Activity_Bin:N", title="Activity Time (Hours/Week)", header=alt.Header(orient='bottom'),
                      sort=activity_labels),
    tooltip=['Mental_Health_Issue:N', "Count:Q", alt.Tooltip("Percentage:Q", format=".2f")]
).properties(
    width=130
)

st.markdown('##### Mental Health Issue Distribution by Sleep Hours')
st.altair_chart(sleep_hist, theme=None)
st.markdown("""
    People who sleep less than 5.5 hours have the highest percentage of mental health issues, 
    which demonstrates the negative impact of sleep deprivation on mental health. And the percentage of 
    mental health issues gradually decreases (although the absolute number increases) as the amount of sleep increases.
    However, the percentage of mental health issues increases again when sleep duration exceeds 8.5 hours, 
    which may need further investigation. One possible explanation is that people who have mental health issues need more sleep
    to recover, or that they are oversleeping due to their mental health issues.
""")

st.markdown('##### Mental Health Issue Distribution by Work Hours')
st.altair_chart(work_hist, theme=None)
st.markdown("""
    People who work more than 67.4 hours per week have the highest rates of mental health issues, 
    which can be attributed to overwork. Meanwhile, those who worked less than 42.5 hours had the lowest rates 
    of mental health issues, proving the importance of work-life balance in the opposite direction.
""")

st.markdown('##### Mental Health Issue Distribution by Physical Activity Hours')
st.altair_chart(activity_hist, theme=None)
st.markdown("""
    People who exercise less than 2.5 hours and more than 7.5 hours per week both have relatively high rates 
    of mental health issues, which indicates that both insufficient and excessive exercise can have negative effects
    on mental health. From the plot, we can see that 20 minutes to 1 hour of exercise per day is the optimal range
    for mental health.
""")
