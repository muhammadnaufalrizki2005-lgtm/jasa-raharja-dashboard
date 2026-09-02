import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Monitoring Penerimaan Jasa Raharja DIY",
    layout="wide",
)

st.title("📊 Dashboard Monitoring Penerimaan Sektor UU 34 Tahun 1964")
st.subheader("Kanwil DIY - Jasa Raharja (Sinkronisasi GitHub)")

# Nama file master di repository GitHub
data_file = "riwayat_penerimaan.xlsx"  # atau "riwayat_penerimaan.csv"

@st.cache_data(ttl=60)
def load_github_data(filename):
  if os.path.exists(filename):
    if filename.endswith(".csv"):
      return pd.read_csv(filename)
    else:
      return pd.read_excel(filename)
  return None

df = load_github_data(data_file)

if df is not None and not df.empty:
  st.success("✅ Terhubung otomatis dengan data harian dari GitHub.")

  # Panel Samping Filter Loket
  pilihan_loket = st.sidebar.selectbox(
      "Pilih Loket SAMSAT",
      [
          "Semua Loket (DIY)",
          "Kota",
          "Sleman",
          "Bantul",
          "Kulon Progo",
          "Gunung Kidul",
      ],
  )

  st.markdown("### 📈 Ringkasan & Tren Penerimaan Terbaru")
  
  # Menampilkan tabel data yang terus bertambah setiap hari
  st.markdown("### 📋 Log Riwayat Penambahan Data Harian")
  st.dataframe(df, use_container_width=True)

  # Jika kolom tanggal tersedia, kita bisa buatkan grafik pertumbuhan otomatis
  if "Tanggal" in df.columns and "Realisasi Harian (Rp)" in df.columns:
    st.markdown("### 📉 Grafik Tren Perkembangan Realisasi")
    st.line_chart(df, x="Tanggal", y="Realisasi Harian (Rp)")

else:
  st.warning(
      f"⚠️ File master `{data_file}` belum ditemukan di repository GitHub."
      " Silakan unggah file tersebut ke GitHub agar dasbor dapat membaca"
      " penambahan data harian Anda."
  )
