import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")
st.title("📊 Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# Load local dataset directly
os.chdir(r"C:\Users\HP\OneDrive\Desktop\python")
df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")

# Clean column names
df.columns = df.columns.str.strip()

# Date conversion with mixed format handling
try:
    df["Order Date"] = pd.to_datetime(df["Order Date"], format='mixed')
except Exception as e:
    st.error(f"Failed to parse 'Order Date' column: {e}")

startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

col1, col2 = st.columns(2)
with col1:
    date1 = st.date_input("Start Date", startDate)
with col2:
    date2 = st.date_input("End Date", endDate)

df = df[(df["Order Date"] >= pd.to_datetime(date1)) & (df["Order Date"] <= pd.to_datetime(date2))].copy()

# Sidebar filters
st.sidebar.header("Choose your filters:")
region = st.sidebar.multiselect("Pick Region", df["Region"].unique())
df_region = df[df["Region"].isin(region)] if region else df

state = st.sidebar.multiselect("Pick State", df_region["State"].unique())
df_state = df_region[df_region["State"].isin(state)] if state else df_region

city = st.sidebar.multiselect("Pick City", df_state["City"].unique())
filtered_df = df_state[df_state["City"].isin(city)] if city else df_state

# --- Charts ---
category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()
region_df = filtered_df.groupby("Region", as_index=False)["Sales"].sum()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Category-wise Sales")
    fig = px.bar(
        category_df,
        x="Category",
        y="Sales",
        text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
        template="seaborn",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Region-wise Sales")
    fig = px.pie(
        region_df,
        values="Sales",
        names="Region",
        hole=0.5,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv")

with cl2:
    with st.expander("Region_ViewData"):
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

# Time series chart
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('📈 Time Series Analysis')
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y-%b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button("Download", data=csv, file_name='TimeSeries.csv', mime='text/csv')

# Treemap
st.subheader("🗂 Hierarchical view of Sales using Treemap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"],
                  values="Sales", hover_data=["Sales"], color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

# Segment and Category pie charts
chart1, chart2 = st.columns(2)
with chart1:
    st.subheader('Segment-wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category-wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# Month-wise Sub-category Sales Summary
st.subheader(":point_right: Month-wise Sub-category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=False)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 📊 Pivot Table: Sub-Category vs Month")
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    elif "Sub-Category" not in filtered_df.columns:
        st.error("Column 'Sub-Category' is missing.")
    else:
        filtered_df["Month"] = filtered_df["Order Date"].dt.month_name()
        pivot = pd.pivot_table(
            data=filtered_df,
            values="Sales",
            index=["Sub-Category"],
            columns="Month",
            aggfunc="sum",
            fill_value=0
        )
        st.dataframe(pivot.style.background_gradient(cmap="YlGnBu"))
        csv = pivot.to_csv().encode("utf-8")
        st.download_button("Download Pivot Table", data=csv, file_name="Month_SubCategory_Sales.csv", mime="text/csv")

# Scatter Plot
st.subheader("Scatter Plot: Sales vs Profit")
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1.update_layout(
    title="Relationship between Sales and Profits using Scatter Plot.",
    titlefont=dict(size=20),
    xaxis=dict(title="Sales", titlefont=dict(size=16)),
    yaxis=dict(title="Profit", titlefont=dict(size=16))
)
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download Original Dataset
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Original Dataset", data=csv, file_name="Original_Dataset.csv", mime="text/csv")
