from telethon import TelegramClient
from telethon.sessions import SQLiteSession
import os

# Ganti dengan API ID dan API Hash dari Telegram Anda
api_id = '28343568'
api_hash = '29cbfe0d8713abefb82c9a016a3bb3db'

# Membuat folder sessions jika belum ada
session_folder = 'sessions'
os.makedirs(session_folder, exist_ok=True)

# Meminta pengguna untuk memasukkan nama sesi kustom
session_name = input("Masukkan nama sesi (tanpa ekstensi .session): ")

# Nama sesi
session_path = os.path.join(session_folder, f"{session_name}.session")
session = SQLiteSession(session_path)

# Membuat client Telethon
client = TelegramClient(
    session=session,
    api_id=api_id,
    api_hash=api_hash,
    device_model="Poco Phone",      # Custom device model
    system_version="Telegram Android",                # Custom system version
    app_version="11.0.0"                     # Custom app version
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
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
