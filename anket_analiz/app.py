# -*- coding: utf-8 -*-
"""Anket Analiz Arayüzü — Dicle Üniversitesi Tarım Makinaları ve Teknolojileri tezi.

Çalıştırma:  streamlit run app.py
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import analysis as A
import data_store as D
import demo_data as DEMO
import survey_schema as S
import os

LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logos")
LOGOS = [
    ("dicle_universitesi.png", "Dicle Üniversitesi"),
    ("ziraat_fakultesi.png", "Ziraat Fakültesi"),
    ("muhendislik_fakultesi.png", "Mühendislik Fakültesi"),
]

st.set_page_config(page_title="Anket Analiz Paneli", page_icon="🌾", layout="wide")

# ---------------------------------------------------------- plotly ayarları
DARK = "#1f2937"
PALETTE = px.colors.qualitative.Safe
AXIS = dict(gridcolor="#E5E7EB", linecolor="#D1D5DB")


def style_fig(fig, y_title=None, x_title=None, title=None, legend_title=None):
    fig.update_layout(
        title=title, template="plotly_white",
        font=dict(size=13, color=DARK),
        margin=dict(l=10, r=10, t=45, b=10),
        legend_title_text=legend_title,
    )
    fig.update_xaxes(**AXIS, title_text=x_title)
    fig.update_yaxes(**AXIS, title_text=y_title)
    return fig


def _fig_bytes(fig, fmt="png", scale=2.5):
    return fig.to_image(format=fmt, scale=scale)


st.markdown(
    """
    <style>
      .block-container {padding-top: 1.2rem;}
      h1 {font-size: 1.65rem !important;}
      .stTabs [data-baseweb="tab-list"] {gap: 4px;}
    </style>""",
    unsafe_allow_html=True,
)

st.title("🌾 Tarım Makinaları Anket Analiz Paneli")
st.caption(
    "Diyarbakır İlinde Bayiler Aracılığıyla Temin Edilen Tarım Makinalarının Çiftçilere "
    "Teknik ve Ekonomik Etkilerinin Değerlendirilmesi — veri girişi ve çapraz analiz"
)

# Logo şeridi (Dicle Üniversitesi · Ziraat Fakültesi · Mühendislik Fakültesi)
_logo_items = ""
for _fname, _caption in LOGOS:
    _path = os.path.join(LOGO_DIR, _fname)
    if os.path.exists(_path):
        import base64
        with open(_path, "rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode()
        _logo_items += (
            f'<div style="text-align:center; padding:0 18px;">'
            f'<img src="data:image/png;base64,{_b64}" style="height:96px; display:block; margin:0 auto;">'
            f'</div>'
        )
if _logo_items:
    st.markdown(
        f'<div style="display:flex; justify-content:flex-start; align-items:center; '
        f'flex-wrap:wrap; margin:2px 0 6px 0;">{_logo_items}</div>',
        unsafe_allow_html=True,
    )

TABS = [
    "🏠 Genel Bakış", "📝 Veri Girişi", "🗂 Kayıtlar",
    "📊 Tek Değişken", "🔀 Çapraz Analiz", "📈 Sayısal × Grup",
    "🔗 Korelasyon", "🧾 Likert / Güvenilirlik", "🏭 Bayi Analizi", "💬 Açık Uçlu",
]
tab_overview, tab_input, tab_records, tab_freq, tab_cross, tab_num, tab_corr, tab_likert, tab_bayi, tab_open = st.tabs(TABS)

# Her sekme kendi verisini yükler
CDF = D.load_df("ciftci")
BDF = D.load_df("bayi")
N_C, N_B = len(CDF), len(BDF)


def empty_state(msg):
    st.info(msg)


# ========================================================== GENEL BAKIŞ
with tab_overview:
    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("Çiftçi kaydı", N_C)
    c2.metric("Bayi kaydı", N_B)
    c3.download_button(
        "⬇️ Tüm verileri Excel olarak indir", D.to_excel_bytes(),
        file_name="anket_verileri.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    if N_C == 0:
        empty_state("Henüz çiftçi kaydı yok. **📝 Veri Girişi** sekmesinden kayıt ekleyin "
                    "veya **🗂 Kayıtlar** sekmesindeki *Örnek Veri Yükle* düğmesiyle deneyin.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("İlçe dağılımı")
            f = A.frequency_table(CDF, "ilce", "ciftci", S.cat_order("ciftci", "ilce"))
            fig = px.bar(x=f.index, y=f["Kişi Sayısı"], color=f.index, color_discrete_sequence=PALETTE)
            style_fig(fig, y_title="Çiftçi sayısı", title="Çiftçilerin ilçe dağılımı")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Arazi büyüklüğü")
            f = A.frequency_table(CDF, "arazi_sinifi", "ciftci", S.cat_order("ciftci", "arazi_sinifi"))
            fig = px.pie(values=f["Kişi Sayısı"], names=f.index, hole=0.45, color_discrete_sequence=PALETTE)
            style_fig(fig, title="İşlenen arazi büyüklüğü")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sayısal göstergeler — özet")
        cols = ["makine_yas", "yillik_kullanim_saati", "ariza_sikligi", "bakim_gideri", "yakit_tuketimi"]
        labels = {c: S.label_map("ciftci").get(c, c) for c in cols}
        num = CDF[cols].apply(pd.to_numeric, errors="coerce")
        if int(num.notna().sum().sum()) == 0:
            st.info(
                "Çiftçi kayıtlarında henüz sayısal gösterge girilmemiş. "
                "**📝 Veri Girişi** formundaki *Ekonomik göstergeler* bölümüne "
                "(makine yaşı, kullanım süresi, arıza sıklığı, bakım-onarım gideri, yakıt tüketimi vb.) "
                "değer girildiğinde bu tablo otomatik dolacaktır."
            )
        else:
            summary = pd.DataFrame({
                "n": num.count().fillna(0).astype(int),
                "Ortalama": num.mean().round(1),
                "Medyan": num.median().round(1),
                "SS": num.std().round(1),
                "Min": num.min(),
                "Maks": num.max(),
            }, index=[labels[c] for c in cols])
            st.dataframe(summary, use_container_width=True)
            st.caption("n = bu göstergeyi dolduran çiftçi sayısı. Boş bırakılan alanlar hesaba katılmaz.")

    if N_B > 0:
        st.divider()
        st.subheader("Bayi anketi — hızlı özet")
        b1, b2, b3 = st.columns(3)
        ys = A.frequency_table(BDF, "yillik_satis", "bayi", S.cat_order("bayi", "yillik_satis"))
        b1.dataframe(ys, use_container_width=True)
        srv = A.frequency_table(BDF, "yetkili_servis", "bayi")
        b2.dataframe(srv, use_container_width=True)
        if "b_ssh1" in BDF.columns:
            b3.metric("SSH ölçek ortalaması (1–5)", round(A.scale_scores(BDF, "bayi")["ssh_puan"].mean(), 2))

# ========================================================== VERİ GİRİŞİ
with tab_input:
    mode = st.radio("Anket türü", ["👨‍🌾 Çiftçi Anketi", "🏢 Bayi Anketi"], horizontal=True)
    kind = "ciftci" if mode.startswith("👨") else "bayi"

    # Arazi tipi formun DIŞINDA tutulur: Sulu/Kuru seçimine göre sulama soruları
    # anlık olarak açılıp kapanır (Streamlit form içi koşullu gösterimi desteklemez).
    arazi_tipi = ""
    if kind == "ciftci":
        arazi_tipi = st.selectbox(
            "Arazi Tipi * — Sulu veya Karışık seçilirse sulama soruları açılır",
            [""] + S.FARMER_SINGLE["arazi_tipi"]["options"],
            key="ciftci_arazi_tipi_outer",
        )

    with st.form(f"form_{kind}", clear_on_submit=True):
        rec = {}

        if kind == "ciftci":
            st.markdown("**Kimlik ve yer bilgileri** *(isteğe bağlı)*")
            idc = st.columns(3)
            for i, (c, lab) in enumerate(S.FARMER_IDENTITY):
                rec[c] = idc[i].text_input(lab)

        st.markdown("---")
        if kind == "ciftci":
            singles = dict(S.FARMER_SINGLE)
            order_keys = ["yas_grubu", "egitim", "ilce", "arazi_sinifi"]
        else:
            singles = dict(S.BAYI_SINGLE)
            order_keys = ["ilce"]
        for i in range(0, len(order_keys), 3):
            cols = st.columns(3)
            for j, key in enumerate(order_keys[i:i + 3]):
                spec = singles[key]
                with cols[j]:
                    opts = [""] + spec["options"]
                    rec[key] = st.selectbox(spec["label"] + (" *" if spec.get("required") else ""), opts,
                                            key=f"{kind}_{key}")

        if kind == "ciftci":
            sulama_goster = arazi_tipi in ("Sulu", "Karışık (sulu + kuru)")
            if sulama_goster:
                sulama_notu = ""
            elif arazi_tipi == "Kuru":
                sulama_notu = " — *(Kuru arazi seçildiği için uygulanmaz)*"
            else:
                sulama_notu = " — *(Sulu veya Karışık seçildiğinde açılır)*"
            st.markdown("---")
            st.markdown(f"**Sulama**{sulama_notu}")
            cols = st.columns(3)
            for j, key in enumerate(["sulama_kaynagi", "sulama_temin", "sulama_sekli"]):
                spec = singles[key]
                if sulama_goster:
                    rec[key] = cols[j].selectbox(spec["label"], [""] + spec["options"], key=f"{kind}_{key}")
                else:
                    rec[key] = ""
                    cols[j].caption("— (kuru arazi)")

            st.markdown("**Traktör bilgileri**")
            t1, t2, t3, t4 = st.columns(4)
            rec["traktor_marka"] = t1.text_input("Traktör markası")
            rec["traktor_model"] = t2.text_input("Model")
            rec["traktor_guc"] = t3.text_input("Motor gücü (BG)")
            rec["makine_yas"] = t4.text_input("Makine yaşı (yıl)")

        st.markdown("---")
        st.markdown("**Çoklu seçim soruları**")
        multis = S.FARMER_MULTI if kind == "ciftci" else S.BAYI_MULTI
        for key, spec in multis.items():
            sel = st.multiselect(spec["label"], spec["options"], key=f"{kind}_{key}")
            rec[key] = ", ".join(sel)

        if kind == "ciftci":
            st.markdown("**Alım yeri ve servis**")
            a1, a2 = st.columns(2)
            rec["alim_yeri"] = a1.selectbox("Makineyi nereden aldınız?", [""] + singles["alim_yeri"]["options"], key=f"{kind}_alim_yeri")
            rec["alim_yeri_not"] = a2.text_input("Açıklama (il / diğer)")
            s1, s2, s3, s4 = st.columns(4)
            rec["servis_kullanim"] = s1.selectbox("Teknik servisten yararlanıyor musunuz?", [""] + S.EVET_HAYIR)
            rec["servis_memnuniyet"] = s2.selectbox("Servisten memnun musunuz?", [""] + S.EVET_HAYIR)
            rec["servis_yeterlilik"] = s3.selectbox("Servis arızayı giderebilecek yeterlilikte mi?", [""] + S.EVET_HAYIR)
            rec["servis_memnuniyet_puani"] = s4.selectbox("Servis memnuniyet puanı (1–5)", ["", "1", "2", "3", "4", "5"])

            st.markdown("---")
            st.markdown("**Ekonomik göstergeler** *(boş bırakılabilir)*")
            num_fields = [(c, lab, unit) for c, lab, unit in S.FARMER_NUMERIC
                          if c not in ("traktor_guc", "makine_yas")]
            for i in range(0, len(num_fields), 4):
                cols = st.columns(4)
                for j, (c, lab, unit) in enumerate(num_fields[i:i + 4]):
                    rec[c] = cols[j].text_input(f"{lab} ({unit})" if unit else lab, key=f"{kind}_{c}")

        if kind == "bayi":
            st.markdown("---")
            b1, b2, b3 = st.columns(3)
            rec["satilan_markalar"] = b1.text_input("Satılan Markalar")
            rec["kurulus_yili"] = b2.text_input("Kuruluş Yılı")
            rec["calisan_sayisi"] = b3.text_input("Çalışan Sayısı")
            rec["termin_nakliye_tutari"] = st.text_input("Termin Nakliye Tutarı (TL) — makine başına nakliye bedeli")

        st.markdown("---")
        st.markdown("**Likert ifadeleri (1 = Hiç katılmıyorum … 5 = Tamamen katılıyorum)**")
        groups = S.likert_groups(kind)
        for gname, cols_d in groups.items():
            st.markdown(f"*{gname}*")
            gkeys = list(cols_d)
            for i in range(0, len(gkeys), 2):
                cols = st.columns(2)
                for j, key in enumerate(gkeys[i:i + 2]):
                    rec[key] = cols[j].select_slider(cols_d[key], options=["", "1", "2", "3", "4", "5"])

        st.markdown("---")
        opens = S.FARMER_OPEN if kind == "ciftci" else S.BAYI_OPEN
        st.markdown("**Açık uçlu sorular**")
        for key, lab in opens.items():
            rec[key] = st.text_area(lab, key=f"{kind}_{key}")

        submitted = st.form_submit_button("💾 Kaydı Ekle", use_container_width=True, type="primary")

    if submitted:
        if kind == "ciftci":
            rec["arazi_tipi"] = arazi_tipi  # form dışında seçildiği için buraya ekleniyor
        if kind == "ciftci" and (not rec.get("yas_grubu") or not rec.get("egitim") or not rec.get("ilce") or not arazi_tipi):
            st.error("Zorunlu alanlar (Yaş, Eğitim, İlçe, Arazi Tipi) boş bırakılamaz.")
        else:
            rec = {k: ("" if v is None else str(v).strip()) for k, v in rec.items()}
            rid = D.add_record(kind, rec)
            st.success(f"✅ Kayıt eklendi — Kayıt No: **{rid}**")
            st.rerun()

# ========================================================== KAYITLAR
with tab_records:
    view = st.radio("Görüntülenecek kayıtlar", ["Çiftçi", "Bayi"], horizontal=True)
    kind = "ciftci" if view == "Çiftçi" else "bayi"
    df = CDF if kind == "ciftci" else BDF

    c1, c2, c3 = st.columns([2, 1.4, 1.2])
    with c1:
        st.metric(f"{view} kayıt sayısı", len(df))
    with c2:
        if st.button("🧪 60 çiftçi + 10 bayi örnek verisi yükle", disabled=(kind == "bayi")):
            n0 = len(D.load_df("ciftci"))
            m0 = len(D.load_df("bayi"))
            for row in DEMO.generate_ciftci(60):
                D.add_record("ciftci", row)
            for row in DEMO.generate_bayi(10):
                D.add_record("bayi", row)
            st.success("Örnek veriler eklendi.")
            st.rerun()
    with c3:
        dl = st.download_button(
            "⬇️ Excel indir", D.to_excel_bytes(),
            file_name=f"anket_{kind}_veri.xlsx", mime="xlsx",
        )

    if len(df) == 0:
        empty_state("Kayıt yok.")
    else:
        st.markdown("**Kayıt düzenleme / silme**")
        ids = ["—"] + list(df["kayit_id"].astype(str))
        edit_id = st.selectbox("Kayıt No seçin", ids)
        label_map = S.label_map(kind)

        if edit_id != "—":
            row = D.get_record(kind, edit_id)
            with st.expander(f"Kayıt No {edit_id} — tüm alanlar", expanded=True):
                with st.form(f"edit_{kind}_{edit_id}"):
                    upd = {}
                    for c in S.all_columns(kind):
                        val = str(row.get(c, "") or "")
                        if S.is_likert(kind, c):
                            upd[c] = st.select_slider(label_map.get(c, c),
                                                      options=["", "1", "2", "3", "4", "5"],
                                                      value=val if val in ("", "1", "2", "3", "4", "5") else "")
                        elif S.is_multi(kind, c):
                            opts = S.multi_options(kind, c)
                            cur = [x.strip() for x in val.split(",") if x.strip()]
                            cur = [x for x in cur if x in opts] + [x for x in cur if x not in opts]
                            sel = st.multiselect(label_map.get(c, c), opts + [x for x in cur if x not in opts],
                                                 default=cur, key=f"ed_{c}")
                            upd[c] = ", ".join(sel)
                        else:
                            upd[c] = st.text_input(label_map.get(c, c), value=val, key=f"ed_{c}")
                    ok = st.form_submit_button("💾 Güncelle", type="primary")
                if ok:
                    upd = {k: str(v).strip() for k, v in upd.items()}
                    D.update_record(kind, edit_id, upd)
                    st.success("Kayıt güncellendi.")
                    st.rerun()

            if st.button(f"🗑 Bu kaydı sil ({edit_id})"):
                D.delete_records(kind, [edit_id])
                st.success(f"Kayıt {edit_id} silindi.")
                st.rerun()

            if st.button("🗑 TÜM kayıtları sil", type="secondary"):
                D.save_df(kind, pd.DataFrame(columns=D.STORE_COLS[kind]))
                st.success("Tüm kayıtlar silindi.")
                st.rerun()

        st.divider()
        st.markdown("**Kayıt tablosu (ilk 60 kolon)**")
        st.dataframe(df.head(200), use_container_width=True, height=420)

# ========================================================== TEK DEĞİŞKEN
with tab_freq:
    st.header("📊 Tek Değişkenli Analiz")
    if N_C == 0 and N_B == 0:
        empty_state("Önce veri girin.")
    else:
        scope = st.radio("Anket", ["Çiftçi", "Bayi"], horizontal=True)
        kind = "ciftci" if scope == "Çiftçi" else "bayi"
        df = CDF if kind == "ciftci" else BDF
        if len(df) == 0:
            empty_state(f"{scope} kaydı yok.")
        else:
            labels = S.label_map(kind)
            singles = list(S.FARMER_SINGLE) if kind == "ciftci" else list(S.BAYI_SINGLE)
            multis = list(S.FARMER_MULTI) if kind == "ciftci" else list(S.BAYI_MULTI)
            choice = st.selectbox("Soru seçin", singles + multis, format_func=lambda c: labels.get(c, c))

            if S.is_multi(kind, choice):
                tab = A.multi_frequency(df, choice, kind)
                if tab.empty:
                    empty_state("Bu soruda yanıt yok.")
                else:
                    c1, c2 = st.columns([2, 3])
                    c1.dataframe(tab, use_container_width=True)
                    fig = px.bar(tab.reset_index(), x="Seçim Sayısı", y="Seçenek", orientation="h",
                                 text="Seçim Sayısı", color="Seçenek", color_discrete_sequence=PALETTE)
                    fig.update_yaxes(autorange="reversed")
                    style_fig(fig, x_title="Seçim sayısı", title=f"{labels.get(choice, choice)} — seçenek seçim sayıları")
                    c2.plotly_chart(fig, use_container_width=True)
            else:
                order = S.cat_order(kind, choice)
                tab = A.frequency_table(df, choice, kind, order)
                if tab.empty:
                    empty_state("Bu soruda yanıt yok.")
                else:
                    c1, c2 = st.columns([2, 3])
                    c1.dataframe(tab, use_container_width=True)
                    fig = px.bar(x=tab.index, y=tab["Kişi Sayısı"], text=tab["Yüzde (%)"].astype(str) + "%",
                                 color=tab.index, color_discrete_sequence=PALETTE)
                    style_fig(fig, y_title="Kişi sayısı", x_title=labels.get(choice, choice),
                              title=f"{labels.get(choice, choice)} dağılımı")
                    c2.plotly_chart(fig, use_container_width=True)
                    figp = px.pie(values=tab["Kişi Sayısı"], names=tab.index, hole=0.4, color_discrete_sequence=PALETTE)
                    style_fig(figp, title="Yüzde dağılımı")
                    c2.plotly_chart(figp, use_container_width=True)

# ========================================================== ÇAPRAZ ANALİZ
with tab_cross:
    st.header("🔀 Çapraz Analiz (Ki-Kare + Cramér's V)")
    if N_C == 0 and N_B == 0:
        empty_state("Önce veri girin.")
    else:
        scope = st.radio("Anket", ["Çiftçi", "Bayi"], horizontal=True, key="cross_scope")
        kind = "ciftci" if scope == "Çiftçi" else "bayi"
        df = CDF if kind == "ciftci" else BDF
        if len(df) == 0:
            empty_state(f"{scope} kaydı yok.")
        else:
            labels = S.label_map(kind)
            singles = list(S.FARMER_SINGLE) if kind == "ciftci" else list(S.BAYI_SINGLE)
            multis = list(S.FARMER_MULTI) if kind == "ciftci" else list(S.BAYI_MULTI)
            all_cat = singles + multis

            def fmt(c):
                return labels.get(c, c) + (" (çoklu)" if S.is_multi(kind, c) else "")

            rc1, rc2 = st.columns(2)
            row_col = rc1.selectbox("Satır değişkeni", all_cat, index=0 if kind == "ciftci" else 2, format_func=fmt)
            col_col = rc2.selectbox("Sütun değişkeni", all_cat, index=min(2, len(all_cat) - 1), format_func=fmt)

            if row_col == col_col:
                st.warning("Farklı iki değişken seçin.")
            else:
                def multi_cat_df(dfin, col, kind_):
                    """Çoklu kolonu kayıt bazında tek satıra genişletir (seçim başına satır çoğaltma)."""
                    if not S.is_multi(kind_, col):
                        return dfin[["kayit_id", col]].rename(columns={col: "deger"})
                    rows = []
                    for _, r in dfin.iterrows():
                        parts = [p.strip() for p in str(r[col]).split(",") if p.strip()]
                        for p in parts:
                            rows.append({"kayit_id": r["kayit_id"], "deger": p})
                    return pd.DataFrame(rows)

                # Çoklu değişkenleri 'seçim başına' genişletip kayıt id üzerinden birleştir
                ra = multi_cat_df(df, row_col, kind)
                ca = multi_cat_df(df, col_col, kind)
                merged = ra.merge(ca, on="kayit_id", suffixes=("_r", "_c"))
                tab = pd.crosstab(merged["deger_r"], merged["deger_c"])
                ro = S.cat_order(kind, row_col)
                co = S.cat_order(kind, col_col)
                if ro:
                    tab = tab.reindex([x for x in ro if x in tab.index])
                if co:
                    tab = tab[[x for x in co if x in tab.columns]]

                if tab.empty:
                    empty_state("Seçilen değişkenlerde ortak yanıt yok.")
                else:
                    pct_disp = st.radio("Tablo görünümü", ["Kişi Sayısı", "Satır %", "Sütun %"], horizontal=True)
                    disp = A.crosstab_pct(tab, pct_disp.split()[0].lower()) if pct_disp != "Kişi Sayısı" else tab
                    st.markdown(f"**{fmt(row_col)} × {fmt(col_col)}** — {pct_disp}")
                    st.dataframe(disp, use_container_width=True)

                    fig = px.imshow(disp, text_auto=".1f" if pct_disp != "Kişi Sayısı" else True,
                                    color_continuous_scale="Blues", aspect="auto")
                    style_fig(fig, title="Çapraz tablo ısı haritası")
                    st.plotly_chart(fig, use_container_width=True)

                    # Yığılmış yüzde grafiği
                    pctr = A.crosstab_pct(tab, "row")
                    figb = go.Figure()
                    for i, cn in enumerate(pctr.columns):
                        figb.add_trace(go.Bar(
                            name=str(cn), x=pctr.index.astype(str), y=pctr[cn],
                            marker_color=PALETTE[i % len(PALETTE)], text=pctr[cn].round(0).astype(int).astype(str) + "%",
                            textposition="inside"))
                    figb.update_layout(barmode="stack")
                    style_fig(figb, y_title="Satır yüzdesi (%)", x_title=fmt(row_col),
                              title=f"{fmt(col_col)} dağılımı — {fmt(row_col)} kırılımında",
                              legend_title=fmt(col_col))
                    st.plotly_chart(figb, use_container_width=True)

                    # Ki-kare testi
                    res = A.chi2_test(tab)
                    if res is None:
                        st.info("Ki-kare testi için yeterli kategori yok (her değişkende en az 2 kategori gerekli).")
                    else:
                        st.subheader("İstatistiksel testler")
                        note = ""
                        if res["low_expected_pct"] > 20:
                            note = (" ⚠️ Beklenen kişi sayılarının **%.0f%%**'i 5'in altında: ki-kare yaklaşımı zayıf; "
                                    "kategori birleştirme veya Fisher tarzı kesin test düşünün."
                                    % res["low_expected_pct"])
                        k1, k2, k3, k4, k5 = st.columns(5)
                        k1.metric("χ²", f"{res['chi2']:.2f}")
                        k2.metric("sd", res["dof"])
                        k3.metric("p değeri", f"{res['p']:.4f}")
                        k4.metric("Cramér's V", f"{res['cramers_v']:.3f}")
                        k5.metric("n", res["n"])
                        verdict = " ✅ Anlamlı ilişki (p < 0.05)" if res["p"] < 0.05 else " ⛔ Anlamlı ilişki bulunamadı (p ≥ 0.05)"
                        st.markdown(f"**Sonuç:** {verdict}{note}")
                        strength = ("ihmal edilebilir" if res["cramers_v"] < 0.1 else
                                    "zayıf" if res["cramers_v"] < 0.2 else
                                    "orta" if res["cramers_v"] < 0.4 else "güçlü")
                        st.markdown(f"Cramér's V yorumu: **{strength}** ilişki.")
                        with st.expander("Beklenen kişi sayıları (iki değişken bağımsız olsaydı beklenen dağılım)"):
                            st.dataframe(res["expected"].round(1), use_container_width=True)

# ========================================================== SAYISAL × GRUP
with tab_num:
    st.header("📈 Sayısal Değişken × Kategori Karşılaştırması")
    if N_C == 0 and N_B == 0:
        empty_state("Önce veri girin.")
    else:
        scope = st.radio("Anket", ["Çiftçi", "Bayi"], horizontal=True, key="num_scope")
        kind = "ciftci" if scope == "Çiftçi" else "bayi"
        df = CDF if kind == "ciftci" else BDF
        if len(df) == 0:
            empty_state(f"{scope} kaydı yok.")
        else:
            labels = S.label_map(kind)
            num_cols = ([c for c, _, _ in S.FARMER_NUMERIC] if kind == "ciftci"
                        else [c for c, _, _ in S.BAYI_NUMERIC])
            num_cols += S.likert_columns(kind)
            num_cols = [c for c in num_cols if c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().sum() >= 3]
            cat_cols = (list(S.FARMER_SINGLE) if kind == "ciftci" else list(S.BAYI_SINGLE))

            c1, c2 = st.columns(2)
            num_col = c1.selectbox("Sayısal değişken", num_cols, format_func=lambda c: labels.get(c, c))
            cat_col = c2.selectbox("Grup değişkeni", cat_cols, format_func=lambda c: labels.get(c, c))

            if num_col and cat_col:
                stats_tab, _ = A.group_numeric_stats(df, num_col, cat_col, kind)
                if stats_tab.empty:
                    empty_state("Yeterli veri yok.")
                else:
                    st.markdown(f"**{labels.get(num_col, num_col)}** — **{labels.get(cat_col, cat_col)}** gruplarına göre")
                    st.dataframe(stats_tab.round(2), use_container_width=True)

                    # Testler
                    x = pd.to_numeric(df[num_col], errors="coerce")
                    g = df[cat_col].astype(str).str.strip()
                    groups = {name: x[g == name].dropna().values for name in g[g != ""].unique()}
                    tests = A.group_tests(groups)
                    if tests:
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("ANOVA F", f"{tests['anova_F']:.2f}" if not np.isnan(tests['anova_F']) else "—")
                        m2.metric("ANOVA p", f"{tests['anova_p']:.4f}" if not np.isnan(tests['anova_p']) else "—")
                        m3.metric("Kruskal-Wallis H", f"{tests['kruskal_H']:.2f}" if not np.isnan(tests['kruskal_H']) else "—")
                        m4.metric("KW p", f"{tests['kruskal_p']:.4f}" if not np.isnan(tests['kruskal_p']) else "—")
                        sig = (not np.isnan(tests["anova_p"]) and tests["anova_p"] < 0.05) or \
                              (not np.isnan(tests["kruskal_p"]) and tests["kruskal_p"] < 0.05)
                        st.markdown("**Sonuç:** " + (" ✅ Gruplar arasında anlamlı fark var (p < 0.05)."
                                                     if sig else " ⛔ Gruplar arasında anlamlı fark bulunamadı (p ≥ 0.05)."))

                    fig = px.box(df, x=cat_col, y=num_col, color=cat_col, points="all",
                                 color_discrete_sequence=PALETTE)
                    style_fig(fig, y_title=labels.get(num_col, num_col), x_title=labels.get(cat_col, cat_col),
                              title=f"{labels.get(num_col, num_col)} — {labels.get(cat_col, cat_col)} kırılımında (kutu grafiği)")
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                    figv = px.violin(df, x=cat_col, y=num_col, color=cat_col,
                                     color_discrete_sequence=PALETTE, box=True)
                    style_fig(figv, y_title=labels.get(num_col, num_col), x_title=labels.get(cat_col, cat_col),
                              title="Keman grafiği")
                    figv.update_layout(showlegend=False)
                    st.plotly_chart(figv, use_container_width=True)

            st.divider()
            st.subheader("Sayısal değişkenlerin betimsel istatistikleri")
            present = [c for c in num_cols]
            desc = A.numeric_summary(df, present)
            if desc.empty:
                empty_state("Henüz sayısal veri girilmemiş.")
            else:
                st.dataframe(desc, use_container_width=True)

# ========================================================== KORELASYON
with tab_corr:
    st.header("🔗 Korelasyon Analizi")
    if N_C == 0:
        empty_state("Korelasyon analizi için çiftçi verisi gerekli.")
    else:
        labels = S.label_map("ciftci")
        num_cols = [c for c, _, _ in S.FARMER_NUMERIC]
        num_cols += ["servis_memnuniyet_puani"]
        num_cols = [c for c in num_cols if c in CDF.columns and pd.to_numeric(CDF[c], errors="coerce").notna().sum() >= 5]
        method = st.radio("Yöntem", ["Pearson", "Spearman"], horizontal=True)
        default = [c for c in ["makine_yas", "yillik_kullanim_saati", "ariza_sikligi", "ariza_suresi",
                               "bakim_gideri", "onarim_gideri", "yakit_tuketimi", "kullanilabilirlik",
                               "yedek_parca_suresi", "servis_mudahale_suresi"] if c in num_cols]
        selected = st.multiselect("Değişkenler (en az 2)", num_cols, default=default,
                                  format_func=lambda c: labels.get(c, c))
        if len(selected) < 2:
            empty_state("En az 2 değişken seçin.")
        else:
            corr, pmat = A.correlation_matrix(CDF, selected, method.lower())
            if corr.empty:
                empty_state("Yeterli ortak gözlem yok.")
            else:
                disp = corr.copy()
                disp.index = [labels.get(c, c) for c in disp.index]
                disp.columns = [labels.get(c, c) for c in disp.columns]
                fig = px.imshow(disp, text_auto=".2f", zmin=-1, zmax=1,
                                color_continuous_scale="RdBu_r", aspect="auto")
                style_fig(fig, title=f"{method} korelasyon matrisi")
                st.plotly_chart(fig, use_container_width=True)

                rows = []
                for i, a in enumerate(corr.index):
                    for j, b in enumerate(corr.columns):
                        if j > i and not np.isnan(corr.loc[a, b]):
                            p = pmat.loc[a, b]
                            rows.append({
                                "Değişken 1": labels.get(a, a), "Değişken 2": labels.get(b, b),
                                "r": round(corr.loc[a, b], 3),
                                "p": round(p, 4) if not np.isnan(p) else np.nan,
                                "Anlamlılık": ("p<0.01 **" if (not np.isnan(p) and p < 0.01) else
                                               "p<0.05 *" if (not np.isnan(p) and p < 0.05) else "ns"),
                            })
                corr_tab = pd.DataFrame(rows).sort_values("r", key=lambda s: s.abs(), ascending=False)
                st.markdown("**Eşleşme tablosu (|r|'ye göre sıralı)**")
                st.dataframe(corr_tab, use_container_width=True)
                st.caption("r > 0.7: güçlü · 0.3–0.7: orta · < 0.3: zayıf ilişki. p < 0.05 anlamlı kabul edilir.")

                c1, c2 = st.columns(2)
                pick1 = c1.selectbox("X değişkeni (serpme)", selected, format_func=lambda c: labels.get(c, c))
                pick2 = c2.selectbox("Y değişkeni (serpme)", selected, index=min(1, len(selected) - 1),
                                     format_func=lambda c: labels.get(c, c))
                if pick1 != pick2:
                    sx = pd.to_numeric(CDF[pick1], errors="coerce")
                    sy = pd.to_numeric(CDF[pick2], errors="coerce")
                    scat = pd.DataFrame({"x": sx, "y": sy}).dropna()
                    figs = px.scatter(scat, x="x", y="y")
                    if len(scat) >= 3:
                        coef = np.polyfit(scat["x"], scat["y"], 1)
                        xs = np.array([scat["x"].min(), scat["x"].max()])
                        r_val = np.corrcoef(scat["x"], scat["y"])[0, 1]
                        figs.add_scatter(x=xs, y=coef[0] * xs + coef[1], mode="lines",
                                         name=f"Eğilim (r = {r_val:.2f})", line=dict(color="red", dash="dash"))
                    style_fig(figs, x_title=labels.get(pick1, pick1), y_title=labels.get(pick2, pick2),
                              title=f"{labels.get(pick1, pick1)} × {labels.get(pick2, pick2)}")
                    st.plotly_chart(figs, use_container_width=True)

# ========================================================== LİKERT
with tab_likert:
    st.header("🧾 Likert Ölçekleri ve Güvenilirlik")
    if N_C == 0 and N_B == 0:
        empty_state("Önce veri girin.")
    else:
        scope = st.radio("Anket", ["Çiftçi", "Bayi"], horizontal=True, key="lik_scope")
        kind = "ciftci" if scope == "Çiftçi" else "bayi"
        df = CDF if kind == "ciftci" else BDF
        if len(df) == 0:
            empty_state(f"{scope} kaydı yok.")
        else:
            groups = S.likert_groups(kind)
            for gname, cols_d in groups.items():
                cols = list(cols_d)
                st.subheader(gname)
                dist = A.likert_distribution(df, cols, kind)
                if dist.empty:
                    empty_state("Bu grupta yanıt yok.")
                    continue
                st.dataframe(dist, use_container_width=True)

                # 100% yığılmış çubuk
                mlong = dist.melt(id_vars=["Madde"], value_vars=[str(v) for v in range(1, 6)],
                                  var_name="Puan", value_name="Yüzde")
                fig = px.bar(mlong, x="Madde", y="Yüzde", color="Puan", barmode="stack",
                             category_orders={"Puan": [str(v) for v in range(1, 6)]},
                             color_discrete_sequence=px.colors.diverging.RdYlGn[::-1])
                style_fig(fig, y_title="Yüzde (%)", title=f"{gname} — madde puan dağılımları (%)")
                fig.update_xaxes(tickangle=-15)
                st.plotly_chart(fig, use_container_width=True)

                alpha, n_used = A.cronbach_alpha(df[cols])
                st.markdown(
                    f"**Cronbach α = {alpha:.3f}** (n = {n_used}) — " +
                    ("çok güvenilir" if alpha >= 0.9 else "yüksek güvenilirlik" if alpha >= 0.8 else
                     "kabul edilebilir güvenilirlik" if alpha >= 0.7 else
                     "şüpheli (revizyon düşünülebilir)" if alpha >= 0.6 else "düşük güvenilirlik")
                    if not np.isnan(alpha) else "Cronbach α hesaplanamadı (yeterli veri yok).")
                st.divider()

            if kind == "ciftci":
                st.subheader("Ölçek puanları × demografik özet")
                scores = A.scale_scores(df, "ciftci")
                if not scores.empty:
                    smean = scores.mean().round(2)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Teknik Hizmet (1–5)", smean.get("tek_puan", "—"))
                    c2.metric("Ekonomik Boyut (1–5)", smean.get("eko_puan", "—"))
                    c3.metric("Memnuniyet (1–5)", smean.get("mem_puan", "—"))
                    gcol = st.selectbox("Kırılım", ["yas_grubu", "egitim", "ilce", "arazi_sinifi"],
                                        format_func=lambda c: S.label_map("ciftci").get(c, c))
                    tmp = pd.concat([df[["kayit_id", gcol]], scores.reset_index(drop=True)], axis=1)
                    gm = tmp.melt(id_vars=[gcol], value_vars=list(S.scale_defs("ciftci").keys()),
                                  var_name="Ölçek", value_name="Puan").dropna()
                    gm["Ölçek"] = gm["Ölçek"].map(S.scale_labels("ciftci"))
                    fig = px.bar(gm, x=gcol, y="Puan", color="Ölçek", barmode="group",
                                 color_discrete_sequence=PALETTE)
                    style_fig(fig, y_title="Ortalama ölçek puanı", x_title=S.label_map("ciftci").get(gcol, gcol),
                              title="Ölçek puanlarının demografik kırılımı", legend_title="Ölçek")
                    st.plotly_chart(fig, use_container_width=True)

# ========================================================== BAYİ ANALİZİ
with tab_bayi:
    st.header("🏭 Bayi Anketi Analizi")
    if N_B == 0:
        empty_state("Bayi kaydı yok. **📝 Veri Girişi** sekmesinden ekleyin.")
    else:
        labels = S.label_map("bayi")
        st.subheader("Firma profili")
        c1, c2 = st.columns(2)
        with c1:
            f1 = A.frequency_table(BDF, "yillik_satis", "bayi", S.cat_order("bayi", "yillik_satis"))
            fig = px.pie(values=f1["Kişi Sayısı"], names=f1.index, hole=0.4, color_discrete_sequence=PALETTE)
            style_fig(fig, title="Yıllık satış miktarı aralıkları")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            f2 = A.frequency_table(BDF, "urun_yonelim", "bayi", S.cat_order("bayi", "urun_yonelim"))
            fig = px.bar(x=f2.index, y=f2["Kişi Sayısı"], color=f2.index, color_discrete_sequence=PALETTE)
            style_fig(fig, y_title="Bayi sayısı", title="Satışların yönlendiği ürün")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Çoklu seçim soruları")
        for key in ["acma_nedeni", "satilan_makineler", "musteri_ilceler", "sorunlar", "gelecek_gorusler"]:
            tab = A.multi_frequency(BDF, key, "bayi")
            if tab.empty:
                continue
            with st.expander(f"{labels.get(key, key)}"):
                c1, c2 = st.columns([2, 3])
                c1.dataframe(tab, use_container_width=True)
                fig = px.bar(tab.reset_index(), x="Seçim Sayısı", y="Seçenek", orientation="h",
                             text="Seçim Sayısı", color="Seçenek", color_discrete_sequence=PALETTE)
                fig.update_yaxes(autorange="reversed")
                style_fig(fig, x_title="Seçim sayısı", title=labels.get(key, key))
                c2.plotly_chart(fig, use_container_width=True)

        st.subheader("Satış Sonrası Hizmet değerlendirmesi")
        dist = A.likert_distribution(BDF, S.likert_columns("bayi"), "bayi")
        if not dist.empty:
            st.dataframe(dist, use_container_width=True)
            alpha, _ = A.cronbach_alpha(BDF[S.likert_columns("bayi")])
            if not np.isnan(alpha):
                st.markdown(f"**Cronbach α = {alpha:.3f}**")

# ========================================================== AÇIK UÇLU
with tab_open:
    st.header("💬 Açık Uçlu Yanıtlar")
    scope = st.radio("Anket", ["Çiftçi", "Bayi"], horizontal=True, key="open_scope")
    kind = "ciftci" if scope == "Çiftçi" else "bayi"
    df = CDF if kind == "ciftci" else BDF
    opens = S.FARMER_OPEN if kind == "ciftci" else S.BAYI_OPEN
    if len(df) == 0:
        empty_state("Kayıt yok.")
    else:
        for key, lab in opens.items():
            if key not in df.columns:
                continue
            answers = df[["kayit_id", key]].copy()
            answers = answers[answers[key].astype(str).str.strip() != ""]
            with st.expander(f"{lab} ({len(answers)} yanıt)"):
                for _, r in answers.iterrows():
                    st.markdown(f"- **#{r['kayit_id']}** — {r[key]}")

st.sidebar.markdown("---")
st.sidebar.caption(
    "Veriler `anket_analiz/data/` klasöründe CSV olarak saklanır. "
    "Uygulamayı yeniden başlatın: `streamlit run app.py`")
