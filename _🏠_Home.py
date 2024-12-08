import streamlit as st
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

st.title("🏠 Mental Health Analysis")

st.markdown("This interactive application:\n"
            "- provides the exploration and visuailzation of the Mental Health dataset and the World Happiness Reports Dataset.\n"
            "- provides insights of people's mental health with respect to socioeconomic and psychological factors.\n"
            "- predicts adults' mental health scores by self-reported information.\n")

st.markdown("## Analysis page")
st.markdown("The **Analysis** page contains extensive analysis on the whole dataset and important features.\n")

st.markdown("## Map page")
st.markdown("The **Map** page contains visualization of the Happiness dataset, exploring each country's happiness score and metrics.\n")

st.markdown("## Prediction page")
st.markdown("The **Prediction** page contains our regression model for mental health score prediction.\n")

st.markdown("## Datasets")
st.markdown("### World Happiness Report Dataset")
country = pd.read_csv("https://raw.githubusercontent.com/xueqili02/fall24-ids-superawesometeamname/refs/heads/main/Data/processed/country_all_years.csv")
st.write(country.head(10))

st.markdown("### Mental Health Dataset")
mental = pd.read_csv("https://raw.githubusercontent.com/xueqili02/fall24-ids-superawesometeamname/refs/heads/main/Data/processed/mental_health_country.csv")
st.write(mental.head(10))