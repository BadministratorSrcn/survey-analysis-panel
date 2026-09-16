# -*- coding: utf-8 -*-
"""
Anket şeması — "Arjen Anket soruları.docx"
(Dicle Üniversitesi, Tarım Makinaları ve Teknolojileri Mühendisliği yüksek lisans tezi:
"Diyarbakır İlinde Bayiler Aracılığıyla Temin Edilen Tarım Makinalarının Çiftçilere
Teknik ve Ekonomik Etkilerinin Değerlendirilmesi")

Bu dosya; çiftçi (A) ve bayi (B) anketlerinin tüm sorularını, seçeneklerini ve
C bölümündeki teknik/ekonomik göstergeleri tek yerde tanımlar.
"""

LIKERT_LABELS = {
    1: "Hiç katılmıyorum",
    2: "Katılmıyorum",
    3: "Kararsızım",
    4: "Katılıyorum",
    5: "Tamamen katılıyorum",
}
LIKERT_ORDER = ["1", "2", "3", "4", "5"]
EVET_HAYIR = ["Evet", "Hayır"]
DISTRICTS = ["Bismil", "Çınar", "Silvan", "Ergani", "Sur", "Yenişehir", "Diğer"]

# =========================== A. ÇİFTÇİ ANKETİ ===========================

FARMER_IDENTITY = [
    ("ad_soyad", "Çiftçinin Adı Soyadı"),
    ("koy", "Köy"),
    ("iletisim", "İletişim Bilgileri"),
]

FARMER_SINGLE = {
    "yas_grubu": {"label": "Yaş", "options": ["18-30", "31-40", "41-50", "51-60", "60+"], "required": True},
    "egitim": {"label": "Eğitim Durumu", "options": ["İlkokul", "Ortaokul", "Lise", "Üniversite", "Lisansüstü"], "required": True},
    "ilce": {"label": "İlçe", "options": DISTRICTS, "required": True},
    "arazi_sinifi": {"label": "Toplam İşlenen Arazi Büyüklüğü", "options": ["0-50 da", "51-100 da", "101-250 da", "251-500 da", "500+ da"]},
    "sulama_kaynagi": {"label": "Sulama Suyu Kaynağı", "options": ["Kuyudan", "Kanaldan", "Barajdan"]},
    "sulama_temin": {"label": "Sulama Suyunu Temin Şekli", "options": ["Dalgıç Pompa", "Santrifüj Pompa", "Kanal Suyu", "Diğer"]},
    "sulama_sekli": {"label": "Sulama Şekli", "options": ["Salma", "Yağmurlama", "Damlama", "Karma"]},
    "alim_yeri": {"label": "Makine Alım Yeri", "options": ["Diyarbakır Bayisi", "Diyarbakır İmalatçısı", "Başka il", "Diğer"]},
    "servis_kullanim": {"label": "Teknik Servisten Yararlanma", "options": EVET_HAYIR},
    "servis_memnuniyet": {"label": "Teknik Servisten Memnuniyet", "options": EVET_HAYIR},
    "servis_yeterlilik": {"label": "Servisin Arızayı Giderme Yeterliliği", "options": EVET_HAYIR},
    "servis_memnuniyet_puani": {"label": "Servis Memnuniyeti (1-5 puan)", "options": ["1", "2", "3", "4", "5"]},
}

FARMER_MULTI = {
    "urunler": {"label": "Yetiştirilen Ürünler", "options": ["Pamuk", "Mısır", "Buğday", "Çeltik", "Mercimek", "Nohut", "Diğer"]},
    "makineler": {"label": "Sahip Olunan Makineler", "options": [
        "Traktör", "Ekim makinesi", "Hassas (havalı) ekim makinesi", "Pulluk", "Diskaro",
        "Kültüvatör", "Rotovatör", "Pülverizatör", "Gübre dağıtma makinesi",
        "Pamuk hasat makinesi", "Mısır hasat makinesi", "Biçerdöver", "Balya makinesi", "Römork", "Diğer"]},
    "tercih_nedenleri": {"label": "Makineyi Bu Bayiden Alma Nedenleri", "options": ["Fiyat", "Marka", "Servis", "Yedek parça", "Tavsiye", "Kampanya", "Hibe", "Diğer"]},
}

