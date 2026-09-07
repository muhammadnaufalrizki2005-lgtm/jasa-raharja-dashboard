import base64
from datetime import date
from PIL import Image
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from supabase import create_client

# ==========================================
# ⚙️ KONFIGURASI DATA MASTER (EDIT VIA GITHUB)
# ==========================================
# Ubah nilai-nilai di bawah ini langsung melalui GitHub sesuai kebutuhan tahun/bulan berjalan
TARGET_TAHUN = 2026
TARGET_BULAN = 8  # Bulan berjalan saat ini (contoh: Agustus = Bulan ke-8)

# 1. Prosentase Siklikal per Jenis Dana (%)
SIKLIKAL = {
    "Kartu Dana / Sertifikat": 30.93,
    "SWDKLLJ": 30.30,
    "Denda": 32.00
}

# Variabel pembantu untuk sel pengurang/unknown
NILAI_UNKNOWN_VAR = 0.0 

# 2. Anggaran (Tahun X) per Loket dan Jenis Dana
ANGGARAN = {
    "Kartu Dana / Sertifikat": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "SWDKLLJ": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "Denda": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0}
}

# 3. Data Historis Khusus Bulan tsb (Tahun X-1) - misal: Realisasi bulan Agustus 2025
KHUSUS_X1 = {
    "Kartu Dana / Sertifikat": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "SWDKLLJ": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "Denda": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0}
}

# 4. Data Historis Jan s.d Bulan tsb (Tahun X-1) - misal: Akumulasi Jan - Agustus 2025
JAN_SD_X1 = {
    "Kartu Dana / Sertifikat": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "SWDKLLJ": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "Denda": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0}
}


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

if "toast_count" not in st.session_state:
  st.session_state.toast_count = 0

