import base64
from datetime import date
from PIL import Image
import pandas as pd
import streamlit as st
from supabase import create_client

try:
  favicon_img = Image.open("jasa raharja logo.png")
  bbox = favicon_img.getbbox()
  if bbox:
    favicon_img = favicon_img.crop(bbox)
except Exception:
  favicon_img = "jasa raharja logo.png"

st.set_page_config(
    page_title="Dashboard Jasa Raharja DIY",
    page_icon=favicon_img,
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def get_img_base64(file_path):
  try:
    with open(file_path, "rb") as f:
      data = f.read()
    return base64.b64encode(data).decode()
  except Exception:
    return ""


img_base64 = get_img_base64("LOGO_JASA_RAHARJA_2024.png")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    [data-testid="stHeader"] {
        display: none !important;
    }
    [data-testid="stToolbar"] {
        display: none !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    div.stButton > button:first-child {
        background-color: #005ba8;
        color: white;
        width: 100%;
        border-radius: 8px;
        padding: 10px;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #004580;
        color: white;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

SUPABASE_URL = "https://puavbvbsnxbwjsgajgre.supabase.co"
SUPABASE_KEY = "sb_publishable_MEgagKB7_FQGuDpg4ORosA_F60IfKMS"


@st.cache_resource
def init_connection():
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_connection()

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "role" not in st.session_state:
  st.session_state.role = None

if not st.session_state.logged_in:
  # CSS khusus untuk mengunci scrollbar di halaman login
  st.markdown(
      """
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            overflow: hidden !important;
            height: 100vh !important;
        }
        </style>
    """,
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 1.2, 1])

  with col2:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    with st.container():
      if img_base64:
        st.markdown(
            f"""
                <div style="text-align: center; margin-bottom: 5px;">
                    <img src="data:image/png;base64,{img_base64}" width="220" style="display: block; margin: 0 auto; height: auto;">
                </div>
                """,
            unsafe_allow_html=True,
        )
      else:
        st.markdown(
            "<h2 style='text-align: center; color: #005ba8;'>PT JASA"
            " RAHARJA</h2>",
            unsafe_allow_html=True,
        )

      st.markdown(
          "<div style='text-align: center; color: #333333; font-size: 1.2rem;"
          " font-weight: 600; margin-top: 5px;'>Portal Monitoring Kanwil"
          " DIY</div>",
          unsafe_allow_html=True,
      )
      st.markdown("---")

      username = st.text_input("ID Pengguna", placeholder="Masukkan ID Pengguna")
      password = st.text_input(
          "Password", type="password", placeholder="Masukkan Password"
      )

      st.write("")
      login_button = st.button("Login")

      if login_button:
        if username.lower() == "petugas" and password == "123456":
          st.session_state.logged_in = True
          st.session_state.role = "Petugas SAMSAT"
          st.rerun()
        elif username.lower() == "pimpinan" and password == "123456":
          st.session_state.logged_in = True
          st.session_state.role = "Pimpinan"
          st.rerun()
        else:
          st.error("❌ ID Pengguna atau Password salah!")

      st.markdown(
          "<p style='text-align: center; font-size: 12px; margin-top:"
          " 15px; color: #666666;'>Akun akses dikelola dan disediakan oleh"
          " Administrator Kanwil.</p>",
          unsafe_allow_html=True,
      )

else:
  if img_base64:
    st.sidebar.markdown(
        f"""
            <div style="text-align: center; margin-bottom: 10px;">
                <img src="data:image/png;base64,{img_base64}" width="180" style="display: block; margin: 0 auto; height: auto;">
            </div>
            """,
        unsafe_allow_html=True,
    )
  st.sidebar.markdown("---")
  st.sidebar.markdown(f"**Status:** Login sebagai {st.session_state.role}")
  if st.sidebar.button("🚪 Keluar (Logout)"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()

  if st.session_state.role == "Petugas SAMSAT":
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
          supabase.table("penerimaan_harian").insert(data_insert).execute()
          st.success("✅ Data berhasil disimpan ke database!")
        except Exception as e:
          st.error(f"❌ Gagal menyimpan data: {e}")

  elif st.session_state.role == "Pimpinan":
    st.title("📊 Dashboard Laporan Penerimaan")
    st.subheader("Monitoring Harian, Bulanan, dan Tahunan Kanwil DIY")

    try:
      response = supabase.table("penerimaan_harian").select("*").execute()
      df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
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

      if not df_filtered.empty:
        df_tampilan = df_filtered.copy()
        if "dt_tanggal" in df_tampilan.columns:
          df_tampilan["dt_tanggal"] = pd.to_datetime(
              df_tampilan["dt_tanggal"]
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
