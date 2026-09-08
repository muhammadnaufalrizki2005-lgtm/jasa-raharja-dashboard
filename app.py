import base64
import calendar
from datetime import date
from PIL import Image
import pandas as pd
import numpy as np
import openpyxl
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client

# ==========================================
# ⚙️ SISTEM LOGIN & SESI
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
# ⚙️ LOGIKA PENENTUAN JUDUL TAB BROWSER (DYNAMIC)
# ==========================================
if not st.session_state.logged_in:
    dynamic_title = "Portal Monitoring DIY"
elif st.session_state.role == "Petugas SAMSAT":
    dynamic_title = "Portal Petugas SAMSAT"
else:
    dynamic_title = "Dashboard Realisasi"

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
    page_title=dynamic_title,
    page_icon=favicon_img,
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
# TAMPILAN HALAMAN LOGIN
# ==========================================
if not st.session_state.logged_in:
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Lora:wght@400;500;600&display=swap');
    
    .stApp { 
        background-color: #f4f7fc; 
        font-family: 'Lora', serif;
        color: #1a1a1a;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif !important;
    }
    
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    .stHeadingAnchor, [data-testid="stHeadingAnchor"], h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
        visibility: hidden !important;
    }

    button[kind="primary"] {
        background-color: #005ba8 !important;
        border-color: #005ba8 !important;
        color: white !important;
        font-family: 'Lora', serif !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 8px 24px !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: #004580 !important;
        border-color: #004580 !important;
        box-shadow: 0 4px 12px rgba(0, 91, 168, 0.2) !important;
    }

    div[data-testid="stForm"] {
        background-color: #ffffff;
        border: 1px solid #eaedf2;
        border-radius: 12px;
        padding: 32px 24px;
        box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1);
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
        background-color: #f4f7fc;
    }
    ::-webkit-scrollbar { display: none !important; width: 0px !important; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True)
        with st.container():
            if img_base64:
                st.markdown(
                    f"""
                <div style="text-align: center; margin-bottom: 16px;">
                    <img src="data:image/png;base64,{img_base64}" width="200" style="display: block; margin: 0 auto; height: auto;">
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<h2 style='text-align: center; color: #005ba8; margin-bottom: 0;'>PT JASA RAHARJA</h2>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<div style='text-align: center; color: #1a1a1a; font-family:\"Playfair Display\", serif; font-size: 1.3rem; font-weight: 700; margin-bottom: 4px;'>Portal Monitoring Kanwil DIY</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div style='text-align: center; color: #6c757d; font-size: 0.9rem; margin-bottom: 20px;'>Silakan masuk menggunakan kredensial resmi Anda</div>",
                unsafe_allow_html=True,
            )

            with st.form("form_login_portal", clear_on_submit=False):
                username = st.text_input("ID Pengguna", placeholder="Masukkan ID Pengguna")
                password = st.text_input("Password", type="password", placeholder="Masukkan Password")
                st.markdown("<br>", unsafe_allow_html=True)
                login_button = st.form_submit_button("Masuk Sistem", type="primary")

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
                        st.error("ID Pengguna atau Password salah. Silakan coba lagi.")

            st.markdown(
                "<p style='text-align: center; font-size: 11px; margin-top: 20px; color: #a0aabf;'>© 2026 PT Jasa Raharja Kanwil DIY — Hak Cipta Dilindungi Undang-Undang.</p>",
                unsafe_allow_html=True,
            )

# ==========================================
# TAMPILAN DASHBOARD SETELAH LOGIN
# ==========================================
else:
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Lora:wght@400;500;600&display=swap');
    
    .stApp { 
        background-color: #ffffff; 
        font-family: 'Lora', serif;
        color: #1a1a1a;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif !important;
    }
    
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    .stHeadingAnchor, [data-testid="stHeadingAnchor"], h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
        visibility: hidden !important;
    }

    button[kind="primary"] {
        background-color: #005ba8 !important;
        border-color: #005ba8 !important;
        color: white !important;
        font-family: 'Lora', serif !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 8px 24px !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: #004580 !important;
        border-color: #004580 !important;
        box-shadow: 0 4px 12px rgba(0, 91, 168, 0.2) !important;
    }

    div[data-testid="stForm"] {
        background-color: #ffffff;
        border: 1px solid #eaedf2;
        border-radius: 12px;
        padding: 32px 24px;
        box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 2px solid #eaedf2;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: nowrap;
        background-color: transparent;
        border-radius: 0;
        font-family: 'Playfair Display', serif !important;
        font-weight: 600;
        color: #6c757d;
        padding: 0 4px;
    }
    .stTabs [aria-selected="true"] {
        color: #005ba8 !important;
        border-bottom: 3px solid #005ba8 !important;
        background-color: transparent !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #eaedf2;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }
    [data-testid="stDataFrame"] > div:hover {
        box-shadow: none !important;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        overflow: auto !important;
        height: auto !important;
        background-color: #ffffff;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
        unsafe_allow_html=True,
    )

    # HEADER NAVIGATION
    st.markdown("<div style='padding-top: 1rem;'></div>", unsafe_allow_html=True)
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        if st.session_state.role == "Petugas SAMSAT":
            st.markdown(
                "<h2 style='color: #005ba8; margin-bottom: 4px; font-weight: 700; letter-spacing: -0.5px;'>Portal Petugas SAMSAT</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='color: #6c757d; font-size: 1rem;'>Kanwil DIY — PT Jasa Raharja</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<h2 style='color: #005ba8; margin-bottom: 4px; font-weight: 700; letter-spacing: -0.5px;'>Dashboard Realisasi Kinerja</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='color: #6c757d; font-size: 1rem;'>Monitoring Penerimaan Sektor UU 34 Tahun 1964</p>",
                unsafe_allow_html=True,
            )
    with header_col2:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("Keluar", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.query_params.clear()
            st.rerun()

    st.markdown(
        "<hr style='border-top: 1px solid #eaedf2; margin-top: 0px; margin-bottom: 30px;'>",
        unsafe_allow_html=True,
    )

    # ----------------------------------------
    # TAMPILAN: PETUGAS SAMSAT (INPUT & KOREKSI RIWAYAT)
    # ----------------------------------------
    if st.session_state.role == "Petugas SAMSAT":
        st.markdown("### Formulir Input Laporan Penerimaan Harian")
        st.markdown(
            "<p style='color: #6c757d; margin-bottom: 24px;'>Silakan masukkan data penerimaan harian berdasarkan loket SAMSAT dan jenis pembayaran yang melayani.</p>",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            f_tanggal = st.date_input("Tanggal Transaksi / Laporan", value=date.today())
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
            st.caption(f"Nominal Terbaca: **{f_realisasi_str}**")

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

        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.button("Simpan Laporan Penerimaan", type="primary")

        if submit_button:
            if f_realisasi <= 0:
                st.error("Jumlah Uang Masuk / Penerimaan (Rp) tidak valid.")
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
                        f"Laporan berhasil disimpan ke sistem! (Loket: {f_loket})",
                        icon="✅",
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menyimpan laporan: {e}")

        st.markdown(
            "<br><hr style='border-top: 1px solid #eaedf2;'><br>",
            unsafe_allow_html=True,
        )

        st.markdown("### Riwayat & Koreksi Laporan")
        st.markdown(
            "<p style='color: #6c757d; margin-bottom: 24px;'>Tentukan rentang tanggal di bawah ini untuk menampilkan, memeriksa, atau mengoreksi data historis.</p>",
            unsafe_allow_html=True,
        )

        fc_tgl1, fc_tgl2 = st.columns(2)
        with fc_tgl1:
            filter_dari = st.date_input("Tampilkan Dari Tanggal", value=date.today().replace(day=1))
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

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### Ubah atau Hapus Laporan")
                with st.expander("Buka menu ini untuk melakukan koreksi data yang telah dipilih"):
                    options_record = []
                    record_map = {}
                    for idx, row in df_recent.iterrows():
                        label = f"ID #{row['id']} — Tgl: {row['tanggal']} | Loket: {row['loket']} | {row['jenis_dana']} | Rp {row['realisasi']:,.0f}".replace(",", ".")
                        options_record.append(label)
                        record_map[label] = row

                    if options_record:
                        selected_label = st.selectbox(
                            "Pilih Laporan Target",
                            options=options_record,
                        )
                        selected_row = record_map[selected_label]
                        sel_id = int(selected_row["id"])

                        with st.form("form_edit_data"):
                            st.markdown("**Detail Koreksi Data**")
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
                                "Koreksi Jumlah Penerimaan (Rp)",
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

                            st.markdown("<br>", unsafe_allow_html=True)
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                update_btn = st.form_submit_button("Perbarui Data", type="primary")
                            with col_btn2:
                                delete_btn = st.form_submit_button("Hapus Laporan")

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
                                    st.success("Data berhasil diperbarui dalam sistem.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Terjadi kesalahan pembaruan: {e}")

                            if delete_btn:
                                try:
                                    supabase.table("penerimaan_harian").delete().eq("id", sel_id).execute()
                                    st.warning("Data laporan berhasil dihapus dari sistem.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Terjadi kesalahan penghapusan: {e}")
            else:
                st.info("Tidak ditemukan data laporan pada rentang tanggal tersebut.")
        except Exception as err:
            st.info(f"Mengambil data historis... ({err})")

    # ----------------------------------------
    # TAMPILAN: PIMPINAN (DASHBOARD LENGKAP)
    # ----------------------------------------
    elif st.session_state.role == "Pimpinan":
        tab_pimpinan_1, tab_pimpinan_2, tab_pimpinan_3, tab_pimpinan_4 = st.tabs([
            "Laporan Eksekutif Realisasi",
            "Dashboard Rekap & Grafik Tren",
            "Proyeksi & Skenario Kinerja",
            "Viewer File Excel (Master)",
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
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Laporan Eksekutif Realisasi Penerimaan SAMSAT")
            st.markdown(
                "<p style='color: #6c757d; margin-bottom: 24px;'>Pilih filter di bawah ini untuk menghasilkan komparasi kinerja tahun berjalan terhadap tahun sebelumnya.</p>",
                unsafe_allow_html=True,
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
                df_calc["Proyeksi Akhir Tahun"] = safe_div(
                    df_calc["Akumulasi s.d Bulan Ini (Thn Berjalan)"], target_bulan_pilih
                ) * 12
                df_calc["Indeks Efisiensi Siklikal"] = safe_div(
                    df_calc["Persentase Capaian (%)"], df_calc["Siklikal_H"]
                )

                def get_status_kinerja(val):
                    if val >= 0:
                        return "🟢 Optimal"
                    elif val >= -5:
                        return "🟡 Waspada"
                    else:
                        return "🔴 Defisit Kritis"

                df_calc["Status Kinerja"] = df_calc["Capaian vs Siklikal (%)"].apply(
                    get_status_kinerja
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
                df_total["Proyeksi Akhir Tahun"] = safe_div(
                    df_total["Akumulasi s.d Bulan Ini (Thn Berjalan)"], target_bulan_pilih
                ) * 12
                df_total["Indeks Efisiensi Siklikal"] = safe_div(
                    df_total["Persentase Capaian (%)"], siklikal_tot
                )

                def get_status_kinerja(val):
                    if val >= 0:
                        return "🟢 Optimal"
                    elif val >= -5:
                        return "🟡 Waspada"
                    else:
                        return "🔴 Defisit Kritis"

                df_total["Status Kinerja"] = df_total["Capaian vs Siklikal (%)"].apply(
                    get_status_kinerja
                )
                df_final = df_total
            else:
                df_final = generate_excel_table(kat_pilihan)

            row_summary = df_final[df_final["Loket SAMSAT"] == "JUMLAH Keseluruhan"]
            if not row_summary.empty:
                tot_real = row_summary[
                    "Akumulasi s.d Bulan Ini (Thn Berjalan)"
                ].values[0]
                tot_cap = row_summary["Persentase Capaian (%)"].values[0]
                tot_dev = row_summary["Deviasi Target (Surplus/Defisit)"].values[0]
                tot_stat = row_summary["Status Kinerja"].values[0]
                dev_str = f"Rp {abs(tot_dev):,.0f}".replace(",", ".")
                dev_label = "surplus" if tot_dev >= 0 else "defisit"

                st.info(
                    f"💡 **Ringkasan Eksekutif ({bulan_mapping[target_bulan_pilih]}"
                    f" {target_tahun_pilih}):** Total realisasi akumulatif mencapai"
                    f" **Rp {tot_real:,.0f}** (".replace(",", ".")
                    + f"**{tot_cap:.2f}%** dari target anggaran tahunan). Performa"
                    f" wilayah secara keseluruhan berada pada status **{tot_stat}**"
                    f" dengan posisi **{dev_label} sebesar {dev_str}** terhadap"
                    " target proporsional bulanan."
                )

            df_display = df_final.copy()
            for col in df_display.columns:
                if col in ["Loket SAMSAT", "Status Kinerja"]:
                    continue
                elif "(%)" in col or "YoY" in col:
                    df_display[col] = df_display[col].apply(
                        lambda x: f"{x:,.2f}%" if pd.notnull(x) else "0.00%"
                    )
                elif col == "Indeks Efisiensi Siklikal":
                    df_display[col] = df_display[col].apply(
                        lambda x: f"{x:,.2f}x" if pd.notnull(x) else "0.00x"
                    )
                else:
                    df_display[col] = df_display[col].apply(
                        lambda x: f"Rp {x:,.0f}".replace(",", ".")
                        if pd.notnull(x)
                        else "Rp 0"
                    )

            st.markdown(
                f"<div style='font-weight: 600; margin-top: 10px; margin-bottom:"
                f" 10px;'>Tabel Detail Komparasi & Kinerja:"
                f" {bulan_mapping[target_bulan_pilih]} {target_tahun_pilih}"
                f" (Komparasi {tahun_x1})</div>",
                unsafe_allow_html=True,
            )
            st.dataframe(df_display, use_container_width=True, hide_index=True)

        # ---------------- TAB 2: DASHBOARD REKAP, AUDIT & GRAFIK ----------------
        with tab_pimpinan_2:
            st.markdown("<br>", unsafe_allow_html=True)
            if not df_db.empty:
                df_db["dt_tanggal"] = pd.to_datetime(df_db["tanggal"])
                df_db["Tahun_Str"] = df_db["dt_tanggal"].dt.year.astype(str)
                all_years = sorted(df_db["Tahun_Str"].unique())
                if not all_years:
                    all_years = [str(date.today().year)]

                mode_waktu = st.radio(
                    "Cakupan Periode Analisis:",
                    ["Harian", "Bulanan", "Tahunan"],
                    horizontal=True,
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
                    st.info("Tidak ada data laporan pada rentang filter yang dipilih.")

                st.markdown(
                    "<hr style='border-top: 1px solid #eaedf2; margin-top: 20px;'>",
                    unsafe_allow_html=True,
                )

                with st.expander("Audit & Deteksi Validasi Anomali Data"):
                    df_zero = df_db[df_db["realisasi"] <= 0]
                    df_dup = df_db[
                        df_db.duplicated(
                            subset=["tanggal", "loket", "jenis_dana"], keep=False
                        )
                    ]
                    df_outlier = df_db[df_db["realisasi"] > 500000000]

                    col_a1, col_a2, col_a3 = st.columns(3)
                    with col_a1:
                        st.markdown("**Nilai 0 / Negatif**")
                        if not df_zero.empty:
                            st.dataframe(
                                df_zero[["tanggal", "loket", "jenis_dana", "realisasi"]],
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.success("Tidak ada anomali")
                    with col_a2:
                        st.markdown("**Duplikasi Entri**")
                        if not df_dup.empty:
                            st.dataframe(
                                df_dup[["tanggal", "loket", "jenis_dana", "realisasi"]],
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.success("Tidak ada anomali")
                    with col_a3:
                        st.markdown("**Potensi Salah Input (>500 Juta)**")
                        if not df_outlier.empty:
                            st.dataframe(
                                df_outlier[["tanggal", "loket", "jenis_dana", "realisasi"]],
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.success("Tidak ada anomali")

                st.markdown(
                    "<hr style='border-top: 1px solid #eaedf2; margin-top: 20px;'>",
                    unsafe_allow_html=True,
                )
                st.markdown("### Visualisasi Tren Realisasi")

                tipo_grafik = st.radio(
                    "Format Tampilan Visual:",
                    ["Diagram Batang (Bar)", "Grafik Garis (Line)", "Grafik Area (Area)"],
                    horizontal=True,
                    key="pilih_jenis_grafik",
                )

                all_lokets = sorted(df_db["loket"].unique())
                all_jenis = sorted(df_db["jenis_dana"].unique())
                gc1, gc2 = st.columns(2)
                with gc1:
                    sel_loket_gr = st.multiselect(
                        "Filter Loket", options=all_lokets, default=all_lokets, key="g_loket"
                    )
                with gc2:
                    sel_jenis_gr = st.multiselect(
                        "Filter Kategori Dana",
                        options=all_jenis,
                        default=all_jenis,
                        key="g_jenis",
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
                        "Data tidak tersedia untuk memuat visualisasi grafik pada parameter"
                        " yang dipilih."
                    )
            else:
                st.info("Database laporan realisasi harian masih kosong.")

        # ---------------- TAB 3: PROYEKSI & SKENARIO KINERJA (AUTO-MODEL SELECTION) ----------------
        with tab_pimpinan_3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Simulasi Peramalan & Skenario Kinerja Pendapatan")
            st.markdown(
                "<p style='color: #6c757d; margin-bottom: 24px;'>Evaluasi akurasi model statistik dan proyeksi skenario manajemen risiko berbasis data historis.</p>",
                unsafe_allow_html=True,
            )

            # Tarik & Gabungkan Data Historis dari Excel
            list_history_dfs = []
            for thn in [2024, 2025, 2026]:
                df_h = load_historis_excel(thn)
                if not df_h.empty and "Bulan" in df_h.columns and "Jenis_Dana" in df_h.columns:
                    loket_cols = [c for c in df_h.columns if c not in ["Jenis_Dana", "Bulan", "No"]]
                    df_h["Total_Realisasi"] = df_h[loket_cols].sum(axis=1)
                    df_h["Tahun"] = thn
                    df_h["Bulan_Dt"] = pd.to_datetime(df_h["Tahun"].astype(str) + "-" + df_h["Bulan"].astype(str).str.zfill(2) + "-01")
                    df_grouped = df_h.groupby(["Jenis_Dana", "Bulan_Dt"])["Total_Realisasi"].sum().reset_index()
                    list_history_dfs.append(df_grouped)

            df_excel_combined = pd.concat(list_history_dfs, ignore_index=True) if list_history_dfs else pd.DataFrame(columns=["Jenis_Dana", "Bulan_Dt", "Total_Realisasi"])

            # Tarik Data dari Supabase
            if not df_db.empty:
                df_db["dt_tanggal"] = pd.to_datetime(df_db["tanggal"])
                df_db["Bulan_Dt"] = df_db["dt_tanggal"].dt.to_period("M").dt.to_timestamp()
                df_db_grouped = df_db.groupby(["jenis_dana", "Bulan_Dt"])["realisasi"].sum().reset_index()
                df_db_grouped.columns = ["Jenis_Dana", "Bulan_Dt", "Total_Realisasi"]
            else:
                df_db_grouped = pd.DataFrame(columns=["Jenis_Dana", "Bulan_Dt", "Total_Realisasi"])

            df_master_fc = pd.concat([df_excel_combined, df_db_grouped], ignore_index=True)

            if not df_master_fc.empty:
                df_master_fc["Jenis_Dana"] = df_master_fc["Jenis_Dana"].str.strip()
                kategori_options = ["Total (Overall)"] + sorted(df_master_fc["Jenis_Dana"].unique())

                kategori_forecast = st.selectbox(
                    "Pilih Kategori untuk Proyeksi Peramalan:",
                    options=kategori_options,
                    key="fc_kategori_pilih"
                )

                if kategori_forecast == "Total (Overall)":
                    df_monthly_fc = df_master_fc.groupby("Bulan_Dt")["Total_Realisasi"].sum().reset_index()
                else:
                    df_fc_source = df_master_fc[df_master_fc["Jenis_Dana"] == kategori_forecast].copy()
                    df_monthly_fc = df_fc_source.groupby("Bulan_Dt")["Total_Realisasi"].sum().reset_index()

                df_monthly_fc = df_monthly_fc.sort_values("Bulan_Dt")

                if len(df_monthly_fc) >= 6:
                    try:
                        from statsmodels.tsa.holtwinters import ExponentialSmoothing

                        ts_data = df_monthly_fc.set_index("Bulan_Dt")["Total_Realisasi"].astype(float)
                        ts_data = ts_data.fillna(0)

                        # --- PENGAMAN: BUANG BULAN BERJALAN YANG BELUM SELESAI ---
                        current_year_month = pd.Timestamp(date.today().year, date.today().month, 1)
                        if current_year_month in ts_data.index:
                            ts_data = ts_data.drop(current_year_month)

                        # Cek ulang data setelah dibersihkan
                        st.write("Cek Data Bulanan (Cleaned):", ts_data)

                        # Hitung langkah peramalan (sisa bulan tahun ini + tahun depan)
                        last_date = ts_data.index[-1]
                        next_year = last_date.year + 1
                        end_forecast_date = pd.Timestamp(year=next_year, month=12, day=1)
                        forecast_steps = (end_forecast_date.year - last_date.year) * 12 + (end_forecast_date.month - last_date.month)
                        if forecast_steps < 1:
                            forecast_steps = 12

                        # Baseline minimum untuk mencegah nilai 0
                        active_historical = ts_data[ts_data > 0]
                        fallback_mean = active_historical.mean() if not active_historical.empty else 500000000

                        # --- SISTEM AUTO-MODEL SELECTION ---
                        methods_results = []

                        # 1. Holt-Winters Exponential Smoothing
                        try:
                            hw_model = ExponentialSmoothing(
                                ts_data, trend="add", seasonal="add", 
                                seasonal_periods=12 if len(ts_data) >= 12 else None
                            ).fit()
                            fc_hw = hw_model.forecast(forecast_steps)
                            fc_hw = np.maximum(fc_hw, fallback_mean * 0.3)
                            
                            hw_fitted = hw_model.fittedvalues
                            common_idx = ts_data.index.intersection(hw_fitted.index)
                            resid_hw = ts_data.loc[common_idx] - hw_fitted.loc[common_idx]
                            mae_hw = np.mean(np.abs(resid_hw))
                            rmse_hw = np.sqrt(np.mean(resid_hw**2))
                            
                            methods_results.append({
                                "name": "Holt-Winters Exponential Smoothing",
                                "mae": mae_hw,
                                "rmse": rmse_hw,
                                "forecast": fc_hw
                            })
                        except Exception:
                            pass

                        # 2. Moving Average (3-Month Rolling)
                        try:
                            ma_series = ts_data.rolling(window=3, min_periods=1).mean()
                            last_ma = ma_series.iloc[-1] if not pd.isna(ma_series.iloc[-1]) else fallback_mean
                            if last_ma <= 0:
                                last_ma = fallback_mean
                            fc_ma = np.full(forecast_steps, max(last_ma, fallback_mean * 0.5))
                            
                            resid_ma = ts_data - ts_data.shift(1).fillna(fallback_mean)
                            mae_ma = np.mean(np.abs(resid_ma))
                            rmse_ma = np.sqrt(np.mean(resid_ma**2))
                            
                            methods_results.append({
                                "name": "Moving Average (3-Bulan)",
                                "mae": mae_ma,
                                "rmse": rmse_ma,
                                "forecast": fc_ma
                            })
                        except Exception:
                            pass

                        # 3. Historical Mean Baseline
                        try:
                            fc_base = np.full(forecast_steps, fallback_mean)
                            resid_base = ts_data - fallback_mean
                            mae_base = np.mean(np.abs(resid_base))
                            rmse_base = np.sqrt(np.mean(resid_base**2))
                            
                            methods_results.append({
                                "name": "Historical Mean Baseline",
                                "mae": mae_base,
                                "rmse": rmse_base,
                                "forecast": fc_base
                            })
                        except Exception:
                            pass

                        # Pilih model dengan RMSE terendah
                        if methods_results:
                            best_model = min(methods_results, key=lambda x: x["rmse"])
                            winning_name = best_model["name"]
                            mae = best_model["mae"]
                            rmse = best_model["rmse"]
                            forecast_point = best_model["forecast"]
                        else:
                            winning_name = "Safe Baseline"
                            mae = ts_data.std() if not pd.isna(ts_data.std()) else 10000000
                            rmse = mae
                            forecast_point = np.full(forecast_steps, fallback_mean)

                        # --- PENGAMAN MUTLAK: TIDAK BOLEH ADA NILAI 0 ---
                        forecast_point = np.maximum(forecast_point, fallback_mean * 0.4)

                        # Perhitungan Tingkat Keandalan Model Terbaik
                        mean_actual = active_historical.mean() if not active_historical.empty else 1.0
                        nrmse = (rmse / mean_actual) if mean_actual > 0 else 0.2
                        persentase_error = min(max(nrmse * 100, 3.0), 30.0)
                        tingkat_keandalan = max(70.0, 100.0 - persentase_error)

                        st.success(
                            f"🤖 **Auto-Model Selection:** Untuk kategori **{kategori_forecast}**, sistem otomatis memilih metode **{winning_name}** "
                            f"karena menghasilkan error terendah dan tingkat keandalan paling optimal."
                        )

                        st.markdown("#### 📊 Rangkuman Performa & Keandalan Model")
                        err_col1, err_col2, err_col3 = st.columns(3)
                        
                        err_col1.metric("Rata-rata Meleset", f"Rp {mae:,.0f}".replace(",", "."))
                        err_col2.metric("Tingkat Volatilitas", f"Rp {rmse:,.0f}".replace(",", "."))
                        err_col3.metric("Tingkat Keandalan Model", f"{tingkat_keandalan:.1f}%")

                        st.markdown("<br>", unsafe_allow_html=True)
                        mae_str = f"Rp {mae:,.0f}".replace(",", ".")
                        st.info(
                            f"💡 **Kesimpulan untuk Manajemen:** Model terpilih memiliki tingkat keandalan **{tingkat_keandalan:.1f}%**. "
                            f"Estimasi pergeseran target bulanan berada di kisaran **{mae_str}**. "
                            f"Gunakan **Batas Pengamanan (Pesimis)** pada tabel di bawah sebagai acuan aman penyusunan anggaran."
                        )

                        deviasi_faktor = 0.15

                        future_dates = pd.date_range(start=ts_data.index[-1] + pd.DateOffset(months=1), periods=forecast_steps, freq="ME")

                        df_scenarios = pd.DataFrame({
                            "Bulan Proyeksi": future_dates.strftime("%B %Y"),
                            "Batas Pengamanan (Pesimis)": forecast_point * (1 - deviasi_faktor),
                            "Target Utama (Moderat)": forecast_point,
                            "Potensi Maksimal (Optimis)": forecast_point * (1 + deviasi_faktor)
                        })

                        df_scenarios_display = df_scenarios.copy()
                        for col in ["Batas Pengamanan (Pesimis)", "Target Utama (Moderat)", "Potensi Maksimal (Optimis)"]:
                            df_scenarios_display[col] = df_scenarios_display[col].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(f"#### Matriks Proyeksi Skenario ({forecast_steps} Bulan ke Depan)")
                        st.dataframe(df_scenarios_display, use_container_width=True, hide_index=True)

                        # Plot Grafik Skenario
                        fig_sc = go.Figure()
                        fig_sc.add_trace(go.Scatter(
                            x=df_scenarios["Bulan Proyeksi"], y=df_scenarios["Potensi Maksimal (Optimis)"],
                            mode='lines', name='Potensi Maksimal (Optimis)', line=dict(color='green', dash='dash')
                        ))
                        fig_sc.add_trace(go.Scatter(
                            x=df_scenarios["Bulan Proyeksi"], y=df_scenarios["Target Utama (Moderat)"],
                            mode='lines+markers', name=f'Target Utama ({winning_name})', line=dict(color='#005ba8', width=3)
                        ))
                        fig_sc.add_trace(go.Scatter(
                            x=df_scenarios["Bulan Proyeksi"], y=df_scenarios["Batas Pengamanan (Pesimis)"],
                            mode='lines', name='Batas Pengamanan (Pesimis)', line=dict(color='red', dash='dash')
                        ))

                        fig_sc.update_layout(
                            title=f"Grafik Skenario Proyeksi Penerimaan ({kategori_forecast})",
                            xaxis_title="Periode Bulan",
                            yaxis_title="Estimasi Nominal (Rp)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            hovermode="x unified"
                        )
                        st.plotly_chart(fig_sc, use_container_width=True)

                    except Exception as ex:
                        st.error(f"Gagal memproses model peramalan: {ex}")
                else:
                    st.warning(f"Data historis bulanan untuk kategori ini hanya tersedia {len(df_monthly_fc)} bulan. Minimal 6 bulan diperlukan.")
            else:
                st.info("Belum ada data historis yang tersedia.")

        # ---------------- TAB 4: VIEWER FILE EXCEL ASLI ----------------
        with tab_pimpinan_4:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Viewer Repositori Master Excel")
            selected_kategori_ex = st.selectbox(
                "Pilih Segmentasi Tampilan Sheet Master:",
                ["Total (Overall)", "Kartu Dana (KD)", "SWDKLLJ (SW)", "Denda"],
                key="viewer_excel",
            )

           try:
                sheet_name = f"Historis{viewer_tahun}"
                df_viewer = load_historis_excel(viewer_tahun)

                if not df_viewer.empty:
                    if selected_kategori_ex != "Semua Kategori":
                        df_viewer = df_viewer[df_viewer["Jenis_Dana"].str.strip() == selected_kategori_ex].reset_index(drop=True)
                    
                    st.markdown(f"**Menampilkan data dari sheet: `{sheet_name}`**")
                    st.dataframe(df_viewer, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"Sheet '{sheet_name}' tidak ditemukan atau kosong dalam file Excel.")
                    table_subset.columns = table_subset.iloc[0]
                    table_subset = table_subset.iloc[1:].reset_index(drop=True)
                    st.dataframe(table_subset, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"Baris dalam sheet Excel tidak mencukupi untuk rentang indeks {start_r} sampai {end_r}.")
                    st.dataframe(df_raw, use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(
                    f"Gagal memuat file Excel. Pastikan file 'Penerimaan Sektor UU 34 Tahun 1964.xlsx' ada di direktori yang sama. Detail error: {e}"
                )
