# -*- coding: utf-8 -*-
"""Demo/örnek veri üretici — uygulamayı test etmek ve göstermek için.

Bu kayıtlar 'Örnek Veri Yükle' düğmesiyle eklenir ve tek tek silinebilir.
"""
import random

import survey_schema as S


def _pick(options, n=None):
    if n is None:
        return random.choice(options)
    return random.sample(options, min(n, len(options)))


def _likert(bias=0.0):
    w = [5 + bias, 10 + bias, 15, 25 + 2 * bias, 20 + 3 * bias]
    return random.choices([1, 2, 3, 4, 5], weights=w)[0]


def _num(lo, hi, decimals=0):
    v = random.uniform(lo, hi)
    return round(v, decimals)


def generate_ciftci(n=60):
    rows = []
    for _ in range(n):
        age = _pick(S.FARMER_SINGLE["yas_grubu"]["options"])
        edu = _pick(S.FARMER_SINGLE["egitim"]["options"])
        ilce = _pick(["Bismil", "Silvan", "Çınar", "Ergani", "Sur", "Yenişehir"])
        arazi = _pick(S.FARMER_SINGLE["arazi_sinifi"]["options"])
        has_tractor = random.random() < 0.8
        # Demografik örüntüler: eğitim ve yaş arttıkça teknik memnuniyet artar
        bias = ({"İlkokul": -2, "Ortaokul": -1, "Lise": 0, "Üniversite": 1.5, "Lisansüstü": 2}[edu]
                + ({"18-30": 1, "31-40": 0.5, "41-50": 0, "51-60": -0.5, "60+": -1}[age]))
        urunler = _pick(S.FARMER_MULTI["urunler"]["options"], n=random.randint(1, 3))
        traktor_guc = _num(45, 120) if has_tractor else ""
        # Arazi tipi: sulu ağırlıklı (Diyarbakır ovası); Kuru ise sulama alanları boş kalır
        arazi_tipi = _pick(["Sulu", "Sulu", "Karışık (sulu + kuru)", "Kuru"])
        sulu = arazi_tipi in ("Sulu", "Karışık (sulu + kuru)")
        rows.append({
            "ad_soyad": "", "koy": "", "iletisim": "",
            "yas_grubu": age, "egitim": edu, "ilce": ilce, "arazi_sinifi": arazi,
            "arazi_tipi": arazi_tipi,
            "sulu_da": _num(10, 400) if sulu else "",
            "kuru_da": _num(20, 800) if arazi_tipi != "Sulu" else _num(0, 40),
            "sulama_kaynagi": _pick(S.FARMER_SINGLE["sulama_kaynagi"]["options"]) if sulu else "",
            "sulama_temin": _pick(S.FARMER_SINGLE["sulama_temin"]["options"]) if sulu else "",
            "sulama_sekli": _pick(S.FARMER_SINGLE["sulama_sekli"]["options"]) if sulu else "",
            "urunler": ", ".join(urunler),
            "makineler": ", ".join(_pick(S.FARMER_MULTI["makineler"]["options"], n=random.randint(2, 6))),
            "traktor_marka": _pick(["Massey Ferguson", "New Holland", "Ford", "Case IH", "Tümosan", "Deutz"]) if has_tractor else "",
            "traktor_model": str(random.randint(1995, 2024)) if has_tractor else "",
            "traktor_guc": traktor_guc,
            "alim_yeri": _pick(S.FARMER_SINGLE["alim_yeri"]["options"]),
            "alim_yili": random.randint(2005, 2025),
            "alim_bedeli": _num(150_000, 3_500_000),
            "nakliye_maliyeti": _num(2_000, 40_000),
            "servis_kullanim": "Evet" if random.random() < 0.75 else "Hayır",
            "servis_memnuniyet": _likert(bias) >= 3 and "Evet" or "Hayır",
            "servis_yeterlilik": _likert(bias) >= 3 and "Evet" or "Hayır",
            "servis_memnuniyet_puani": str(_likert(bias)),
            "makine_yas": _num(1, 25),
            "yillik_kullanim_saati": _num(120, 900),
            "yillik_kullanim_alani": _num(50, 2000),
            "ariza_sikligi": _num(0, 8, 1),
            "ariza_suresi": _num(1, 20, 1),
            "bakim_gideri": _num(5_000, 80_000),
            "onarim_gideri": _num(3_000, 120_000),
            "yakit_tuketimi": _num(8, 25, 1),
            "kullanilabilirlik": _num(70, 99, 1),
            "yedek_parca_suresi": _num(0, 15, 1),
            "servis_mudahale_suresi": _num(0, 10, 1),
            "iscilik_tasarrufu": _num(10, 120),
            "ikinci_el_degeri": _num(60_000, 2_000_000),
            "tercih_nedenleri": ", ".join(_pick(S.FARMER_MULTI["tercih_nedenleri"]["options"], n=random.randint(1, 3))),
            "makineler_diger": "",
            "alim_yeri_not": "",
            **{c: str(_likert(bias)) for g in S.FARMER_LIKERT.values() for c in g},
            "acik_sorun": _pick(["Yedek parça gecikmesi", "Servis yoğunluğu", "Hidrolik arızalar", "Yakıt maliyeti", "Pahalı bakım"]),
            "acik_beklenti": _pick(["Daha hızlı servis", "Uygun fiyat", "Eğitim", "Yedek parça stoğu"]),
        })
    return rows


