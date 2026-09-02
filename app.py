import glob
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Monitoring Penerimaan Jasa Raharja DIY",
    layout="wide",
)

st.title("📊 Dashboard Monitoring Penerimaan Sektor UU 34 Tahun 1964")
st.subheader("Kanwil DIY - Jasa Raharja (Arsip Harian GitHub)")

# Folder penyimpanan arsip di GitHub
folder_arsip = "data_harian"


@st.cache_data(ttl=10)
def load_all_daily_files(folder):
  if not os.path.exists(folder):
    os.makedirs(folder)
    return pd.DataFrame()

  daftar_file = glob.glob(os.path.join(folder, "*.xlsx"))
  if not daftar_file:
    return pd.DataFrame()

  list_data = []
  daftar_file.sort()  # Mengurutkan file secara kronologis

  for file_path in daftar_file:
    try:
      df_raw = pd.read_excel(file_path, sheet_name=0)
      periode = (
          df_raw.iloc[2, 1] if pd.notna(df_raw.iloc[2, 1]) else "Tidak Diketahui"
      )

      # Ekstraksi tabel sektor (Baris 6 sampai 9, Kolom B, C, D, E -> Indeks 1, 2, 3, 4)
      tabel_sektor = df_raw.iloc[6:10, [1, 2, 3, 4]].copy()
      tabel_sektor.columns = [
          "Jenis Dana",
          "Realisasi s.d. Hari Ini",
          "Prosentase Siklikal (%)",
          "Siklikal YTY (%)",
      ]
      tabel_sektor["Sumber File"] = os.path.basename(file_path)
      tabel_sektor["Periode Laporan"] = periode

      list_data.append(tabel_sektor)
    except Exception as e:
      st.warning(f"Gagal membaca file {os.path.basename(file_path)}: {e}")

  if list_data:
    return pd.concat(list_data, ignore_index=True)
  return pd.DataFrame()


# Memuat data gabungan
df_gabungan = load_all_daily_files(folder_arsip)

if not df_gabungan.empty:
  st.success("✅ Berhasil memuat seluruh arsip laporan dari folder GitHub.")

  # Panel Samping Pilihan Loket & Arsip File
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

  daftar_file_tersedia = df_gabungan["Sumber File"].unique()
  file_pilihan = st.sidebar.selectbox(
      "Pilih Berkas Laporan Harian",
      daftar_file_tersedia,
      index=len(daftar_file_tersedia) - 1,
  )

  # Filter data berdasarkan file yang dipilih di sidebar
  df_terpilih = df_gabungan[df_gabungan["Sumber File"] == file_pilihan]
  periode_aktif = (
      df_terpilih["Periode Laporan"].iloc[0] if not df_terpilih.empty else "-"
  )

  st.info(
      f"📌 Menampilkan Laporan dari Berkas: **{file_pilihan}** | Periode:"
      f" **{periode_aktif}**"
  )

  st.markdown("### 📈 Ringkasan Penerimaan Keseluruhan")

  try:
    val_kartu = float(
        df_terpilih[
            df_terpilih["Jenis Dana"].str.contains(
                "Kartu", case=False, na=False
            )
        ]["Realisasi s.d. Hari Ini"].values[0]
    )
    val_sw = float(
        df_terpilih[
            df_terpilih["Jenis Dana"].str.contains(
                "SWDKLLJ", case=False, na=False
            )
        ]["Realisasi s.d. Hari Ini"].values[0]
    )
    val_denda = float(
        df_terpilih[
            df_terpilih["Jenis Dana"].str.contains("Denda", case=False, na=False)
        ]["Realisasi s.d. Hari Ini"].values[0]
    )
    val_total = float(
        df_terpilih[
            df_terpilih["Jenis Dana"].str.contains("Total", case=False, na=False)
        ]["Realisasi s.d. Hari Ini"].values[0]
    )
  except:
    val_kartu, val_sw, val_denda, val_total = 0, 0, 0, 0

  # Tata letak metrik 2 kolom agar tidak terpotong
  row1_col1, row1_col2 = st.columns(2)
  with row1_col1:
    st.metric(
        label="Kartu Dana",
        value=f"Rp {val_kartu/1e6:,.2f} Juta".replace(".", ","),
    )
  with row1_col2:
    st.metric(
        label="SWDKLLJ", value=f"Rp {val_sw/1e6:,.2f} Juta".replace(".", ",")
    )

  row2_col1, row2_col2 = st.columns(2)
  with row2_col1:
    st.metric(
        label="Denda", value=f"Rp {val_denda/1e6:,.2f} Juta".replace(".", ",")
    )
  with row2_col2:
    st.metric(
        label="Total Penerimaan",
        value=f"Rp {val_total/1e6:,.2f} Juta".replace(".", ","),
    )

  st.markdown("---")

  st.markdown("### 📋 Detail Tabel Sektor Pendanaan")
  st.dataframe(
      df_terpilih[[
          "Jenis Dana",
          "Realisasi s.d. Hari Ini",
          "Prosentase Siklikal (%)",
          "Siklikal YTY (%)",
      ]],
      use_container_width=True,
  )

  with st.expander("📁 Lihat Seluruh Riwayat Gabungan Semua File Harian"):
    st.dataframe(df_gabungan, use_container_width=True)

else:
  st.warning(
      "⚠️ Belum ada file Excel di dalam folder `data_harian/` di GitHub. "
      "Silakan unggah file laporan harian Anda (misal:"
      " `laporan_harian_20260902.xlsx`) ke dalam folder tersebut."
  )
