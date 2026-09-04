import base64
from datetime import date
from PIL import Image
import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
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

# ==========================================
# KONEKSI DATABASE SUPABASE
# ==========================================
SUPABASE_URL = "https://puavbvbsnxbwjsgajgre.supabase.co"
SUPABASE_KEY = "sb_publishable_MEgagKB7_FQGuDpg4ORosA_F60IfKMS"


@st.cache_resource
def init_connection():
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_connection()

# ==========================================
# SISTEM LOGIN & SESI
# ==========================================
if "logged_in" not in st.session_state:
  qp_logged = st.query_params.get("logged_in")
  qp_role = st.query_params.get("role")
  if qp_logged == "true" and qp_role in ["Petugas SAMSAT", "Pimpinan"]:
    st.session_state.logged_in = True
    st.session_state.role = qp_role
  else:
    st.session_state.logged_in = False
    st.session_state.role = None

if "success_msg" not in st.session_state:
  st.session_state.success_msg = ""

css_base = """
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stHeadingAnchor, [data-testid="stHeaderActionElements"], a[href^="#"] { display: none !important; }
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
"""

# ==========================================
# TAMPILAN HALAMAN LOGIN
# ==========================================
if not st.session_state.logged_in:
  st.markdown(
      css_base
      + """
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
            overflow: hidden !important;
            height: 100vh !important;
            max-height: 100vh !important;
        }
        ::-webkit-scrollbar { display: none !important; width: 0px !important; }
        </style>
    """,
      unsafe_allow_html=True,
  )

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

