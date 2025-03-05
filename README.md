# Advanced Air Quality Dashboard
## Exploring Air Quality and Weather Data 2013-2017 in Beijing, China

Dashboard ini dibuat menggunakan **Streamlit** untuk menampilkan analisis kualitas udara berdasarkan berbagai parameter seperti PM2.5, PM10, CO, AQI, dan faktor cuaca. Dashboard ini mendukung visualisasi interaktif dengan **Plotly** serta peta geografis berbasis **Map**.

---

## 📌 Cara Menjalankan Dashboard

### 1️⃣ Persiapan Awal
Pastikan Anda sudah menginstal **Python 3.7 atau lebih baru** di perangkat Anda.  
Jika belum, unduh dan instal dari [python.org](https://www.python.org/downloads/).

### 2️⃣ Clone Repository
Jika Anda belum memiliki proyek ini di perangkat lokal, unduh dengan perintah berikut:

```bash
git clone https://github.com/zidisw/AQI_Data_Analysis_with_Dashboard.git
```
```bash
cd advanced-air-quality-dashboard
```

atau dapat melakukan fork/download terhadap dataset, lalu membukanya di code editor

### 3️⃣ Buat Virtual ENvirontment (Opsional, tetapi Direkomendasikan)
#### Untuk macOS/Linux
python -m venv venv
source venv/bin/activate

#### Untuk Windows
python -m venv venv
venv\Scripts\activate

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 5️⃣ Jalankan Aplikasi
```bash
streamlit run app.py
```
