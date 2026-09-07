import base64
from datetime import date
from PIL import Image
import pandas as pd
import numpy as np
import openpyxl
import plotly.express as px
import streamlit as st
from supabase import create_client

# ==========================================
# ⚙️ KONFIGURASI DATA MASTER (EDIT VIA GITHUB)
# ==========================================
TARGET_TAHUN = 2026
TARGET_BULAN = 8  # Agustus (Bulan ke-8)

# 1. Prosentase Siklikal per Jenis Dana (%)
SIKLIKAL = {
    "Kartu Dana / Sertifikat": 30.93,
    "SWDKLLJ": 30.30,
    "Denda": 32.00
}

NILAI_UNKNOWN_VAR = 0.0 

# 2. Anggaran (Tahun X) per Loket dan Jenis Dana
ANGGARAN = {
    "Kartu Dana / Sertifikat": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "SWDKLLJ": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "Denda": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0}
}

# 3. Data Historis Khusus Bulan tsb (Tahun X-1)
KHUSUS_X1 = {
    "Kartu Dana / Sertifikat": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "SWDKLLJ": {"Kota": 0, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0},
    "Denda": {"Kota": 48, "Sleman": 0, "Bantul": 0, "Kulon Progo": 0, "Gunung Kidul": 0}
}

# 4. Data Historis Jan s.d Bulan tsb (Tahun X-1)
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
  # TAMPILAN: PETUGAS SAMSAT (INPUT HARIAN + VERIFIKASI)
  # ----------------------------------------
  if st.session_state.role == "Petugas SAMSAT":
    tab_petugas_1, tab_petugas_2 = st.tabs([
        "📥 Form Input Data Harian",
        "🧮 Kalkulator & Simulator Manual"
    ])

    with tab_petugas_1:
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

      col3, col4 = st.columns(2)
      with col3:
        f_siklikal = st.number_input("Prosentase Siklikal (%)", min_value=0.0, step=0.01)
      with col4:
        f_yty = st.number_input("Siklikal YTY (%)", min_value=0.0, step=0.01)

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
              "prosentase_siklikal": f_siklikal,
              "siklikal_yty": f_yty,
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
          df_recent["realisasi_fmt"] = df_recent["realisasi"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
          st.dataframe(
              df_recent[["tanggal", "loket", "jenis_dana", "realisasi_fmt", "prosentase_siklikal"]],
              use_container_width=True, hide_index=True
          )
        else:
          st.info("Belum ada data yang diinput.")
      except Exception:
        st.info("Memuat riwayat input...")

    with tab_petugas_2:
      st.markdown("### 🧮 Kalkulator Simulasi Format Excel")
      st.caption("Masukkan data mentah pada tabel di bawah untuk melakukan simulasi perhitungan rumus secara mandiri.")
      
      c1, c2, c3, c4 = st.columns(4)
      with c1:
        p_jenis = st.selectbox("Kategori Dana", ["Kartu Dana", "SWDKLLJ", "Denda", "Total"])
      with c2:
        p_bulan_ke = st.number_input("Bulan Ke (1-12)", min_value=1, max_value=12, value=8)
      with c3:
        p_siklikal = st.number_input("Nilai Siklikal (%)", value=30.0, step=0.1, key="sim_sik")
      with c4:
        p_unknown = st.number_input("Nilai Pengurang Unknown (%)", value=0.0, step=0.1, key="sim_unk")

      if "df_input" not in st.session_state:
        st.session_state.df_input = pd.DataFrame({
            "Loket": ["KOTA", "SLEMAN", "BANTUL", "KULON PROGO", "GUNUNG KIDUL"],
            "Anggaran (Thn X)": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Khusus Bln (X-1)": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Khusus Bln (X)": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Jan s.d Bln (X-1)": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Jan s.d Bln (X)": [0.0, 0.0, 0.0, 0.0, 0.0],
        })

      edited_df = st.data_editor(st.session_state.df_input, use_container_width=True, hide_index=True)

      if st.button("🚀 Hitung Simulasi"):
        df_calc = edited_df.copy()
        jumlah_row = pd.DataFrame({
            "Loket": ["JUMLAH"],
            "Anggaran (Thn X)": [df_calc["Anggaran (Thn X)"].sum()],
            "Khusus Bln (X-1)": [df_calc["Khusus Bln (X-1)"].sum()],
            "Khusus Bln (X)": [df_calc["Khusus Bln (X)"].sum()],
            "Jan s.d Bln (X-1)": [df_calc["Jan s.d Bln (X-1)"].sum()],
            "Jan s.d Bln (X)": [df_calc["Jan s.d Bln (X)"].sum()],
        })
        df_calc = pd.concat([df_calc, jumlah_row], ignore_index=True)

        def safe_div(a, b):
            return np.where(b == 0, 0, a / b)

        df_calc["Akt Khusus (%)"] = safe_div(df_calc["Khusus Bln (X)"] - df_calc["Khusus Bln (X-1)"], df_calc["Khusus Bln (X-1)"]) * 100
        df_calc["Real (%)"] = safe_div(df_calc["Jan s.d Bln (X)"], df_calc["Anggaran (Thn X)"]) * 100
        df_calc["Aktv (%)"] = safe_div(df_calc["Jan s.d Bln (X)"] - df_calc["Jan s.d Bln (X-1)"], df_calc["Jan s.d Bln (X-1)"]) * 100
        df_calc["Kurang/Lebih Pencapaian"] = df_calc["Jan s.d Bln (X)"] - (df_calc["Anggaran (Thn X)"] * p_bulan_ke / 12)
        df_calc["Perbulan"] = df_calc["Anggaran (Thn X)"] / 12
        df_calc["Rata Perhari"] = df_calc["Anggaran (Thn X)"] / (12 * 25)
        df_calc["(+/-) Realisasi"] = df_calc["Jan s.d Bln (X)"] - df_calc["Jan s.d Bln (X-1)"]
        df_calc["Real vs Unknown (%)"] = df_calc["Real (%)"] - p_unknown
        df_calc["Real vs Siklikal (%)"] = df_calc["Real (%)"] - p_siklikal
        df_calc["Seharusnya"] = df_calc["Anggaran (Thn X)"] * (p_siklikal / 100)
        df_calc["Selisih vs Seharusnya"] = df_calc["Jan s.d Bln (X)"] - df_calc["Seharusnya"]

        for col in df_calc.columns:
            if col not in ["Loket"] and "(%)" not in col:
                df_calc[col] = df_calc[col].apply(lambda x: f"{x:,.0f}")
            elif "(%)" in col:
                df_calc[col] = df_calc[col].apply(lambda x: f"{x:,.2f}%")

        st.success("✅ Simulasi Berhasil!")
        st.dataframe(df_calc, use_container_width=True, hide_index=True)

  # ----------------------------------------
  # TAMPILAN: PIMPINAN (DASHBOARD LENGKAP + EXCEL AUTO-CALCULATOR)
  # ----------------------------------------
  elif st.session_state.role == "Pimpinan":
    tab_pimpinan_1, tab_pimpinan_2, tab_pimpinan_3 = st.tabs([
        "📊 Laporan Format Excel (Otomatis)",
        "📈 Dashboard Rekap & Grafik",
        "📂 Viewer File Excel Asli"
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

    # ---------------- TAB 1: LAPORAN FORMAT EXCEL (OTOMATIS MASTER + SUPABASE) ----------------
    with tab_pimpinan_1:
      st.markdown(f"### 📊 Laporan Realisasi Kinerja Tahun {TARGET_TAHUN}")
      st.write("Tabel ini menggabungkan Data Master (Anggaran & Histori X-1) dari GitHub dengan Realisasi Harian Petugas dari Supabase.")
      
      kat_pilihan = st.selectbox(
          "Pilih Kategori Pendanaan",
          ["Total (Overall)", "Kartu Dana / Sertifikat", "SWDKLLJ", "Denda"]
      )

      def generate_excel_table(jenis_dana):
        lokets = ["Kota", "Sleman", "Bantul", "Kulon Progo", "Gunung Kidul"]
        rows = []
        
        for loket in lokets:
          anggaran_x = ANGGARAN[jenis_dana].get(loket, 0)
          khusus_x1 = KHUSUS_X1[jenis_dana].get(loket, 0)
          jan_sd_x1 = JAN_SD_X1[jenis_dana].get(loket, 0)
          siklikal = SIKLIKAL[jenis_dana]

          khusus_x = 0
          jan_sd_x = 0
          if not df_db.empty:
              m_khusus = (df_db["loket"].str.lower() == loket.lower()) & (df_db["jenis_dana"].str.contains(jenis_dana[:5], case=False, na=False)) & (df_db["Bulan"] == TARGET_BULAN) & (df_db["Tahun"] == TARGET_TAHUN)
              khusus_x = df_db.loc[m_khusus, "realisasi"].sum()
              
              m_jansd = (df_db["loket"].str.lower() == loket.lower()) & (df_db["jenis_dana"].str.contains(jenis_dana[:5], case=False, na=False)) & (df_db["Bulan"] <= TARGET_BULAN) & (df_db["Tahun"] == TARGET_TAHUN)
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

        # RUMUS EXCEL LENGKAP
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

      df_display = df_final.copy()
      for col in df_display.columns:
          if col not in ["Loket"] and "(%)" not in col:
              df_display[col] = df_display[col].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
          elif "(%)" in col:
              df_display[col] = df_display[col].apply(lambda x: f"{x:,.2f}%" if pd.notnull(x) else "0.00%")

      st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ---------------- TAB 2: DASHBOARD REKAP, AUDIT & GRAFIK LENGKAP ----------------
    with tab_pimpinan_2:
      if not df_db.empty:
        df_db["dt_tanggal"] = pd.to_datetime(df_db["tanggal"])
        df_db["Bulan_Str"] = df_db["dt_tanggal"].dt.to_period("M").astype(str)
        df_db["Tahun_Str"] = df_db["dt_tanggal"].dt.year.astype(str)

        mode_waktu = st.radio("Filter Periode", ["Harian", "Bulanan", "Tahunan"], horizontal=True)

        if mode_waktu == "Harian":
          min_tgl, max_tgl = df_db["dt_tanggal"].dt.date.min(), df_db["dt_tanggal"].dt.date.max()
          dc1, dc2 = st.columns(2)
          with dc1: start_tgl = st.date_input("Dari Tanggal", value=min_tgl)
          with dc2: end_tgl = st.date_input("Sampai Tanggal", value=max_tgl)
          df_filtered = df_db[(df_db["dt_tanggal"].dt.date >= start_tgl) & (df_db["dt_tanggal"].dt.date <= end_tgl)]
        elif mode_waktu == "Bulanan":
          all_years = sorted(df_db["Tahun_Str"].unique())
          mc1, mc2 = st.columns(2)
          with mc1: start_y = st.selectbox("Tahun", all_years, key="p_sy")
          with mc2: start_m = st.selectbox("Bulan (01-12)", ["01","02","03","04","05","06","07","08","09","10","11","12"], key="p_sm")
          target_bln_str = f"{start_y}-{start_m}"
          df_filtered = df_db[df_db["Bulan_Str"] == target_bln_str]
        else:
          all_years = sorted(df_db["Tahun_Str"].unique())
          thn_pilih = st.selectbox("Pilih Tahun", all_years, key="p_thn")
          df_filtered = df_db[df_db["Tahun_Str"] == thn_pilih]

        if not df_filtered.empty:
          df_tampilan = df_filtered.drop(columns=[c for c in ["dt_tanggal", "Bulan", "Tahun", "id", "Bulan_Str", "Tahun_Str"] if c in df_filtered.columns]).copy()
          df_tampilan["realisasi"] = df_tampilan["realisasi"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
          st.dataframe(df_tampilan, use_container_width=True, hide_index=True)
        else:
          st.info("Tidak ada data pada filter tersebut.")

        # FITUR AUDIT OTOMATIS (ANOMALI)
        st.markdown("---")
        with st.expander("🔍 Audit & Deteksi Otomatis Kesalahan Ketik (Anomali Data)", expanded=False):
          df_zero = df_db[df_db["realisasi"] <= 0]
          df_dup = df_db[df_db.duplicated(subset=["tanggal", "loket", "jenis_dana"], keep=False)]
          df_outlier = df_db[df_db["realisasi"] > 500000000]

          col_a1, col_a2, col_a3 = st.columns(3)
          with col_a1:
            st.markdown("##### ⚠️ Realisasi 0 / Negatif")
            if not df_zero.empty: st.dataframe(df_zero[["tanggal", "loket", "jenis_dana", "realisasi"]], use_container_width=True, hide_index=True)
            else: st.success("✅ Aman")
          with col_a2:
            st.markdown("##### ⚠️ Duplikat Input")
            if not df_dup.empty: st.dataframe(df_dup[["tanggal", "loket", "jenis_dana", "realisasi"]], use_container_width=True, hide_index=True)
            else: st.success("✅ Aman")
          with col_a3:
            st.markdown("##### ⚠️ Potensi Typo (>500 Juta)")
            if not df_outlier.empty: st.dataframe(df_outlier[["tanggal", "loket", "jenis_dana", "realisasi"]], use_container_width=True, hide_index=True)
            else: st.success("✅ Aman")

        # GRAFIK TREN
        st.markdown("---")
        st.markdown("### 📉 Grafik Tren Realisasi")
        all_lokets = sorted(df_db["loket"].unique())
        all_jenis = sorted(df_db["jenis_dana"].unique())
        gc1, gc2 = st.columns(2)
        with gc1: sel_loket_gr = st.multiselect("Loket", options=all_lokets, default=all_lokets, key="g_loket")
        with gc2: sel_jenis_gr = st.multiselect("Jenis Dana", options=all_jenis, default=all_jenis, key="g_jenis")

        df_c = df_db[df_db["loket"].isin(sel_loket_gr) & df_db["jenis_dana"].isin(sel_jenis_gr)].copy()
        if not df_c.empty:
          df_c["Periode"] = df_c["dt_tanggal"].dt.strftime("%Y-%m-%d")
          df_chart_agg = df_c.groupby("Periode")["realisasi"].sum().reset_index()
          fig = px.bar(df_chart_agg, x="Periode", y="realisasi", color_discrete_sequence=["#005ba8"])
          fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=10, b=20))
          st.plotly_chart(fig, use_container_width=True)
      else:
        st.warning("Belum ada data di database.")

    # ---------------- TAB 3: VIEWER FILE EXCEL ASLI ----------------
    with tab_pimpinan_3:
      st.markdown("### 📂 Viewer File Excel Asli")
      selected_kategori_ex = st.selectbox(
          "Pilih Tabel dari File Excel",
          ["Total (Overall)", "Kartu Dana (KD)", "SWDKLLJ (SW)", "Denda"],
          key="viewer_excel"
      )

      try:
        wb_excel = openpyxl.load_workbook("Penerimaan Sektor UU 34 Tahun 1964.xlsx", data_only=True)
        sheet_excel = wb_excel['HARIAN BARU (2)']
        raw_data = [list(r) for r in sheet_excel.iter_rows(values_only=True)]
        df_raw = pd.DataFrame(raw_data)

        if selected_kategori_ex == "Total (Overall)": start_r, end_r = 31, 39
        elif selected_kategori_ex == "Kartu Dana (KD)": start_r, end_r = 41, 49
        elif selected_kategori_ex == "SWDKLLJ (SW)": start_r, end_r = 51, 59
        else: start_r, end_r = 61, 69

        table_subset = df_raw.iloc[start_r:end_r+1, 1:21].copy()
        table_subset.columns = table_subset.iloc[0]
        table_subset = table_subset.iloc[1:].reset_index(drop=True)

        st.dataframe(table_subset, use_container_width=True, hide_index=True)
      except Exception as e:
        st.info("File Excel cadangan tidak ditemukan di direktori root, namun sistem utama berjalan normal via Supabase.")