# ==========================================
# TAMPILAN DASHBOARD SETELAH LOGIN
# ==========================================
else:
  if st.session_state.role == "Pimpinan":
    st.markdown(
        css_base
        + """
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
            overflow: auto !important;
            height: auto !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        css_base
        + """
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
            overflow: hidden !important;
            height: 100vh !important;
            max-height: 100vh !important;
        }
        ::-webkit-scrollbar { display: none !important; width: 0px !important; }
        </style>
    """,
        unsafe_allow_html=True,
    )

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

  # ----------------------------------------
  # TAMPILAN: PETUGAS SAMSAT (INPUT DATA + LIVE PREVIEW)
  # ----------------------------------------
  if st.session_state.role == "Petugas SAMSAT":
    if st.session_state.success_msg:
      st.success(st.session_state.success_msg)
      st.session_state.success_msg = ""  # Bersihkan pesan setelah ditampilkan

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
            ["Kartu Dana / Sertifikat", "SWDKLLJ", "Denda"],
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
          st.session_state.success_msg = (
              "✅ Data berhasil disimpan ke database!"
          )
          st.rerun()
        except Exception as e:
          st.error(f"❌ Gagal menyimpan data: {e}")

    # VERIFIKASI LANGSUNG (LIVE PREVIEW)
    st.markdown("---")
    st.markdown("### 👀 Verifikasi Input Terbaru")
    st.caption("Cek tabel di bawah ini untuk memastikan nilai realisasi yang baru diinput sudah benar (tidak salah ketik).")
    
    try:
      res_recent = supabase.table("penerimaan_harian").select("*").order("id", desc=True).limit(10).execute()
      df_recent = pd.DataFrame(res_recent.data) if res_recent.data else pd.DataFrame()
      if not df_recent.empty:
        df_recent["realisasi_fmt"] = df_recent["realisasi"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
        st.dataframe(
            df_recent[["tanggal", "loket", "jenis_dana", "realisasi_fmt", "prosentase_siklikal"]],
            use_container_width=True,
            hide_index=True
        )
      else:
        st.info("Belum ada data yang diinput.")
    except Exception:
      st.info("Memuat riwayat input...")

  # ----------------------------------------
  # TAMPILAN: PIMPINAN (REKAP, AUDIT & ANALISIS)
  # ----------------------------------------
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

        dc1, dc2 = st.columns(2)
        with dc1:
          start_tgl = st.date_input("Dari Tanggal", value=min_tgl)
        with dc2:
          end_tgl = st.date_input("Sampai Tanggal", value=max_tgl)

        if start_tgl > end_tgl:
          start_tgl, end_tgl = end_tgl, start_tgl

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
        all_years_list = sorted(df["Tahun"].unique())
        month_names = {
            "01": "Januari", "02": "Februari", "03": "Maret", "04": "April",
            "05": "Mei", "06": "Juni", "07": "Juli", "08": "Agustus",
            "09": "September", "10": "Oktober", "11": "November", "12": "Desember"
        }
        all_months_num = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
          start_y = st.selectbox("Dari Tahun", all_years_list, index=0, key="s_y")
        with mc2:
          start_m = st.selectbox("Dari Bulan", all_months_num, format_func=lambda x: month_names[x], index=0, key="s_m")
        with mc3:
          end_y = st.selectbox("Sampai Tahun", all_years_list, index=len(all_years_list)-1, key="e_y")
        with mc4:
          end_m = st.selectbox("Sampai Bulan", all_months_num, format_func=lambda x: month_names[x], index=11, key="e_m")

        start_bln = f"{start_y}-{start_m}"
        end_bln = f"{end_y}-{end_m}"

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
        st.info(f"Menampilkan Rata-rata Bulan: **{month_names[start_m]} {start_y} s.d. {month_names[end_m]} {end_y}**")

      else:
        all_years_list = sorted(df["Tahun"].unique())
        yc1, yc2 = st.columns(2)
        with yc1:
          start_thn = st.selectbox("Dari Tahun", all_years_list, index=0, key="start_thn")
        with yc2:
          end_thn = st.selectbox("Sampai Tahun", all_years_list, index=len(all_years_list)-1, key="end_thn")

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

      # ==========================================
      # FITUR AUDIT OTOMATIS (DETEKSI TYPO / ANOMALI)
      # ==========================================
      st.markdown("---")
      with st.expander(
          "🔍 Audit & Deteksi Otomatis Kesalahan Ketik (Anomali Data)",
          expanded=False,
      ):
        st.write("Sistem mendeteksi anomali seperti nilai nol, duplikat, atau lonjakan ekstrem (potensi salah ketik).")
        
        df_zero = df[df["realisasi"] <= 0]
        df_dup = df[
            df.duplicated(subset=["tanggal", "loket", "jenis_dana"], keep=False)
        ]
        df_outlier = df[df["realisasi"] > 500000000]

        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
          st.markdown("##### ⚠️ Realisasi 0 / Negatif")
          if not df_zero.empty:
            st.dataframe(df_zero[["tanggal", "loket", "jenis_dana", "realisasi"]], use_container_width=True, hide_index=True)
          else:
            st.success("✅ Aman")

        with col_a2:
          st.markdown("##### ⚠️ Duplikat Input")
          if not df_dup.empty:
            st.dataframe(df_dup[["tanggal", "loket", "jenis_dana", "realisasi"]], use_container_width=True, hide_index=True)
          else:
            st.success("✅ Aman")

        with col_a3:
          st.markdown("##### ⚠️ Potensi Typo (>500 Juta)")
          if not df_outlier.empty:
            st.dataframe(df_outlier[["tanggal", "loket", "jenis_dana", "realisasi"]], use_container_width=True, hide_index=True)
          else:
            st.success("✅ Aman")

      # ==========================================
      # GRAFIK ANALISIS (STRICT FILTER)
      # ==========================================
      st.markdown("---")
      st.markdown("### 📉 Grafik Tren Penerimaan & Analisis Multi-Indikator")

      all_lokets = sorted(df["loket"].unique())
      all_jenis = sorted(df["jenis_dana"].unique())

      gc1, gc2 = st.columns(2)
      with gc1:
        selected_lokets = st.multiselect(
            "Pilih Wilayah (Loket)",
            options=all_lokets,
            default=all_lokets,
            key="ms_loket_clean"
        )

      with gc2:
        selected_jenis = st.multiselect(
            "Pilih Jenis Dana",
            options=all_jenis,
            default=all_jenis,
            key="ms_jenis_clean"
        )

      df_c = df.copy()
      if mode_waktu == "Harian":
        df_c = df_c[
            (df_c["dt_tanggal"].dt.date >= start_tgl)
            & (df_c["dt_tanggal"].dt.date <= end_tgl)
        ]
        x_axis_val = "Periode"
        df_c["Periode"] = df_c["dt_tanggal"].dt.strftime("%Y-%m-%d")
      elif mode_waktu == "Bulanan":
        df_c = df_c[(df_c["Bulan"] >= start_bln) & (df_c["Bulan"] <= end_bln)]
        x_axis_val = "Bulan"
      else:
        df_c = df_c[(df_c["Tahun"] >= start_thn) & (df_c["Tahun"] <= end_thn)]
        x_axis_val = "Tahun"

      df_c = df_c[df_c["loket"].isin(selected_lokets)]
      df_c = df_c[df_c["jenis_dana"].isin(selected_jenis)]

      if not df_c.empty:
        df_chart_agg = (
            df_c.groupby([x_axis_val, "loket", "jenis_dana"])["realisasi"]
            .sum()
            .reset_index()
        )
        df_chart_agg["Kategori"] = (
            df_chart_agg["loket"] + " - " + df_chart_agg["jenis_dana"]
        )

        fig = px.bar(
            df_chart_agg,
            x=x_axis_val,
            y="realisasi",
            color="Kategori",
            barmode="stack",
            labels={
                "realisasi": "Total Realisasi (Rp)",
                x_axis_val: "Periode",
                "Kategori": "Wilayah & Jenis Dana",
            },
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis=dict(showgrid=False, type="category"),
            yaxis=dict(showgrid=True, gridcolor="#e5e5e5"),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
      else:
        st.warning("Silakan pilih minimal satu wilayah dan jenis dana untuk menampilkan grafik.")

    else:
      st.warning("Belum ada data di dalam database.")
