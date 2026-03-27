# cara run: streamlit run kospinus_umi.py

import streamlit as st
import pandas as pd
import json
import os

from streamlit_lottie import st_lottie


# --- INITIAL SETUP ---
st.set_page_config(page_title="Kospinus UMI - Decision Support System", layout="wide")

# --- CUSTOM CSS (BIRU - GOLD - HIJAU) ---
st.markdown("""
    <style>
    .main { background-color: #f1f5f9; }
    .report-card { 
        background-color: #ffffff; padding: 25px; border-radius: 15px; 
        border-left: 10px solid #0056b3; /* Biru Premium */
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #0056b3; color: white; border-radius: 10px;
        font-weight: bold; height: 3em; width: 100%;
    }
    .stMetric {
        background: white; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Animasi Pulse Watermark */
    @keyframes pulse { 0% {opacity: 0.5;} 50% {opacity: 0.8;} 100% {opacity: 0.5;} }
    .footer-watermark {
        position: fixed; bottom: 10px; right: 20px; color: #0056b3;
        font-weight: bold; opacity: 0.5; animation: pulse 3s infinite;
    }
            
            /* Styling Badge Kategori */
    .badge-cat {
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        color: white;
        font-size: 0.9rem;
    }
    .bg-umi { background-color: #0056b3; } /* Biru */
    .bg-cbi { background-color: #eab308; } /* Gold */
    
    /* Card DSR Khusus */
    .dsr-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #0056b3;
        margin-top: 10px;
    }
    .stTable { border-radius: 5px; overflow: hidden; border: 1px solid #334155; }
    .stTable th { background-color: #334155 !important; color: #e2e8f0 !important; text-transform: uppercase; }

    /* 5. REVISI: Tooltip agar selalu di atas dan berwarna Gold OJK */
    .stTooltipIcon {
        color: #eab308 !important;
        margin-bottom: 5px;
    
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_lottie_local(path):
    if os.path.exists(path):
        with open(path, "r") as f: return json.load(f)
    return None

def format_rp(val):
    return f"Rp {val:,.0f}".replace(",", ".")

def st_animated_subheader(lottie_path, text, height=60, key="anim"):
    lottie_data = load_lottie_local(lottie_path)
    col_a, col_t = st.columns([0.15, 2])
    with col_a:
        if lottie_data: st_lottie(lottie_data, height=height, key=key)
        else: st.write("🔍")
    with col_t:
        st.markdown(f"<h3 style='margin-top:10px; color:#1e293b;'>{text}</h3>", unsafe_allow_html=True)

# --- PINDAHKAN KE AREA HELPER FUNCTIONS (DI ATAS) ---

def get_pt_wt(group, value):
    """Fungsi Global untuk mengambil Poin dan Bobot dari Master JSON"""
    if not MASTER or 'scoring_rules' not in MASTER:
        return 0, 0
        
    rules = MASTER['scoring_rules'].get(group, [])
    for r in rules:
        if 'min' in r: # Logic untuk data angka/range (DSR, Usia, Tinggal)
            if r['min'] <= value <= r['max']: 
                return r['point'], r['weight']
        else: # Logic untuk data teks/pilihan (Rumah, Listrik, Nikah)
            if str(r['desc']) == str(value): 
                return r['point'], r['weight']
    return 0, 0

def lookup_ui_point(group, val):
    """Fungsi bantu untuk menampilkan poin di label UI secara real-time"""
    p, _ = get_pt_wt(group, val)
    return p

# --- LOAD MASTER DATA ---
MASTER = load_json('master_kospinus.json')
if not MASTER:
    st.error("File 'master_kospinus.json' tidak ditemukan! Pastikan file tersebut ada di folder yang sama.")
    st.stop()

# --- SIDEBAR: KONFIGURASI KEBIJAKAN ---
st.sidebar.header("⚙️ Konfigurasi Kebijakan")
PARAM_FIELDS = {
    'p_sekolah': 'Biaya Sekolah', 'p_transport': 'Transportasi',
    'p_listrik': 'Listrik', 'p_telepon': 'Telepon',
    'p_hutang': 'Hutang SLIK', 'p_arisan': 'Arisan'
}

with st.sidebar.expander("📊 Parameter DSR (Kapasitas)"):
    selected_dsr = st.multiselect("Beban masuk DSR:", list(PARAM_FIELDS.keys()), default=['p_hutang'])
    st.caption("Pilih biaya yang akan diperhitungkan dalam cicilan bulanan.")

cbi_score_input = st.sidebar.number_input("CBI Score (External)", 0, 1000, 450)

# --- HEADER SECTION (FIX ERROR IMAGE) ---
header_col1, header_col2 = st.columns([0.4, 2])

with header_col1:
    lottie_logo = load_lottie_local("kCredit.json")
    if lottie_logo:
        st_lottie(lottie_logo, height=150, key="logo_header")
    elif os.path.exists("logo_kospinus.png"):
        # HANYA panggil st.image jika filenya benar-benar ADA
        st.image("logo_kospinus.png", width=180)
    else:
        # Jika keduanya tidak ada, tampilkan logo placeholder teks agar tidak error
        st.markdown("<div style='padding:20px; background:#0056b3; color:white; border-radius:10px; text-align:center;'><b>KOSPINUS LOGO</b></div>", unsafe_allow_html=True)

# with header_col2:
#     st.markdown("<h1 style='color: #0056b3; margin-bottom:0;'>KOSPINUS UMI</h1>", unsafe_allow_html=True)
#     st.markdown("<p style='font-size:1.2rem; color:#64748b;'>Sistem Analisa Risiko & Putusan Kredit Mikro</p>", unsafe_allow_html=True)
# st.divider()

with header_col2:
    st.markdown("""
        <div style='margin-left: 10px;'>
            <h1 style='margin-top: 0; margin-bottom: 5px; color: #0056b3 !important; font-size: 2rem;'>KOSPINUS UMI</h1>
            <p style='color: #64748b !important; font-size: 1.1rem; margin: 0;'>Sistem Verifikasi Scoring & Audit Risiko Kredit</p>
            <hr style='margin: 10px 0; border: none; height: 2px; background: linear-gradient(to right, #0056b3, #f4f7f9);'>
        </div>
    """, unsafe_allow_html=True)


# --- PILAR 1: FATAL SCORE ---
# st_animated_subheader("Ai_Robot.json", "Fatal Score Check (SLIK)", key="slik_anim")

st.divider()
# Opsi 1: Menggunakan markdown agar warna teks tetap #1e293b (Sesuai desain awal)
st.markdown("<h3 style='color: #1e293b;'>Fatal Score Check (SLIK)</h3>", unsafe_allow_html=True)

cf1, cf2 = st.columns(2)
val_dpd = cf1.number_input("Maksimal DPD (Hari)", 0, 2000, 0)
val_tunggakan = cf2.number_input("Total Tunggakan Aktif (Rp)", 0, 50000000, 0, step=1000000)

# Logika Fatal dari Master JSON
is_fatal = (val_dpd >= MASTER['fatal_score_config']['max_dpd'] or 
            val_tunggakan >= MASTER['fatal_score_config']['max_tunggakan'])

if is_fatal:
    st.error(f"⚠️ STATUS: REJECT ({MASTER['fatal_score_config']['action']})")
else:
    st.success("✅ STATUS: LOLOS (Checking SLIK dalam batas aman)")

# --- PILAR 2: KAPASITAS & PROFIL ---
st.divider()
# Opsi 1: Menggunakan markdown agar warna teks tetap #1e293b (Sesuai desain awal)
st.markdown("<h3 style='color: #1e293b;'>Analisa Kapasitas & Profiling</h3>", unsafe_allow_html=True)

# st.divider()
# st_animated_subheader("Thinking.json", "Analisa Kapasitas & Profiling", key="cap_anim")


# Helper internal untuk cari poin cepat buat tampilan UI
def lookup_ui_point(group, val):
    p, _ = get_pt_wt(group, val)
    return p

# --- ANALISA PROFIL NASABAH ---
# col1, col2 = st.columns(2)
# with col1:
#     listrik_val = st.selectbox("Daya Listrik", [r['desc'] for r in MASTER['scoring_rules']['daya_listrik']])
#     st.caption(f"Poin: **{lookup_ui_point('daya_listrik', listrik_val)}**")
    
#     rumah_val = st.selectbox("Kepemilikan Rumah", [r['desc'] for r in MASTER['scoring_rules']['kepemilikan_rumah']])
#     st.caption(f"Poin: **{lookup_ui_point('kepemilikan_rumah', rumah_val)}**")
    
#     usia_val = st.number_input("Usia Nasabah", 18, 90, 35)
#     st.caption(f"Poin: **{lookup_ui_point('usia', usia_val)}**")

# with col2:
#     nikah_val = st.selectbox("Status Pernikahan", [r['desc'] for r in MASTER['scoring_rules']['status_pernikahan']])
#     st.caption(f"Poin: **{lookup_ui_point('status_pernikahan', nikah_val)}**")
    
#     tinggal_val = st.number_input("Lama Tinggal (Tahun)", 0.0, 50.0, 5.0)
#     st.caption(f"Poin: **{lookup_ui_point('lama_tinggal', tinggal_val)}**")
    
#     # DSR diambil dari Sidebar/Default (Karena Kospinus UMI seringkali DSR sudah dipretally)
#     st.info(f"DSR Score dihitung otomatis dari kebijakan.")

# --- PILAR 2: KAPASITAS & PROFIL ---
col1, col2 = st.columns(2)
with col1:
    # --- INPUT KEUANGAN UNTUK DSR ---
    income = st.number_input("Total Pendapatan Perbulan", value=5000000)
    
    # Ambil rincian biaya dari sidebar yang sudah dipilih user
    exp_vals = {}
    st.write("---")
    st.caption("Rincian Pengeluaran (Beban):")
    for k, label in PARAM_FIELDS.items():
        exp_vals[k] = st.number_input(label, value=0, key=f"in_{k}")
    
    angs_umi = st.number_input("Rencana Angsuran UMI Baru", value=500000)

with col2:
    # HITUNG DSR AKTUAL (LOGIKA EXCEL)
    total_beban = sum(exp_vals[k] for k in selected_dsr) + angs_umi
    dsr_calc = round((total_beban / income * 100), 2) if income > 0 else 0
    
    # --- TAMPILAN DSR CARD DENGAN TOOLTIP ---
    # 1. Ambil Poin DSR secara real-time menggunakan fungsi global kita
    p_dsr, _ = get_pt_wt('dsr', dsr_calc)
    
    # 2. Tampilkan Card dengan tambahan informasi Poin
    st.markdown(f"""
        <div class="dsr-card">
            <p style='margin:0; color:#64748b; font-size:0.8rem;'>HASIL ANALISA KAPASITAS:</p>
            <h2 style='margin:0; color:#1e293b;'>DSR: {dsr_calc}%</h2>
            <div style='margin-top: 8px; padding-top: 8px; border-top: 1px solid #cbd5e1;'>
                <span style='color:#64748b; font-size:0.9rem;'>Poin Berdasarkan Master:</span>
                <span style='color:#0056b3; font-size:1.2rem; font-weight:bold; margin-left:10px;'>{p_dsr}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3. Tooltip tetap dipertahankan untuk transparansi rumus
    st.caption("ℹ️ Tooltip: Rumus DSR = (Total Beban Terpilih + Angsuran Baru) / Pendapatan * 100", 
               help=f"Perhitungan: ({format_rp(sum(exp_vals[k] for k in selected_dsr))} + {format_rp(angs_umi)}) / {format_rp(income)}")
    
    st.write("---")
    # Dropdown Profiling Sisanya
    listrik_val = st.selectbox("Daya Listrik", [r['desc'] for r in MASTER['scoring_rules']['daya_listrik']])
    st.caption(f"Poin: **{lookup_ui_point('daya_listrik', listrik_val)}**")
    
    rumah_val = st.selectbox("Kepemilikan Rumah", [r['desc'] for r in MASTER['scoring_rules']['kepemilikan_rumah']])
    st.caption(f"Poin: **{lookup_ui_point('kepemilikan_rumah', rumah_val)}**")
    
    usia_val = st.number_input("Usia Nasabah", 18, 90, 35)
    st.caption(f"Poin: **{lookup_ui_point('usia', usia_val)}**")

    nikah_val = st.selectbox("Status Pernikahan", [r['desc'] for r in MASTER['scoring_rules']['status_pernikahan']])
    st.caption(f"Poin: **{lookup_ui_point('status_pernikahan', nikah_val)}**")
    
    tinggal_val = st.number_input("Lama Tinggal (Tahun)", 0.0, 50.0, 5.0)
    st.caption(f"Poin: **{lookup_ui_point('lama_tinggal', tinggal_val)}**")


# --- PROSES SCORING ---

if st.button("RUN SCORING KOSPINUS", type="primary"):
    # 1. FIX: Gunakan dsr_calc, bukan angka 25
    p1, w1 = get_pt_wt('dsr', dsr_calc) 
    p2, w2 = get_pt_wt('kepemilikan_rumah', rumah_val)
    p3, w3 = get_pt_wt('daya_listrik', listrik_val)
    p4, w4 = get_pt_wt('usia', usia_val)
    p5, w5 = get_pt_wt('status_pernikahan', nikah_val)
    p6, w6 = get_pt_wt('lama_tinggal', tinggal_val)

    total_score = (p1*w1 + p2*w2 + p3*w3 + p4*w4 + p5*w5 + p6*w6) * 100
    
    # 2. Tentukan Kategori UMI & CBI
    u_cat = "1"; c_cat = "1"
    for r in MASTER['category_ranges']['umi']:
        if r['min'] <= total_score <= r['max']: u_cat = r['cat']
    for r in MASTER['category_ranges']['cbi']:
        if r['min'] <= cbi_score_input <= r['max']: c_cat = r['cat']

    # 3. LOGIKA KEPUTUSAN (REVISI: CEK FATAL SCORE DULU)
    if is_fatal:
        decision = "REJECTED (Fatal Score)"
        color = "#ef4444" # Merah
    else:
        decision = MASTER['matrix_approval'][u_cat][c_cat]
        color = "#22c55e" if "Approve 1" in decision else ("#eab308" if "Approve 2" in decision else "#ef4444")

    # --- OUTPUT DISPLAY ---
    st.divider()
    res_l, res_r = st.columns([1, 2])
    with res_l:
        # Animasi berubah jadi Warning jika is_fatal
        path_anim = "Warning.json" if (is_fatal or "Reject" in decision) else "Success.json"
        l_res = load_lottie_local(path_anim)
        if l_res: st_lottie(l_res, height=250)

    with res_r:
        st.markdown(f"""
            <div class="report-card" style="border-left-color: {color};">
                <p style='margin:0; color:#64748b; font-weight:bold;'>HASIL PUTUSAN FINAL:</p>
                <h1 style='color: {color}; font-size: 3rem; margin:10px 0;'>{decision}</h1>
                <hr>
                <div style='display: flex; gap: 10px; margin-top:15px;'>
                    <span class="badge-cat bg-umi">UMI: Kat {u_cat}</span>
                    <span class="badge-cat bg-cbi">CBI: Kat {c_cat}</span>
                </div>
                <p style='margin-top:10px; font-size:0.9rem; color:#1e293b;'>
                    Skor Internal: <b>{round(total_score, 0)}</b> | Skor Eksternal: <b>{cbi_score_input}</b>
                </p>
                {"<p style='color:#ef4444; font-weight:bold;'>⚠️ REJECT KARENA MELEBIHI BATAS DPD/TUNGGAKAN</p>" if is_fatal else ""}
            </div>
        """, unsafe_allow_html=True)

  
    # Tabel Rincian dengan pembulatan 2 desimal dan format :g (menghilangkan nol mubazir)
    df_det = pd.DataFrame([
        {"Parameter": "Daya Listrik", "Poin": p3, "Skor Final": f"{round(p3*w3*100, 2):g}"},
        {"Parameter": "Kepemilikan Rumah", "Poin": p2, "Skor Final": f"{round(p2*w2*100, 2):g}"},
        {"Parameter": "Usia Nasabah", "Poin": p4, "Skor Final": f"{round(p4*w4*100, 2):g}"},
        {"Parameter": "Status Pernikahan", "Poin": p5, "Skor Final": f"{round(p5*w5*100, 2):g}"},
        {"Parameter": "Lama Tinggal", "Poin": p6, "Skor Final": f"{round(p6*w6*100, 2):g}"},
        {"Parameter": "DSR (Policy Check)", "Poin": p1, "Skor Final": f"{round(p1*w1*100, 2):g}"},
    ])
    
    st.table(df_det)

st.markdown("<div class='footer-watermark'>Kospinus UMI Scoring v1.0 © M.Suparman</div>", unsafe_allow_html=True)
