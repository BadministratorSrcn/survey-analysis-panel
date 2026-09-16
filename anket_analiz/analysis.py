# -*- coding: utf-8 -*-
"""İstatistiksel analiz fonksiyonları: kişi sayısı (frekans), ki-kare, ANOVA/Kruskal-Wallis,
korelasyon, Cronbach alfa ve Likert ölçek puanları."""
import numpy as np
import pandas as pd
from scipy import stats

import survey_schema as S


def _as_float(series):
    return pd.to_numeric(series, errors="coerce")


# ---------------------------------------------------------------- frekans
def frequency_table(df, col, kind, order=None):
    """Tek kategorik değişken için kişi sayısı + yüzde tablosu."""
    if col not in df.columns:
        return pd.DataFrame()
    s = df[col].astype(str).str.strip()
    s = s[s != ""] if not S.is_likert(kind, col) else s[s != ""]
    vc = s.value_counts()
    if order:
        vc = vc.reindex([o for o in order if o in vc.index]).dropna()
    tab = pd.DataFrame({"Kişi Sayısı": vc.astype(int)})
    tab["Yüzde (%)"] = (tab["Kişi Sayısı"] / tab["Kişi Sayısı"].sum() * 100).round(1)
    return tab


def explode_multi(df, col, kind):
    """Çoklu seçim kolonunu (virgülle ayrılmış) satırlara açar.
    Döner: (genişletilmiş df, seçenek adı kolonu)."""
    rows = []
    if col in df.columns:
        for idx, val in df[col].items():
            rid = df.at[idx, "kayit_id"] if "kayit_id" in df.columns else idx
            for part in str(val).split(","):
                p = part.strip()
                if p:
                    rows.append({"kayit_id": rid, "secenek": p})
    return pd.DataFrame(rows), "secenek"


def multi_frequency(df, col, kind):
    """Çoklu seçim sorusu için seçim sayısı tablosu."""
    ex, c = explode_multi(df, col, kind)
    if ex.empty:
        return pd.DataFrame()
    vc = ex[c].value_counts()
    opts = S.multi_options(kind, col)
    known = [o for o in opts if o in vc.index]
    extra = [o for o in vc.index if o not in opts]
    vc = vc.reindex(known + extra)
    tab = pd.DataFrame({"Seçim Sayısı": vc.astype(int)})
    n_resp = df[col].astype(str).str.strip().ne("").sum()
    tab["Yanıt %"] = (tab["Seçim Sayısı"] / max(n_resp, 1) * 100).round(1)
    tab["Vaka %"] = (tab["Seçim Sayısı"] / max(len(df), 1) * 100).round(1)
    tab.index.name = "Seçenek"
    return tab


# ---------------------------------------------------------------- çapraz
def crosstab(df, col_row, col_col, kind):
    """İki kategorik değişken arasındaki çapraz tablo (kişi sayıları)."""
    if col_row not in df.columns or col_col not in df.columns:
        return pd.DataFrame()
    a = df[col_row].astype(str).str.strip()
    b = df[col_col].astype(str).str.strip()
    mask = (a != "") & (b != "")
    a, b = a[mask], b[mask]
    if len(a) == 0:
        return pd.DataFrame()
    ro = S.cat_order(kind, col_row)
    co = S.cat_order(kind, col_col)
    t = pd.crosstab(a, b)
    if ro:
        t = t.reindex([x for x in ro if x in t.index])
    if co:
        t = t[[x for x in co if x in t.columns]]
    return t


def chi2_test(tab):
    """Çapraz tabloya ki-kare bağımsızlık testi + Cramér's V uygular."""
    tab = tab.loc[(tab.sum(axis=1) > 0), (tab.sum(axis=0) > 0)]
    if tab.shape[0] < 2 or tab.shape[1] < 2:
        return None
    chi2, p, dof, expected = stats.chi2_contingency(tab)
    n = tab.values.sum()
    r, k = tab.shape
    cramers_v = float(np.sqrt(chi2 / (n * (min(r, k) - 1)))) if n and min(r, k) > 1 else np.nan
    low = (expected < 5).mean()
    return {
        "chi2": chi2, "p": p, "dof": dof,
        "cramers_v": cramers_v, "n": n,
        "low_expected_pct": low * 100,
        "expected": pd.DataFrame(expected, index=tab.index, columns=tab.columns),
    }


def crosstab_pct(tab, by="row"):
    """Çapraz tabloyu yüzdeye çevirir."""
    if tab.empty:
        return tab
    if by == "row":
        return (tab.div(tab.sum(axis=1), axis=0) * 100).round(1)
    return (tab.div(tab.sum(axis=0), axis=1) * 100).round(1)


# ------------------------------------------------- sayısal × kategori
def group_numeric_stats(df, num_col, cat_col, kind):
    """Kategori gruplarına göre sayısal değişken özet istatistikleri."""
    if num_col not in df.columns or cat_col not in df.columns:
        return pd.DataFrame(), []
    x = _as_float(df[num_col])
    g = df[cat_col].astype(str).str.strip()
    mask = x.notna() & (g != "") & (g.str.lower() != "nan")
    if mask.sum() == 0:
        return pd.DataFrame(), []
    d = pd.DataFrame({"x": x[mask], "g": g[mask]})
    order = S.cat_order(kind, cat_col)
    groups = [gg for gg in (order or d["g"].unique()) if gg in set(d["g"])]
    rows = []
    for name, sub in d.groupby("g"):
        rows.append({
            "Grup": name, "n": len(sub), "Ortalama": sub["x"].mean(),
            "SS": sub["x"].std(ddof=1) if len(sub) > 1 else np.nan,
            "Medyan": sub["x"].median(), "Min": sub["x"].min(), "Maks": sub["x"].max(),
        })
    tab = pd.DataFrame(rows)
    if order:
        tab = tab.set_index("Grup").reindex(groups).reset_index()
    return tab, [g for g in d["g"].unique()]