css_base = """
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stHeadingAnchor, [data-testid="stHeaderActionElements"], a[href^="#"] { display: none !important; }
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

  header_col1, header_col2 = st.columns([4, 1])
  with header_col1:
    if st.session_state.role == "Petugas SAMSAT":
      st.title("📝 Portal Petugas SAMSAT")
      st.subheader("Kanwil DIY - Jasa Raharja")
    else:
      st.title("📊 Dashboard Laporan Realisasi")
      st.subheader("Monitoring Penerimaan Sektor UU 34 Tahun 1964")
  with header_col2:
    st.write("")
    if st.button("🚪 Keluar"):
      st.session_state.logged_in = False
      st.session_state.role = None
      st.query_params.clear()
      st.rerun()

  st.markdown("---")

  # ----------------------------------------
  # TAMPILAN: PETUGAS SAMSAT (INPUT HARIAN)
  # ----------------------------------------
  if st.session_state.role == "Petugas SAMSAT":
    st.info("💡 **Petunjuk:** Cukup masukkan data realisasi harian. Kalkulasi laporan lengkap dan persentase akan diolah otomatis oleh sistem.")
    
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
      f_realisasi_str = f"Rp {f_realisasi:,.0f}".replace(",", ".")
      st.caption(f"💡 Terbaca: **{f_realisasi_str}**")

    st.write("")
    submit_button = st.button("💾 Simpan Data")

    if submit_button:
      if f_realisasi <= 0:
        st.error("❌ Field Realisasi (Rp) tidak boleh 0 atau kosong.")
      else:
        data_insert = {
            "tanggal": str(f_tanggal),
            "loket": f_loket,
            "jenis_dana": f_jenis,
            "realisasi": f_realisasi,
            "prosentase_siklikal": 0,
            "siklikal_yty": 0,
        }
        try:
          supabase.table("penerimaan_harian").insert(data_insert).execute()
          st.session_state.toast_count += 1
          st.toast(
              f"[{st.session_state.toast_count}] Data berhasil disimpan! Loket: {f_loket} | Jenis: {f_jenis}",
              icon="✅",
          )
          st.rerun()
        except Exception as e:
          st.error(f"❌ Gagal menyimpan data: {e}")

    st.markdown("---")
    st.markdown("### 👀 Verifikasi Input Terbaru")
    try:
      res_recent = supabase.table("penerimaan_harian").select("*").order("id", desc=True).limit(5).execute()
      df_recent = pd.DataFrame(res_recent.data) if res_recent.data else pd.DataFrame()
      if not df_recent.empty:
        df_recent["Realisasi Input"] = df_recent["realisasi"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
        st.dataframe(
            df_recent[["tanggal", "loket", "jenis_dana", "Realisasi Input"]],
            use_container_width=True, hide_index=True
        )
      else:
        st.info("Belum ada data yang diinput.")
    except Exception:
      st.info("Memuat riwayat input...")

  # ----------------------------------------
  # TAMPILAN: PIMPINAN (LAPORAN EXCEL OTOMATIS)
  # ----------------------------------------
  elif st.session_state.role == "Pimpinan":
    tab_pimpinan_1, tab_pimpinan_2 = st.tabs([
        "📊 Laporan Format Excel (Otomatis)",
        "📉 Grafik & Data Mentah Harian"
    ])

    # Ambil data inputan harian dari Supabase
    try:
      response = supabase.table("penerimaan_harian").select("*").execute()
      df_db = pd.DataFrame(response.data) if response.data else pd.DataFrame()
      if not df_db.empty:
        df_db["dt_tanggal"] = pd.to_datetime(df_db["tanggal"])
        df_db["Bulan"] = df_db["dt_tanggal"].dt.month
        df_db["Tahun"] = df_db["dt_tanggal"].dt.year
    except Exception as e:
      df_db = pd.DataFrame()

    def safe_div(a, b):
        return np.where(b == 0, 0, a / b)

    # ---------------- TAB 1: LAPORAN FORMAT EXCEL ----------------
    with tab_pimpinan_1:
      st.markdown(f"### 📊 Laporan Realisasi Kinerja Tahun {TARGET_TAHUN}")
      st.write("Tabel di bawah ini memadukan Data Master (Anggaran & Histori X-1) dengan akumulasi Realisasi Harian Petugas SAMSAT, serta menghitung otomatis seluruh rumus performa.")
      
      kat_pilihan = st.selectbox(
          "Pilih Kategori Pendanaan",
          ["Total (Overall)", "Kartu Dana / Sertifikat", "SWDKLLJ", "Denda"]
      )

      def generate_excel_table(jenis_dana):
        lokets = ["Kota", "Sleman", "Bantul", "Kulon Progo", "Gunung Kidul"]
        rows = []
        
        for loket in lokets:
          # Data Given dari Master Config
          anggaran_x = ANGGARAN[jenis_dana].get(loket, 0)
          khusus_x1 = KHUSUS_X1[jenis_dana].get(loket, 0)
          jan_sd_x1 = JAN_SD_X1[jenis_dana].get(loket, 0)
          siklikal = SIKLIKAL[jenis_dana]

          # Data Realisasi dari Database Harian SAMSAT
          khusus_x = 0
          jan_sd_x = 0
          if not df_db.empty:
              # Khusus Bulan tertentu di Tahun X (Misal: Bulan Agustus)
              m_khusus = (df_db["loket"] == loket) & (df_db["jenis_dana"] == jenis_dana) & (df_db["Bulan"] == TARGET_BULAN) & (df_db["Tahun"] == TARGET_TAHUN)
              khusus_x = df_db.loc[m_khusus, "realisasi"].sum()
              
              # Akumulasi Jan s.d Bulan tertentu di Tahun X
              m_jansd = (df_db["loket"] == loket) & (df_db["jenis_dana"] == jenis_dana) & (df_db["Bulan"] <= TARGET_BULAN) & (df_db["Tahun"] == TARGET_TAHUN)
              jan_sd_x = df_db.loc[m_jansd, "realisasi"].sum()

          rows.append({
              "Loket": f"LOKET SAMSAT {loket.upper()}",
              "Anggaran (Thn X)": anggaran_x,
              "Khusus Bln (X-1)": khusus_x1,
              "Khusus Bln (X)": khusus_x,
              "Jan s.d Bln (X-1)": jan_sd_x1,
              "Jan s.d Bln (X)": jan_sd_x,
              "Siklikal_H": siklikal
          })

        df_calc = pd.DataFrame(rows)
        
        # Baris JUMLAH
        jumlah_row = pd.DataFrame({
            "Loket": ["JUMLAH"],
            "Anggaran (Thn X)": [df_calc["Anggaran (Thn X)"].sum()],
            "Khusus Bln (X-1)": [df_calc["Khusus Bln (X-1)"].sum()],
            "Khusus Bln (X)": [df_calc["Khusus Bln (X)"].sum()],
            "Jan s.d Bln (X-1)": [df_calc["Jan s.d Bln (X-1)"].sum()],
            "Jan s.d Bln (X)": [df_calc["Jan s.d Bln (X)"].sum()],
            "Siklikal_H": [SIKLIKAL[jenis_dana]]
        })
        df_calc = pd.concat([df_calc, jumlah_row], ignore_index=True)

        # PENERAPAN RUMUS MATEMATIKA EXCEL
        df_calc["Akt Khusus (%)"] = safe_div(df_calc["Khusus Bln (X)"] - df_calc["Khusus Bln (X-1)"], df_calc["Khusus Bln (X-1)"]) * 100
        df_calc["Real (%)"] = safe_div(df_calc["Jan s.d Bln (X)"], df_calc["Anggaran (Thn X)"]) * 100
        df_calc["Aktv (%)"] = safe_div(df_calc["Jan s.d Bln (X)"] - df_calc["Jan s.d Bln (X-1)"], df_calc["Jan s.d Bln (X-1)"]) * 100
        df_calc["Kurang/Lebih Pencapaian"] = df_calc["Jan s.d Bln (X)"] - (df_calc["Anggaran (Thn X)"] * TARGET_BULAN / 12)
        df_calc["Perbulan"] = df_calc["Anggaran (Thn X)"] / 12
        df_calc["Rata Perhari"] = df_calc["Anggaran (Thn X)"] / (12 * 25)
        df_calc["(+/-) Realisasi"] = df_calc["Jan s.d Bln (X)"] - df_calc["Jan s.d Bln (X-1)"]
        df_calc["Real vs Var_X (%)"] = df_calc["Real (%)"] - NILAI_UNKNOWN_VAR
        df_calc["Real vs Siklikal (%)"] = df_calc["Real (%)"] - df_calc["Siklikal_H"]
        df_calc["Seharusnya"] = df_calc["Anggaran (Thn X)"] * (df_calc["Siklikal_H"] / 100)
        df_calc["Selisih vs Seharusnya"] = df_calc["Jan s.d Bln (X)"] - df_calc["Seharusnya"]

        df_calc = df_calc.drop(columns=["Siklikal_H"])
        return df_calc

      if kat_pilihan == "Total (Overall)":
        df_kd = generate_excel_table("Kartu Dana / Sertifikat")
        df_sw = generate_excel_table("SWDKLLJ")
        df_dn = generate_excel_table("Denda")
        
        df_total = df_kd[["Loket", "Anggaran (Thn X)", "Khusus Bln (X-1)", "Khusus Bln (X)", "Jan s.d Bln (X-1)", "Jan s.d Bln (X)"]].copy()
        for col in ["Anggaran (Thn X)", "Khusus Bln (X-1)", "Khusus Bln (X)", "Jan s.d Bln (X-1)", "Jan s.d Bln (X)"]:
            df_total[col] = df_kd[col] + df_sw[col] + df_dn[col]
            
        df_total["Akt Khusus (%)"] = safe_div(df_total["Khusus Bln (X)"] - df_total["Khusus Bln (X-1)"], df_total["Khusus Bln (X-1)"]) * 100
        df_total["Real (%)"] = safe_div(df_total["Jan s.d Bln (X)"], df_total["Anggaran (Thn X)"]) * 100
        df_total["Aktv (%)"] = safe_div(df_total["Jan s.d Bln (X)"] - df_total["Jan s.d Bln (X-1)"], df_total["Jan s.d Bln (X-1)"]) * 100
        df_total["Kurang/Lebih Pencapaian"] = df_total["Jan s.d Bln (X)"] - (df_total["Anggaran (Thn X)"] * TARGET_BULAN / 12)
        df_total["Perbulan"] = df_total["Anggaran (Thn X)"] / 12
        df_total["Rata Perhari"] = df_total["Anggaran (Thn X)"] / (12 * 25)
        df_total["(+/-) Realisasi"] = df_total["Jan s.d Bln (X)"] - df_total["Jan s.d Bln (X-1)"]
        
        df_final = df_total
      else:
        df_final = generate_excel_table(kat_pilihan)

      # Formatting Tampilan Angka & Persentase
      df_display = df_final.copy()
      for col in df_display.columns:
          if col in ["Anggaran (Thn X)", "Khusus Bln (X-1)", "Khusus Bln (X)", "Jan s.d Bln (X-1)", "Jan s.d Bln (X)", "Kurang/Lebih Pencapaian", "Perbulan", "Rata Perhari", "(+/-) Realisasi", "Seharusnya", "Selisih vs Seharusnya"]:
              df_display[col] = df_display[col].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
          elif "(%)" in col:
              df_display[col] = df_display[col].apply(lambda x: f"{x:,.2f}%" if pd.notnull(x) else "0.00%")

      st.dataframe(df_display, use_container_width=True, hide_index=True)


    # ---------------- TAB 2: GRAFIK & DATA MENTAH ----------------
    with tab_pimpinan_2:
      st.markdown("### 📉 Grafik Realisasi Harian")
      
      if not df_db.empty:
        all_lokets = sorted(df_db["loket"].unique())
        all_jenis = sorted(df_db["jenis_dana"].unique())

        gc1, gc2 = st.columns(2)
        with gc1:
          selected_lokets = st.multiselect("Pilih Wilayah (Loket)", options=all_lokets, default=all_lokets)
        with gc2:
          selected_jenis = st.multiselect("Pilih Jenis Dana", options=all_jenis, default=all_jenis)

        df_c = df_db.copy()
        df_c["Periode"] = df_c["dt_tanggal"].dt.strftime("%Y-%m-%d")
        df_c = df_c[df_c["loket"].isin(selected_lokets)]
        df_c = df_c[df_c["jenis_dana"].isin(selected_jenis)]

        if not df_c.empty:
          df_chart_agg = df_c.groupby("Periode")["realisasi"].sum().reset_index()

          fig = px.bar(
              df_chart_agg, x="Periode", y="realisasi",
              labels={"realisasi": "Total Realisasi (Rp)", "Periode": "Tanggal Input"},
              color_discrete_sequence=["#005ba8"],
          )
          fig.update_layout(
              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
              margin=dict(l=20, r=20, t=10, b=20), xaxis=dict(showgrid=False, type="category"),
              yaxis=dict(showgrid=True, gridcolor="#e5e5e5"), showlegend=False,
          )
          st.plotly_chart(fig, use_container_width=True)
        else:
          st.warning("Silakan pilih filter wilayah dan jenis dana.")
          
        with st.expander("🔍 Lihat Log Input Harian Mentah"):
            df_show = df_c.copy()
            df_show["realisasi"] = df_show["realisasi"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            st.dataframe(df_show[["tanggal", "loket", "jenis_dana", "realisasi"]], use_container_width=True, hide_index=True)
      else:
        st.warning("Belum ada data input harian di database.")
