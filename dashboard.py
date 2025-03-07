import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
@st.cache_data
def load_data():
    customers_df = pd.read_csv("https://raw.githubusercontent.com/acah21/dataset/refs/heads/main/customers_dataset.csv")
    orders_df = pd.read_csv("https://raw.githubusercontent.com/acah21/dataset/refs/heads/main/orders_dataset.csv")
    order_items_df = pd.read_csv("https://raw.githubusercontent.com/acah21/dataset/refs/heads/main/order_items_dataset.csv")
    return customers_df, orders_df, order_items_df

customers_df, orders_df, order_items_df = load_data()

# Konversi tanggal transaksi
orders_df["order_purchase_timestamp"] = pd.to_datetime(orders_df["order_purchase_timestamp"])
latest_date = orders_df["order_purchase_timestamp"].max()

# RFM Analysis
rfm = orders_df.groupby("customer_id").agg(
    Recency=("order_purchase_timestamp", lambda x: (latest_date - x.max()).days),
    Frequency=("order_id", "count")
).reset_index()

monetary = order_items_df.groupby("order_id")["price"].sum().reset_index()
rfm = rfm.merge(orders_df[["customer_id", "order_id"]], on="customer_id", how="left").merge(monetary, on="order_id", how="left")
rfm = rfm.groupby("customer_id").agg(
    Recency=("Recency", "min"),
    Frequency=("Frequency", "max"),
    Monetary=("price", "sum")
).reset_index()

# Distribusi geografis
customer_city_counts = customers_df["customer_city"].value_counts().reset_index()
customer_city_counts.columns = ["customer_city", "count"]

customer_state_counts = customers_df["customer_state"].value_counts().reset_index()
customer_state_counts.columns = ["customer_state", "count"]

# Streamlit UI
st.title("📊 Dashboard Analisis RFM dan Distribusi Pelanggan")

st.header("1️⃣ RFM Analysis")
st.subheader("Distribusi Recency, Frequency, Monetary")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
sns.histplot(rfm["Recency"], bins=20, kde=True, ax=axes[0], color="blue").set(title='Distribusi Recency')
sns.histplot(rfm["Frequency"], bins=20, kde=True, ax=axes[1], color="green").set(title='Distribusi Frequency')
sns.histplot(rfm["Monetary"], bins=20, kde=True, ax=axes[2], color="red").set(title='Distribusi Monetary')
st.pyplot(fig)

st.header("2️⃣ Distribusi Geografis Pelanggan")
st.subheader("Top 10 Kota dengan Pelanggan Terbanyak")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y=customer_city_counts["customer_city"][:10], x=customer_city_counts["count"][:10], palette="Blues_r")
ax.set_xlabel("Jumlah Pelanggan")
st.pyplot(fig)

st.subheader("Distribusi Pelanggan per Negara Bagian")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y=customer_state_counts["customer_state"], x=customer_state_counts["count"], palette="Greens_r")
ax.set_xlabel("Jumlah Pelanggan")
st.pyplot(fig)

st.write("📌 *Dashboard ini memberikan wawasan tentang pola pembelian pelanggan dan distribusi geografis mereka untuk pengambilan keputusan bisnis yang lebih baik.*")
