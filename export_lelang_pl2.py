import sqlite3
import json
from datetime import datetime
import subprocess
import os

DB_NAME = 'lelang-pl2.db'
TABLE_NAME = 'jadwal_lelang'
OUTPUT_FILE = 'data/jadwal_lelang_pl2.json'

# === Ambil semua data dan urutkan ===
def fetch_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f"""
        SELECT pejabat_lelang, tanggal, pemohon
        FROM {TABLE_NAME}
        ORDER BY tanggal DESC, pejabat_lelang ASC
    """)
    rows = c.fetchall()
    conn.close()

    result = {
        "judul": "Jadwal Lelang Oleh Pejabat Lelang Kelas II - SJB",
        "data": []
    }
    for row in rows:
        result["data"].append({
            "pejabat_lelang": row[0],
            "tanggal": row[1],
            "pemohon": row[2]
        })
    return result

# === Simpan ke JSON ===
def save_to_json(data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === Git Push ===
def git_push():
    timestamp = datetime.now().strftime("%a %Y-%m-%d %H:%M:%S")
    commit_msg = f"Update PL2 - {timestamp}"
    try:
        subprocess.run(['git', 'add', OUTPUT_FILE], check=True)
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("[OK] Push berhasil")
    except subprocess.CalledProcessError as e:
        print("[ERROR] Gagal push:", e)

# === Main ===
if __name__ == '__main__':
    data = fetch_data()
    save_to_json(data)
    print(f"[INFO] Export {len(data['data'])} data lelang PL2 ke {OUTPUT_FILE}")
    git_push()
