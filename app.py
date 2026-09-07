import base64
import calendar
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

# ==========================================
# GAYA UI KORPORAT JASA RAHARJA
# ==========================================
css_common = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp { 
        background-color: #ffffff; 
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stHeadingAnchor, [data-testid="stHeaderActionElements"], a[href^="#"] { display: none !important; }

    /* Tombol Korporat Jasa Raharja */
    div.stButton > button:first-child {
        background-color: #005ba8;
        color: white;
        width: 100%;
        border-radius: 6px;
        padding: 10px 16px;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 91, 168, 0.2);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        background-color: #004580;
        box-shadow: 0 4px 8px rgba(0, 91, 168, 0.3);
    }

    /* Container Card Style */
    div.stForm {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #f0f2f5;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: nowrap;
        background-color: transparent;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
        color: #555555;
        padding: 0 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0f7ff !important;
        color: #005ba8 !important;
        border-bottom: 2px solid #005ba8;
    }

    /* DataFrame & Table Polish */
    [data-testid="stDataFrame"] {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""

# ==========================================
# TAMPILAN HALAMAN LOGIN
# ==========================================
if not st.session_state.logged_in:
  st.markdown(
      css_common
      + """
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
        background-color: #f4f7fc !important;
    }
    ::-webkit-scrollbar { display: none !important; width: 0px !important; }
    </style>
    """,
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 1.3, 1])

  with col2:
    st.markdown("<div style='height: 4vh;'></div>", unsafe_allow_html=True)
    with st.container():
      if img_base64:
        st.markdown(
            f"""
                <div style="text-align: center; margin-bottom: 15px;">
                    <img src="data:image/png;base64,{img_base64}" width="220" style="display: block; margin: 0 auto; height: auto;">
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
          "<div style='text-align: center; color: #333333; font-size: 1.25rem;"
          " font-weight: 700; margin-bottom: 4px;'>Portal Monitoring Kanwil"
          " DIY</div>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<div style='text-align: center; color: #666666; font-size: 0.9rem;"
          " margin-bottom: 20px;'>Silakan masuk dengan akun resmi Anda</div>",
          unsafe_allow_html=True,
      )

      with st.form("form_login_portal"):
        username = st.text_input(
            "ID Pengguna", placeholder="Masukkan ID Pengguna"
        )
        password = st.text_input(
            "Password", type="password", placeholder="Masukkan Password"
        )
        st.write("")
        login_button = st.form_submit_button("Masuk Sistem")

        if login_button:
          if username.lower() == "petugas" and password == "PetugasDIY2026!":
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
          " 20px; color: #888888;'>© 2026 PT Jasa Raharja Kanwil DIY — All"
          " Rights Reserved</p>",
          unsafe_allow_html=True,
      )

# ==========================================
# TAMPILAN DASHBOARD SETELAH LOGIN
# ==========================================
else:
  st.markdown(
      css_common
      + """
    <style>
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
      st.markdown(
          "<h2 style='color: #005ba8; margin-bottom: 0; font-weight:"
          " 700;'>Portal Petugas SAMSAT</h2>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='color: #666; margin-top: 2px;'>Kanwil DIY — PT Jasa"
          " Raharja</p>",
          unsafe_allow_html=True,
      )
    else:
      st.markdown(
          "<h2 style='color: #005ba8; margin-bottom: 0; font-weight:"
          " 700;'>Dashboard Laporan Realisasi Kinerja</h2>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='color: #666; margin-top: 2px;'>Monitoring Penerimaan Sektor"
          " UU 34 Tahun 1964</p>",
          unsafe_allow_html=True,
      )
  with header_col2:
    st.write("")
    if st.button("🚪 Keluar"):
      st.session_state.logged_in = False
      st.session_state.role = None
      st.query_params.clear()
      st.rerun()

  st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

  # ----------------------------------------
  # TAMPILAN: PETUGAS SAMSAT (INPUT & KOREKSI RIWAYAT DENGAN FILTER TANGGAL)
  # ----------------------------------------
  if st.session_state.role == "Petugas SAMSAT":
    st.markdown("### 📥 Formulir Input Laporan Penerimaan Harian")
    st.write(
        "Silakan masukkan jumlah penerimaan harian berdasarkan Loket SAMSAT"
        " dan Jenis Pembayaran yang melayani."
    )

    col1, col2 = st.columns(2)
    with col1:
      f_tanggal = st.date_input(
          "Tanggal Transaksi / Laporan", value=date.today()
      )
      f_loket = st.selectbox(
          "Loket SAMSAT",
          ["Kota", "Sleman", "Bantul", "Kulon Progo", "Gunung Kidul"],
      )
    with col2:
      f_jenis = st.selectbox(
          "Jenis Pembayaran / Dana",
          ["Kartu Dana / Sertifikat", "SWDKLLJ", "Denda"],
      )
      f_realisasi = st.number_input(
          "Jumlah Uang Masuk / Penerimaan (Rp)",
          min_value=0.0,
          step=1000.0,
          format="%.2f",
      )
      f_realisasi_str = f"Rp {f_realisasi:,.0f}".replace(",", ".")
      st.caption(f"💡 Terbaca: **{f_realisasi_str}**")

    col3, col4 = st.columns(2)
    with col3:
      f_siklikal = st.number_input(
          "Persentase Siklus Bulanan (%)",
          min_value=0.0,
          step=0.01,
          help="Persentase target bulanan berdasarkan pola siklus penerimaan.",
      )
    with col4:
      f_yty = st.number_input(
          "Target Pertumbuhan Tahun Lalu / YoY (%)",
          min_value=0.0,
          step=0.01,
          help="Perbandingan atau target pertumbuhan dibanding periode yang sama tahun lalu.",
      )

    st.write("")
    submit_button = st.button("💾 Simpan Laporan Penerimaan")

    if submit_button:
      if f_realisasi <= 0:
        st.error("❌ Jumlah Uang Masuk / Penerimaan (Rp) tidak boleh 0 atau kosong.")
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
              f"[{st.session_state.toast_count}] Laporan berhasil disimpan ke"
              f" sistem! Loket: {f_loket} | Jenis: {f_jenis}",
              icon="✅",
          )
          st.rerun()
        except Exception as e:
          st.error(f"❌ Gagal menyimpan laporan: {e}")

    st.markdown("---")
    st.markdown("### 👀 Riwayat & Koreksi Laporan Berdasarkan Tanggal")
    st.write(
        "Pilih rentang tanggal laporan di bawah ini. Data pada tabel riwayat"
        " serta menu Ubah/Hapus akan otomatis menyesuaikan dengan rentang"
        " tanggal tersebut."
    )

    fc_tgl1, fc_tgl2 = st.columns(2)
    with fc_tgl1:
      filter_dari = st.date_input(
          "Tampilkan Dari Tanggal", value=date.today().replace(day=1)
      )
    with fc_tgl2:
      filter_sampai = st.date_input("Sampai Tanggal", value=date.today())

    try:
      res_recent = (
          supabase.table("penerimaan_harian")
          .select("*")
          .gte("tanggal", str(filter_dari))
          .lte("tanggal", str(filter_sampai))
          .order("tanggal", desc=True)
          .execute()
      )
      df_recent = (
          pd.DataFrame(res_recent.data) if res_recent.data else pd.DataFrame()
      )

      if not df_recent.empty:
        df_show = df_recent.copy()
        df_show["Jumlah Penerimaan"] = df_show["realisasi"].apply(
            lambda x: f"Rp {x:,.0f}".replace(",", ".")
        )
        df_show = df_show.rename(
            columns={
                "id": "ID",
                "tanggal": "Tanggal",
                "loket": "Loket SAMSAT",
                "jenis_dana": "Jenis Pembayaran",
                "prosentase_siklikal": "Siklus Bulanan (%)",
            }
        )
        st.dataframe(
            df_show[[
                "ID",
                "Tanggal",
                "Loket SAMSAT",
                "Jenis Pembayaran",
                "Jumlah Penerimaan",
                "Siklus Bulanan (%)",
            ]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### ✏️ Ubah atau Hapus Laporan Tertentu")
        with st.expander(
            "Klik di sini untuk Mengoreksi / Menghapus Data Sesuai Pilihan"
            " Tanggal"
        ):
          options_record = []
          record_map = {}
          for idx, row in df_recent.iterrows():
            label = f"ID #{row['id']} — Tgl: {row['tanggal']} | Loket: {row['loket']} | {row['jenis_dana']} | Rp {row['realisasi']:,.0f}".replace(
                ",", "."
            )
            options_record.append(label)
            record_map[label] = row

          if options_record:
            selected_label = st.selectbox(
                "Pilih Laporan dari Rentang Tanggal di Atas",
                options=options_record,
            )
            selected_row = record_map[selected_label]
            sel_id = int(selected_row["id"])

            with st.form("form_edit_data"):
              e_tanggal = st.date_input(
                  "Koreksi Tanggal",
                  value=pd.to_datetime(selected_row["tanggal"]).date(),
              )
              e_loket = st.selectbox(
                  "Koreksi Loket SAMSAT",
                  ["Kota", "Sleman", "Bantul", "Kulon Progo", "Gunung Kidul"],
                  index=[
                      "Kota",
                      "Sleman",
                      "Bantul",
                      "Kulon Progo",
                      "Gunung Kidul",
                  ].index(selected_row["loket"])
                  if selected_row["loket"]
                  in ["Kota", "Sleman", "Bantul", "Kulon Progo", "Gunung Kidul"]
                  else 0,
              )
              e_jenis = st.selectbox(
                  "Koreksi Jenis Pembayaran",
                  ["Kartu Dana / Sertifikat", "SWDKLLJ", "Denda"],
                  index=[
                      "Kartu Dana / Sertifikat",
                      "SWDKLLJ",
                      "Denda",
                  ].index(selected_row["jenis_dana"])
                  if selected_row["jenis_dana"]
                  in ["Kartu Dana / Sertifikat", "SWDKLLJ", "Denda"]
                  else 0,
              )
              e_realisasi = st.number_input(
                  "Koreksi Jumlah Uang Masuk / Penerimaan (Rp)",
                  min_value=0.0,
                  value=float(selected_row["realisasi"]),
                  step=1000.0,
                  format="%.2f",
              )
              e_siklikal = st.number_input(
                  "Koreksi Siklus Bulanan (%)",
                  min_value=0.0,
                  value=float(selected_row["prosentase_siklikal"]),
                  step=0.01,
              )
              e_yty = st.number_input(
                  "Koreksi YoY (%)",
                  min_value=0.0,
                  value=float(selected_row["siklikal_yty"]),
                  step=0.01,
              )

              col_btn1, col_btn2 = st.columns(2)
              with col_btn1:
                update_btn = st.form_submit_button("🔄 Perbarui Data")
              with col_btn2:
                delete_btn = st.form_submit_button("🗑️ Hapus Laporan Ini")

              if update_btn:
                try:
                  supabase.table("penerimaan_harian").update({
                      "tanggal": str(e_tanggal),
                      "loket": e_loket,
                      "jenis_dana": e_jenis,
                      "realisasi": e_realisasi,
                      "prosentase_siklikal": e_siklikal,
                      "siklikal_yty": e_yty,
                  }).eq("id", sel_id).execute()
                  st.success("✅ Laporan berhasil diperbarui!")
                  st.rerun()
                except Exception as e:
                  st.error(f"❌ Gagal memperbarui: {e}")

              if delete_btn:
                try:
                  supabase.table("penerimaan_harian").delete().eq(
                      "id", sel_id
                  ).execute()
                  st.warning("🗑️ Laporan berhasil dihapus dari sistem!")
                  st.rerun()
                except Exception as e:
                  st.error(f"❌ Gagal menghapus: {e}")
      else:
        st.info("Tidak ada data laporan pada rentang tanggal tersebut.")
    except Exception as err:
      st.info(f"Memuat riwayat laporan... ({err})")

  # ----------------------------------------
  # TAMPILAN: PIMPINAN (DASHBOARD LENGKAP)
  # ----------------------------------------
  elif st.session_state.role == "Pimpinan":
    tab_pimpinan_1, tab_pimpinan_2, tab_pimpinan_3 = st.tabs([
        "📊 Laporan Eksekutif Realisasi",
        "📈 Dashboard Rekap & Grafik Tren",
        "📂 Viewer File Master Excel",
    ])

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
            index=7,
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

    # ---------------- TAB 2: DASHBOARD REKAP, AUDIT & GRAFIK (DENGAN FILTER RENTANG BULAN & TAHUN) ----------------
    with tab_pimpinan_2:
      if not df_db.empty:
        df_db["dt_tanggal"] = pd.to_datetime(df_db["tanggal"])
        df_db["Tahun_Str"] = df_db["dt_tanggal"].dt.year.astype(str)
        all_years = sorted(df_db["Tahun_Str"].unique())
        if not all_years:
          all_years = [str(date.today().year)]

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
          st.markdown(
              "**Pilih Rentang Bulan (Dari Bulan ... Sampai Bulan ...)**"
          )
          mc1, mc2 = st.columns(2)
          with mc1:
            start_m_year = st.selectbox(
                "Dari Tahun", all_years, key="p_sy_start"
            )
            start_m_val = st.selectbox(
                "Dari Bulan",
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
                key="p_sm_start",
            )
          with mc2:
            end_m_year = st.selectbox(
                "Sampai Tahun",
                all_years,
                key="p_sy_end",
                index=len(all_years) - 1,
            )
            end_m_val = st.selectbox(
                "Sampai Bulan",
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
                key="p_sm_end",
                index=11,
            )

          start_date_str = f"{start_m_year}-{start_m_val}-01"
          last_day = calendar.monthrange(
              int(end_m_year), int(end_m_val)
          )[1]
          end_date_str = f"{end_m_year}-{end_m_val}-{last_day}"

          df_filtered = df_db[
              (df_db["dt_tanggal"] >= pd.to_datetime(start_date_str))
              & (df_db["dt_tanggal"] <= pd.to_datetime(end_date_str))
          ]

        else:
          st.markdown(
              "**Pilih Rentang Tahun (Dari Tahun ... Sampai Tahun ...)**"
          )
          tc1, tc2 = st.columns(2)
          with tc1:
            start_thn = st.selectbox("Dari Tahun", all_years, key="p_thn_start")
          with tc2:
            end_thn = st.selectbox(
                "Sampai Tahun",
                all_years,
                key="p_thn_end",
                index=len(all_years) - 1,
            )

          df_filtered = df_db[
              (df_db["Tahun"] >= int(start_thn))
              & (df_db["Tahun"] <= int(end_thn))
          ]

        if not df_filtered.empty:
          df_tampilan = df_filtered.drop(
              columns=[
                  c
                  for c in [
                      "dt_tanggal",
                      "Bulan",
                      "Tahun",
                      "id",
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
          st.info("Tidak ada data pada rentang filter tersebut.")

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

        st.markdown("---")
        st.markdown("### 📉 Grafik Tren Perolehan Realisasi")

        tipo_grafik = st.radio(
            "Pilih Format Tampilan Grafik:",
            ["Diagram Batang (Bar)", "Grafik Garis (Line)", "Grafik Area (Area)"],
            horizontal=True,
            key="pilih_jenis_grafik",
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

        df_c = df_filtered[
            df_filtered["loket"].isin(sel_loket_gr)
            & df_filtered["jenis_dana"].isin(sel_jenis_gr)
        ].copy()

        if not df_c.empty:
          if mode_waktu == "Tahunan":
            df_c["Periode"] = df_c["dt_tanggal"].dt.strftime("%Y")
          elif mode_waktu == "Bulanan":
            df_c["Periode"] = df_c["dt_tanggal"].dt.strftime("%B %Y")
          else:
            df_c["Periode"] = df_c["dt_tanggal"].dt.strftime("%Y-%m-%d")

          df_chart_agg = (
              df_c.groupby("Periode")["realisasi"].sum().reset_index()
          )

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
          else:
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
          st.warning(
              "Tidak ada data grafik yang sesuai dengan rentang filter periode"
              " tersebut."
          )
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
