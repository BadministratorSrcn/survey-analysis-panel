# -*- coding: utf-8 -*-
"""Modüllerin fonksiyonel testleri: kayıt ekleme, analiz fonksiyonları, Excel dışa aktarma."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "anket_analiz")

import numpy as np
import pandas as pd

import analysis as A
import data_store as D
import demo_data as DEMO
import survey_schema as S

ok = fail = 0


def check(name, cond):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS {name}")
    else:
        fail += 1
        print(f"  FAIL {name}")


print("[1] Sema tutarlariği")
for kind in ("ciftci", "bayi"):
    cols = S.all_columns(kind)
    check(f"{kind} kolonları benzersiz", len(cols) == len(set(cols)))
    lm = S.label_map(kind)
    check(f"{kind} etiket haritası tüm kolonları kapsıyor", set(cols) == set(lm))
    check(f"{kind} yedek kolonları tanımlı", set(D.STORE_COLS[kind]) == set(["kayit_id", "kayit_zamani"] + cols))

print("[1b] Yeni alanlar (arazi tipi, ürünler, termin nakliye)")
check("arazi_tipi şemada", "arazi_tipi" in S.FARMER_SINGLE)
check("arazi_tipi seçenekleri", S.FARMER_SINGLE["arazi_tipi"]["options"] == ["Sulu", "Kuru", "Karışık (sulu + kuru)"])
for p in ("Arpa", "Yem Bitkisi", "Şeker Pancarı"):
    check(f"ürün listesinde {p}", p in S.FARMER_MULTI["urunler"]["options"])
    check(f"bayi ürün yöneliminde {p}", p in S.BAYI_SINGLE["urun_yonelim"]["options"])
check("termin_nakliye_tutarı şemada", any(c == "termin_nakliye_tutari" for c, _, _ in S.BAYI_NUMERIC))
check("termin_nakliye_tutarı bayi kolonlarında", "termin_nakliye_tutari" in S.all_columns("bayi"))

print("[2] Veri saklama (geçici kayıt)")
rid = D.add_record("ciftci", {"yas_grubu": "31-40", "egitim": "Lise", "ilce": "Bismil", "urunler": "Pamuk, Mısır"})
check("kayıt eklendi", rid is not None)
df = D.load_df("ciftci")
check("kayıt CSV'de", str(rid) in set(df["kayit_id"].astype(str)))
row = D.get_record("ciftci", rid)
check("get_record doğru", row["ilce"] == "Bismil")
D.update_record("ciftci", rid, {"ilce": "Silvan"})
check("update_record doğru", D.get_record("ciftci", rid)["ilce"] == "Silvan")
D.delete_records("ciftci", [rid])
check("kayıt silindi", str(rid) not in set(D.load_df("ciftci")["kayit_id"].astype(str)))

print("[3] Demo veri üretimi")
rows = DEMO.generate_ciftci(30)
check("30 demo çiftçi üretildi", len(rows) == 30)
check("demo alanları semada", set(rows[0]) <= set(S.all_columns("ciftci")))
check("demo arazi_tipi dolu", all(r.get("arazi_tipi") in ("Sulu", "Kuru", "Karışık (sulu + kuru)") for r in rows))
kuru_rows = [r for r in rows if r["arazi_tipi"] == "Kuru"]
check("Kuru arazide sulama alanları boş", all(r["sulama_kaynagi"] == "" and r["sulama_sekli"] == "" for r in kuru_rows))
bayi_demo = DEMO.generate_bayi(5)
check("bayi demo termin nakliye dolu", all(str(r.get("termin_nakliye_tutari", "")) != "" for r in bayi_demo))

print("[4] Analiz fonksiyonları (demo veri ile)")
cdf = pd.DataFrame(rows)
ft = A.frequency_table(cdf, "ilce", "ciftci", S.cat_order("ciftci", "ilce"))
check("kişi sayısı tablosu dolu", len(ft) > 0 and ft["Kişi Sayısı"].sum() == 30)
mf = A.multi_frequency(cdf, "urunler", "ciftci")
check("çoklu seçim toplamı >= vaka sayısı", mf["Seçim Sayısı"].sum() >= 30)
ct = A.crosstab(cdf, "ilce", "egitim", "ciftci")
check("çapraz tablo oluştu", ct.shape[0] >= 2 and ct.shape[1] >= 2)
res = A.chi2_test(ct)
check("ki-kare sonucu", res is not None and 0 <= res["p"] <= 1 and 0 <= res["cramers_v"] <= 1)
tab2, groups = A.group_numeric_stats(cdf, "ariza_sikligi", "yas_grubu", "ciftci")
check("grup istatistikleri", len(tab2) >= 2)
gb = {}
x = pd.to_numeric(cdf["ariza_sikligi"], errors="coerce")
for g in cdf["yas_grubu"].unique():
    gb[g] = x[cdf["yas_grubu"] == g].dropna().values
t = A.group_tests(gb)
check("ANOVA/KW testleri", t is not None and not np.isnan(t["anova_p"]))
corr, pmat = A.correlation_matrix(cdf, ["ariza_sikligi", "bakim_gideri", "yillik_kullanim_saati"])
check("korelasyon matrisi", corr.shape == (3, 3))
items = cdf[["l_tek1", "l_tek2", "l_tek3"]].apply(pd.to_numeric, errors="coerce")
alpha, n_used = A.cronbach_alpha(items)
check("cronbach alfa aralıkta", -1 <= alpha <= 1)
dist = A.likert_distribution(cdf, S.likert_columns("ciftci"), "ciftci")
check("likert dağılım satır sayısı", len(dist) == len(S.likert_columns("ciftci")))
scores = A.scale_scores(cdf, "ciftci")
check("ölçek puanları", scores["tek_puan"].between(1, 5).all())
summ = A.numeric_summary(cdf, ["ariza_sikligi", "yakit_tuketimi"])
check("betimsel özet", list(summ.index) == ["ariza_sikligi", "yakit_tuketimi"])

print("[4b] Birleşik çiftçi-bayi analizleri")
bdf_demo = pd.DataFrame(DEMO.generate_bayi(10))
pair = A.common_key_pair_counts(cdf, bdf_demo, "ilce", "ilce", False, False)
check("ortak ilçe tablosu", not pair.empty and {"Çiftçi (kişi)", "Bayi (firma)"} <= set(pair.columns))
check("çiftçi sütunu toplamı", pair["Çiftçi (kişi)"].sum() >= 0 and pair["Bayi (firma)"].sum() > 0)
tres = A.survey_comparison_test(pair)
check("homojenlik testi", tres is None or (0 <= tres["p"] <= 1 and 0 <= tres["cramers_v"] <= 1))
pair_urun = A.common_key_pair_counts(cdf, bdf_demo, "urunler", "urun_yonelim", True, False)
check("ürün karşılaştırma (çoklu-tek)", not pair_urun.empty)
comb, note = A.combined_numeric_frames(cdf, bdf_demo, "termin_nakliye_tutari", "ilce")
check("birleşik sayısal (eksik anket atlanır)",
      len(comb) > 0 and set(comb["anket"].unique()) == {"Bayi"} and note != "")
comb2, _ = A.combined_numeric_frames(cdf, bdf_demo, "ilce", "ilce")
check("sayısal olmayan seçimde boş", len(comb2) == 0)
gstats = A.combined_group_stats(comb)
check("birleşik grup istatistiği", not gstats.empty and {"Anket", "Grup", "Ortalama"} <= set(gstats.columns))
gtests = A.combined_group_tests(comb)
check("birleşik test seti anahtarları", set(gtests) == {"ciftci", "bayi", "birlesik"})

print("[5] Excel dışa aktarma")
bdf = pd.DataFrame(DEMO.generate_bayi(5))
for r in bdf.to_dict("records"):
    D.add_record("bayi", r)
xlsx = D.to_excel_bytes()
check("excel üretildi", len(xlsx) > 1000 and xlsx[:2] == b"PK")

print("[6] Temizlik")
D.delete_records("ciftci", list(D.load_df("ciftci")["kayit_id"]))
D.delete_records("bayi", list(D.load_df("bayi")["kayit_id"]))
check("veri temizlendi", len(D.load_df("ciftci")) == 0 and len(D.load_df("bayi")) == 0)

print(f"\nSONUÇ: {ok} PASS, {fail} FAIL")
sys.exit(1 if fail else 0)
