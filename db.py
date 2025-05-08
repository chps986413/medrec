# db.py
import sqlite3
from pathlib import Path

# 調整此路徑至你的 Google Drive 同步資料夾
DB_PATH = Path.home() / "Google Drive" / "medrec" / "med_records.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS meds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            med_id  INTEGER NOT NULL,
            date    TEXT    NOT NULL,
            dosage  TEXT,
            FOREIGN KEY(med_id) REFERENCES meds(id)
        )
        """
    )
    conn.commit()
    conn.close()


def add_med(name):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO meds(name) VALUES(?)", (name,))
    conn.commit()
    conn.close()


def remove_med(name):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM meds WHERE name=?", (name,))
    conn.commit()
    conn.close()


def get_meds():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name FROM meds ORDER BY name")
    meds = [r[0] for r in c.fetchall()]
    conn.close()
    return meds


def add_entry(med_name, date, dosage):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM meds WHERE name=?", (med_name,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"找不到藥物 {med_name}")
    med_id = row[0]
    c.execute(
        "INSERT INTO entries(med_id,date,dosage) VALUES(?,?,?)",
        (med_id, date, dosage)
    )
    conn.commit()
    conn.close()


def delete_entry(entry_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()


def update_entry(entry_id, new_dt_iso, new_dosage):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE entries SET date=?, dosage=? WHERE id=?",
        (new_dt_iso, new_dosage, entry_id)
    )
    conn.commit()
    conn.close()


def get_all_entries_df():
    import pandas as pd
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT
          e.id     AS id,
          e.date   AS date,
          e.dosage AS dosage,
          m.name   AS name
        FROM entries e
        JOIN meds m ON e.med_id = m.id
        ORDER BY date
        """,
        conn
    )
    conn.close()

    if not df.empty:
        # 嘗試 parse，parse 失敗轉成 NaT
        df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
        bad = df[df['date_parsed'].isna()]
        if not bad.empty:
            print("Unparseable dates:", bad['date'].tolist())
            df = df[df['date_parsed'].notna()]
        df['date'] = df['date_parsed']
        df = df.drop(columns=['date_parsed'])
    return df

# 啟動時自動建立資料庫與表格
init_db()