import streamlit as st
import pandas as pd
import plotly.express as px



df = pd.read_csv("hospital_dataset.csv")

df.columns = df.columns.str.strip()
df.fillna(0, inplace=True)

st.title("🏥  Healthcare Analytics & Decision System ")



def find_col(name):
    for col in df.columns:
        if name.lower() in col.lower():
            return col
    return None

disease_col = find_col("disease")
age_col = find_col("age")
dept_col = find_col("department")


if age_col:
    df[age_col] = pd.to_numeric(df[age_col], errors='coerce')
    df = df.dropna(subset=[age_col])


st.sidebar.header(" Filters")

filtered_df = df.copy()

if disease_col:
    disease = st.sidebar.multiselect("Disease", df[disease_col].unique())
    if disease:
        filtered_df = filtered_df[filtered_df[disease_col].isin(disease)]

if dept_col:
    dept = st.sidebar.multiselect("Department", df[dept_col].unique())
    if dept:
        filtered_df = filtered_df[filtered_df[dept_col].isin(dept)]

if age_col:
    min_age = int(filtered_df[age_col].min())
    max_age = int(filtered_df[age_col].max())

    age_range = st.sidebar.slider("Age Range", min_age, max_age, (min_age, max_age))

    filtered_df = filtered_df[
        (filtered_df[age_col] >= age_range[0]) &
        (filtered_df[age_col] <= age_range[1])
    ]


st.subheader(" Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Patients", filtered_df.shape[0])
col2.metric("Avg Age", int(filtered_df[age_col].mean()) if age_col else 0)
col3.metric("Unique Diseases", filtered_df[disease_col].nunique() if disease_col else 0)


st.subheader("Filtered Data")
st.write(filtered_df)


st.download_button(
    "Download Data",
    filtered_df.to_csv(index=False),
    "filtered_data.csv"
)

# ----------------------

numeric_cols = filtered_df.select_dtypes(include=['int64', 'float64']).columns

if len(numeric_cols) < 2:
    st.warning("Not enough numeric data")
    st.stop()

st.sidebar.header("Graph Settings")

x_axis = st.sidebar.selectbox("X-axis", numeric_cols)
y_axis = st.sidebar.selectbox("Y-axis", numeric_cols)


st.subheader(" Bar Graph")

fig_bar = px.bar(filtered_df, x=x_axis, y=y_axis)
st.plotly_chart(fig_bar)

if disease_col:
    st.subheader("Disease Distribution")

    disease_count = filtered_df[disease_col].value_counts().reset_index()
    disease_count.columns = [disease_col, "Count"]

    fig_pie = px.pie(disease_count, names=disease_col, values="Count")
    st.plotly_chart(fig_pie)

if age_col:
    st.subheader("Age Distribution")

    fig_hist = px.histogram(filtered_df, x=age_col, nbins=20)
    st.plotly_chart(fig_hist)


st.subheader("2D Graph")

fig2d = px.scatter(filtered_df, x=x_axis, y=y_axis)
st.plotly_chart(fig2d)

if len(numeric_cols) >= 3:
    z_axis = st.sidebar.selectbox("Z-axis", numeric_cols)

    st.subheader("3D Graph")

    fig3d = px.scatter_3d(filtered_df, x=x_axis, y=y_axis, z=z_axis)
    st.plotly_chart(fig3d)


st.subheader(" Box Plot")

fig_box = px.box(filtered_df, y=y_axis)
st.plotly_chart(fig_box)

if disease_col:
    st.subheader("Top 5 Diseases")

    top5 = filtered_df[disease_col].value_counts().head(5)
    st.bar_chart(top5)

st.subheader("Correlation Heatmap")

corr = filtered_df[numeric_cols].corr()
fig_heatmap = px.imshow(corr, text_auto=True)
st.plotly_chart(fig_heatmap)

st.subheader(" Search Data")

search = st.text_input("Type anything")

if search:
    result = filtered_df[
        filtered_df.astype(str).apply(
            lambda row: row.str.lower().str.contains(search.lower()).any(),
            axis=1
        )
    ]

    st.write(result if len(result) > 0 else "No data found")


st.subheader("Column Statistics")

selected_col = st.selectbox("Select column", numeric_cols)

st.write("Mean:", filtered_df[selected_col].mean())
st.write("Max:", filtered_df[selected_col].max())
st.write("Min:", filtered_df[selected_col].min())


st.subheader(" Recommendations")

if age_col:
    avg_age = filtered_df[age_col].mean()

    if avg_age > 50:
        st.warning("Focus more on elderly patient care")

    elif avg_age < 30:
        st.info("Younger patient group is dominant")

if disease_col:
    top_disease = filtered_df[disease_col].value_counts().idxmax()
    st.success(f"Most common disease: {top_disease} → Increase resources for this")

    st.subheader(" Alerts")

if age_col:
    if filtered_df[age_col].max() > 75:
        st.error("High number of elderly patients → Need special care")

if disease_col:
    if filtered_df[disease_col].value_counts().iloc[0] > 20:
        st.warning("One disease is dominating → Check outbreak possibility")


