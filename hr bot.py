import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(layout="wide", page_title="HR Analytics Dashboard", page_icon="📊")

# --- Function to Generate Sample Data ---
def generate_sample_data(num_rows=200):
    """Generates a sample HR dataset as a pandas DataFrame."""
    np.random.seed(42)
    departments = ['Sales', 'Marketing', 'Engineering', 'Human Resources', 'Finance']
    genders = ['Male', 'Female']
    attrition = ['Yes', 'No']
    
    data = {
        'Employee ID': range(1, num_rows + 1),
        'Department': np.random.choice(departments, num_rows),
        'Age': np.random.randint(22, 60, size=num_rows),
        'Gender': np.random.choice(genders, num_rows),
        'Attrition': np.random.choice(attrition, num_rows, p=[0.15, 0.85]),
        'Salary': np.random.randint(40000, 150000, size=num_rows),
        'Years at Company': np.random.randint(1, 15, size=num_rows),
        'Performance Rating': np.random.randint(1, 5, size=num_rows),
        'Hiring Date': [datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1825)) for _ in range(num_rows)]
    }
    df = pd.DataFrame(data)
    return df

# --- Main Dashboard ---
st.title("📊 HR Analytics Dashboard")

# --- Data Loading ---
st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()
else:
    if st.sidebar.button("Use Sample Data"):
        df = generate_sample_data()
        st.session_state.df = df
    if 'df' in st.session_state:
        df = st.session_state.df
    else:
        st.info("Upload a CSV file or click 'Use Sample Data' to begin.")
        st.stop()

# Ensure 'Hiring Date' is in datetime format
df['Hiring Date'] = pd.to_datetime(df['Hiring Date'])


# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Filter by Department
departments = df['Department'].unique()
selected_departments = st.sidebar.multiselect("Department", departments, default=departments)

# Filter by Gender
genders = df['Gender'].unique()
selected_gender = st.sidebar.selectbox("Gender", ["All"] + list(genders))

# Filter by Attrition
attrition_status = df['Attrition'].unique()
selected_attrition = st.sidebar.selectbox("Attrition", ["All"] + list(attrition_status))

# --- Filtering Data ---
filtered_df = df[df['Department'].isin(selected_departments)]

if selected_gender != "All":
    filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
if selected_attrition != "All":
    filtered_df = filtered_df[filtered_df['Attrition'] == selected_attrition]

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()


# --- High-Level KPIs ---
st.header("Key Performance Indicators")

# Calculate KPIs
total_employees = len(filtered_df)
attrition_rate = (filtered_df['Attrition'] == 'Yes').sum() / total_employees * 100
average_salary = filtered_df['Salary'].mean()
average_years_at_company = filtered_df['Years at Company'].mean()

# Display KPIs in columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="Total Employees", value=f"{total_employees:,}")
kpi2.metric(label="Attrition Rate", value=f"{attrition_rate:.2f}%")
kpi3.metric(label="Average Salary", value=f"${average_salary:,.2f}")
kpi4.metric(label="Avg. Years at Company", value=f"{average_years_at_company:.2f}")


st.markdown("---")


# --- Visualizations ---
st.header("Visualizations")

# Create two columns for charts
col1, col2 = st.columns(2)

with col1:
    # Pie Chart: Department-wise Distribution
    st.subheader("Department-wise Distribution")
    dept_dist = filtered_df['Department'].value_counts()
    fig_pie = px.pie(
        values=dept_dist.values, 
        names=dept_dist.index, 
        title="Employee Distribution by Department"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Line Chart: Monthly hiring trend
    st.subheader("Monthly Hiring Trend")
    filtered_df['Hiring Month'] = filtered_df['Hiring Date'].dt.to_period('M').astype(str)
    hiring_trend = filtered_df.groupby('Hiring Month').size().reset_index(name='count')
    fig_line = px.line(
        hiring_trend, 
        x='Hiring Month', 
        y='count', 
        title="Hiring Trend Over Time",
        labels={'Hiring Month': 'Month', 'count': 'Number of Hires'}
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    # Bar Chart: Attrition count by Department
    st.subheader("Attrition Count by Department")
    attrition_by_dept = filtered_df[filtered_df['Attrition'] == 'Yes']['Department'].value_counts().reset_index()
    attrition_by_dept.columns = ['Department', 'Attrition Count']
    fig_bar = px.bar(
        attrition_by_dept, 
        x='Department', 
        y='Attrition Count', 
        title="Attrition by Department"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Box Plot: Salary distribution by Department
    st.subheader("Salary Distribution by Department")
    fig_box = px.box(
        filtered_df, 
        x='Department', 
        y='Salary', 
        title="Salary Distribution by Department",
        color='Department'
    )
    st.plotly_chart(fig_box, use_container_width=True)

# --- Display Raw Data ---
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data")
    st.dataframe(filtered_df)