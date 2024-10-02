import asyncio
from telethon import TelegramClient
from telethon.sessions import SQLiteSession
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError
from dotenv import load_dotenv, set_key
from colorama import Fore, Style, init  # Pustaka untuk warna
import os
import qrcode_terminal  # Untuk QR code di konsol
from datetime import datetime  # Untuk timestamp

# Inisialisasi colorama
init(autoreset=True)

# Load .env variables
load_dotenv()

# Fungsi untuk mendapatkan waktu saat ini
def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Fungsi untuk menyimpan api_id dan api_hash ke dalam .env
def save_api_credentials(api_id, api_hash):
    with open('.env', 'a') as f:
        f.write(f'API_ID={api_id}\n')
        f.write(f'API_HASH={api_hash}\n')

# Fungsi untuk mendapatkan api_id dan api_hash
def get_api_credentials():
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')

    if not api_id or not api_hash:
        print(f"{Fore.YELLOW}[{get_timestamp()}] API credentials are missing, please input them manually.")
        api_id = input(f"{Fore.YELLOW}[{get_timestamp()}] Enter your API ID: {Style.RESET_ALL}")
        api_hash = input(f"{Fore.YELLOW}[{get_timestamp()}] Enter your API Hash: {Style.RESET_ALL}")
        
        # Simpan kredensial ke .env
        save_api_credentials(api_id, api_hash)

    return int(api_id), api_hash

# Fungsi untuk login dengan nomor telepon
async def login_with_phone(client):
    try:
        phone_number = input(f"{Fore.YELLOW}[{get_timestamp()}] Masukkan nomor telepon (format internasional): {Style.RESET_ALL}")
        await client.send_code_request(phone_number)
        code = input(f"{Fore.YELLOW}[{get_timestamp()}] Masukkan kode verifikasi yang dikirim ke nomor telepon: {Style.RESET_ALL}")
        await client.sign_in(phone_number, code)

        # Jika two-step verification diaktifkan
        if not client.is_user_authorized():
            print(f"{Fore.YELLOW}[{get_timestamp()}] Diperlukan verifikasi dua langkah.{Style.RESET_ALL}")
            password = input(f"{Fore.YELLOW}[{get_timestamp()}] Masukkan kata sandi dua langkah: {Style.RESET_ALL}")
            await client.sign_in(password=password)
        
    except Exception as e:
        print(f"{Fore.RED}[{get_timestamp()}] Terjadi kesalahan: {str(e)}{Style.RESET_ALL}")

async def login_with_qr(client):
    while True:  # Loop untuk otomatis refresh QR code jika expired
        try:
            print(f"{Fore.GREEN}[{get_timestamp()}] Silakan scan QR code di aplikasi Telegram untuk login.{Style.RESET_ALL}")

            # Generate QR code for login
            qr = await client.qr_login()

            # Menampilkan QR code di terminal
            qrcode_terminal.draw(qr.url)

            # Menunggu login selesai atau dibatalkan
            await qr.wait()  # Menunggu hingga pengguna melakukan scan atau membatalkan

            # Cek jika sudah terautorisasi
            if await client.is_user_authorized():
                print(f"{Fore.GREEN}[{get_timestamp()}] Login berhasil melalui QR code.{Style.RESET_ALL}")
                break  # Keluar dari loop jika login berhasil
            else:
                print(f"{Fore.YELLOW}[{get_timestamp()}] Login belum berhasil, coba scan lagi.{Style.RESET_ALL}")

        except Exception as e:
            # Cek jika QR code expired atau kesalahan lain
            if "QR code expired" in str(e):
                print(f"{Fore.YELLOW}[{get_timestamp()}] QR code expired, menghasilkan QR code baru...{Style.RESET_ALL}")
                continue  # Kembali ke awal loop untuk menghasilkan QR code baru
            elif isinstance(e, SessionPasswordNeededError):
                print(f"{Fore.YELLOW}[{get_timestamp()}] Diperlukan verifikasi dua langkah.{Style.RESET_ALL}")
                password = input(f"{Fore.YELLOW}[{get_timestamp()}] Masukkan kata sandi dua langkah: {Style.RESET_ALL}")
                try:
                    await client.sign_in(password=password)
                    print(f"{Fore.GREEN}[{get_timestamp()}] Login berhasil dengan verifikasi dua langkah.{Style.RESET_ALL}")
                    break  # Keluar dari loop jika login berhasil
                except PasswordHashInvalidError:
                    print(f"{Fore.RED}[{get_timestamp()}] Kata sandi salah.{Style.RESET_ALL}")
                    break  # Keluar dari loop jika kata sandi salah
            else:
                print(f"{Fore.RED}[{get_timestamp()}] Terjadi kesalahan saat login melalui QR code: {str(e)}{Style.RESET_ALL}")
                # Jika kesalahan yang tidak terduga, coba lagi
                print(f"{Fore.YELLOW}[{get_timestamp()}] Menghasilkan QR code baru...{Style.RESET_ALL}")
                continue  # Coba lagi untuk menghasilkan QR code baru

