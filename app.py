import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Penerimaan Jasa Raharja DIY",
    layout="wide",
)

st.title("📊 Dashboard Monitoring Penerimaan Sektor UU 34 Tahun 1964")
st.subheader("Kanwil DIY - Jasa Raharja")

uploaded_file = st.sidebar.file_uploader(
    "Unggah File Laporan Excel", type=["xlsx", "xls"]
)

if uploaded_file is not None:
  try:
    # Membaca sheet pertama secara otomatis
    df_raw = pd.read_excel(uploaded_file, sheet_name=0)
    periode_teks = (
        df_raw.iloc[2, 1] if pd.notna(df_raw.iloc[2, 1]) else "Periode Aktif"
    )

    # Menyesuaikan rentang baris agar mencakup Kartu Dana (Indeks 6 sampai 9)
    tabel_sektor = df_raw.iloc[6:10, [1, 2, 3, 4]].copy()
    tabel_sektor.columns = [
        "Jenis Dana",
        "Realisasi s.d. Hari Ini",
        "Prosentase Siklikal (%)",
        "Siklikal YTY (%)",
    ]

    st.success("✅ Berhasil memuat dan memproses data dari file Excel!")
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
          label="Kartu Dana", value=f"Rp {val_kartu:,.0f}".replace(",", ".")
      )
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

    st.markdown("### 📋 Detail Rekapitulasi Per Sektor Pendanaan")
    st.dataframe(tabel_sektor, use_container_width=True)

    st.markdown("### 🎯 Evaluasi Target Siklikal Kantor Pusat")
    tabel_siklikal = tabel_sektor[
        ["Jenis Dana", "Prosentase Siklikal (%)", "Siklikal YTY (%)"]
    ]
    st.table(tabel_siklikal)

  except Exception as e:
    st.error(
        f"Terjadi kesalahan saat membaca struktur file Excel: {e}. Pastikan posisi"
        " tabel utama dimulai dari baris ke-7 Excel."
    )
else:
  st.info(
      "📂 **Silakan unggah file Excel laporan Anda** menggunakan panel di"
      " sebelah kiri untuk menampilkan dasbor secara instan."
  )
