from telethon import TelegramClient
from telethon.sessions import SQLiteSession
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError
from dotenv import load_dotenv
from colorama import Fore, Style, init  # Pustaka untuk warna
import os
import qrcode_terminal  # Untuk QR code di konsol
from datetime import datetime  # Untuk timestamp

# Inisialisasi colorama
init(autoreset=True)

# Load .env variables
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Membuat folder sessions jika belum ada
session_folder = 'sessions'
os.makedirs(session_folder, exist_ok=True)

# Fungsi untuk mendapatkan waktu saat ini
def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

# Fungsi untuk login dengan QR code
async def login_with_qr(client):
    print(f"{Fore.GREEN}[{get_timestamp()}] Silakan scan QR code di aplikasi Telegram untuk login.{Style.RESET_ALL}")

    # Generate QR code for login
    qr = await client.qr_login()

    # Menampilkan QR code di terminal
    qrcode_terminal.draw(qr.url)

    # Menunggu login selesai atau dibatalkan
    try:
        await qr.wait()
        print(f"{Fore.GREEN}[{get_timestamp()}] Login berhasil melalui QR code.{Style.RESET_ALL}")
    except SessionPasswordNeededError:
        print(f"{Fore.YELLOW}[{get_timestamp()}] Diperlukan verifikasi dua langkah.{Style.RESET_ALL}")
        password = input(f"{Fore.YELLOW}[{get_timestamp()}] Masukkan kata sandi dua langkah: {Style.RESET_ALL}")
        try:
            await client.sign_in(password=password)
            print(f"{Fore.GREEN}[{get_timestamp()}] Login berhasil dengan verifikasi dua langkah.{Style.RESET_ALL}")
        except PasswordHashInvalidError:
            print(f"{Fore.RED}[{get_timestamp()}] Kata sandi salah.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[{get_timestamp()}] Terjadi kesalahan saat login melalui QR code: {str(e)}{Style.RESET_ALL}")

# Fungsi utama untuk mengatur sesi dan memilih metode login
async def main():
    login_option = input(f"{Fore.CYAN}[{get_timestamp()}] Ingin login dengan QR code atau nomor telepon? (ketik 'qr' untuk QR code, atau 'phone' untuk nomor telepon): {Style.RESET_ALL}").strip().lower()

    session_name = ""
    while not session_name.strip():
        session_name = input(f"{Fore.CYAN}[{get_timestamp()}] Masukkan nama sesi (tanpa ekstensi .session): {Style.RESET_ALL}").strip()

    session_path = os.path.join(session_folder, f"{session_name}.session")

    # Meminta input baru jika user memilih untuk tidak mengganti sesi
    while os.path.exists(session_path):
        use_existing = input(f"{Fore.YELLOW}[{get_timestamp()}] Sesi '{session_name}' sudah ada. Ingin menimpa sesi ini? (y/n): {Style.RESET_ALL}").lower()
        if use_existing == 'y':
            os.remove(session_path)
            print(f"{Fore.GREEN}[{get_timestamp()}] Sesi '{session_name}' diganti.{Style.RESET_ALL}")
            break  # Lanjut ke proses login setelah sesi lama dihapus
        else:
            session_name = input(f"{Fore.CYAN}[{get_timestamp()}] Masukkan nama sesi baru (tanpa ekstensi .session): {Style.RESET_ALL}").strip()
            session_path = os.path.join(session_folder, f"{session_name}.session")

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
        client = TelegramClient('my_session', api_id, api_hash)
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print(f"{Fore.RED}[{get_timestamp()}] Program dihentikan oleh pengguna.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[{get_timestamp()}] Terjadi kesalahan: {str(e)}{Style.RESET_ALL}")