# Fungsi utama untuk mengatur sesi dan memilih metode login
async def main():
    # Mendapatkan api_id dan api_hash dari .env atau input user
    api_id, api_hash = get_api_credentials()

    # Membuat folder sessions jika belum ada
    session_folder = 'sessions'
    os.makedirs(session_folder, exist_ok=True)  # Pastikan folder dapat dibuat

    # Pertanyaan pertama: QR atau nomor telepon
    login_option = input(f"{Fore.CYAN}[{get_timestamp()}] Ingin login dengan QR code atau nomor telepon? (ketik 'qr' untuk QR code, atau 'phone' untuk nomor telepon): {Style.RESET_ALL}").strip().lower()

    # Meminta pengguna untuk memasukkan nama sesi setelah memilih metode login
    session_name = ""
    while not session_name.strip():
        session_name = input(f"{Fore.CYAN}[{get_timestamp()}] Masukkan nama sesi (tanpa ekstensi .session): {Style.RESET_ALL}").strip()

    # Nama sesi
    session_path = os.path.abspath(os.path.join(session_folder, f"{session_name}.session"))  # Jalur absolut

    # Memeriksa apakah sesi sudah ada
    if os.path.exists(session_path):
        use_existing = input(f"{Fore.YELLOW}[{get_timestamp()}] Sesi '{session_name}' sudah ada. Ingin menggunakan sesi ini? (y/n): {Style.RESET_ALL}").lower()
        if use_existing != 'y':
            print(f"{Fore.RED}[{get_timestamp()}] Membatalkan operasi.{Style.RESET_ALL}")
            return

    # Membuat sesi dan client Telethon
    session = SQLiteSession(session_path)
    client = TelegramClient(
        session=session,
        api_id=api_id,
        api_hash=api_hash,
        device_model="ROG Phone 8",  # Custom device model
        system_version="Android",    # Custom system version
        app_version="11.0.0"         # Custom app version
    )

    await client.connect()

    # Memeriksa apakah sudah login
    if not await client.is_user_authorized():
        if login_option == 'qr':
            await login_with_qr(client)  # Login menggunakan QR code
        elif login_option == 'phone':
            await login_with_phone(client)  # Login menggunakan nomor telepon
        else:
            print(f"{Fore.RED}[{get_timestamp()}] Pilihan tidak valid, harap masukkan 'qr' atau 'phone'.{Style.RESET_ALL}")
            return

    # Tampilkan nama pengguna yang sudah login
    me = await client.get_me()
    print(f"{Fore.GREEN}[{get_timestamp()}] Anda sudah login sebagai {me.first_name}{Style.RESET_ALL}")

# Menjalankan client dengan penanganan kesalahan
if __name__ == "__main__":    
    try:
        # Menggunakan asyncio.run() untuk menjalankan fungsi main
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"{Fore.RED}[{get_timestamp()}] Program dihentikan oleh pengguna.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[{get_timestamp()}] Terjadi kesalahan: {str(e)}{Style.RESET_ALL}")
