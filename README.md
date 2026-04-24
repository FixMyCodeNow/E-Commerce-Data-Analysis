# 📊 E-Commerce Public Dataset — Analisis Data
**Proyek Analisis Data Dicoding**  
Satriyo Akbar Maulana · satrioakbar357@gmail.com · CDCC254D6Y2493

---

## 📁 Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv       ← Data gabungan hasil cleaning
│   └── dashboard.py        ← Aplikasi Streamlit
├── data/
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

---

## 🚀 Cara Menjalankan Dashboard

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan Streamlit
```bash
cd submission
streamlit run dashboard/dashboard.py
```

Buka browser di **http://localhost:8501**

---

## ❓ Pertanyaan Bisnis (Metode SMART)

### Pertanyaan 1
> **Kategori produk apa yang menghasilkan total pendapatan tertinggi sepanjang 2017–2018?**

- **Specific:** Fokus pada kategori produk dan total revenue
- **Measurable:** Diukur dari nilai `price` × jumlah item per kategori
- **Achievable:** Data tersedia di `order_items_dataset` & `products_dataset`
- **Relevant:** Mendukung keputusan inventori dan strategi marketing
- **Time-bound:** Periode 2017–2018

### Pertanyaan 2
> **Bagaimana tren rata-rata waktu pengiriman per bulan dan apakah keterlambatan berpengaruh terhadap review score?**

- **Specific:** Fokus pada durasi pengiriman dan kepuasan pelanggan
- **Measurable:** Selisih tanggal aktual vs estimasi & `review_score`
- **Achievable:** Data tersedia di `orders_dataset` & `order_reviews_dataset`
- **Relevant:** Mendukung perbaikan operasional logistik
- **Time-bound:** Periode 2017–2018

---

## ✅ Kesimpulan

1. **health_beauty** adalah kategori dengan revenue tertinggi. Top 10 kategori menyumbang >55% total pendapatan.
2. Keterlambatan pengiriman berkorelasi negatif kuat dengan review score. On-time ≈ 4.3⭐, terlambat >15 hari ≈ 1.8⭐.