FARMER_TEXT_EXTRA = [
    ("traktor_marka", "Traktör Markası"),
    ("traktor_model", "Traktör Modeli"),
    ("alim_yeri_not", "Alım Yeri Açıklaması (il / diğer)"),
    ("makineler_diger", "Diğer Makineler (belirtin)"),
]

# C bölümündeki teknik/ekonomik göstergeler (bağımlı/bağımsız değişkenler)
FARMER_NUMERIC = [
    ("sulu_da", "Sulu arazi", "da"),
    ("kuru_da", "Kuru arazi", "da"),
    ("traktor_guc", "Traktör motor gücü", "BG"),
    ("makine_yas", "Makine yaşı", "yıl"),
    ("alim_yili", "Satın alma yılı", ""),
    ("alim_bedeli", "Satın alma bedeli", "TL"),
    ("nakliye_maliyeti", "Nakliye maliyeti", "TL"),
    ("yillik_kullanim_saati", "Yıllık kullanım süresi", "h/yıl"),
    ("yillik_kullanim_alani", "Yıllık kullanım alanı", "da/yıl"),
    ("ariza_sikligi", "Arıza sıklığı", "adet/yıl"),
    ("ariza_suresi", "Ortalama arıza süresi", "saat"),
    ("bakim_gideri", "Yıllık bakım gideri", "TL/yıl"),
    ("onarim_gideri", "Yıllık onarım gideri", "TL/yıl"),
    ("yakit_tuketimi", "Yakıt tüketimi", "L/h"),
    ("kullanilabilirlik", "Makine kullanılabilirlik oranı", "%"),
    ("yedek_parca_suresi", "Yedek parça temin süresi", "gün"),
    ("servis_mudahale_suresi", "Servis müdahale süresi", "gün"),
    ("iscilik_tasarrufu", "İşçilik tasarrufu", "işgücü-gün/yıl"),
    ("ikinci_el_degeri", "İkinci el satış değeri", "TL"),
]

FARMER_LIKERT = {
    "Teknik Hizmet": {
        "l_tek1": "Makine bölgemizin tarım koşullarına uygundur.",
        "l_tek2": "Makine beklediğim performansı sağlamaktadır.",
        "l_tek3": "Yakıt tüketimi ekonomiktir.",
        "l_tek4": "Arıza oranı düşüktür.",
        "l_tek5": "Servis yeterlidir.",
        "l_tek6": "Yedek parçaya kolay ulaşılmaktadır.",
        "l_tek7": "Arızalar kısa sürede giderilmektedir.",
    },
    "Ekonomik Boyut": {
        "l_eko1": "Makinenin fiyatı uygundur.",
        "l_eko2": "Nakliye maliyeti yüksektir.",
        "l_eko3": "Servis maliyetleri yüksektir.",
        "l_eko4": "Yedek parça pahalıdır.",
        "l_eko5": "Makine yatırımını kısa sürede amorti etmiştir.",
        "l_eko6": "Makine işçilik maliyetini azaltmıştır.",
        "l_eko7": "Yakıt tasarrufu sağlamaktadır.",
        "l_eko8": "Verimimi artırmıştır.",
    },
    "Memnuniyet": {
        "l_mem1": "Bayiden memnunum.",
        "l_mem2": "Satış sonrası hizmetlerden memnunum.",
        "l_mem3": "Aynı markayı tekrar alırım.",
        "l_mem4": "Başka çiftçilere tavsiye ederim.",
    },
}

FARMER_OPEN = {
    "acik_sorun": "Makinede en büyük sorun nedir?",
    "acik_beklenti": "Bayilerden beklentiniz nedir?",
}

# =========================== B. BAYİ ANKETİ ===========================

