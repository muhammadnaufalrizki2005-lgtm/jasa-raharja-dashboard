import glob
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Monitoring Penerimaan Jasa Raharja DIY",
    layout="wide",
)

st.title("📊 Dashboard Monitoring Penerimaan Sektor UU 34 Tahun 1964")
st.subheader("Kanwil DIY - Jasa Raharja (Akumulasi Kumulatif Harian)")

folder_arsip = "data_harian"


@st.cache_data(ttl=10)
def load_cumulative_archives(folder):
  if not os.path.exists(folder):
    os.makedirs(folder)
    return pd.DataFrame()

  daftar_file = glob.glob(os.path.join(folder, "*.xlsx"))
  if not daftar_file:
    return pd.DataFrame()

  # Urutkan file agar kronologis (berdasarkan nama file)
  daftar_file.sort()

  list_ringkasan = []
  list_detail = []

  for file_path in daftar_file:
    nama_file = os.path.basename(file_path)
    try:
      df_raw = pd.read_excel(file_path, sheet_name=0)
      periode = (
          df_raw.iloc[2, 1] if pd.notna(df_raw.iloc[2, 1]) else "Tidak Diketahui"
      )

      # Ekstraksi tabel sektor (Baris 6 s.d. 9, Kolom B, C, D, E)
      tabel_sektor = df_raw.iloc[6:10, [1, 2, 3, 4]].copy()
      tabel_sektor.columns = [
          "Jenis Dana",
          "Realisasi s.d. Hari Ini",
          "Prosentase Siklikal (%)",
          "Siklikal YTY (%)",
      ]
      tabel_sektor["Sumber File"] = nama_file
      tabel_sektor["Periode Laporan"] = periode
      list_detail.append(tabel_sektor)

      # Ambil nilai Total Penerimaan untuk grafik tren historis
      row_total = tabel_sektor[
          tabel_sektor["Jenis Dana"].str.contains("Total", case=False, na=False)
      ]
      if not row_total.empty:
        total_val = float(row_total["Realisasi s.d. Hari Ini"].values[0])
        list_ringkasan.append(
            {"File": nama_file, "Periode": periode, "Total Penerimaan": total_val}
        )

    except Exception as e:
      st.warning(f"Gagal membaca file {nama_file}: {e}")

  df_detail_gabungan = (
      pd.concat(list_detail, ignore_index=True) if list_detail else pd.DataFrame()
  )
  df_tren = (
      pd.DataFrame(list_ringkasan) if list_ringkasan else pd.DataFrame()
  )

  return df_detail_gabungan, df_tren


df_detail, df_tren = load_cumulative_archives(folder_arsip)

if not df_detail.empty:
  st.success("✅ Berhasil memuat arsip laporan kumulatif dari GitHub.")

  # Panel Samping
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

  daftar_file_tersedia = df_detail["Sumber File"].unique()
  file_pilihan = st.sidebar.selectbox(
      "Pilih Tanggal Laporan yang Ingin Dilihat",
      daftar_file_tersedia,
      index=len(daftar_file_tersedia) - 1,
  )

  # Filter data sesuai file/tanggal yang dipilih di sidebar
  df_terpilih = df_detail[df_detail["Sumber File"] == file_pilihan]
  periode_aktif = (
      df_terpilih["Periode Laporan"].iloc[0] if not df_terpilih.empty else "-"
  )

  st.info(
      f"📌 Menampilkan Posisi Laporan Per Tanggal Berkas: **{file_pilihan}** |"
      f" {periode_aktif}"
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

  # Tata letak metrik 2x2 agar tidak terpotong
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
        label="Total Penerimaan Kumulatif",
        value=f"Rp {val_total/1e6:,.2f} Juta".replace(".", ","),
    )

  st.markdown("---")

  st.markdown("### 📋 Detail Sektor Pendanaan pada Tanggal Tersebut")
  st.dataframe(
      df_terpilih[[
          "Jenis Dana",
          "Realisasi s.d. Hari Ini",
          "Prosentase Siklikal (%)",
          "Siklikal YTY (%)",
      ]],
      use_container_width=True,
  )

  # Grafik Perbandingan Tren Pertumbuhan Antar Tanggal Laporan
  if not df_tren.empty and len(df_tren) > 1:
    st.markdown("---")
    st.markdown("### 📉 Grafik Tren Pertumbuhan Total Penerimaan (Historis)")
    st.line_chart(df_tren.set_index("File")["Total Penerimaan"])

else:
  st.warning(
      "⚠️ Belum ada file Excel di dalam folder `data_harian/` di GitHub."
      " Silakan unggah file data awal (misal: laporan s.d. 31 Agustus) dan file"
      " harian berikutnya ke dalam folder tersebut."
  )
