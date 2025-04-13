import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Pengaturan halaman Streamlit
st.set_page_config(page_title="Dashboard Lift Prioritas", layout="wide")

# Judul Aplikasi
st.title("🚠 Dashboard Lift Prioritas di Jembatan Penyeberangan Orang")
st.markdown("Selamat datang di **Dashboard Lift Prioritas**, di mana kamu bisa melihat informasi terkait penggunaan lift oleh masyarakat, khususnya kelompok rentan. 👥")

st.markdown("---")

# Fungsi untuk Membuat Data Dummy
def create_dummy_data():
    dates = pd.date_range(start="2025-04-01", periods=30)
    data = {
        "timestamp": np.random.choice(dates, size=100),
        "is_vulnerable": np.random.choice([True, False], size=100),
        "gender": np.random.choice(["Pria", "Wanita"], size=100),
        "age": np.random.randint(18, 80, size=100),
        "vulnerable_type": np.random.choice(["Disabilitas", "Lansia", "Ibu Hamil"], size=100)
    }
    return pd.DataFrame(data)

# Generate Data
df = create_dummy_data()

# Statistik Utama
st.header("📊 Statistik Umum Pengguna")
col1, col2, col3 = st.columns(3)

with col1:
    total_vulnerable_users = df[df['is_vulnerable']].shape[0]
    st.metric("Kelompok Rentan", f"{total_vulnerable_users} Orang")

with col2:
    total_users = df.shape[0]
    percentage_vulnerable = (total_vulnerable_users / total_users) * 100 if total_users > 0 else 0.0
    st.metric("% Pengguna Rentan", f"{percentage_vulnerable:.2f}%")

with col3:
    average_daily_users = df.groupby(df['timestamp'].dt.date).size().mean()
    st.metric("Rata-rata per Hari", f"{average_daily_users:.2f} Orang")

st.markdown("---")

# Line Chart
st.subheader("📈 Tren Penggunaan Lift Per Hari")
daily_counts = df.groupby(df['timestamp'].dt.date).size()
plt.figure(figsize=(10, 5))
plt.plot(daily_counts.index.astype(str), daily_counts.values, marker='o', linestyle='-', color='royalblue')
plt.title('Jumlah Pengguna Lift Prioritas per Hari')
plt.xlabel('Tanggal')
plt.ylabel('Jumlah Pengguna')
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(plt)

# Pie Chart Jenis Kelamin
st.subheader("👤 Distribusi Pengguna Berdasarkan Jenis Kelamin")
gender_counts = df['gender'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%', startangle=90, colors=['#66b3ff','#ff9999'])
ax1.axis('equal')
plt.title('Distribusi Jenis Kelamin Pengguna')
st.pyplot(fig1)

st.markdown("---")

# Tabel Data Pengguna
st.subheader("📋 Tabel Data Pengguna JPO")
user_table_columns = ["No.", "Timestamp", "Apakah Kelompok Rentan?"]
user_table_data = [
    [i + 1 for i in range(len(df))],
    df["timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
    df["is_vulnerable"].apply(lambda x: '✅ Ya' if x else '❌ Tidak').tolist(),
]

user_table_df = pd.DataFrame(user_table_data).T.rename(columns={0: user_table_columns[0], 
                                                                1: user_table_columns[1], 
                                                                2: user_table_columns[2]})
st.dataframe(user_table_df)

# Tabel Kelompok Rentan
st.subheader("🧓👩‍🦽👶 Tabel Data Anggota Kelompok Rentan")
vulnerable_group_df = df[df['is_vulnerable']][["timestamp", "gender", "age", "vulnerable_type"]].reset_index(drop=True)

vulnerability_user_columns = ["No.", 'Timestamp', 'Jenis Kelamin', 'Usia', 'Jenis Kelompok Rentan']
vulnerability_user_data = [
    [i + 1 for i in range(len(vulnerable_group_df))],
    vulnerable_group_df["timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
    vulnerable_group_df["gender"].tolist(),
    vulnerable_group_df["age"].tolist(),
    vulnerable_group_df["vulnerable_type"].tolist()
]

vulnerability_user_dataframe = pd.DataFrame(vulnerability_user_data).T.rename(columns={0: vulnerability_user_columns[0],
                                                                                       1: vulnerability_user_columns[1],
                                                                                       2: vulnerability_user_columns[2],
                                                                                       3: vulnerability_user_columns[3],
                                                                                       4: vulnerability_user_columns[4]})

if not vulnerability_user_dataframe.empty:
    st.dataframe(vulnerability_user_dataframe)
else:
    st.info("Tidak ada data kelompok rentan saat ini.")

