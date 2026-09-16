# -*- coding: utf-8 -*-
"""CSV tabanlı veri saklama ve Excel dışa aktarma."""
import os

import pandas as pd

import survey_schema as S

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILES = {
    "ciftci": os.path.join(DATA_DIR, "ciftci_veri.csv"),
    "bayi": os.path.join(DATA_DIR, "bayi_veri.csv"),
}

# CSV'de saklanan kolonlar (id + zaman damgası dahil)
STORE_COLS = {
    "ciftci": ["kayit_id", "kayit_zamani"] + S.all_columns("ciftci"),
    "bayi": ["kayit_id", "kayit_zamani"] + S.all_columns("bayi"),
}


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_df(kind):
    """Kayıtlı veriyi DataFrame olarak yükler (yoksa boş döner)."""
    path = FILES[kind]
    if not os.path.exists(path):
        return pd.DataFrame(columns=STORE_COLS[kind])
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame(columns=STORE_COLS[kind])
    for c in STORE_COLS[kind]:
        if c not in df.columns:
            df[c] = ""
    return df[STORE_COLS[kind]]


def save_df(kind, df):
    _ensure_dir()
    df[STORE_COLS[kind]].to_csv(FILES[kind], index=False, encoding="utf-8-sig")


def add_record(kind, values: dict):
    """Yeni kayıt ekler ve CSV'ye yazar. Yeni kayıt id'sini döndürür."""
    df = load_df(kind)
    existing = set(df["kayit_id"].astype(str)) if len(df) else set()
    n = len(df) + 1
    while str(n) in existing:
        n += 1
    rid = str(n)
    row = {c: "" for c in STORE_COLS[kind]}
    row["kayit_id"] = rid
    row["kayit_zamani"] = pd.Timestamp.now().strftime("%d.%m.%Y %H:%M")
    for k, v in values.items():
        if k in row:
            row[k] = v
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_df(kind, df)
    return rid


def delete_records(kind, ids):
    df = load_df(kind)
    df = df[~df["kayit_id"].astype(str).isin({str(i) for i in ids})]
    save_df(kind, df)


def update_record(kind, rid, values: dict):
    """Mevcut kaydın alanlarını güncelleyip CSV'ye yazar."""
    df = load_df(kind)
    mask = df["kayit_id"].astype(str) == str(rid)
    if not mask.any():
        return False
    for k, v in values.items():
        if k in df.columns:
            df.loc[mask, k] = v
    save_df(kind, df)
    return True


def get_record(kind, rid):
    df = load_df(kind)
    m = df[df["kayit_id"].astype(str) == str(rid)]
    return m.iloc[0].to_dict() if len(m) else None


def to_excel_bytes():
    """Çiftçi + bayi verilerini iki sayfalı Excel dosyasına çevirir."""
    import io

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for kind, sheet in (("ciftci", "Çiftçi"), ("bayi", "Bayi")):
            df = load_df(kind)
            nice = df.rename(columns=S.label_map(kind))
            nice.to_excel(writer, sheet_name=sheet, index=False)
    return buf.getvalue()
