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

SUPABASE_URL = "https://puavbvbsnxbwjsgajgre.supabase.co"
SUPABASE_KEY = "sb_publishable_MEgagKB7_FQGuDpg4ORosA_F60IfKMS"


@st.cache_resource
def init_connection():
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_connection()

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
    [data-testid="stSidebar"] {
        display: none !important;
    }
    .stHeadingAnchor, [data-testid="stHeaderActionElements"], a[href^="#"] {
        display: none !important;
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
    }
    ::-webkit-scrollbar {
        display: none !important;
        width: 0px !important;
        background: transparent !important;
    }
    div.stButton > button:first-child, div.stFormSubmitButton > button:first-child {
        background-color: #005ba8;
        color: white;
        width: 100%;
        border-radius: 8px;
        padding: 10px;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:first-child:hover, div.stFormSubmitButton > button:first-child:hover {
        background-color: #004580;
        color: white;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

if "logged_in" not in st.session_state:
  qp_logged = st.query_params.get("logged_in")
  qp_role = st.query_params.get("role")
  if qp_logged == "true" and qp_role in ["Petugas SAMSAT", "Pimpinan"]:
    st.session_state.logged_in = True
    st.session_state.role = qp_role
  else:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
  col1, col2, col3 = st.columns([1, 1.3, 1])

  with col2:
    st.markdown("<div style='height: 3vh;'></div>", unsafe_allow_html=True)
    with st.container():
      if img_base64:
        st.markdown(
            f"""
                <div style="text-align: center; margin-bottom: 5px;">
                    <img src="data:image/png;base64,{img_base64}" width="250" style="display: block; margin: 0 auto; height: auto;">
                </div>
                """,
            unsafe_allow_html=True,
        )
      else:
        st.markdown(
            "<h2 style='text-align: center; color: #005ba8; margin-bottom:"
            " 0;'>PT JASA RAHARJA</h2>",
            unsafe_allow_html=True,
        )

      st.markdown(
          "<div style='text-align: center; color: #333333; font-size: 1.2rem;"
          " font-weight: 600; margin-bottom: 5px;'>Portal Monitoring Kanwil"
          " DIY</div>",
          unsafe_allow_html=True,
      )
      st.markdown("---")

      with st.form("form_login_portal"):
        username = st.text_input(
            "ID Pengguna", placeholder="Masukkan ID Pengguna"
        )
        password = st.text_input(
            "Password", type="password", placeholder="Masukkan Password"
        )

        st.write("")
        login_button = st.form_submit_button("Login")

        if login_button:
          if username.lower() == "petugas" and password == "123456":
            st.session_state.logged_in = True
            st.session_state.role = "Petugas SAMSAT"
            st.query_params["logged_in"] = "true"
            st.query_params["role"] = "Petugas SAMSAT"
            st.rerun()
          elif username.lower() == "pimpinan" and password == "123456":
            st.session_state.logged_in = True
            st.session_state.role = "Pimpinan"
            st.query_params["logged_in"] = "true"
            st.query_params["role"] = "Pimpinan"
            st.rerun()
          else:
            st.error("❌ ID Pengguna atau Password salah!")

      st.markdown(
          "<p style='text-align: center; font-size: 12px; margin-top:"
          " 10px; color: #666666;'>Akun akses dikelola dan disediakan oleh"
          " Administrator Kanwil.</p>",
          unsafe_allow_html=True,
      )

else:
  header_col1, header_col2 = st.columns([4, 1])
  with header_col1:
    if st.session_state.role == "Petugas SAMSAT":
      st.title("📝 Form Input Data Harian")
      st.subheader("Kanwil DIY - Jasa Raharja")
    else:
      st.title("📊 Dashboard Laporan Penerimaan")
      st.subheader("Monitoring Harian, Bulanan, dan Tahunan Kanwil DIY")
  with header_col2:
    st.write("")
    if st.button("🚪 Keluar"):
      st.session_state.logged_in = False
      st.session_state.role = None
      st.query_params.clear()
      st.rerun()

  st.markdown("---")

  if st.session_state.role == "Petugas SAMSAT":
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

      mode_waktu = st.radio(
          "Filter Periode", ["Harian", "Bulanan", "Tahunan"], horizontal=True
      )

      if mode_waktu == "Harian":
        min_tgl = df["dt_tanggal"].dt.date.min()
        max_tgl = df["dt_tanggal"].dt.date.max()
        date_range = st.date_input(
            "Pilih Rentang Tanggal", value=(min_tgl, max_tgl)
        )

        if isinstance(date_range, tuple):
          if len(date_range) == 2:
            start_tgl, end_tgl = date_range
          else:
            start_tgl = end_tgl = date_range[0]
        else:
          start_tgl = end_tgl = date_range

        df_filtered = df[
            (df["dt_tanggal"].dt.date >= start_tgl)
            & (df["dt_tanggal"].dt.date <= end_tgl)
        ]
        if start_tgl == end_tgl:
          st.info(f"Menampilkan Laporan Tanggal: **{start_tgl}**")
        else:
          st.info(
              f"Menampilkan Laporan dari **{start_tgl}** sampai **{end_tgl}**"
          )

      elif mode_waktu == "Bulanan":
        all_months = sorted(df["Bulan"].unique())
        col_m1, col_m2 = st.columns(2)
        with col_m1:
          start_bln = st.selectbox(
              "Dari Bulan", all_months, index=0, key="start_bln"
          )
        with col_m2:
          end_bln = st.selectbox(
              "Sampai Bulan",
              all_months,
              index=len(all_months) - 1,
              key="end_bln",
          )

        if start_bln > end_bln:
          start_bln, end_bln = end_bln, start_bln

        df_filtered = (
            df[(df["Bulan"] >= start_bln) & (df["Bulan"] <= end_bln)]
            .groupby(["loket", "jenis_dana"])[
                ["realisasi", "prosentase_siklikal", "siklikal_yty"]
            ]
            .mean()
            .reset_index()
        )
        st.info(f"Menampilkan Rata-rata Bulan: **{start_bln} s.d. {end_bln}**")

      else:
        all_years = sorted(df["Tahun"].unique())
        col_y1, col_y2 = st.columns(2)
        with col_y1:
          start_thn = st.selectbox(
              "Dari Tahun", all_years, index=0, key="start_thn"
          )
        with col_y2:
          end_thn = st.selectbox(
              "Sampai Tahun",
              all_years,
              index=len(all_years) - 1,
              key="end_thn",
          )

        if start_thn > end_thn:
          start_thn, end_thn = end_thn, start_thn

        df_filtered = (
            df[(df["Tahun"] >= start_thn) & (df["Tahun"] <= end_thn)]
            .groupby(["loket", "jenis_dana"])[
                ["realisasi", "prosentase_siklikal", "siklikal_yty"]
            ]
            .mean()
            .reset_index()
        )
        st.info(f"Menampilkan Rekap Tahun: **{start_thn} s.d. {end_thn}**")

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
