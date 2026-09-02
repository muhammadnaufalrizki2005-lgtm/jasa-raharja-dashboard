import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Penerimaan Jasa Raharja DIY",
    layout="wide",
)

st.title("📊 Dashboard Monitoring Penerimaan Sektor UU 34 Tahun 1964")
st.subheader("Kanwil DIY - Jasa Raharja")

# Widget upload di sidebar
uploaded_file = st.sidebar.file_uploader(
    "Unggah File Laporan Excel (Opsional)", type=["xlsx", "xls"]
)

# Menentukan sumber file (prioritas file upload, jika kosong gunakan file default di GitHub)
default_filename = "Penerimaan Sektor UU 34 Tahun 1964.xlsx"
source_to_read = None

if uploaded_file is not None:
  source_to_read = uploaded_file
  st.sidebar.success("✅ Menggunakan file dari hasil unggahan.")
elif os.path.exists(default_filename):
  source_to_read = default_filename
  st.sidebar.info(
      "📌 Menggunakan file default dari GitHub (aman dari reset/restart)."
  )

if source_to_read is not None:
  try:
    df_raw = pd.read_excel(source_to_read, sheet_name=0)
    periode_teks = (
        df_raw.iloc[2, 1] if pd.notna(df_raw.iloc[2, 1]) else "Periode Aktif"
    )

    tabel_sektor = df_raw.iloc[6:10, [1, 2, 3, 4]].copy()
    tabel_sektor.columns = [
        "Jenis Dana",
        "Realisasi s.d. Hari Ini",
        "Prosentase Siklikal (%)",
        "Siklikal YTY (%)",
    ]

    st.info(f"📌 Informasi Periode Laporan: **{periode_teks}**")

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
      st.metric(
          label="Kartu Dana", value=f"Rp {val_kartu/1e6:,.2f} Juta".replace(".", ",")
      )
    with col2:
      st.metric(
          label="SWDKLLJ", value=f"Rp {val_sw/1e6:,.2f} Juta".replace(".", ",")
      )
    with col3:
      st.metric(
          label="Denda", value=f"Rp {val_denda/1e6:,.2f} Juta".replace(".", ",")
      )
    with col4:
      st.metric(
          label="Total Penerimaan",
          value=f"Rp {val_total/1e6:,.2f} Juta".replace(".", ","),
      )

    st.markdown("---")

    st.markdown("### 📋 Detail Rekapitulasi Per Sektor Pendanaan")
    st.dataframe(tabel_sektor, use_container_width=True)

    st.markdown("### 🎯 Evaluasi Target Siklikal Kantor Pusat")
    tabel_siklikal = tabel_sektor[
        ["Jenis Dana", "Prosentase Siklikal (%)", "Siklikal YTY (%)"]
    ]
    st.table(tabel_siklikal)

  except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca struktur file Excel: {e}")
else:
  st.warning(
      "⚠️ Belum ada file Excel yang diunggah dan file default belum tersedia di"
      " GitHub. Unggah file Excel melalui panel kiri atau masukkan file"
      " bernama 'Penerimaan Sektor UU 34 Tahun 1964.xlsx' langsung ke dalam"
      " repository GitHub Anda."
  )
