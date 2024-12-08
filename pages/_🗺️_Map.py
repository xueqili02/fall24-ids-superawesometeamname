import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


def get_filtered_df(df, year, gdp, healthy_life_expectancy, corruption):
    labels = pd.Series([1] * len(df), index=df.index)
    labels &= df['Year'] == year
    labels &= df['GDP'] >= gdp[0]
    labels &= df['GDP'] <= gdp[1]
    labels &= df['Healthy life expectancy'] >= healthy_life_expectancy[0]
    labels &= df['Healthy life expectancy'] <= healthy_life_expectancy[1]
    labels &= df['Corruption'] >= corruption[0]
    labels &= df['Corruption'] <= corruption[1]
    return df[labels]


def get_filtered_by_country_df(df, country):
    labels = pd.Series([1] * len(df), index=df.index)
    labels &= df['Country'] == country
    return df[labels]


st.title("🗺️ Geographic Visualization of Happiness Dataset")
st.markdown(
    "This interactive dashboard supports the exploration of the World Happiness Report.\n"
    "You can filter by year and metrics like GDP per capita, Healthy life expectancy, and Corruption. The scale means by how "
    "much happiness score is explained this metric.\n"
    "The happiness scores are relative ranging from 0 to 1.\n")

df_coordinate = pd.read_csv("https://raw.githubusercontent.com/xueqili02/fall24-ids-superawesometeamname/refs/heads/main/Data/processed/happiness_coordinates.csv")

year = st.selectbox('Year:',
                    options=df_coordinate['Year'].unique())

gdp = st.slider('GDP per capita:',
                min_value=df_coordinate['GDP'].min(),
                max_value=df_coordinate['GDP'].max(),
                value=(df_coordinate['GDP'].min(), df_coordinate['GDP'].max()))

healthy_life_expectancy = st.slider('Healthy life expectancy:',
                                    min_value=df_coordinate['Healthy life expectancy'].min(),
                                    max_value=df_coordinate['Healthy life expectancy'].max(),
                                    value=(df_coordinate['Healthy life expectancy'].min(),
                                           df_coordinate['Healthy life expectancy'].max()))

corruption = st.slider('Corruption:',
                       min_value=df_coordinate['Corruption'].min(),
                       max_value=df_coordinate['Corruption'].max(),
                       value=(df_coordinate['Corruption'].min(), df_coordinate['Corruption'].max()))

df_filtered = get_filtered_df(df_coordinate, year, gdp, healthy_life_expectancy, corruption)
# st.map(df_filtered, latitude='latitude', longitude='longitude', size='Happiness score', zoom=0)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_filtered,
    stroked=True,
    filled=True,
    get_position=["longitude", "latitude"],
    radius_scale=400000,
    radius_min_pixels=1,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_radius="Happiness sore",
    get_fill_color=[218, 72, 164, 160],
    pickable=True
)

view_state = pdk.ViewState(
    latitude=0,
    longitude=0,
    zoom=1,
    pitch=0
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{Country}'s Happiness Score: {Happiness score}"},
)

st.pydeck_chart(r)

st.markdown(
    "To take a look at each country's change in happiness score from 2016 to 2021, you can select a country from the "
    "list.\n")

country = st.selectbox('Country:',
                       options=df_coordinate['Country'].unique())
df_filter_by_country = get_filtered_by_country_df(df_coordinate, country)

chart = alt.Chart(df_filter_by_country).mark_line().encode(
    x="Year:O",
    y="Happiness score:Q",
    tooltip=["Year", "Happiness score"],
).interactive()

st.altair_chart(chart, use_container_width=True)
