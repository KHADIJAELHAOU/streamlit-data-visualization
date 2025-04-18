import streamlit as st
import pandas as pd
import plotly.express as px
#import seaborn as sns

#from streamlit.runtime.caching import clear_cache

# Page configuration
# MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Employees Analysis",
    page_icon="📊",
    layout="wide"
)
st.cache_data.clear()
# Load data
@st.cache_data
def load_data():
    return pd.read_excel("employees.xlsx")

df = load_data()

# Title
st.title("📊 Employees Data Analysis")

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
selected_education = st.sidebar.multiselect(
    "Select the education field:",
    options=df["Education"].unique(),
    default=None
)
selected_department = st.sidebar.multiselect(
    "Select the department:",
    options=df["Department"].unique(),
    default=None
)

selected_attrition = st.sidebar.multiselect(
    "Select the Attrition Status:",
    options=df["Attrition"].unique(),
    default=None
)

# Filtre Niveau de poste
import pandas as pd

# Exemple de transformation des niveaux en nombres
job_level_mapping = {
    'Entry-level': 1,
    'Junior': 2,
    'Mid-level': 3,
    'Senior': 4,
    'Executive': 5
}

# Appliquer la conversion
df['JobLevel'] = df['JobLevel'].map(job_level_mapping)

# Vérifier s'il reste des NaN après la conversion
df['JobLevel'].fillna(1, inplace=True)  # Valeur par défaut si non reconnue


if 'JobLevel' in df.columns:
    min_level = int(df['JobLevel'].min())
    max_level = int(df['JobLevel'].max())
else:
    min_level, max_level = 1, 5
    st.sidebar.warning("Données JobLevel manquantes - utilisation des valeurs par défaut")

# Job Level filter (numeric values already mapped)
job_level_filter = st.sidebar.slider(
    "Select Job Level:",
    min_value=int(df["JobLevel"].min()),
    max_value=int(df["JobLevel"].max()),
    value=(int(df["JobLevel"].min()), int(df["JobLevel"].max()))
)

# Age filter
if 'Age' in df.columns:
    age_min = int(df['Age'].min())
    age_max = int(df['Age'].max())
else:
    age_min, age_max = 18, 65
    st.sidebar.warning("Données Age manquantes - utilisation des valeurs par défaut")

age_filter = st.sidebar.slider(
    "Select age",
    min_value=age_min,
    max_value=age_max,
    value=(age_min, age_max))




# Build dynamic query
query_parts = []
if selected_education:
    query_parts.append("Education in @selected_education")
if selected_department:
    query_parts.append(f"Department in @selected_department")
if selected_attrition:
    query_parts.append(f"Attrition in @selected_attrition")

query_parts.append("(JobLevel >= @job_level_filter[0] & JobLevel <= @job_level_filter[1])")
query_parts.append("(Age >= @age_filter[0] & Age <= @age_filter[1])")


final_query = " & ".join(query_parts) if query_parts else ""

# Apply filters
df_selection = df.query(final_query) if final_query else df


# Basic Visualization Section
#st.header("Basic Visualizations")

# ---- CUSTOM CSS for KPI's section----
st.markdown("""
    <style>
        .kpi-box {
            border: 2px solid #ADB2D4;  /*  border */
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            background-color: #E7FBE6; /* Light gray background */
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 15px; /* Adds spacing between rows */
            width: 70%
        }
        .kpi-label {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 22px;
            font-weight: bold;
            color: #5F99AE; /* Blue color */
        }
        
    </style>
""", unsafe_allow_html=True)

# Calculate KPIs
total_employees = int(df_selection["EmployeeID"].sum())
average_age = round(df_selection["Age"].mean(), 1)
average_salary = round(df_selection["MonthlyIncome"].mean(), 1)

# Calculate Loyalty Rate
loyal_employees = int(df_selection[df_selection["YearsAtCompany"] > 5]["EmployeeID"].sum())  # Assuming YearsAtCompany column exists
loyalty_rate = round((loyal_employees / total_employees) * 100, 1) if total_employees != 0 else 0

left_column, right_column = st.columns(2)

