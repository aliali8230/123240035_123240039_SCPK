# SPK Kesehatan Mental Mahasiswa 🧠

Sistem Pendukung Keputusan berbasis **Logika Fuzzy Mamdani** untuk menganalisis dan meranking tingkat kesehatan mental mahasiswa berdasarkan 5 indikator utama.

---

## Fitur

- Memuat dan menampilkan dataset mahasiswa (hingga 260 baris)
- Konfigurasi batas membership function secara dinamis via slider
- Visualisasi kurva keanggotaan fuzzy (Rendah / Sedang / Tinggi)
- Perhitungan skor kesehatan mental otomatis untuk seluruh data
- Perankingan mahasiswa dari skor tertinggi ke terendah
- Distribusi kondisi mahasiswa dalam bentuk bar chart

---

## Instalasi

### 1. Clone repository

```bash
git clone https://github.com/username/spk-kesehatan-mental.git
cd spk-kesehatan-mental
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Siapkan dataset

Letakkan file CSV di folder yang sama dengan `app.py`:
