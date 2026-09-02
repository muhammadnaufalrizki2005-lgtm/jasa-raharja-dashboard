import glob
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Monitoring Penerimaan Jasa Raharja DIY",
    layout="wide",
)

st.title("📊 Dashboard Monitoring Penerimaan Sektor UU 34 Tahun 1964")
st.subheader("Kanwil DIY - Jasa Raharja (Multi-Loket SAMSAT)")

folder_arsip = "data_harian"


@st.cache_data(ttl=10)
def load_multi_loket_archives(folder):
  if not os.path.exists(folder):
    os.makedirs(folder)
    return pd.DataFrame(), pd.DataFrame()

  daftar_file = glob.glob(os.path.join(folder, "*.xlsx"))
  if not daftar_file:
    return pd.DataFrame(), pd.DataFrame()

  daftar_file.sort()
  list_semua_data = []
  list_tren = []

  for file_path in daftar_file:
    nama_file = os.path.basename(file_path)
    try:
      df_raw = pd.read_excel(file_path, sheet_name=0)
      # Periode berada di baris indeks 1
      periode = (
          df_raw.iloc[1, 1] if pd.notna(df_raw.iloc[1, 1]) else "Tidak Diketahui"
      )

      # Mapping indeks baris data yang tepat di pandas (0-based index)
      mapping_loket = [
          ("Kota", 5, 8),
          ("Sleman", 10, 13),
          ("Bantul", 15, 18),
          ("Kulon Progo", 20, 23),
          ("Gunung Kidul", 25, 28),
      ]

      for loket, start_r, end_r in mapping_loket:
        try:
          sub_df = df_raw.iloc[start_r : end_r + 1, [1, 2, 3, 4]].copy()
          sub_df.columns = [
              "Jenis Dana",
              "Realisasi s.d. Hari Ini",
              "Prosentase Siklikal (%)",
              "Siklikal YTY (%)",
          ]
          sub_df["Loket SAMSAT"] = loket
          sub_df["Sumber File"] = nama_file
          sub_df["Periode Laporan"] = periode
          list_semua_data.append(sub_df)
        except Exception:
          continue

    except Exception as e:
      st.warning(f"Gagal membaca file {nama_file}: {e}")

  df_gabungan = (
      pd.concat(list_semua_data, ignore_index=True)
      if list_semua_data
      else pd.DataFrame()
  )

  if not df_gabungan.empty:
    df_diy = (
        df_gabungan[
            df_gabungan["Jenis Dana"].str.contains("Total", case=False, na=False)
        ]
        .groupby(["Sumber File", "Periode Laporan"])["Realisasi s.d. Hari Ini"]
        .sum()
        .reset_index()
    )
    df_tren = df_diy.rename(
        columns={"Realisasi s.d. Hari Ini": "Total DIY"}
    )
  else:
    df_tren = pd.DataFrame()

  return df_gabungan, df_tren


df_gabungan, df_tren = load_multi_loket_archives(folder_arsip)

if not df_gabungan.empty:
  st.success("✅ Berhasil memuat arsip multi-loket dari GitHub.")

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
      "Pilih Tanggal Laporan yang Ingin Dilihat",
      daftar_file_tersedia,
      index=len(daftar_file_tersedia) - 1,
  )

  df_filtered_file = df_gabungan[df_gabungan["Sumber File"] == file_pilihan]

  if pilihan_loket == "Semua Loket (DIY)":
    df_aktif = (
        df_filtered_file.groupby(
            ["Jenis Dana", "Periode Laporan", "Sumber File"]
        )[["Realisasi s.d. Hari Ini"]]
        .sum()
        .reset_index()
    )
    df_pct = (
        df_filtered_file.groupby("Jenis Dana")[[
            "Prosentase Siklikal (%)",
            "Siklikal YTY (%)",
        ]]
        .mean()
        .reset_index()
    )
    df_aktif = pd.merge(df_aktif, df_pct, on="Jenis Dana")
  else:
    df_aktif = df_filtered_file[
        df_filtered_file["Loket SAMSAT"] == pilihan_loket
    ]

  periode_aktif = (
      df_aktif["Periode Laporan"].iloc[0] if not df_aktif.empty else "-"
  )

  st.info(
      f"📌 Menampilkan Posisi Laporan Per Tanggal Berkas: **{file_pilihan}** |"
      f" {periode_aktif}"
  )

  st.markdown("### 📈 Ringkasan Penerimaan Keseluruhan")

  try:
    val_kartu = float(
        df_aktif[
            df_aktif["Jenis Dana"].str.contains(
                "Kartu", case=False, na=False
            )
        ]["Realisasi s.d. Hari Ini"].values[0]
    )
    val_sw = float(
        df_aktif[
            df_aktif["Jenis Dana"].str.contains(
                "SWDKLLJ", case=False, na=False
            )
        ]["Realisasi s.d. Hari Ini"].values[0]
    )
    val_denda = float(
        df_aktif[
            df_aktif["Jenis Dana"].str.contains("Denda", case=False, na=False)
        ]["Realisasi s.d. Hari Ini"].values[0]
    )
    val_total = float(
        df_aktif[
            df_aktif["Jenis Dana"].str.contains("Total", case=False, na=False)
        ]["Realisasi s.d. Hari Ini"].values[0]
    )
  except:
    val_kartu, val_sw, val_denda, val_total = 0, 0, 0, 0

  r1c1, r1c2 = st.columns(2)
  with r1c1:
    st.metric(
        label="Kartu Dana",
        value=f"Rp {val_kartu/1e6:,.2f} Juta".replace(".", ","),
    )
  with r1c2:
    st.metric(
        label="SWDKLLJ", value=f"Rp {val_sw/1e6:,.2f} Juta".replace(".", ",")
    )

  r2c1, r2c2 = st.columns(2)
  with r2c1:
    st.metric(
        label="Denda", value=f"Rp {val_denda/1e6:,.2f} Juta".replace(".", ",")
    )
  with r2c2:
    st.metric(
        label="Total Penerimaan Kumulatif",
        value=f"Rp {val_total/1e6:,.2f} Juta".replace(".", ","),
    )

  st.markdown("---")

  st.markdown("### 📋 Detail Sektor Pendanaan pada Tanggal Tersebut")
  st.dataframe(
      df_aktif[[
          "Jenis Dana",
          "Realisasi s.d. Hari Ini",
          "Prosentase Siklikal (%)",
          "Siklikal YTY (%)",
      ]],
      use_container_width=True,
  )

  if not df_tren.empty and len(df_tren) > 1:
    st.markdown("---")
    st.markdown("### 📉 Grafik Tren Historis Total Penerimaan DIY")
    st.line_chart(df_tren.set_index("Sumber File")["Total DIY"])

else:
  st.warning(
      "⚠️ Belum ada file Excel multi-loket di dalam folder `data_harian/` di"
      " GitHub."
  )
