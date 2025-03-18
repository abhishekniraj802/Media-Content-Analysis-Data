import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# Database Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Abhishek",
        database="Mediacontent"
    )

# Fetch Data from MySQL
def fetch_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT dc.headline, dc.grouped_category, dd.date, dd.month, dd.day_of_week,
               de.views, de.likes, de.comments, de.engagement_rate
        FROM fact_content fc
        JOIN dim_content dc ON fc.content_id = dc.content_id
        JOIN dim_date dd ON fc.date_id = dd.date_id
        JOIN dim_engagement de ON fc.engagement_id = de.engagement_id
        ORDER BY dd.date DESC;
    """
    
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    
    return pd.DataFrame(data)

# Load Data
df = fetch_data()

# 🏆 Streamlit UI
st.set_page_config(page_title="Media Content Dashboard", layout="wide")

# 📌 Title
st.title("📊 Media Content Analytics Platform")

# 📌 Summary Metrics
total_views = df["views"].sum()
total_likes = df["likes"].sum()
total_comments = df["comments"].sum()
avg_engagement_rate = df["engagement_rate"].mean()

# 📊 Display Summary Metrics with Colors
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="📺 Total Views", value=f"{total_views:,}", delta="📈 Trending", help="Total number of views across all content.")

with col2:
    st.metric(label="❤️ Total Likes", value=f"{total_likes:,}", delta="🔥 Popular", help="Total likes received on all content.")

with col3:
    st.metric(label="💬 Total Comments", value=f"{total_comments:,}", delta="💡 Engagement", help="Total number of comments.")

with col4:
    st.metric(label="📊 Avg Engagement Rate", value=f"{avg_engagement_rate:.2f}%", delta="📉 Performance", help="Average engagement rate across content.")

st.markdown("---")  # Divider for better visual separation

# 📌 Sidebar Filters
st.sidebar.header("📌 Filter the Data")
category_filter = st.sidebar.multiselect("Select Category", df["grouped_category"].unique())
month_filter = st.sidebar.multiselect("Select Month", df["month"].unique())

# 📦 **Engagement Rate Filter (Inside a Box)**
with st.sidebar.expander("📈 **Engagement Rate Filter**"):
    min_engagement = st.number_input("Min Engagement Rate (%)", 
                                     min_value=float(df["engagement_rate"].min()), 
                                     value=float(df["engagement_rate"].min()))
    
    max_engagement = st.number_input("Max Engagement Rate (%)", 
                                     max_value=float(df["engagement_rate"].max()), 
                                     value=float(df["engagement_rate"].max()))

# Apply Filters
if category_filter:
    df = df[df["grouped_category"].isin(category_filter)]
if month_filter:
    df = df[df["month"].isin(month_filter)]
if min_engagement or max_engagement:
    df = df[(df["engagement_rate"] >= min_engagement) & 
            (df["engagement_rate"] <= max_engagement)]

# 📄 Data Preview
st.subheader("📄 Data Preview")
st.dataframe(df)

# 📊 Visualization 1: Views by Category
fig1 = px.bar(df, x="grouped_category", y="views", color="grouped_category", title="Total Views per Category")
st.plotly_chart(fig1, use_container_width=True)

# 📈 Visualization 2: Engagement Rate Over Time
fig2 = px.line(df, x="date", y="engagement_rate", title="Engagement Rate Trend")
st.plotly_chart(fig2, use_container_width=True)

# 📌 Visualization 3: Likes vs Comments Scatter Plot
fig3 = px.scatter(df, x="likes", y="comments", color="grouped_category", size="views",
                  title="Likes vs Comments (Bubble Chart)")
st.plotly_chart(fig3, use_container_width=True)

# 📊 Visualization 4: Engagement Rate by Category
fig4 = px.bar(df, x="grouped_category", y="engagement_rate", color="grouped_category", 
              title="Average Engagement Rate per Category", barmode="group")
st.plotly_chart(fig4, use_container_width=True)

# 📊 Visualization 5: Trending Content on Weekends
df_weekends = df[df["day_of_week"].isin(["Saturday", "Sunday"])]
fig5 = px.bar(df_weekends, x="day_of_week", y="views", color="grouped_category",
              title="Trending Content on Weekends")
st.plotly_chart(fig5, use_container_width=True)

# 📌 Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.write("📌 Built with ❤ using Streamlit")