with left_column:
    #st.metric(label="Total Employees", value=f"{total_employees:,}")
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Total Employees</div>
            <div class="kpi-value">{total_employees:,}</div>
        </div>
    """, unsafe_allow_html=True)

with right_column:
    #st.metric(label="Average Age", value=f"{average_age}")
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Average Age</div>
            <div class="kpi-value">{average_age:,}</div>
        </div>
    """, unsafe_allow_html=True)

left_column, right_column = st.columns(2)

with right_column:
    #st.metric(label="Average Salary", value=f"US $ {average_salary:,}")
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Average Salary</div>
            <div class="kpi-value">{average_salary:,}</div>
        </div>
    """, unsafe_allow_html=True)

with left_column:
    #st.metric(label="Loyalty Rate (+5 years)", value=f"{loyalty_rate}%")
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Loyalty Rate</div>
            <div class="kpi-value">{loyalty_rate}%</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""---""")

#mainpage
# Add custom CSS for chart borders
st.markdown("""
<style>
    [data-testid="stPlotlyChart"] {
        border: 2px solid #DBDBDB !important;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }
    
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
        gap: 2rem;
    }
    
    .st-emotion-cache-1kyxreq {
        padding: 10px;
        border: 1px solid #DBDBDB !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5, 5])
# ---- Total Employees by Department ----

with col1:

    # Prepare data
    dept_counts = df_selection['Department'].value_counts().reset_index()
    dept_counts.columns = ['Department', 'Total Employees']

    # Create chart
    try:
        fig_dept = px.bar(
            dept_counts,
            x='Department',
            y='Total Employees',
            title='<b>Total Employees by Department</b>',
            color_discrete_sequence=['#5F99AE'],  # Single color for all bars
            template='plotly_white'
        )
        
        # Customize layout
        fig_dept.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            hovermode='x unified'
        )

        st.plotly_chart(fig_dept, use_container_width=True)

        
    except Exception as e:
        st.error(f"Department chart error: {str(e)}")   

with col2:


    # ---- Total Employees by Job Role ----
    jobrole_counts = df_selection['JobRole'].value_counts().reset_index()
    jobrole_counts.columns = ['JobRole', 'Total Employees']

    try:
        fig_jobrole = px.bar(
            jobrole_counts,
            x='JobRole',
            y='Total Employees',
            title='<b>Total Employees by Job Role</b>',
            color_discrete_sequence=['#5F99AE'],  # Single color
            template='plotly_white'
        )
        
        fig_jobrole.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=False,
                tickangle=-45,
                showticklabels=False  # Remove x-axis labels
            ),
            yaxis=dict(showgrid=False),
            hovermode='x unified',
            showlegend=False,  # Ensure legend is hidden
            
        )
        st.plotly_chart(fig_jobrole, use_container_width=True)

        
        
        
    except Exception as e:
        st.error(f"Job Role chart error: {str(e)}")


# ---- Attrition & Job Level Charts ----
col1, col2 = st.columns([5, 5])

with col1:
    # Attrition by Department Chart
    #st.subheader("Attrition by Department")
    
    # Prepare data in long format
    attrition_dept = df_selection.groupby(['Department', 'Attrition']).size().reset_index(name='Count')
    
    try:
        fig_bar = px.bar(
            attrition_dept,
            x='Department',
            y='Count',
            title='<b>Attrition by Department</b>',
            color='Attrition',
            barmode='group',
            color_discrete_sequence=['#56021F', '#5F99AE'],  # Red for Yes, Dark teal for No
            labels={'Count': 'Employee Count'}
        )
        
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(showgrid=False, title=None),
            legend=dict(title='Attrition Status'),
            margin=dict(l=20, r=20, t=30, b=20),
            height=400,
            
        )
            
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    except Exception as e:
        st.error(f"Bar chart error: {str(e)}")
        #st.markdown('</div>', unsafe_allow_html=True)


with col2:
    # Job Level Pie Chart
    #st.subheader("Count of EmployeeID by JobLevel")
    joblevel_counts = df_selection['JobLevel'].value_counts().reset_index()
    joblevel_counts.columns = ['JobLevel', 'Count']
    
    try:
        fig_pie = px.pie(
            joblevel_counts,
            names='JobLevel',
            values='Count',
            title='<b>Count of EmployeeID by JobLevel',
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.5,
            height=400
        )
        
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            insidetextorientation='radial',
            marker=dict(line=dict(color='#ffffff', width=1))
        )
        fig_pie.update_layout(
            showlegend=True,  # ENABLE LEGEND
            legend=dict(
                title='Job Levels',
                orientation='v',
                yanchor='middle',
                xanchor='left',
                x=1.2,  # Move legend to right side
                y=0.5,
                font=dict(size=12)
            ),
            #margin=dict(l=0, r=150, t=40, b=0),  # Add right margin for legend
            uniformtext_minsize=14,
            uniformtext_mode='hide'
            
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    except Exception as e:
        st.error(f"Pie chart error: {str(e)}")
    #st.markdown('</div>', unsafe_allow_html=True)
#st.markdown("""---""")

# Correlation Matrix Heatmap 
numeric_cols = df_selection.select_dtypes(include=['number']).columns
corr_matrix = df_selection[numeric_cols].corr()

fig = px.imshow(
    corr_matrix,
    labels=dict(color="Correlation"),
    title='<b>Feature Correlation Matrix<b>',
    x=corr_matrix.columns,
    y=corr_matrix.columns,
    color_continuous_scale="Blues",
    zmin=-1,
    zmax=1
)
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

#Salary distribution analysis
st.subheader("Salary Distribution Analysis")
col1, col2 = st.columns(2)

with col1:
    fig = px.box(
        df_selection,
        x="Department",
        y="MonthlyIncome",
        color="Attrition",
        title="Salary Distribution by Department"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.violin(
        df_selection,
        x="JobRole",
        y="YearsAtCompany",
        color="Gender",
        box=True,
        title="Tenure Distribution by Job Role"
    )
    st.plotly_chart(fig, use_container_width=True)


#3D Employee Profile Analysis
fig = px.scatter_3d(
    df_selection,
    x='Age',
    y='YearsAtCompany',
    z='MonthlyIncome',
    color='JobRole',
    symbol='Attrition',
    hover_name='Department',
    opacity=0.7,
    height=700,
    title="3D Employee Profile Analysis"
)
fig.update_traces(marker_size=3)
st.plotly_chart(fig, use_container_width=True)

#Sunburst Chart (Employee Hierarchy Analysis)
fig = px.sunburst(
    df_selection,
    path=['Department', 'JobRole', 'Attrition'],
    values='EmployeeID',
    color='MonthlyIncome',
    color_continuous_scale='Blues',
    maxdepth=2,
    title="Employee Hierarchy Analysis"
)
st.plotly_chart(fig, use_container_width=True)



# ---- Scatter Plot Section ----
st.subheader("Employee Profile Scatter Analysis")

# Create columns for controls
col1, col2, col3 = st.columns(3)
with col1:
    x_axis = st.selectbox(
        "X-axis",
        options=['Age', 'MonthlyIncome', 'YearsAtCompany', 'TotalWorkingYears'],
        index=0
    )
with col2:
    y_axis = st.selectbox(
        "Y-axis",
        options=['MonthlyIncome', 'Age', 'YearsAtCompany', 'TotalWorkingYears'],
        index=0
    )
with col3:
    color_by = st.selectbox(
        "Color by",
        options=['Department', 'JobRole', 'Attrition', 'Gender', None],
        index=0
    )

# Create interactive scatter plot
fig = px.scatter(
    df_selection,
    x=x_axis,
    y=y_axis,
    color=color_by,
    hover_name="EmployeeID",
    hover_data=["JobRole", "Department"],
    size_max=15,
    opacity=0.7,
    height=600,
    title=f"{y_axis} vs {x_axis} Relationship"
)

# Add trendline option
if st.checkbox("Show trendline"):
    fig.update_traces(
        line=dict(dash="dot", width=1),
        selector=dict(mode="lines")
    )
    fig.add_scatter(
        x=df_selection[x_axis],
        y=df_selection[y_axis],
        mode="lines",
        line=dict(color="grey", width=2),
        name="Trend"
    )

# Customize layout
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    hovermode="closest"
)

st.plotly_chart(fig, use_container_width=True)
#HIDE STREAMLIT STYLE
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

