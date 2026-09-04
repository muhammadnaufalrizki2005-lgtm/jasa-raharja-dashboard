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
            overflow: auto !important;
            height: auto !important;
        }
        ::-webkit-scrollbar { display: none !important; width: 0px !important; }
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
  # TAMPILAN: PETUGAS SAMSAT (MEMILIKI 2 TAB)
  # ----------------------------------------
  if st.session_state.role == "Petugas SAMSAT":
    tab_petugas_1, tab_petugas_2 = st.tabs([
        "📥 Form Input Data Harian",
        "🧮 Kalkulator & Simulator Excel"
    ])

    # ---- TAB 1: FORM INPUT HARIAN (SEPERTI BIASA) ----
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
                f"[{st.session_state.toast_count}] Data berhasil disimpan!"
                f" Loket: {f_loket} | Jenis: {f_jenis}",
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

    # ---- TAB 2: KALKULATOR & SIMULATOR EXCEL ----
    with tab_petugas_2:
      st.markdown("### 🧮 Kalkulator Simulasi Format Excel")
      st.caption("Masukkan data mentah pada tabel di bawah, sistem akan otomatis menghitung persentase, perbandingan, siklikal, dan rata-rata persis seperti di Excel.")
      
      c1, c2, c3, c4 = st.columns(4)
      with c1:
        p_jenis = st.selectbox("Kategori Dana", ["Kartu Dana", "SWDKLLJ", "Denda", "Total"])
      with c2:
        p_bulan_ke = st.number_input("Bulan Ke (1-12)", min_value=1, max_value=12, value=8)
      with c3:
        p_siklikal = st.number_input("Nilai Siklikal (%)", value=30.0, step=0.1)
      with c4:
        p_unknown = st.number_input("Nilai Pengurang Unknown (%)", value=0.0, step=0.1)

      st.markdown("##### 📝 Input Data Mentah (Silakan edit tabel di bawah):")
      
      # Data Default / Kosong untuk diisi user
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

      if st.button("🚀 Hitung & Generate Tabel Lengkap"):
        df_calc = edited_df.copy()

        # Tambah baris JUMLAH
        jumlah_row = pd.DataFrame({
            "Loket": ["JUMLAH"],
            "Anggaran (Thn X)": [df_calc["Anggaran (Thn X)"].sum()],
            "Khusus Bln (X-1)": [df_calc["Khusus Bln (X-1)"].sum()],
            "Khusus Bln (X)": [df_calc["Khusus Bln (X)"].sum()],
            "Jan s.d Bln (X-1)": [df_calc["Jan s.d Bln (X-1)"].sum()],
            "Jan s.d Bln (X)": [df_calc["Jan s.d Bln (X)"].sum()],
        })
        df_calc = pd.concat([df_calc, jumlah_row], ignore_index=True)

        # Fungsi aman untuk pembagian (mencegah error div/0)
        def safe_div(a, b):
            return np.where(b == 0, 0, a / b)

        # 1. Akt Khusus (%) = 100 * (Khusus X - Khusus X-1) / Khusus X-1
        df_calc["Akt Khusus (%)"] = safe_div(df_calc["Khusus Bln (X)"] - df_calc["Khusus Bln (X-1)"], df_calc["Khusus Bln (X-1)"]) * 100
        
        # 2. Real (%) = 100 * (Jan sd X / Anggaran X)
        df_calc["Real (%)"] = safe_div(df_calc["Jan s.d Bln (X)"], df_calc["Anggaran (Thn X)"]) * 100
        
        # 3. Aktv (%) = 100 * (Jan sd X - Jan sd X-1) / Jan sd X-1
        df_calc["Aktv (%)"] = safe_div(df_calc["Jan s.d Bln (X)"] - df_calc["Jan s.d Bln (X-1)"], df_calc["Jan s.d Bln (X-1)"]) * 100
        
        # 4. Kurang/Lebih Pencapaian = (Jan sd X) - (Anggaran * BulanKe / 12)
        df_calc["Kurang/Lebih Pencapaian"] = df_calc["Jan s.d Bln (X)"] - (df_calc["Anggaran (Thn X)"] * p_bulan_ke / 12)
        
        # 5. Perbulan = Anggaran / 12
        df_calc["Perbulan"] = df_calc["Anggaran (Thn X)"] / 12
        
        # 6. Rata Perhari = Anggaran / 12 / 25
        df_calc["Rata Perhari"] = df_calc["Anggaran (Thn X)"] / (12 * 25)
        
        # 7. (+/-) Realisasi = Jan sd X - Jan sd X-1
        df_calc["(+/-) Realisasi"] = df_calc["Jan s.d Bln (X)"] - df_calc["Jan s.d Bln (X-1)"]
        
        # 8. Real vs Unknown = Real (%) - Unknown Data
        df_calc["Real vs Unknown (%)"] = df_calc["Real (%)"] - p_unknown
        
        # 9. Real vs Siklikal = Real (%) - Siklikal
        df_calc["Real vs Siklikal (%)"] = df_calc["Real (%)"] - p_siklikal
        
        # 10. Seharusnya = Anggaran X * Siklikal / 100
        df_calc["Seharusnya"] = df_calc["Anggaran (Thn X)"] * (p_siklikal / 100)
        
        # 11. Selisih dgn Seharusnya = Jan sd X - Seharusnya
        df_calc["Selisih vs Seharusnya"] = df_calc["Jan s.d Bln (X)"] - df_calc["Seharusnya"]

        # Formatting tampilan biar rapi persis Excel
        for col in df_calc.columns:
            if "Rp" in col or col in ["Anggaran (Thn X)", "Khusus Bln (X-1)", "Khusus Bln (X)", "Jan s.d Bln (X-1)", "Jan s.d Bln (X)", "Kurang/Lebih Pencapaian", "Perbulan", "Rata Perhari", "(+/-) Realisasi", "Seharusnya", "Selisih vs Seharusnya"]:
                df_calc[col] = df_calc[col].apply(lambda x: f"{x:,.0f}")
            elif "(%)" in col:
                df_calc[col] = df_calc[col].apply(lambda x: f"{x:,.2f}%")

        st.success(f"✅ Kalkulasi Berhasil untuk Kategori: **{p_jenis}**")
        st.dataframe(df_calc, use_container_width=True, hide_index=True)


  # ----------------------------------------
  # TAMPILAN: PIMPINAN (TAB 1: DASHBOARD & TAB 2: EXCEL VIEWER DINAMIS)
  # ----------------------------------------
  elif st.session_state.role == "Pimpinan":
    tab_pimpinan_1, tab_pimpinan_2 = st.tabs([
        "📊 Dashboard Rekap & Grafik",
        "📂 Viewer Laporan Excel",
    ])

    # ---------------- TAB 1: DASHBOARD REKAP & GRAFIK ----------------
    with tab_pimpinan_1:
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
          cols_to_drop = ["dt_tanggal", "Bulan", "Tahun", "id"]
          for c in cols_to_drop:
            if c in df_tampilan.columns:
              df_tampilan = df_tampilan.drop(columns=[c])

          if "realisasi" in df_tampilan.columns:
            df_tampilan["realisasi"] = df_tampilan["realisasi"].apply(
                lambda x: f"Rp {x:,.0f}".replace(",", ".")
            )
        else:
          df_tampilan = df_filtered

        st.markdown("### 📋 Rekapitulasi Data")
        st.dataframe(df_tampilan, use_container_width=True, hide_index=True)

        # Audit Otomatis
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
              df_zero_clean = df_zero.drop(columns=[c for c in ["dt_tanggal", "Bulan", "Tahun", "id"] if c in df_zero.columns])
              st.dataframe(df_zero_clean, use_container_width=True, hide_index=True)
            else:
              st.success("✅ Aman")

          with col_a2:
            st.markdown("##### ⚠️ Duplikat Input")
            if not df_dup.empty:
              df_dup_clean = df_dup.drop(columns=[c for c in ["dt_tanggal", "Bulan", "Tahun", "id"] if c in df_dup.columns])
              st.dataframe(df_dup_clean, use_container_width=True, hide_index=True)
            else:
              st.success("✅ Aman")

          with col_a3:
            st.markdown("##### ⚠️ Potensi Typo (>500 Juta)")
            if not df_outlier.empty:
              df_outlier_clean = df_outlier.drop(columns=[c for c in ["dt_tanggal", "Bulan", "Tahun", "id"] if c in df_outlier.columns])
              st.dataframe(df_outlier_clean, use_container_width=True, hide_index=True)
            else:
              st.success("✅ Aman")

        # Grafik Analisis
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
              df_c.groupby(x_axis_val)["realisasi"]
              .sum()
              .reset_index()
          )

          fig = px.bar(
              df_chart_agg,
              x=x_axis_val,
              y="realisasi",
              labels={
                  "realisasi": "Total Realisasi (Rp)",
                  x_axis_val: "Periode",
              },
              color_discrete_sequence=["#005ba8"],
          )
          fig.update_layout(
              plot_bgcolor="rgba(0,0,0,0)",
              paper_bgcolor="rgba(0,0,0,0)",
              margin=dict(l=20, r=20, t=10, b=20),
              xaxis=dict(showgrid=False, type="category"),
              yaxis=dict(showgrid=True, gridcolor="#e5e5e5"),
              showlegend=False,
          )
          st.plotly_chart(fig, use_container_width=True)
        else:
          st.warning("Silakan pilih minimal satu wilayah dan jenis dana untuk menampilkan grafik.")

      else:
        st.warning("Belum ada data di dalam database.")

    # ---------------- TAB 2: VIEWER LAPORAN EXCEL (DENGAN DROPDOWN KATEGORI) ----------------
    with tab_pimpinan_2:
      st.markdown("### 📂 Viewer Laporan Excel Resmi")
      st.caption("Pilih kategori laporan untuk menampilkan data spesifik dari file Excel.")

      selected_kategori = st.selectbox(
          "Pilih Kategori Pendanaan",
          ["Total (Overall)", "Kartu Dana (KD)", "SWDKLLJ (SW)", "Denda"]
      )

      try:
        wb_excel = openpyxl.load_workbook("Penerimaan Sektor UU 34 Tahun 1964.xlsx", data_only=True)
        sheet_excel = wb_excel['HARIAN BARU (2)']
        raw_data = []
        for r_row in sheet_excel.iter_rows(values_only=True):
          raw_data.append(list(r_row))
        df_raw = pd.DataFrame(raw_data)

        if selected_kategori == "Total (Overall)":
          start_r, end_r = 31, 39
        elif selected_kategori == "Kartu Dana (KD)":
          start_r, end_r = 41, 49
        elif selected_kategori == "SWDKLLJ (SW)":
          start_r, end_r = 51, 59
        else: 
          start_r, end_r = 61, 69

        table_subset = df_raw.iloc[start_r:end_r+1, 1:21].copy()
        table_subset.columns = table_subset.iloc[0]
        table_subset = table_subset.iloc[1:].reset_index(drop=True)

        st.markdown(f"#### 📌 Tabel Kategori: **{selected_kategori}**")
        st.dataframe(table_subset, use_container_width=True, hide_index=True)

      except Exception as e:
        st.error(f"Gagal memuat tabel dari file Excel: {e}")
