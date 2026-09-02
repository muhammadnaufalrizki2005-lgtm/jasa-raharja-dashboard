from datetime import date
import pandas as pd
import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://puavbvbsnxbwjsgajgre.supabase.co"
SUPABASE_KEY = "sb_publishable_MEgagKB7_FQGuDpg4ORosA_F60IfKMS"


@st.cache_resource
def init_connection():
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_connection()

st.set_page_config(
    page_title="Sistem Monitoring Penerimaan Jasa Raharja DIY", layout="wide"
)

# Menampilkan Logo Resmi di Sidebar
st.sidebar.image("LOGO_JASA_RAHARJA_2024.png", use_container_width=True)
st.sidebar.markdown("---")

st.sidebar.title("🔐 Menu Utama")
role = st.sidebar.selectbox(
    "Pilih Akses Menu", ["Pilih Peran...", "Petugas SAMSAT", "Pimpinan"]
)

if role == "Pilih Peran...":
  st.info(
      "Silakan pilih menu akses di panel sebelah kiri untuk masuk ke sistem."
  )

elif role == "Petugas SAMSAT":
  st.title("📝 Form Input Data Harian")
  st.subheader("Kanwil DIY - Jasa Raharja")

  with st.form("form_penerimaan"):
    col1, col2 = st.columns(2)
    with col1:
      f_tanggal = st.date_input("Tanggal Laporan", value=date.today())
      f_loket = st.selectbox(
          "Loket SAMSAT",
          ["Kota", "Sleman", "Bantul", "Kulon Progo", "Gunung Kidul"],
      )
    with col2:
      f_jenis = st.selectbox(
          "Jenis Dana",
          ["Kartu Dana / Sertifikat", "SWDKLLJ", "Denda", "Total Penerimaan"],
      )
      f_realisasi = st.number_input(
          "Realisasi (Rp)", min_value=0.0, step=1000.0, format="%.2f"
      )

    col3, col4 = st.columns(2)
    with col3:
      f_siklikal = st.number_input(
          "Prosentase Siklikal (%)", min_value=0.0, step=0.01
      )
    with col4:
      f_yty = st.number_input("Siklikal YTY (%)", min_value=0.0, step=0.01)

    submit_button = st.form_submit_button("💾 Simpan Data")

    if submit_button:
      data_insert = {
          "tanggal": str(f_tanggal),
          "loket": f_loket,
          "jenis_dana": f_jenis,
          "realisasi": f_realisasi,
          "prosentase_siklikal": f_siklikal,
          "siklikal_yty": f_yty,
      }
      try:
        response = (
            supabase.table("penerimaan_harian").insert(data_insert).execute()
        )
        st.success("Data berhasil disimpan.")
      except Exception as e:
        st.error(f"Gagal menyimpan data: {e}")

elif role == "Pimpinan":
  st.title("📊 Dashboard Laporan Penerimaan")
  st.subheader("Monitoring Harian, Bulanan, dan Tahunan Kanwil DIY")

  try:
    response = supabase.table("penerimaan_harian").select("*").execute()
    data = response.data
    df = pd.DataFrame(data)
  except Exception as e:
    st.error(f"Gagal memuat data dari database: {e}")
    df = pd.DataFrame()

  if not df.empty:
    df["dt_tanggal"] = pd.to_datetime(df["tanggal"])
    df["Bulan"] = df["dt_tanggal"].dt.to_period("M").astype(str)
    df["Tahun"] = df["dt_tanggal"].dt.year.astype(str)

    mode_waktu = st.sidebar.radio(
        "Filter Periode", ["Harian", "Bulanan", "Tahunan"]
    )

    if mode_waktu == "Harian":
      list_tanggal = sorted(df["dt_tanggal"].dt.date.unique(), reverse=True)
      pilih_tgl = st.sidebar.selectbox("Pilih Tanggal", list_tanggal)
      df_filtered = df[df["dt_tanggal"].dt.date == pilih_tgl]
      st.info(f"Menampilkan Laporan Tanggal: **{pilih_tgl}**")

    elif mode_waktu == "Bulanan":
      list_bulan = sorted(df["Bulan"].unique(), reverse=True)
      pilih_bln = st.sidebar.selectbox("Pilih Bulan", list_bulan)
      df_filtered = (
          df[df["Bulan"] == pilih_bln]
          .groupby(["loket", "jenis_dana"])[
              ["realisasi", "prosentase_siklikal", "siklikal_yty"]
          ]
          .mean()
          .reset_index()
      )
      st.info(f"Menampilkan Rata-rata Bulan: **{pilih_bln}**")

    else:
      list_tahun = sorted(df["Tahun"].unique(), reverse=True)
      pilih_thn = st.sidebar.selectbox("Pilih Tahun", list_tahun)
      df_filtered = (
          df[df["Tahun"] == pilih_thn]
          .groupby(["loket", "jenis_dana"])[
              ["realisasi", "prosentase_siklikal", "siklikal_yty"]
          ]
          .mean()
          .reset_index()
      )
      st.info(f"Menampilkan Rekap Tahun: **{pilih_thn}**")

    # Format tampilan tabel agar bersih tanpa 00:00:00 dan format Rupiah
    if not df_filtered.empty:
      df_tampilan = df_filtered.copy()
      if "tanggal" in df_tampilan.columns:
        df_tampilan["tanggal"] = pd.to_datetime(
            df_tampilan["tanggal"]
        ).dt.strftime("%Y-%m-%d")
      if "realisasi" in df_tampilan.columns:
        df_tampilan["realisasi"] = df_tampilan["realisasi"].apply(
            lambda x: f"Rp {x:,.0f}".replace(",", ".")
        )
    else:
      df_tampilan = df_filtered

    st.markdown("### 📋 Rekapitulasi Data")
    st.dataframe(df_tampilan, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📉 Grafik Tren Penerimaan")
    df_chart = (
        df.groupby("dt_tanggal")["realisasi"]
        .sum()
        .reset_index()
        .set_index("dt_tanggal")
    )
    st.line_chart(df_chart)

  else:
    st.warning("Belum ada data di dalam database.")