def group_tests(values_by_group):
    """Grup karşılaştırma testleri: ANOVA (F) ve Kruskal-Wallis (H).
    values_by_group: {grup_adı: sayısal dizi}"""
    vals = [np.asarray(v, dtype=float) for v in values_by_group.values()]
    vals = [v[~np.isnan(v)] for v in vals]
    vals = [v for v in vals if len(v) >= 2]
    if len(vals) < 2:
        return None
    res = {"n_groups": len(vals), "n_total": int(sum(len(v) for v in vals))}
    try:
        F, p = stats.f_oneway(*vals)
        res["anova_F"], res["anova_p"] = float(F), float(p)
    except Exception:
        res["anova_F"], res["anova_p"] = np.nan, np.nan
    try:
        H, p = stats.kruskal(*vals)
        res["kruskal_H"], res["kruskal_p"] = float(H), float(p)
    except Exception:
        res["kruskal_H"], res["kruskal_p"] = np.nan, np.nan
    return res


# ---------------------------------------------------------------- korelasyon
def correlation_matrix(df, cols, method="pearson"):
    """Sayısal kolonlar arası korelasyon matrisi (min 3 ortak gözlem)."""
    x = df[cols].apply(_as_float)
    x = x.dropna(axis=0, how="all")
    keep = [c for c in x.columns if x[c].notna().sum() >= 3]
    x = x[keep]
    if len(keep) < 2:
        return pd.DataFrame(), pd.DataFrame()
    if method == "spearman":
        corr = x.corr(method="spearman")
    else:
        corr = x.corr(method="pearson")
    # p değerleri
    n = len(x)
    pmat = pd.DataFrame(np.nan, index=corr.index, columns=corr.columns)
    for i, a in enumerate(corr.index):
        for j, b in enumerate(corr.columns):
            if i <= j:
                continue
            sub = x[[a, b]].dropna()
            if len(sub) >= 4:
                r = corr.loc[a, b]
                if not np.isnan(r) and abs(r) < 1:
                    t = r * np.sqrt((len(sub) - 2) / (1 - r ** 2))
                    pmat.loc[a, b] = pmat.loc[b, a] = 2 * stats.t.sf(abs(t), len(sub) - 2)
                elif abs(r) == 1:
                    pmat.loc[a, b] = pmat.loc[b, a] = 0.0
    return corr, pmat


# ---------------------------------------------------------------- Likert
def cronbach_alpha(items: pd.DataFrame):
    """Likert maddeleri için Cronbach alfa (iç tutarlılık)."""
    x = items.apply(_as_float)
    x = x.dropna()
    if len(x) < 3 or x.shape[1] < 2:
        return np.nan, len(x)
    k = x.shape[1]
    var_items = x.var(axis=0, ddof=1)
    if (var_items == 0).all():
        return np.nan, len(x)
    alpha = k / (k - 1) * (1 - var_items.sum() / x.sum(axis=1).var(ddof=1))
    return float(alpha), len(x)


def likert_distribution(df, cols, kind):
    """Her Likert maddesi için 1–5 dağılımı (yüzde) tablosu."""
    rows = []
    labels = S.label_map(kind)
    for c in cols:
        if c not in df.columns:
            continue
        s = _as_float(df[c]).dropna().astype(int)
        s = s[(s >= 1) & (s <= 5)]
        n = len(s)
        if n == 0:
            continue
        row = {"Madde": labels.get(c, c), "n": n, "Ortalama": round(s.mean(), 2)}
        for v in range(1, 6):
            row[str(v)] = round((s == v).mean() * 100, 1)
        rows.append(row)
    return pd.DataFrame(rows)


def scale_scores(df, kind):
    """Ölçek puanlarını (madde ortalamaları) hesaplar."""
    out = pd.DataFrame(index=df.index)
    for name, cols in S.scale_defs(kind).items():
        present = [c for c in cols if c in df.columns]
        if present:
            x = df[present].apply(_as_float)
            x = x.where((x >= 1) & (x <= 5))
            out[name] = x.mean(axis=1)
    return out


# ---------------------------------------------------------------- yardımcı
def numeric_summary(df, cols):
    """Sayısal kolonların betimsel istatistikleri (veri yoksa boş tablo döner)."""
    cols = [c for c in cols if c in df.columns]
    if not cols:
        return pd.DataFrame()
    x = df[cols].apply(_as_float)
    x = x.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if x.shape[1] == 0:
        return pd.DataFrame()
    desc = x.describe().T
    desc["medyan"] = x.median()
    desc = desc[["count", "mean", "std", "min", "medyan", "max"]]
    desc.columns = ["n", "Ortalama", "SS", "Min", "Medyan", "Maks"]
    return desc.round(2)
