from telethon import TelegramClient
from telethon.sessions import SQLiteSession
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Membuat folder sessions jika belum ada
session_folder = 'sessions'
os.makedirs(session_folder, exist_ok=True)

# Meminta pengguna untuk memasukkan nama sesi kustom dengan validasi
session_name = ""
while not session_name.strip():
    session_name = input("Masukkan nama sesi (tanpa ekstensi .session): ").strip()

# Nama sesi
session_path = os.path.join(session_folder, f"{session_name}.session")

# Memeriksa apakah sesi sudah ada
if os.path.exists(session_path):
    use_existing = input(f"Sesi '{session_name}' sudah ada. Ingin menggunakan sesi ini? (y/n): ").lower()
    if use_existing != 'y':
        print("Membatalkan operasi.")
        exit()

# Membuat sesi
session = SQLiteSession(session_path)

# Membuat client Telethon
client = TelegramClient(
    session=session,
    api_id=api_id,
    api_hash=api_hash,
    device_model="ROG Phone 8",      # Custom device model
    system_version="Android",  # Custom system version
    app_version="11.0.0"  # Custom app version
)

# Fungsi utama untuk koneksi
async def main():
    await client.start()

    # Tampilkan nama pengguna yang sudah login
    me = await client.get_me()
    print(f'Anda sudah login sebagai {me.first_name}')

# Menjalankan client dengan penanganan kesalahan
if __name__ == "__main__":
    try:
        with client:
            client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Program dihentikan oleh pengguna.")
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
