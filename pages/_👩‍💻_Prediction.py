import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import altair as alt
import seaborn as sns
import plotly.express as px

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

st.title("👩‍💻 Prediction")
st.markdown(
    "This interactive dashboard supports the prediction of the mental health score based on the regression model trained by historical data. You can report your current situation in the selection boxes. Information will be only used for prediction and not stored.")


# selected_features = ['Consultation_History', 'Stress_Level', 'Sleep_Hours', 'Work_Hours', 'Physical_Activity_Hours','Happiness score']


# Personal information
# Consultation_History, Stress_Level

# add one word as description of this section
st.subheader("Personal Information")
# add sub-subheader
# st.write("Please report your current situation below.")

col1,col2 = st.columns(2)
with col1:
    consultation_list = ['Yes', 'No']
    reported_consultation = st.radio(
        label="Consultation History",
        options=consultation_list,
        index=None
    )
with col2:
    stress_level_list = ['Low', 'Medium', 'High']
    reported_stress_level = st.selectbox(
        label="Stress Level",
        options=stress_level_list,
        index=None,
    )

# col1, col2, col3 = st.columns(3)
# with col1:
#     gender_list = ['Female', 'Male', 'Non-binary', 'Prefer not to say']
#     reported_gender = st.selectbox(
#         label="Gender",
#         options=gender_list,
#         index=None
#     )
# with col2:
#     occupation_list = ['Sales', 'Education', 'Healthcare', 'IT', 'Engineering', 'Finance', 'Other']
#     reported_occupation = st.selectbox(
#         label="Occupation",
#         options=occupation_list,
#         index=None
#     )
# with col3:
#     consultation_list = ['Yes', 'No']
#     reported_consultation = st.selectbox(
#         label="Consultation History",
#         options=consultation_list,
#         index=None
#     )

# Living Habit
# Sleep_Hours, Work_Hours, Physical_Activity_Hours

st.subheader("Living Habit")
col2, col3, col4 = st.columns(3)
with col2:
    reported_sleep_hours = st.slider(
        label="Daily Sleep Hours",
        min_value=0.0,
        max_value=24.0,
        value=7.0,
        step=0.1
    )
with col3:
    reported_work_hours = st.slider(
        label="Weekly Work Hours",
        min_value=0,
        max_value=168,
        value=54,
        step=1
    )
with col4:
    reported_physical_activity_hours = st.slider(
        label="Weekly Physical Activity Hours",
        min_value=0,
        max_value=80,
        value=5,
        step=1
    )

# Country
st.subheader("Country")
country_list = ['Canada', 'UK', 'USA', 'Australia', 'India', 'Other', 'Germany']
reported_country = st.selectbox(
    label="Country",
    options=country_list,
    index=None
)

# Predict
# st.write("Click the button below to predict your mental health score.")
health_score = None
if st.button("Predict"):

    if reported_consultation is None or reported_stress_level is None or reported_sleep_hours is None or reported_work_hours is None or reported_physical_activity_hours is None or reported_country is None:
        #st.write("Predictions and Ranking results require all fields to be filled. Please fill in all fields!")
        st.info('Predictions and Ranking results require all fields to be filled. Please fill in all fields!', icon="ℹ️")
        st.stop()
    else:

        # get country data
        country_data = pd.read_csv('data/processed/country_mean.csv')
        happiness_score = country_data[country_data['Country'] == reported_country]['Happiness score'].values[0]
        corruption = country_data[country_data['Country'] == reported_country]['Corruption'].values[0]

        # get model data from file
        model_data = joblib.load('mental_health_model_58.pkl')
        model = model_data['model']
        scaler = model_data['scaler']
        selector = model_data['selector']
        label_encoders = model_data['label_encoders']
        selected_features = model_data['selected_features']




        new_data = {
            # 'Gender': [reported_gender],
            # 'Occupation': [reported_occupation],
            'Consultation_History': [reported_consultation],
            'Stress_Level': [reported_stress_level],
            'Sleep_Hours': [reported_sleep_hours],
            'Work_Hours': [reported_work_hours],
            'Physical_Activity_Hours': [reported_physical_activity_hours],
            'Happiness score': [happiness_score],
            # 'Corruption': [corruption]
        }


        def predict_health_score(input_data, model, scaler, selector, label_encoders, selected_features):
            if not isinstance(input_data, pd.DataFrame):
                input_data = pd.DataFrame([input_data])

            input_processed = input_data.copy()
            for col, encoder in label_encoders.items():
                if col in input_processed.columns:
                    input_processed[col] = encoder.transform(input_processed[col])

            input_processed = input_processed[selected_features]

            input_scaled = scaler.transform(input_processed)

            prediction_label = model.predict(input_scaled)
            prediction_value = model.predict_proba(input_scaled)
            return prediction_label, prediction_value


            # prediction = model.predict_proba(input_scaled)
            # health_score = 1 - prediction[:, 1] * 100
            # return health_score


        new_data_df = pd.DataFrame(new_data)
        prediction_label,prediction_value = predict_health_score(
            new_data_df,
            model,
            scaler,
            selector,
            label_encoders,
            selected_features
        )

        health_score = prediction_value[0][0] * 100
        health_label = "Yes" if prediction_label[0] == 0 else "No"

        # st.success(f""" Results Predictied!""", icon="✅")
        # st.write(f"Your mental health score is {health_score:.2f}.")

        # st.markdown(
        #     f"""
        #     <div style="background-color: #d4edda; padding: 10px; border-radius: 5px;">
        #         <b style="font-size:12px;">✅ Results Predicted!</b><br>
        #         <span style="font-size:12px;">Your mental health score is <b>{health_score:.2f}</b>.</span>
        #     </div>
        #     """,
        #     unsafe_allow_html=True
        # )

        st.markdown(
            f"""
            <div style="background-color: #e8f9ee; padding: 10px; border-radius: 5px;">
                <b>✅ Results Predicted!</b><br>
                Your mental health score is <b>{health_score:.2f}</b>/100.
            </div>
            """,
            unsafe_allow_html=True
        )