BAYI_TEXT = [
    ("firma_adi", "Firma Adı"),
    ("satilan_markalar", "Satılan Markalar"),
]

BAYI_SINGLE = {
    "ilce": {"label": "Firmanın Bulunduğu İlçe", "options": DISTRICTS},
    "yetkili_servis": {"label": "Yetkili Servis Var mı?", "options": EVET_HAYIR},
    "yillik_satis": {"label": "Yılda Yaklaşık Satılan Makine Sayısı", "options": ["0-50", "51-100", "101-150", "151-200", "200+"]},
    "urun_yonelim": {"label": "Satışların Yönlendiği Ürün", "options": ["Pamuk", "Mısır", "Buğday", "Mercimek", "Nohut", "Çeltik", "Karma"]},
}

BAYI_MULTI = {
    "acma_nedeni": {"label": "Bayi Açma Nedeni", "options": [
        "Bölgedeki yüksek tarımsal potansiyel ve makine talebi",
        "Aile mesleği / sektörel tecrübe ve devamlılığı",
        "Yüksek kâr ve yatırımın geri dönüş potansiyeli",
        "Devlet destekleri ve teşvikler",
        "Bölgedeki bayi ve servis açığı"]},
    "satilan_makineler": {"label": "Satılan Makine Grupları", "options": [
        "Traktör", "Toprak işleme", "Ekim-Dikim", "İlaçlama", "Gübreleme", "Hasat", "Biçerdöver", "Diğer"]},
    "musteri_ilceler": {"label": "Müşterilerin Geldiği İlçeler", "options": ["Bismil", "Silvan", "Çınar", "Ergani", "Yenişehir", "Sur", "Diğer"]},
    "sorunlar": {"label": "Karşılaşılan En Büyük Sorunlar", "options": [
        "Finansman", "Kur artışı", "Nakliye ve lojistik maliyeti", "Servis ağı temini",
        "Tedarik / teslimat sürelerinin uzunluğu", "Kalifiye personel",
        "Çiftçinin ödeme gücü yetersizliği", "Yedek parça temini",
        "Haksız rekabet ve yetkisiz satıcılar", "Diğer"]},
    "gelecek_gorusler": {"label": "Geleceğe Yönelik Görüşler", "options": [
        "Sulama alanlarının artmasıyla satışlar artacaktır",
        "Hassas tarım makinelerine talep artacaktır",
        "GPS destekli makineler yaygınlaşacaktır",
        "Büyük işletmelerin sayısı artacaktır",
        "Devlet destekleri satışları artırmaktadır"]},
}

BAYI_NUMERIC = [
    ("kurulus_yili", "Kuruluş Yılı", ""),
    ("calisan_sayisi", "Çalışan Sayısı", "kişi"),
]

BAYI_LIKERT = {
    "Satış Sonrası Hizmet": {
        "b_ssh1": "Teslim süresi (zamanında teslim edilmektedir).",
        "b_ssh2": "Servis ağımız yeterlidir.",
        "b_ssh3": "Servis personeli sayısı yeterlidir ve ulaşılabilir durumdadır.",
        "b_ssh4": "Yedek parça stoğumuz yeterlidir.",
        "b_ssh5": "Arızalara zamanında müdahale edilmektedir.",
        "b_ssh6": "Çiftçiler teknik eğitim almaktadır.",
        "b_ssh7": "Garanti hizmetleri yeterlidir.",
    },
}

BAYI_OPEN = {
    "b_acik1": "Bölgede en çok talep edilen makine hangisidir?",
    "b_acik2": "Çiftçilerin en önemli beklentisi nedir?",
    "b_acik3": "Bölgede makine imalatçıları neden yetersizdir?",
    "b_acik4": "Çiftçilerin bayinizden ve aldıkları makinelerden beklentileri nelerdir?",
    "b_acik5": "Satış sonrası hizmetlerde bölgede yaşanan en büyük aksaklık nedir?",
    "b_acik6": "Ödeme ve finansman sürecinde en sık karşılaştığınız sorunlar nelerdir?",
    "b_acik7": "Gelecekte talebi artıracağını düşündüğünüz teknik/teknolojik makineler hangileridir?",
}