def generate_bayi(n=10):
    rows = []
    for _ in range(n):
        rows.append({
            "firma_adi": f"Tarım Mak. San. Tic. {random.randint(1, 99)}",
            "ilce": _pick(["Yenişehir", "Sur", "Bismil", "Ergani"]),
            "satilan_markalar": ", ".join(_pick(["Massey Ferguson", "New Holland", "Case IH", "Tümosan", "Deutz", "Landini"], 2)),
            "kurulus_yili": random.randint(1990, 2022),
            "calisan_sayisi": _num(3, 40),
            "termin_nakliye_tutari": _num(5_000, 150_000),
            "yetkili_servis": _pick(S.EVET_HAYIR),
            "acma_nedeni": ", ".join(_pick(S.BAYI_MULTI["acma_nedeni"]["options"], n=random.randint(1, 2))),
            "satilan_makineler": ", ".join(_pick(S.BAYI_MULTI["satilan_makineler"]["options"], n=random.randint(2, 5))),
            "yillik_satis": _pick(S.BAYI_SINGLE["yillik_satis"]["options"]),
            "urun_yonelim": _pick(S.BAYI_SINGLE["urun_yonelim"]["options"]),
            "musteri_ilceler": ", ".join(_pick(S.BAYI_MULTI["musteri_ilceler"]["options"], n=random.randint(1, 4))),
            **{c: str(_likert()) for g in S.BAYI_LIKERT.values() for c in g},
            "sorunlar": ", ".join(_pick(S.BAYI_MULTI["sorunlar"]["options"], n=random.randint(1, 4))),
            "gelecek_gorusler": ", ".join(_tez := _pick(S.BAYI_MULTI["gelecek_gorusler"]["options"], n=random.randint(1, 3))),
            "b_acik1": _pick(["Traktör", "Ekim makinesi", "Rotovatör", "Pamuk hasat makinesi"]),
            "b_acik2": "Uygun fiyat ve kolay finansman",
            "b_acik3": "Yatırım maliyeti yüksek, teknoloji transferi zayıf",
            "b_acik4": "Dayanıklılık ve hızlı servis",
            "b_acik5": "Yedek parça temininde gecikme",
            "b_acik6": "Çek/vasıta ödemelerinde gecikme",
            "b_acik7": "GPS'li hassas ekim makineleri",
        })
    return rows
