import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Monitoring Penerimaan Sektor UU 34 Tahun 1964",
    layout="wide",
)

st.title("📊 Dashboard Monitoring Penerimaan Sektor UU 34 Tahun 1964")
st.subheader("Kanwil DIY - Jasa Raharja (Sinkronisasi GitHub)")

# Nama file master di repository GitHub
data_file = "riwayat_penerimaan.xlsx"


@st.cache_data(ttl=10)
def load_github_data(filename):
  if os.path.exists(filename):
    try:
      return pd.read_excel(filename, sheet_name=0)
    except Exception as e:
      st.error(f"Gagal membaca file Excel: {e}")
      return None
  return None


df = load_github_data(data_file)

if df is not None and not df.empty:
  st.success("✅ Berhasil terhubung dengan data harian dari GitHub.")

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

  st.markdown("### 📋 Log Riwayat Penambahan Data Harian")
  st.dataframe(df, use_container_width=True)

  # Grafik tren otomatis jika kolom tersedia
  if "Tanggal" in df.columns and "Realisasi Harian (Rp)" in df.columns:
    st.markdown("### 📉 Grafik Tren Perkembangan Realisasi")
    st.line_chart(df, x="Tanggal", y="Realisasi Harian (Rp)")

else:
  st.warning(
      f"⚠️ File master `{data_file}` belum terbaca oleh skrip. Pastikan posisi"
      " file berada di direktori utama *repository* GitHub."
  )
