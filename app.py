import pandas as pd
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Dashboard Penerimaan Jasa Raharja DIY",
    layout="wide",
)

# Judul Utama Dashboard
st.title("📊 Dashboard Monitoring Penerimaan Sektor UU 34 Tahun 1964")
st.subheader("Kanwil DIY - Jasa Raharja")

# Fungsi untuk memuat dan membersihkan data dari Excel
@st.cache_data
def load_data():
  file_path = "Penerimaan Sektor UU 34 Tahun 1964.xlsx"
  df = pd.read_excel(file_path, sheet_name="HARIAN BARU (2)")
  return df

# Memuat data
try:
  df_raw = load_data()

  # Mengambil informasi periode dari metadata baris ke-2 Excel
  periode_teks = df_raw.iloc[2, 1] if pd.notna(df_raw.iloc[2, 1]) else "-"
  st.info(f"📌 Informasi Periode Laporan: **{periode_teks}**")

  # Sidebar untuk Filter Interaktif
  st.sidebar.header("Panel Kontrol & Filter")
  pilihan_loket = st.sidebar.selectbox(
      "Pilih Loket SAMSAT",
      ["Semua Loket (DIY)", "Kota", "Sleman", "Bantul", "Kulon Progo", "Gunung Kidul"],
  )

  # Ekstraksi Tabel Utama Sektor (Baris 7-10)
  tabel_sektor = df_raw.iloc[7:11, [1, 5, 6, 9]].copy()
  tabel_sektor.columns = [
      "Jenis Dana",
      "Realisasi s.d. Hari Ini",
      "Prosentase Siklikal (%)",
      "Siklikal YTY (%)",
  ]

  tabel_sektor["Jenis Dana"] = [
      "Kartu Dana / Sertifikat",
      "SWDKLLJ",
      "Denda",
      "Total Penerimaan",
  ]

  # Menampilkan Metrik Utama di Bagian Atas Web
  st.markdown("### 📈 Ringkasan Penerimaan Keseluruhan")
  col1, col2, col3, col4 = st.columns(4)

  try:
    val_kartu = float(tabel_sektor.iloc[0]["Realisasi s.d. Hari Ini"])
    val_sw = float(tabel_sektor.iloc[1]["Realisasi s.d. Hari Ini"])
    val_denda = float(tabel_sektor.iloc[2]["Realisasi s.d. Hari Ini"])
    val_total = float(tabel_sektor.iloc[3]["Realisasi s.d. Hari Ini"])
  except:
    val_kartu, val_sw, val_denda, val_total = 0, 0, 0, 0

  with col1:
    st.metric(label="Kartu Dana", value=f"Rp {val_kartu:,.0f}".replace(",", "."))
  with col2:
    st.metric(label="SWDKLLJ", value=f"Rp {val_sw:,.0f}".replace(",", "."))
  with col3:
    st.metric(label="Denda", value=f"Rp {val_denda:,.0f}".replace(".", "."))
  with col4:
    st.metric(
        label="Overall Penerimaan (Total)",
        value=f"Rp {val_total:,.0f}".replace(",", "."),
    )

  st.markdown("---")

  # Menampilkan Tabel Rinci di Web
  st.markdown("### 📋 Detail Rekapitulasi Per Sektor Pendanaan")
  st.dataframe(tabel_sektor, use_container_width=True)

  # Bagian Target Persentase Siklikal dari Pusat
  st.markdown("### 🎯 Evaluasi Target Siklikal Kantor Pusat")
  tabel_siklikal = tabel_sektor[["Jenis Dana", "Prosentase Siklikal (%)", "Siklikal YTY (%)"]]
  st.table(tabel_siklikal)

except Exception as e:
  st.error(
      f"Terjadi kesalahan saat membaca file Excel: {e}. Pastikan file"
      " 'Penerimaan Sektor UU 34 Tahun 1964.xlsx' sudah diunggah di repository"
      " ini."
  )
