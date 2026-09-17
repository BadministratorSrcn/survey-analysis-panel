# Anket Analiz Paneli 🌾

**Dicle Üniversitesi — Tarım Makinaları ve Teknolojileri Mühendisliği (Yüksek Lisans Tezi)**
*"Diyarbakır İlinde Bayiler Aracılığıyla Temin Edilen Tarım Makinalarının Çiftçilere Teknik ve Ekonomik Etkilerinin Değerlendirilmesi"*

Anket sorularına birebir uygun veri girişi ve tez için hazır istatistiksel çapraz analizler sunan **yerel (offline)** uygulama.

![Dicle Üniversitesi](logos/dicle_universitesi.png) · ![Ziraat Fakültesi](logos/ziraat_fakultesi.png) · ![Mühendislik Fakültesi](logos/muhendislik_fakultesi.png)

## Kurulum ve Çalıştırma

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tarayıcı otomatik açılır (varsayılan `http://localhost:8501`). İnternet gerektirmez.

## Kullanım Akışı

1. **📝 Veri Girişi** — Anket formunu doldurup kaydedin. Yaş, eğitim, ilçe ve **arazi tipi** zorunludur; diğer alanlar opsiyoneldir. **Arazi tipi "Kuru" seçilirse sulama soruları formda görünmez** ve boş kaydedilir; "Sulu" veya "Karışık" seçilirse sulama bölümü (kaynak / temin şekli / sulama şekli) açılır. Her kayıt anında `data/` klasöründeki CSV'ye yazılır.
2. **🗂 Kayıtlar** — Kayıtları görüntüleyin, düzenleyin, silin; gerekirse 60 çiftçi + 10 bayi örnek veriyle deneyin.
3. **Analiz sekmeleri:**

| Sekme | İçerik |
|---|---|
| 🏠 Genel Bakış | Kayıt sayıları, ilçe/arazi dağılımları, sayısal özetler |
| 📊 Tek Değişken | Her soru için kişi sayısı/yüzde tablosu + grafik |
| 🔀 Çapraz Analiz | İki kategorik değişken; χ², sd, p, **Cramér's V**, yığılmış yüzde, ısı haritası, beklenen kişi sayısı uyarısı |
| 📈 Sayısal × Grup | Grup ortalamaları + **ANOVA / Kruskal-Wallis**, kutu-keman grafikleri. Kapsam: **Çiftçi / Bayi / İkisi birlikte (birleşik)** — birleşik modda çiftçi ve bayi verileri aynı grafikte anket bazlı renkle karşılaştırılır |
| 🔗 Korelasyon | **Pearson/Spearman** matrisi + ısı haritası, p değerli eşleşme tablosu, serpme grafiği |
| 🧾 Likert | Madde dağılımları, ölçek ortalamaları, **Cronbach α** |
| 🤝 Çiftçi ↔ Bayi | **Serbest seçimli** birleşik analiz: her iki anketten de istediğiniz değişkeni seçip yan yana dağılım karşılaştırması (ör. İlçe ↔ İlçe, Yaş ↔ Yıllık satış aralığı); ortak etiketler (İlçe, ürünler) tam eşleşme üretir + dağılım benzerliği testi + ortak kırılımda sayısal kutu grafiği |
| 🏭 Bayi Analizi | Firma profili, çoklu seçimler, SSH değerlendirmesi |
| 💬 Açık Uçlu | Serbest yanıtların kayıt bazında listesi |

## Tez İçin Hazır Çapraz Analiz Örnekleri

- İlçe × Yetiştirilen ürün (bölgesel ürün deseni; Pamuk, Mısır, Buğday, **Arpa**, Çeltik, Mercimek, Nohut, **Yem Bitkisi**, **Şeker Pancarı**)
- Eğitim / yaş × Teknik servis memnuniyeti
- Arazi büyüklüğü × Traktör gücü, × Tercih nedenleri
- **Arazi tipi (Sulu/Kuru/Karışık) × Sulama şekli, × Ürün deseni**
- Sulama şekli × Ürün deseni
- Yaş grubu × Arıza sıklığı, Yakıt tüketimi (ANOVA/KW)
- Makine yaşı × Arıza sıklığı; Kullanım saati × Bakım maliyeti (korelasyon)
- Likert ölçek puanları × Demografik kırılımlar
- Bayi: **Termin nakliye tutarı** × yıllık satış aralığı (Sayısal × Grup sekmesi)
- **Çiftçi ↔ Bayi:** Serbest değişken seçimiyle iki anketin dağılım karşılaştırması + homojenlik testi (Çiftçi ↔ Bayi sekmesi)
- **Serbest alan çaprazları:** Traktör markası × İlçe, Model × Eğitim, Bayi: Satılan markalar × Yıllık satış (Çapraz Analiz sekmesindeki seçicilerde)
- Sayısal × Grup sekmesinde kapsam: Çiftçi / Bayi / **İkisi birlikte (birleşik)** — birleşik modda iki anket aynı grafikte anket bazlı renkle karşılaştırılır

## Veri Güvenliği

- Veriler yalnızca kendi bilgisayarınızda, `anket_analiz/data/` klasöründe CSV olarak saklanır; hiçbir yere gönderilmez.
- **⬇️ Excel indir** düğmesi tüm verileri iki sayfalık (Çiftçi/Bayi) tek dosyada dışa aktarır.
- Kimlik alanları (ad, köy, iletişim) yalnızca giriş formunda tutulur, analizlere girmez.