# =========================== YARDIMCILAR ===========================


def likert_columns(kind):
    groups = FARMER_LIKERT if kind == "ciftci" else BAYI_LIKERT
    return [c for g in groups.values() for c in g]


def likert_groups(kind):
    return FARMER_LIKERT if kind == "ciftci" else BAYI_LIKERT


def all_columns(kind):
    if kind == "ciftci":
        cols = [c for c, _ in FARMER_IDENTITY]
        cols += list(FARMER_SINGLE) + list(FARMER_MULTI)
        cols += [c for c, _ in FARMER_TEXT_EXTRA]
        cols += [c for c, _, _ in FARMER_NUMERIC]
        cols += likert_columns(kind)
        cols += list(FARMER_OPEN)
    else:
        cols = [c for c, _ in BAYI_TEXT]
        cols += list(BAYI_SINGLE) + list(BAYI_MULTI)
        cols += [c for c, _, _ in BAYI_NUMERIC]
        cols += likert_columns(kind)
        cols += list(BAYI_OPEN)
    return cols


def label_map(kind):
    m = {}
    if kind == "ciftci":
        for c, lab in FARMER_IDENTITY:
            m[c] = lab
        for c, spec in FARMER_SINGLE.items():
            m[c] = spec["label"]
        for c, spec in FARMER_MULTI.items():
            m[c] = spec["label"] + " (çoklu)"
        for c, lab in FARMER_TEXT_EXTRA:
            m[c] = lab
        for c, lab, unit in FARMER_NUMERIC:
            m[c] = f"{lab} ({unit})" if unit else lab
        for g in FARMER_LIKERT.values():
            for c, lab in g.items():
                m[c] = lab
        for c, lab in FARMER_OPEN.items():
            m[c] = lab
    else:
        for c, lab in BAYI_TEXT:
            m[c] = lab
        for c, spec in BAYI_SINGLE.items():
            m[c] = spec["label"]
        for c, spec in BAYI_MULTI.items():
            m[c] = spec["label"] + " (çoklu)"
        for c, lab, unit in BAYI_NUMERIC:
            m[c] = f"{lab} ({unit})" if unit else lab
        for g in BAYI_LIKERT.values():
            for c, lab in g.items():
                m[c] = lab
        for c, lab in BAYI_OPEN.items():
            m[c] = lab
    return m


def is_multi(kind, col):
    return col in (FARMER_MULTI if kind == "ciftci" else BAYI_MULTI)


def multi_options(kind, col):
    return (FARMER_MULTI if kind == "ciftci" else BAYI_MULTI)[col]["options"]


def is_likert(kind, col):
    return col in likert_columns(kind)


def cat_order(kind, col):
    """Kategorik değişkenin görüntüleme/test sırası."""
    if is_multi(kind, col):
        return multi_options(kind, col)
    specs = FARMER_SINGLE if kind == "ciftci" else BAYI_SINGLE
    if col in specs:
        return specs[col]["options"]
    if is_likert(kind, col):
        return LIKERT_ORDER
    return None


def scale_defs(kind):
    if kind == "ciftci":
        return {
            "tek_puan": list(FARMER_LIKERT["Teknik Hizmet"]),
            "eko_puan": list(FARMER_LIKERT["Ekonomik Boyut"]),
            "mem_puan": list(FARMER_LIKERT["Memnuniyet"]),
        }
    return {"ssh_puan": list(BAYI_LIKERT["Satış Sonrası Hizmet"])}


def scale_labels(kind):
    if kind == "ciftci":
        return {
            "tek_puan": "Teknik Hizmet Ölçek Puanı (1-5)",
            "eko_puan": "Ekonomik Boyut Ölçek Puanı (1-5)",
            "mem_puan": "Memnuniyet Ölçek Puanı (1-5)",
        }
    return {"ssh_puan": "Satış Sonrası Hizmet Ölçek Puanı (1-5)"}
