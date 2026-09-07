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
# ⚙️ KONFIGURASI DATA MASTER
# ==========================================
SIKLIKAL = {
    "Total (Overall)": 66.28,
    "Kartu Dana / Sertifikat": 47.92,
    "SWDKLLJ": 47.00,
    "Denda": 48.00,
}

NILAI_UNKNOWN_VAR = 0.0

# ==========================================
# FUNGSI PEMBACAAN EXCEL (MULTI-SHEET)
# ==========================================
@st.cache_data
def load_historis_excel(tahun):
  try:
    sheet_name = f"Historis{tahun}"
    df_h = pd.read_excel(
        "Penerimaan Sektor UU 34 Tahun 1964.xlsx", sheet_name=sheet_name
    )
    return df_h
  except Exception:
    return pd.DataFrame()


@st.cache_data
def load_anggaran_excel(tahun):
  try:
    sheet_name = f"Anggaran{tahun}"
    df_ang = pd.read_excel(
        "Penerimaan Sektor UU 34 Tahun 1964.xlsx", sheet_name=sheet_name
    )
    return df_ang
  except Exception:
    return pd.DataFrame()


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
          if username.lower() == "petugas" and password == "SamsatDIY2026!":
            st.session_state.logged_in = True
            st.session_state.role = "Petugas SAMSAT"
            st.query_params["logged_in"] = "true"
            st.query_params["role"] = "Petugas SAMSAT"
            st.rerun()
          elif username.lower() == "pimpinan" and password == "PimpinanDIY2026!":
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
      st.title("📊 Dashboard Laporan Realisasi Kinerja")
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
    tab_petugas_1, tab_petugas_2 = st.tabs([
        "📥 Form Input Data Harian",
        "🧮 Kalkulator & Simulator Manual",
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
        f_siklikal = st.number_input(
            "Prosentase Siklikal (%)", min_value=0.0, step=0.01
        )
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
                f"[{st.session_state.toast_count}] Data berhasil disimpan ke"
                f" Supabase! Loket: {f_loket} | Jenis: {f_jenis}",
                icon="✅",
            )
            st.rerun()
          except Exception as e:
            st.error(f"❌ Gagal menyimpan data: {e}")

      st.markdown("---")
      st.markdown("### 👀 Verifikasi Input Terbaru")
      try:
        res_recent = (
            supabase.table("penerimaan_harian")
            .select("*")
            .order("id", desc=True)
            .limit(5)
            .execute()
        )
        df_recent = (
            pd.DataFrame(res_recent.data)
            if res_recent.data
            else pd.DataFrame()
        )
        if not df_recent.empty:
          df_recent["realisasi_fmt"] = df_recent["realisasi"].apply(
              lambda x: f"Rp {x:,.0f}".replace(",", ".")
          )
          st.dataframe(
              df_recent[[
                  "tanggal",
                  "loket",
                  "jenis_dana",
                  "realisasi_fmt",
                  "prosentase_siklikal",
              ]],
              use_container_width=True,
              hide_index=True,
          )
        else:
          st.info("Belum ada data yang diinput.")
      except Exception:
        st.info("Memuat riwayat input...")

    with tab_petugas_2:
      st.markdown("### 🧮 Kalkulator Simulasi Format Laporan")
      c1, c2, c3, c4 = st.columns(4)
      with c1:
        p_jenis = st.selectbox(
            "Kategori Pendanaan", ["Kartu Dana", "SWDKLLJ", "Denda", "Total"]
        )
      with c2:
        p_bulan_ke = st.number_input(
            "Bulan ke-", min_value=1, max_value=12, value=8
        )
      with c3:
        p_siklikal = st.number_input(
            "Target Siklikal (%)", value=30.0, step=0.1, key="sim_sik"
        )
      with c4:
        p_unknown = st.number_input(
            "Pengurang Cadangan (%)", value=0.0, step=0.1, key="sim_unk"
        )

      if "df_input" not in st.session_state:
        st.session_state.df_input = pd.DataFrame({
            "Loket SAMSAT": [
                "KOTA",
                "SLEMAN",
                "BANTUL",
                "KULON PROGO",
                "GUNUNG KIDUL",
            ],
            "Target Anggaran": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Bulan Ini (Thn Lalu)": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Bulan Ini (Thn Berjalan)": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Akumulasi s.d Bulan Ini (Thn Lalu)": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Akumulasi s.d Bulan Ini (Thn Berjalan)": [0.0, 0.0, 0.0, 0.0, 0.0],
        })

      edited_df = st.data_editor(
          st.session_state.df_input, use_container_width=True, hide_index=True
      )

      if st.button("🚀 Jalankan Simulasi"):
        df_calc = edited_df.copy()
        jumlah_row = pd.DataFrame({
            "Loket SAMSAT": ["JUMLAH Keseluruhan"],
            "Target Anggaran": [df_calc["Target Anggaran"].sum()],
            "Bulan Ini (Thn Lalu)": [
                df_calc["Bulan Ini (Thn Lalu)"].sum()
            ],
            "Bulan Ini (Thn Berjalan)": [
                df_calc["Bulan Ini (Thn Berjalan)"].sum()
            ],
            "Akumulasi s.d Bulan Ini (Thn Lalu)": [
                df_calc["Akumulasi s.d Bulan Ini (Thn Lalu)"].sum()
            ],
            "Akumulasi s.d Bulan Ini (Thn Berjalan)": [
                df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"].sum()
            ],
        })
        df_calc = pd.concat([df_calc, jumlah_row], ignore_index=True)

        def safe_div(a, b):
          return np.where(b == 0, 0, a / b)

        df_calc["Pertumbuhan Bulanan (YoY)"] = (
            safe_div(
                df_calc["Bulan Ini (Thn Berjalan)"]
                - df_calc["Bulan Ini (Thn Lalu)"],
                df_calc["Bulan Ini (Thn Lalu)"],
            )
            * 100
        )
        df_calc["Persentase Capaian (%)"] = (
            safe_div(
                df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"],
                df_calc["Target Anggaran"],
            )
            * 100
        )
        df_calc["Pertumbuhan Akumulasi (YoY)"] = (
            safe_div(
                df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"]
                - df_calc["Akumulasi s.d Bulan Ini (Thn Lalu)"],
                df_calc["Akumulasi s.d Bulan Ini (Thn Lalu)"],
            )
            * 100
        )
        df_calc["Deviasi Target (Surplus/Defisit)"] = df_calc[
            "Akumulasi s.d Bulan Ini (Thn Berjalan)"
        ] - (df_calc["Target Anggaran"] * p_bulan_ke / 12)
        df_calc["Target Per Bulan"] = df_calc["Target Anggaran"] / 12
        df_calc["Target Rata-rata Harian"] = df_calc["Target Anggaran"] / (
            12 * 25
        )
        df_calc["Selisih Nominal (YoY)"] = (
            df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"]
            - df_calc["Akumulasi s.d Bulan Ini (Thn Lalu)"]
        )
        df_calc["Capaian vs Cadangan (%)"] = (
            df_calc["Persentase Capaian (%)"] - p_unknown
        )
        df_calc["Capaian vs Siklikal (%)"] = (
            df_calc["Persentase Capaian (%)"] - p_siklikal
        )
        df_calc["Target Berdasarkan Siklikal"] = df_calc[
            "Target Anggaran"
        ] * (p_siklikal / 100)
        df_calc["Selisih vs Target Siklikal"] = (
            df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"]
            - df_calc["Target Berdasarkan Siklikal"]
        )

        for col in df_calc.columns:
          if col not in ["Loket SAMSAT"] and "(%)" not in col:
            df_calc[col] = df_calc[col].apply(lambda x: f"{x:,.0f}")
          elif "(%)" in col:
            df_calc[col] = df_calc[col].apply(lambda x: f"{x:,.2f}%")

        st.success("✅ Simulasi Selesai!")
        st.dataframe(df_calc, use_container_width=True, hide_index=True)

  # ----------------------------------------
  # TAMPILAN: PIMPINAN (DASHBOARD LENGKAP)
  # ----------------------------------------
  elif st.session_state.role == "Pimpinan":
    tab_pimpinan_1, tab_pimpinan_2, tab_pimpinan_3 = st.tabs([
        "📊 Laporan Eksekutif Realisasi",
        "📈 Dashboard Rekap & Grafik Tren",
        "📂 Viewer File Master Excel",
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

    # ---------------- TAB 1: LAPORAN FORMAT EXCEL (PIMPINAN) ----------------
    with tab_pimpinan_1:
      st.markdown("### 📊 Laporan Eksekutif Realisasi Penerimaan SAMSAT")
      st.write(
          "Pilih Tahun dan Bulan laporan untuk melihat ringkasan performa"
          " pencapaian, komparasi tahun sebelumnya, serta analisis pertumbuhan"
          " secara otomatis."
      )

      # Widget Filter Interaktif untuk Pimpinan
      fc1, fc2, fc3 = st.columns(3)
      with fc1:
        target_tahun_pilih = st.selectbox(
            "Tahun Laporan Utama", [2026, 2025, 2024, 2027], index=0
        )
      with fc2:
        bulan_mapping = {
            1: "Januari",
            2: "Februari",
            3: "Maret",
            4: "April",
            5: "Mei",
            6: "Juni",
            7: "Juli",
            8: "Agustus",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember",
        }
        target_bulan_pilih = st.selectbox(
            "Pilih Bulan Pelaporan",
            options=list(bulan_mapping.keys()),
            format_func=lambda x: bulan_mapping[x],
            index=7,  # Default Agustus (8)
        )
      with fc3:
        kat_pilihan = st.selectbox(
            "Kategori Pendanaan",
            ["Total (Overall)", "Kartu Dana / Sertifikat", "SWDKLLJ", "Denda"],
        )

      tahun_x1 = target_tahun_pilih - 1
      loket_col_map = {
          "Kota": "Kota",
          "Sleman": "Sleman",
          "Bantul": "Bantul",
          "Kulon Progo": "Kulon_Progo",
          "Gunung Kidul": "Gunung_Kidul",
      }

      # Load sheet Excel dinamis berdasarkan tahun
      df_anggaran_x = load_anggaran_excel(target_tahun_pilih)
      df_hist_x = load_historis_excel(target_tahun_pilih)
      df_hist_x1 = load_historis_excel(tahun_x1)

      def get_anggaran_value(df_ang, jenis_dana, loket):
        if df_ang.empty:
          return 0.0
        m = df_ang["Jenis_Dana"].str.strip() == jenis_dana.strip()
        if m.any():
          c_name = loket_col_map.get(loket, loket)
          if c_name in df_ang.columns:
            return float(df_ang.loc[m, c_name].values[0])
        return 0.0

      def get_data_value(
          df_sheet, tahun_val, bulan_val, jenis_dana, col_name, is_cumulative=False
      ):
        val = 0.0
        # 1. Cek input harian baru di Supabase
        if not df_db.empty:
          if is_cumulative:
            m_db = (
                (
                    df_db["loket"].str.lower()
                    == col_name.replace("_", " ").lower()
                )
                & (
                    df_db["jenis_dana"].str.contains(
                        jenis_dana[:5], case=False, na=False
                    )
                )
                & (df_db["Bulan"] <= bulan_val)
                & (df_db["Tahun"] == tahun_val)
            )
          else:
            m_db = (
                (
                    df_db["loket"].str.lower()
                    == col_name.replace("_", " ").lower()
                )
                & (
                    df_db["jenis_dana"].str.contains(
                        jenis_dana[:5], case=False, na=False
                    )
                )
                & (df_db["Bulan"] == bulan_val)
                & (df_db["Tahun"] == tahun_val)
            )

          if m_db.any():
            val = df_db.loc[m_db, "realisasi"].sum()
            if val > 0:
              return val

        # 2. Ambil dari sheet Excel Historis{tahun}
        if not df_sheet.empty:
          excel_col = (
              col_name
              if col_name in df_sheet.columns
              else (
                  "Kulon_Progo"
                  if "Kulon" in col_name
                  else "Gunung_Kidul"
              )
          )
          if is_cumulative:
            m_ex = (
                df_sheet["Jenis_Dana"].str.strip() == jenis_dana.strip()
            ) & (df_sheet["Bulan"] <= bulan_val)
            if m_ex.any():
              val = float(df_sheet.loc[m_ex, excel_col].sum())
          else:
            m_ex = (
                df_sheet["Jenis_Dana"].str.strip() == jenis_dana.strip()
            ) & (df_sheet["Bulan"] == bulan_val)
            if m_ex.any():
              val = float(df_sheet.loc[m_ex, excel_col].values[0])
        return val

      def generate_excel_table(jenis_dana):
        lokets = ["Kota", "Sleman", "Bantul", "Kulon Progo", "Gunung Kidul"]
        rows = []

        for loket in lokets:
          anggaran_x = get_anggaran_value(df_anggaran_x, jenis_dana, loket)
          siklikal = SIKLIKAL[jenis_dana]
          col_name = loket_col_map.get(loket, loket)

          # Ambil data komparasi tahun lalu dan tahun berjalan
          khusus_x1 = get_data_value(
              df_hist_x1,
              tahun_x1,
              target_bulan_pilih,
              jenis_dana,
              col_name,
              is_cumulative=False,
          )
          jan_sd_x1 = get_data_value(
              df_hist_x1,
              tahun_x1,
              target_bulan_pilih,
              jenis_dana,
              col_name,
              is_cumulative=True,
          )

          khusus_x = get_data_value(
              df_hist_x,
              target_tahun_pilih,
              target_bulan_pilih,
              jenis_dana,
              col_name,
              is_cumulative=False,
          )
          jan_sd_x = get_data_value(
              df_hist_x,
              target_tahun_pilih,
              target_bulan_pilih,
              jenis_dana,
              col_name,
              is_cumulative=True,
          )

          rows.append({
              "Loket SAMSAT": f"LOKET SAMSAT {loket.upper()}",
              "Target Anggaran": anggaran_x,
              "Bulan Ini (Thn Lalu)": khusus_x1,
              "Bulan Ini (Thn Berjalan)": khusus_x,
              "Akumulasi s.d Bulan Ini (Thn Lalu)": jan_sd_x1,
              "Akumulasi s.d Bulan Ini (Thn Berjalan)": jan_sd_x,
              "Siklikal_H": siklikal,
          })

        df_calc = pd.DataFrame(rows)

        jumlah_row = pd.DataFrame({
            "Loket SAMSAT": ["JUMLAH Keseluruhan"],
            "Target Anggaran": [df_calc["Target Anggaran"].sum()],
            "Bulan Ini (Thn Lalu)": [
                df_calc["Bulan Ini (Thn Lalu)"].sum()
            ],
            "Bulan Ini (Thn Berjalan)": [
                df_calc["Bulan Ini (Thn Berjalan)"].sum()
            ],
            "Akumulasi s.d Bulan Ini (Thn Lalu)": [
                df_calc["Akumulasi s.d Bulan Ini (Thn Lalu)"].sum()
            ],
            "Akumulasi s.d Bulan Ini (Thn Berjalan)": [
                df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"].sum()
            ],
            "Siklikal_H": [SIKLIKAL[jenis_dana]],
        })
        df_calc = pd.concat([df_calc, jumlah_row], ignore_index=True)

        # RUMUS EXECUTIF / LAPORAN PIMPINAN
        df_calc["Pertumbuhan Bulanan (YoY)"] = (
            safe_div(
                df_calc["Bulan Ini (Thn Berjalan)"]
                - df_calc["Bulan Ini (Thn Lalu)"],
                df_calc["Bulan Ini (Thn Lalu)"],
            )
            * 100
        )
        df_calc["Persentase Capaian (%)"] = (
            safe_div(
                df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"],
                df_calc["Target Anggaran"],
            )
            * 100
        )
        df_calc["Pertumbuhan Akumulasi (YoY)"] = (
            safe_div(
                df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"]
                - df_calc["Akumulasi s.d Bulan Ini (Thn Lalu)"],
                df_calc["Akumulasi s.d Bulan Ini (Thn Lalu)"],
            )
            * 100
        )
        df_calc["Deviasi Target (Surplus/Defisit)"] = df_calc[
            "Akumulasi s.d Bulan Ini (Thn Berjalan)"
        ] - (df_calc["Target Anggaran"] * target_bulan_pilih / 12)
        df_calc["Target Per Bulan"] = df_calc["Target Anggaran"] / 12
        df_calc["Target Rata-rata Harian"] = df_calc["Target Anggaran"] / (
            12 * 25
        )
        df_calc["Selisih Nominal (YoY)"] = (
            df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"]
            - df_calc["Akumulasi s.d Bulan Ini (Thn Lalu)"]
        )
        df_calc["Capaian vs Baseline (%)"] = (
            df_calc["Persentase Capaian (%)"] - NILAI_UNKNOWN_VAR
        )
        df_calc["Capaian vs Siklikal (%)"] = (
            df_calc["Persentase Capaian (%)"] - df_calc["Siklikal_H"]
        )
        df_calc["Target Berdasarkan Siklikal"] = df_calc[
            "Target Anggaran"
        ] * (df_calc["Siklikal_H"] / 100)
        df_calc["Selisih vs Target Siklikal"] = (
            df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"]
            - df_calc["Target Berdasarkan Siklikal"]
        )

        df_calc = df_calc.drop(columns=["Siklikal_H"])
        return df_calc

      if kat_pilihan == "Total (Overall)":
        df_kd = generate_excel_table("Kartu Dana / Sertifikat")
        df_sw = generate_excel_table("SWDKLLJ")
        df_dn = generate_excel_table("Denda")

        df_total = df_kd[[
            "Loket SAMSAT",
            "Target Anggaran",
            "Bulan Ini (Thn Lalu)",
            "Bulan Ini (Thn Berjalan)",
            "Akumulasi s.d Bulan Ini (Thn Lalu)",
            "Akumulasi s.d Bulan Ini (Thn Berjalan)",
        ]].copy()
        for col in [
            "Target Anggaran",
            "Bulan Ini (Thn Lalu)",
            "Bulan Ini (Thn Berjalan)",
            "Akumulasi s.d Bulan Ini (Thn Lalu)",
            "Akumulasi s.d Bulan Ini (Thn Berjalan)",
        ]:
          df_total[col] = df_kd[col] + df_sw[col] + df_dn[col]

        df_total["Pertumbuhan Bulanan (YoY)"] = (
            safe_div(
                df_total["Bulan Ini (Thn Berjalan)"]
                - df_total["Bulan Ini (Thn Lalu)"],
                df_total["Bulan Ini (Thn Lalu)"],
            )
            * 100
        )
        df_total["Persentase Capaian (%)"] = (
            safe_div(
                df_total["Akumulasi s.d Bulan Ini (Thn Berjalan)"],
                df_total["Target Anggaran"],
            )
            * 100
        )
        df_total["Pertumbuhan Akumulasi (YoY)"] = (
            safe_div(
                df_total["Akumulasi s.d Bulan Ini (Thn Berjalan)"]
                - df_total["Akumulasi s.d Bulan Ini (Thn Lalu)"],
                df_total["Akumulasi s.d Bulan Ini (Thn Lalu)"],
            )
            * 100
        )
        df_total["Deviasi Target (Surplus/Defisit)"] = df_total[
            "Akumulasi s.d Bulan Ini (Thn Berjalan)"
        ] - (df_total["Target Anggaran"] * target_bulan_pilih / 12)
        df_total["Target Per Bulan"] = df_total["Target Anggaran"] / 12
        df_total["Target Rata-rata Harian"] = df_total["Target Anggaran"] / (
            12 * 25
        )
        df_total["Selisih Nominal (YoY)"] = (
            df_total["Akumulasi s.d Bulan Ini (Thn Berjalan)"]
            - df_total["Akumulasi s.d Bulan Ini (Thn Lalu)"]
        )

        siklikal_tot = SIKLIKAL["Total (Overall)"]
        df_total["Capaian vs Baseline (%)"] = (
            df_total["Persentase Capaian (%)"] - NILAI_UNKNOWN_VAR
        )
        df_total["Capaian vs Siklikal (%)"] = (
            df_total["Persentase Capaian (%)"] - siklikal_tot
        )
        df_total["Target Berdasarkan Siklikal"] = df_total[
            "Target Anggaran"
        ] * (siklikal_tot / 100)
        df_total["Selisih vs Target Siklikal"] = (
            df_total["Akumulasi s.d Bulan Ini (Thn Berjalan)"]
            - df_total["Target Berdasarkan Siklikal"]
        )

        df_final = df_total
      else:
        df_final = generate_excel_table(kat_pilihan)

      df_display = df_final.copy()
      for col in df_display.columns:
        if col not in ["Loket SAMSAT"] and "(%)" not in col:
          df_display[col] = df_display[col].apply(
              lambda x: f"Rp {x:,.0f}".replace(",", ".")
          )
        elif "(%)" in col:
          df_display[col] = df_display[col].apply(
              lambda x: f"{x:,.2f}%" if pd.notnull(x) else "0.00%"
          )

      st.markdown(
          f"**Laporan Realisasi Periode: {bulan_mapping[target_bulan_pilih]}"
          f" {target_tahun_pilih} (Dibandingkan dengan Tahun {tahun_x1})**"
      )
      st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ---------------- TAB 2: DASHBOARD REKAP, AUDIT & GRAFIK (DENGAN PILIHAN JENIS GRAFIK) ----------------
    with tab_pimpinan_2:
      if not df_db.empty:
        df_db["dt_tanggal"] = pd.to_datetime(df_db["tanggal"])
        df_db["Bulan_Str"] = (
            df_db["dt_tanggal"].dt.to_period("M").astype(str)
        )
        df_db["Tahun_Str"] = df_db["dt_tanggal"].dt.year.astype(str)

        mode_waktu = st.radio(
            "Filter Periode", ["Harian", "Bulanan", "Tahunan"], horizontal=True
        )

        if mode_waktu == "Harian":
          min_tgl, max_tgl = (
              df_db["dt_tanggal"].dt.date.min(),
              df_db["dt_tanggal"].dt.date.max(),
          )
          dc1, dc2 = st.columns(2)
          with dc1:
            start_tgl = st.date_input("Dari Tanggal", value=min_tgl)
          with dc2:
            end_tgl = st.date_input("Sampai Tanggal", value=max_tgl)
          df_filtered = df_db[
              (df_db["dt_tanggal"].dt.date >= start_tgl)
              & (df_db["dt_tanggal"].dt.date <= end_tgl)
          ]
        elif mode_waktu == "Bulanan":
          all_years = sorted(df_db["Tahun_Str"].unique())
          mc1, mc2 = st.columns(2)
          with mc1:
            start_y = st.selectbox("Tahun", all_years, key="p_sy")
          with mc2:
            start_m = st.selectbox(
                "Bulan (01-12)",
                [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                ],
                key="p_sm",
            )
          target_bln_str = f"{start_y}-{start_m}"
          df_filtered = df_db[df_db["Bulan_Str"] == target_bln_str]
        else:
          all_years = sorted(df_db["Tahun_Str"].unique())
          thn_pilih = st.selectbox("Pilih Tahun", all_years, key="p_thn")
          df_filtered = df_db[df_db["Tahun_Str"] == thn_pilih]

        if not df_filtered.empty:
          df_tampilan = df_filtered.drop(
              columns=[
                  c
                  for c in [
                      "dt_tanggal",
                      "Bulan",
                      "Tahun",
                      "id",
                      "Bulan_Str",
                      "Tahun_Str",
                  ]
                  if c in df_filtered.columns
              ]
          ).copy()
          df_tampilan["realisasi"] = df_tampilan["realisasi"].apply(
              lambda x: f"Rp {x:,.0f}".replace(",", ".")
          )
          st.dataframe(df_tampilan, use_container_width=True, hide_index=True)
        else:
          st.info("Tidak ada data pada filter tersebut.")

        # FITUR AUDIT OTOMATIS (ANOMALI)
        st.markdown("---")
        with st.expander(
            "🔍 Audit & Deteksi Otomatis Validasi Data", expanded=False
        ):
          df_zero = df_db[df_db["realisasi"] <= 0]
          df_dup = df_db[
              df_db.duplicated(
                  subset=["tanggal", "loket", "jenis_dana"], keep=False
              )
          ]
          df_outlier = df_db[df_db["realisasi"] > 500000000]

          col_a1, col_a2, col_a3 = st.columns(3)
          with col_a1:
            st.markdown("##### ⚠️ Nilai 0 / Negatif")
            if not df_zero.empty:
              st.dataframe(
                  df_zero[["tanggal", "loket", "jenis_dana", "realisasi"]],
                  use_container_width=True,
                  hide_index=True,
              )
            else:
              st.success("✅ Aman")
          with col_a2:
            st.markdown("##### ⚠️ Duplikasi Entri")
            if not df_dup.empty:
              st.dataframe(
                  df_dup[["tanggal", "loket", "jenis_dana", "realisasi"]],
                  use_container_width=True,
                  hide_index=True,
              )
            else:
              st.success("✅ Aman")
          with col_a3:
            st.markdown("##### ⚠️ Potensi Salah Input (>500 Juta)")
            if not df_outlier.empty:
              st.dataframe(
                  df_outlier[["tanggal", "loket", "jenis_dana", "realisasi"]],
                  use_container_width=True,
                  hide_index=True,
              )
            else:
              st.success("✅ Aman")

        # GRAFIK TREN DENGAN PILIHAN BENTUK (BAR, LINE, AREA)
        st.markdown("---")
        st.markdown("### 📉 Grafik Tren Perolehan Realisasi")
        
        # Pilihan Model Grafik untuk Pimpinan
        tipo_grafik = st.radio(
            "Pilih Format Tampilan Grafik:",
            ["Diagram Batang (Bar)", "Grafik Garis (Line)", "Grafik Area (Area)"],
            horizontal=True,
            key="pilih_jenis_grafik"
        )

        all_lokets = sorted(df_db["loket"].unique())
        all_jenis = sorted(df_db["jenis_dana"].unique())
        gc1, gc2 = st.columns(2)
        with gc1:
          sel_loket_gr = st.multiselect(
              "Loket", options=all_lokets, default=all_lokets, key="g_loket"
          )
        with gc2:
          sel_jenis_gr = st.multiselect(
              "Jenis Dana", options=all_jenis, default=all_jenis, key="g_jenis"
          )

        df_c = df_db[
            df_db["loket"].isin(sel_loket_gr)
            & df_db["jenis_dana"].isin(sel_jenis_gr)
        ].copy()
        
        if not df_c.empty:
          df_c["Periode"] = df_c["dt_tanggal"].dt.strftime("%Y-%m-%d")
          df_chart_agg = (
              df_c.groupby("Periode")["realisasi"].sum().reset_index()
          )

          # Render Grafik Berdasarkan Pilihan Pimpinan
          if tipo_grafik == "Diagram Batang (Bar)":
            fig = px.bar(
                df_chart_agg,
                x="Periode",
                y="realisasi",
                color_discrete_sequence=["#005ba8"],
            )
          elif tipo_grafik == "Grafik Garis (Line)":
            fig = px.line(
                df_chart_agg,
                x="Periode",
                y="realisasi",
                markers=True,
                color_discrete_sequence=["#005ba8"],
            )
          else:  # Area Chart
            fig = px.area(
                df_chart_agg,
                x="Periode",
                y="realisasi",
                color_discrete_sequence=["#005ba8"],
            )

          fig.update_layout(
              plot_bgcolor="rgba(0,0,0,0)",
              paper_bgcolor="rgba(0,0,0,0)",
              margin=dict(l=20, r=20, t=10, b=20),
          )
          st.plotly_chart(fig, use_container_width=True)
      else:
        st.warning("Belum ada data realisasi harian di database.")

    # ---------------- TAB 3: VIEWER FILE EXCEL ASLI ----------------
    with tab_pimpinan_3:
      st.markdown("### 📂 Viewer File Master Excel")
      selected_kategori_ex = st.selectbox(
          "Pilih Kategori Tampilan Master",
          ["Total (Overall)", "Kartu Dana (KD)", "SWDKLLJ (SW)", "Denda"],
          key="viewer_excel",
      )

      try:
        wb_excel = openpyxl.load_workbook(
            "Penerimaan Sektor UU 34 Tahun 1964.xlsx", data_only=True
        )
        sheet_excel = wb_excel["HARIAN BARU (2)"]
        raw_data = [list(r) for r in sheet_excel.iter_rows(values_only=True)]
        df_raw = pd.DataFrame(raw_data)

        if selected_kategori_ex == "Total (Overall)":
          start_r, end_r = 31, 39
        elif selected_kategori_ex == "Kartu Dana (KD)":
          start_r, end_r = 41, 49
        elif selected_kategori_ex == "SWDKLLJ (SW)":
          start_r, end_r = 51, 59
        else:
          start_r, end_r = 61, 69

        table_subset = df_raw.iloc[start_r : end_r + 1, 1:21].copy()
        table_subset.columns = table_subset.iloc[0]
        table_subset = table_subset.iloc[1:].reset_index(drop=True)

        st.dataframe(table_subset, use_container_width=True, hide_index=True)
      except Exception:
        st.info(
            "File Excel utama 'Penerimaan Sektor UU 34 Tahun 1964.xlsx' belum"
            " ditemukan di direktori project."
        )