st.write("\n")
st.divider()
st.write("\n")


st.subheader("Ranking")
st.write("Based on the prediction, we rank the mental health score of the existing dataset.")

# df = pd.read_csv("data/processed/mental_health_country.csv")
df = pd.read_csv("data/processed/mental_health_country_prediction.csv")

# columns = st.multiselect(
#     "Select columns to plot CDF:",
#     options=['Sleep_Hours', 'Work_Hours', 'Physical_Activity_Hours'],
#     default=['Sleep_Hours', 'Work_Hours', 'Physical_Activity_Hours']
# )


# if columns:

cdf_charts = []
columns = ['Sleep_Hours','Work_Hours','Physical_Activity_Hours']
reported_values = [reported_sleep_hours,reported_work_hours, reported_physical_activity_hours]

# Prepare data for Altair CDF plot
cdf_data = pd.DataFrame()
highlighted_points = pd.DataFrame(columns=['Value', 'Ranking', 'Category'])

container_width = 400
num_charts = len(columns)
individual_width = container_width // num_charts

legend_config = alt.Legend(
    orient='bottom',
    direction='horizontal',
    padding=10,
    title=None
)

for column, reported_value in zip(columns, reported_values):
    sorted_data = np.sort(df[column])
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data) * 100  # convert to percentage
    temp_df = pd.DataFrame({
        'Value': sorted_data,
        'Ranking': cdf,
        'Category': column
    })
    # cdf_data = pd.concat([cdf_data, temp_df])
    cdf_data = temp_df.copy()

    closest_idx = np.searchsorted(sorted_data, reported_value, side="left")
    cdf_rank = float(closest_idx / len(sorted_data)) * 100  # convert to percentage
    #highlighted_points = pd.concat([highlighted_points, pd.DataFrame({
    highlighted_points = pd.DataFrame({
        'Value': reported_value,
        'Ranking': [cdf_rank],
        'Category': [column]
    })

    # Altair plot
    cdf_chart = alt.Chart(cdf_data).mark_line().encode(
        x=alt.X('Value:Q', title=column + ' Value'),
        y=alt.Y('Ranking:Q', title='Ranking (%)'),  # display as percentage
        color=alt.Color(
            'Category:N',
            legend=None
        ),
        tooltip=['Category', 'Value', alt.Tooltip('Ranking:Q', format='.1f')]
    ).properties(
        width = individual_width,
        height = 200,
    ).interactive()

    # Altair points for highlighted values
    highlight_chart = alt.Chart(highlighted_points).mark_point(size=100, filled=True).encode(
        x='Value:Q',
        y='Ranking:Q',
        color='Category:N',
        tooltip=['Category', 'Value', alt.Tooltip('Ranking:Q', format='.1f')]
    )

    # print(highlighted_points)

    final_chart = cdf_chart + highlight_chart
    cdf_charts.append(final_chart)


combined_chart = alt.hconcat(*cdf_charts).properties(
    title=alt.TitleParams(
        text="Cumulative Distribution Function(CDF) Plots for Reported Values",
        anchor="middle",
        fontSize=16,
        fontWeight="bold"
    )
)

st.altair_chart(combined_chart, use_container_width=True)



# violin plot

violin_data = df.copy()

violin_data['id'] = 0

col1,col2,col3 = st.columns(3)
violin_plot_height = 420
with col1:
    # fig, ax = plt.subplots()
    # sns.violinplot(x=None, y='Sleep_Hours', data=violin_data, ax=ax)
    # st.pyplot(fig)

    fig = px.violin(violin_data,x='id',y="Sleep_Hours", box=True, points="outliers", hover_data=['Sleep_Hours'])

    fig.update_layout(
        xaxis=dict(
            showticklabels=False,
            title=None
        ),
        height=violin_plot_height,
        # margin=dict(l=50, r=50, t=50, b=50)
    )

    fig.add_scatter(
        x = [0],
        y = [reported_sleep_hours],
        mode = 'markers',
        marker=dict(size=8, color='orange', symbol='x'),
        name='Reported Sleep Hours Value',
        showlegend=False
    )

    st.plotly_chart(fig)

