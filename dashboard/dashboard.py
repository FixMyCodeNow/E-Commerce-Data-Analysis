import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")
sns.set_theme(style="whitegrid", palette="muted")

st.markdown("""
<div style="background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);
     padding:2rem 2.5rem;border-radius:16px;margin-bottom:1.5rem;">
  <h1 style="color:#e94560;margin:0;font-size:2.2rem;">🛒 E-Commerce Public Dataset</h1>
  <p style="color:#a8b2d8;margin:0.4rem 0 0;font-size:1rem;">
    Analisis Data Interaktif · Satriyo Akbar Maulana · 2017–2018
  </p>
</div>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    import os
    path = "dashboard/main_data.csv" if os.path.exists("dashboard/main_data.csv") else "main_data.csv"
    df = pd.read_csv(path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
    df["is_late"] = df["is_late"].astype(bool)
    return df


df = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Filter")
    years = sorted(df["purchase_year"].dropna().unique().astype(int))
    years = [y for y in years if y >= 2017]
    sel_years = st.multiselect("Tahun", years, default=years)
    sel_cat   = st.multiselect("Kategori", df["main_category"].dropna().unique(), default=df["main_category"].dropna().unique())
    sel_states = st.multiselect("Negara Bagian", df["customer_state"].dropna().unique(), default=df["customer_state"].dropna().unique())
    sel_months = st.multiselect("Bulan", df["purchase_ym"].dropna().unique(), default=df["purchase_ym"].dropna().unique())
    min_payment = st.number_input("Pembayaran Minimum", min_value=0, value=0)
    top_n     = st.slider("Top N Kategori", 5, 20, 10)
    st.markdown("---")
    st.caption("Satriyo Akbar Maulana\nDicoding · 2024")

dff = df[
    (df["purchase_year"].isin(sel_years)) &
    (df["main_category"].isin(sel_cat)) &
    (df["customer_state"].isin(sel_states)) &
    (df["purchase_ym"].isin(sel_months)) &
    (df["payment_value"] >= min_payment)
].copy()

if dff.empty:
    st.warning("Data kosong, silakan ubah filter.")
    st.stop()

# ── KPI ────────────────────────────────────────────────────────────────────────
st.subheader("📊 Key Metrics")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Orders",      f"{len(dff):,}")
c2.metric("Total Revenue",     f"R$ {dff['payment_value'].sum()/1e6:.2f}M")
c3.metric("Avg Delivery Days", f"{dff['delivery_days'].mean():.1f} hari")
c4.metric("Keterlambatan",     f"{dff['is_late'].mean()*100:.1f}%")
c5.metric("Avg Review Score",  f"{dff['review_score'].mean():.2f} ⭐")
st.markdown("---")

st.caption(
    f"Filter aktif → Tahun: {sel_years} | Kategori: {len(sel_cat)} | State: {len(sel_states)} | Bulan: {len(sel_months)} | Pembayaran Minimum: R$ {min_payment:,.0f}"
)

# ══════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 1 — Revenue per Kategori
# ══════════════════════
st.info("**Kategori produk apa yang menghasilkan total pendapatan tertinggi (2017–2018)?**")

rev_cat = (
    dff.groupby("main_category")["item_price"]
    .sum().sort_values(ascending=False).reset_index()
)
rev_cat.columns = ["category", "total_revenue"]
rev_cat["revenue_pct"] = rev_cat["total_revenue"] / rev_cat["total_revenue"].sum() * 100
top_n_df = rev_cat.head(top_n)

col_a, col_b = st.columns([3, 2])
with col_a:
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = sns.color_palette("Blues_d", len(top_n_df))[::-1]
    ax.barh(top_n_df["category"][::-1], top_n_df["total_revenue"][::-1], color=colors)
    ax.set_xlabel("Total Revenue (BRL)")
    ax.set_title(f"Top {top_n} Kategori Produk by Revenue", fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"R${x/1e3:.0f}K"))
    for i, val in enumerate(top_n_df["total_revenue"][::-1]):
        ax.text(val+500, i, f"R${val/1e3:.0f}K", va="center", fontsize=8)
    ax.set_xlim(0, top_n_df["total_revenue"].max()*1.22)
    fig.tight_layout(); st.pyplot(fig); plt.close()

with col_b:
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    others   = rev_cat.iloc[top_n:]["total_revenue"].sum()
    pie_vals = list(top_n_df["total_revenue"]) + [others]
    pie_labs = list(top_n_df["category"]) + ["Others"]
    _, _, autos = ax2.pie(pie_vals, autopct="%1.1f%%",
        colors=sns.color_palette("tab20", len(pie_vals)),
        startangle=140, pctdistance=0.82, wedgeprops=dict(width=0.6), labels=None)
    for a in autos: a.set_fontsize(7)
    ax2.legend(pie_labs, loc="lower center", bbox_to_anchor=(0.5,-0.35), ncol=2, fontsize=7)
    ax2.set_title("Proporsi Revenue", fontweight="bold")
    fig2.tight_layout(); st.pyplot(fig2); plt.close()

with st.expander("📋 Tabel Revenue per Kategori"):
    show = rev_cat.copy()
    show["total_revenue"] = show["total_revenue"].map(lambda x: f"R$ {x:,.0f}")
    show["revenue_pct"]   = show["revenue_pct"].map(lambda x: f"{x:.2f}%")
    show.columns = ["Kategori Produk", "Total Revenue", "Kontribusi (%)"]
    st.dataframe(show.reset_index(drop=True), use_container_width=True)

st.success("✅ **Kesimpulan:** `health_beauty` revenue tertinggi. Top 10 kategori menyumbang >55% total pendapatan.")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 2 — Keterlambatan vs Review Score
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## ❓ Pertanyaan 2")
st.info("**Bagaimana tren waktu pengiriman & apakah keterlambatan berpengaruh terhadap review score?**")

monthly = (
    dff.groupby("purchase_ym").agg(
        avg_delivery=("delivery_days","mean"),
        avg_score=("review_score","mean"),
        total_orders=("order_id","count"),
        late_orders=("is_late","sum"),
    ).reset_index().sort_values("purchase_ym")
)

tab1, tab2, tab3 = st.tabs(["📈 Tren Bulanan", "📦 On-Time vs Terlambat", "🗓️ Delay Bucket"])

with tab1:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    fig.suptitle("Tren Pengiriman & Review Score per Bulan", fontweight="bold")

    ax1.plot(monthly["purchase_ym"], monthly["avg_delivery"], marker="o", color="steelblue", lw=2)
    ax1.fill_between(monthly["purchase_ym"], monthly["avg_delivery"], alpha=0.12, color="steelblue")
    ax1.axhline(monthly["avg_delivery"].mean(), color="red", ls="--", alpha=0.6,
                label=f'Mean: {monthly["avg_delivery"].mean():.1f} hari')
    ax1.set_ylabel("Avg Delivery Days"); ax1.legend(fontsize=9); ax1.tick_params(axis="x", rotation=45)

    ax2.plot(monthly["purchase_ym"], monthly["avg_score"], marker="s", color="seagreen", lw=2)
    ax2.fill_between(monthly["purchase_ym"], monthly["avg_score"], alpha=0.12, color="seagreen")
    ax2.axhline(monthly["avg_score"].mean(), color="red", ls="--", alpha=0.6,
                label=f'Mean: {monthly["avg_score"].mean():.2f}')
    ax2.set_ylabel("Avg Review Score (1–5)"); ax2.set_ylim(3.2, 4.8)
    ax2.legend(fontsize=9); ax2.tick_params(axis="x", rotation=45)

    fig.tight_layout(); st.pyplot(fig); plt.close()

    c1, c2, c3 = st.columns(3)
    c1.metric("Pengiriman Tercepat (avg)", f'{monthly["avg_delivery"].min():.1f} hari',
              monthly.loc[monthly["avg_delivery"].idxmin(),"purchase_ym"])
    c2.metric("Pengiriman Terlama (avg)",  f'{monthly["avg_delivery"].max():.1f} hari',
              monthly.loc[monthly["avg_delivery"].idxmax(),"purchase_ym"])
    c3.metric("Best Review Month", f'{monthly["avg_score"].max():.2f} ⭐',
              monthly.loc[monthly["avg_score"].idxmax(),"purchase_ym"])

with tab2:
    late_s   = dff[dff["is_late"]]["review_score"].dropna()
    ontime_s = dff[~dff["is_late"]]["review_score"].dropna()

    fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 5))
    bp = ax3.boxplot([ontime_s, late_s], labels=["On-Time","Terlambat"],
                     patch_artist=True, medianprops=dict(color="black", lw=2))
    bp["boxes"][0].set_facecolor("#3498db")
    bp["boxes"][1].set_facecolor("#e74c3c")
    ax3.set_ylabel("Review Score"); ax3.set_title("Distribusi Review Score")
    ax3.text(1, ontime_s.median()+0.05, f'Median: {ontime_s.median():.0f}',
             ha="center", fontsize=9, color="#3498db", fontweight="bold")
    ax3.text(2, late_s.median()-0.35,   f'Median: {late_s.median():.0f}',
             ha="center", fontsize=9, color="#e74c3c", fontweight="bold")

    x = np.arange(5); w = 0.35
    ax4.bar(x-w/2, [ontime_s.value_counts().get(i,0) for i in [1,2,3,4,5]], w,
            label="On-Time", color="#3498db", alpha=0.85)
    ax4.bar(x+w/2, [late_s.value_counts().get(i,0)   for i in [1,2,3,4,5]], w,
            label="Terlambat", color="#e74c3c", alpha=0.85)
    ax4.set_xticks(x); ax4.set_xticklabels(["⭐1","⭐2","⭐3","⭐4","⭐5"])
    ax4.set_title("Frekuensi Score per Status"); ax4.legend()
    ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    fig.tight_layout(); st.pyplot(fig); plt.close()

    c1, c2 = st.columns(2)
    c1.metric("Avg Score — On-Time",   f"{ontime_s.mean():.2f} ⭐")
    c2.metric("Avg Score — Terlambat", f"{late_s.mean():.2f} ⭐",
              f"{late_s.mean()-ontime_s.mean():.2f}")

with tab3:
    delay_score = (
        dff.groupby("delay_bucket", observed=False)["review_score"]
        .agg(["mean","count"]).reset_index()
    )
    delay_score.columns = ["delay_bucket","avg_score","count"]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(delay_score["delay_bucket"], delay_score["avg_score"],
                  color=["#27ae60","#2ecc71","#f1c40f","#e67e22","#e74c3c","#922b21"],
                  edgecolor="white")
    ax.set_title("Rata-Rata Review Score per Tingkat Keterlambatan", fontweight="bold")
    ax.set_ylabel("Avg Review Score"); ax.set_ylim(0, 5.8)
    for bar, val, cnt in zip(bars, delay_score["avg_score"], delay_score["count"]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.06,
                f"{val:.2f}\n(n={cnt:,})", ha="center", fontsize=9, fontweight="bold")
    ax.tick_params(axis="x", labelsize=9)
    fig.tight_layout(); st.pyplot(fig); plt.close()

st.success("✅ **Kesimpulan:** Korelasi negatif kuat — on-time score ~4.3, terlambat >15 hari score ~1.8.")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# GEOSPATIAL — Sebaran Order per State
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 🗺️ Sebaran Order per State")

state_data = (
    dff.groupby("customer_state").agg(
        total_orders=("order_id","count"),
        total_revenue=("payment_value","sum"),
        avg_score=("review_score","mean"),
    ).reset_index().sort_values("total_orders", ascending=False)
)

col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    top_st = state_data.head(15)
    colors = sns.color_palette("YlOrRd", len(top_st))[::-1]
    ax.barh(top_st["customer_state"][::-1], top_st["total_orders"][::-1], color=colors)
    ax.set_title("Top 15 State by Jumlah Order", fontweight="bold")
    ax.set_xlabel("Jumlah Order")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    for i, val in enumerate(top_st["total_orders"][::-1]):
        ax.text(val+100, i, f"{val:,}", va="center", fontsize=8)
    ax.set_xlim(0, top_st["total_orders"].max()*1.18)
    fig.tight_layout(); st.pyplot(fig); plt.close()

with col2:
    fig, ax = plt.subplots(figsize=(8, 6))
    top_rv = state_data.sort_values("total_revenue", ascending=False).head(15)
    colors2 = sns.color_palette("Blues_d", len(top_rv))[::-1]
    ax.barh(top_rv["customer_state"][::-1], top_rv["total_revenue"][::-1], color=colors2)
    ax.set_title("Top 15 State by Revenue", fontweight="bold")
    ax.set_xlabel("Total Revenue (BRL)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"R${x/1e6:.1f}M"))
    for i, val in enumerate(top_rv["total_revenue"][::-1]):
        ax.text(val+1000, i, f"R${val/1e6:.2f}M", va="center", fontsize=8)
    ax.set_xlim(0, top_rv["total_revenue"].max()*1.22)
    fig.tight_layout(); st.pyplot(fig); plt.close()

with st.expander("📋 Tabel Lengkap per State"):
    show_state = state_data.copy()
    show_state["total_revenue"] = show_state["total_revenue"].map(lambda x: f"R$ {x:,.0f}")
    show_state["avg_score"]     = show_state["avg_score"].map(lambda x: f"{x:.2f} ⭐")
    show_state.columns = ["State","Total Orders","Total Revenue","Avg Review Score"]
    st.dataframe(show_state.reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.caption("© 2024 Satriyo Akbar Maulana · E-Commerce Public Dataset · Dicoding")
