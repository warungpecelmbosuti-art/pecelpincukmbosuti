import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# 1. KONEKSI KE GOOGLE SHEETS "Warung Pecel Pincuk Mbo Suti"
def koneksi_sheets(nama_sheet):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("Data.json", scope)
    client = gspread.authorize(creds)
    # Membuka spreadsheet berdasarkan nama baru yang Anda minta
    return client.open("Warung Pecel Pincuk Mbo Suti").worksheet(nama_sheet)

try:
    sheet_menu = koneksi_sheets("Master_Menu")
    sheet_transaksi = koneksi_sheets("Transaksi_Detail")
    sheet_pengeluaran = koneksi_sheets("Pengeluaran")
except Exception as e:
    st.error(f"Gagal koneksi ke Google Sheets. Pastikan 'Data.json' berada di folder yang sama. Error: {e}")

# 2. PENGATURAN TAMPILAN UTAMA (RESPONSIF MOBILE)
st.set_page_config(page_title="POS Pecel Pincuk Mbo Suti", layout="centered")

st.sidebar.title("Mbo Suti Apps")
menu_navigasi = st.sidebar.radio("Pilih Menu:", ["🛒 Kasir (Input Pendapatan)", "💸 Input Pengeluaran", "📊 Dashboard Analitik"])

# =========================================================
# HALAMAN 1: KASIR (INPUT ORDER / PENDAPATAN)
# =========================================================
if menu_navigasi == "🛒 Kasir (Input Pendapatan)":
    st.title("🏪 Kasir Pecel Pincuk Mbo Suti")
    st.write("Catat pesanan pelanggan di bawah ini:")
    st.divider()
    
    df_menu = pd.DataFrame(sheet_menu.get_all_records())
    
    if df_menu.empty:
        st.warning("Data Master_Menu masih kosong di Google Sheets Anda.")
    else:
        df_menu['Pilihan_Tampilan'] = df_menu['Nama_Menu'] + " (" + df_menu['Satuan'] + ")"
        
        with st.form("form_order", clear_on_submit=True):
            pilihan = st.selectbox("Pilih Menu & Satuan:", df_menu['Pilihan_Tampilan'].tolist())
            jumlah = st.number_input("Jumlah Beli:", min_value=1, step=1, value=1)
            metode = st.selectbox("Metode Pembayaran:", ["Tunai", "QRIS", "Transfer"])
            
            detail_menu = df_menu[df_menu['Pilihan_Tampilan'] == pilihan].iloc[0]
            id_menu = detail_menu['ID_Menu']
            nama_menu = detail_menu['Nama_Menu']
            satuan = detail_menu['Satuan']
            harga_jual = int(detail_menu['Harga_Jual'])
            total_bayar = harga_jual * jumlah
            
            st.info(f"💰 Total yang harus dibayar: **Rp {total_bayar:,}**")
            tombol_order = st.form_submit_button("Simpan Transaksi Ke Cloud")
            
        if tombol_order:
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            id_transaksi = "TRX-" + datetime.now().strftime("%d%m%y%H%M%S")
            
            data_baru = [id_transaksi, waktu_sekarang, id_menu, nama_menu, satuan, jumlah, harga_jual, total_bayar, metode]
            sheet_transaksi.append_row(data_baru)
            st.success(f"✅ Sukses! Pendapatan tercatat: {nama_menu} - {jumlah} {satuan} (Rp {total_bayar:,})")

# =========================================================
# HALAMAN 2: INPUT PENGELUARAN MANUAL VIA APLIKASI
# =========================================================
elif menu_navigasi == "💸 Input Pengeluaran":
    st.title("💸 Catat Pengeluaran Warung")
    st.write("Masukkan biaya operasional atau belanja bahan baku di sini:")
    st.divider()
    
    with st.form("form_pengeluaran", clear_on_submit=True):
        kat_pengeluaran = st.selectbox("Kategori Pengeluaran:", ["Belanja Bahan Baku", "Gaji Karyawan", "Listrik & Air", "Sewa Tempat", "Lain-lain"])
        keterangan = st.text_input("Keterangan Detail (Contoh: Beli bumbu kacang pecel):")
        total_biaya = st.number_input("Total Biaya (Rp):", min_value=500, step=500)
        
        tom