with col2:
    fig = px.violin(violin_data, x='id', y="Work_Hours", box=True, points="outliers", hover_data=['Work_Hours'])
    fig.update_layout(title="Violin Plots of Reported Value")
    fig.update_layout(
        xaxis=dict(
            showticklabels=False,
            title=None
        ),
        height=violin_plot_height,
        # margin=dict(l=50, r=50, t=50, b=50)
    )

    fig.add_scatter(
        x=[0],
        y=[reported_work_hours],
        mode='markers',
        marker=dict(size=8, color='orange', symbol='x'),
        name='Reported Sleep Hours Value',
        showlegend=False
    )
    st.plotly_chart(fig)

with col3:
    fig = px.violin(violin_data, x='id', y="Physical_Activity_Hours", box=True, points="outliers", hover_data=['Physical_Activity_Hours'])
    fig.update_layout(
        xaxis=dict(
            showticklabels=False,
            title=None
        ),
        height=violin_plot_height,
        # margin=dict(l=50, r=50, t=50, b=50)
    )

    fig.add_scatter(
        x = [0],
        y = [reported_physical_activity_hours],
        mode = 'markers',
        marker=dict(size=8, color='orange', symbol='x'),
        name='Reported Sleep Hours Value',
        showlegend=False
    )
    st.plotly_chart(fig)


# Mental Score ranking
col1, col2 = st.columns(2)
predicted_value = 0
if health_score is not None:
    predicted_value = health_score

mental_score_plot_height = 340
with (col1):
    column = 'prediction_value'
    sorted_data = np.sort(df["prediction_value"])
    sorted_data = sorted_data * 100
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data) * 100  # convert to percentage
    temp_df = pd.DataFrame({
        'Value': sorted_data,
        'Ranking': cdf,
        'Category': column
    })
    # cdf_data = pd.concat([cdf_data, temp_df])
    cdf_data = temp_df.copy()

    closest_idx = np.searchsorted(sorted_data, predicted_value, side="left")
    cdf_rank = float(closest_idx / len(sorted_data)) * 100  # convert to percentage
    #highlighted_points = pd.concat([highlighted_points, pd.DataFrame({
    highlighted_points = pd.DataFrame({
        'Value': predicted_value,
        'Ranking': [cdf_rank],
        'Category': [column]
    })

    # Altair plot
    cdf_chart = alt.Chart(cdf_data).mark_line().encode(
        x=alt.X('Value:Q', title='Predicted Mental Health Score'),
        y=alt.Y('Ranking:Q', title='Ranking (%)'),  # display as percentage
        color=alt.Color(
            'Category:N',
            legend=None
        ),
        tooltip=['Category', 'Value', alt.Tooltip('Ranking:Q', format='.1f')]
    ).properties(
        #height = mental_score_plot_height,
    ).interactive()

    # Altair points for highlighted values
    highlight_chart = alt.Chart(highlighted_points).mark_point(size=100, filled=True).encode(
        x='Value:Q',
        y='Ranking:Q',
        color='Category:N',
        tooltip=['Category', 'Value', alt.Tooltip('Ranking:Q', format='.1f')]
    )

    # print(highlighted_points)

    final_chart = cdf_chart + highlight_chart

    # add title to the chart
    final_chart = final_chart.properties(
        title=alt.TitleParams(
            text="Predicted Mental Health Score(CDF)",
            anchor="middle",
            fontSize=16,
            fontWeight="bold"
        )
    )

    # show the chart
    st.altair_chart(final_chart, use_container_width=True)

with col2:
    # multiply the prediction_value in violin_data by 100
    violin_data['prediction_value'] = violin_data['prediction_value'] * 100
    fig = px.violin(violin_data, x='id', y="prediction_value", box=True, points="outliers", hover_data=['prediction_value'])
    fig.update_layout(
        title={
            "text": "Predicted Mental Health Score(Violin)",
            "x": 0.5,
            "xanchor": "center"
        }
    )
    fig.update_layout(
        # revise y axis label as "Predicted Mental Health Score"
        yaxis_title="Predicted Mental Health Score",
        xaxis=dict(
            showticklabels=False,
            title="Mental Health Score Distribution"
        ),
        height=mental_score_plot_height,
        margin=dict(l=50, r=50, t=25, b=20)
    )

    fig.add_scatter(
        x = [0],
        y = [predicted_value],
        mode = 'markers',
        marker=dict(size=8, color='orange', symbol='x'),
        name='Predicted Mental Health Score',
        showlegend=False
    )

    st.plotly_chart(fig)