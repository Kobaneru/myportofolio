# Personal Portfolio Website - PBP

Repositori ini berisi proyek website portofolio pribadi statis yang dikembangkan untuk memenuhi tugas mata kuliah **Pemrograman Berbasis Platform (CSGE602022)**, Fakultas Ilmu Komputer, Universitas Indonesia.

* **Nama:** Jonathan Sebastian Sindhu
* **NPM:** 2506619650
* **Kelas:** PBP B / Gasal 2026/2027

---

## 🚀 Panduan Menjalankan Proyek Secara Lokal

Pastikan Anda telah menginstal Python (>= 3.10) dan Git di perangkat Anda.

1. **Kloning Repositori:**
   ```bash
   git clone https://github.com/Kobaneru/myportofolio.git
   cd myportofolio
   ```

2. **Buat dan Aktifkan Virtual Environment:**
   * **Windows:**
     ```bash
     python -m venv env
     env\Scripts\activate
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv env
     source env/bin/activate
     ```

3. **Instal Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan Server Django:**
   ```bash
   python manage.py runserver
   ```
   Buka peramban dan akses alamat `http://127.0.0.1:8000/`.

---

## 📌 Log Perkembangan Proyek

### Minggu 1 (Tutorial 01 & Individual Assignment 1)
* Menginisialisasi proyek Django dan konfigurasi berkas statis (`settings.py`, `urls.py`).
* Menyusun struktur semantik HTML5 pada halaman profil (`<header>`, `<main>`, `<section>`, `<article>`, `<dl>`).
* Mengimplementasikan tata letak dua kolom pada *Hero Section* menggunakan CSS Grid.
* Menambahkan section baru *Achievements* menggunakan Flexbox berorientasi baris dan kolom.
* Menerapkan desain responsif dengan CSS Media Queries untuk layar ponsel (< 600px).

---

### Tugas 1

1. Iya, saya menggunakan tag HTML `<section>` dan `<article>`. Meski penggunaan tag di HTML tidak mengubah tampilan apa-apa, saya memilih untuk menggunakan tag-tag tersebut supaya memudahkan saya dalam melakukan tracing code ketika ingin mencari bagian kode yang ingin diubah ataupun ketika terdapat error, saya menjadi lebih mudah dalam melakukan debug kode. Selain itu, penggunaan tag tersebut juga meningkatkan aspek accessibility (memudahkan pembacaan di screen reader) serta meningkatkan SEO di browser sehingga pencarian website portofolio di browser menjadi lebih teroptimasi.

2. Tantangan utama saat berpindah dari desktop ke mobile adalah ruang horizontal yang terbatas. Navbar yang awalnya berupa flex horizontal harus diubah ke flex vertical (berisi navigasi ke Profile dan Achievements). Elemen yang harus diubah posisinya umumnya terletak di sebelah kanan website yang akan dipindahkan ke sebelah kiri bawah ketika website dibuka dari HP. Umumnya bagian text yang lebih penting seperti judul atau subjudul diprioritaskan ukurannya sehingga masih terbaca dengan mudah di HP, sedangkan informasi minor lain akan diperkecil supaya tidak mendominasi tampilan jika diperlukan. 

3. Karena website ini hanya static web, semua informasi yang ditampilkan bersifat hard-coded sehingga jika kita ingin menambahkan banyak card pada suatu section, diperlukan banyak copy-paste kode yang melanggar prinsip DRY. Karena itu, pada iterasi berikutnya, saya ingin mencoba untuk menggunakan database yang dapat menyimpan informasi/data yang ingin ditampilkan sehingga website cukup untuk melakukan iterasi pada database dan kode program menjadi lebih ringkas dan mengurangi risiko bug melalui Django models.

---

## 🤖 Pernyataan Penggunaan AI (AI Disclosure)

Dalam pengerjaan Tugas 1 ini, saya memanfaatkan asisten kecerdasan buatan dengan rincian transparansi sebagai berikut:

* **Alat yang Digunakan:** Google Gemini
* **Strategi Prompting:**
  * Memastikan pemahaman serta meminta AI untuk membuat checklist mengenai ketentuan pembuatan tugas 1.
  * Menanyakan cara memperbaiki bagian yang ingin saya perbaiki karena adanya keterbatasan AI dalam memahami konteks.
* **Bagian Spesifik yang Dibantu:**
  * Melakukan perbaikan & copy menjadi 3 achievements cards dari 1 card yang dibuat manual.
  * Membuat bagian style dari class, id dan lainnya dari file HTML yang sudah dibuat.
  * Mempercantik website dengan menambahkan fitur interaktif.
* **Log Obrolan / Riwayat:** [Tautan log chat atau ringkasan obrolan](https://share.gemini.google/TI1fwDat3NZm)

### Analisis Kritis Keterbatasan AI & Perbaikan Manual
Meskipun AI mempermudah saya dalam pembuatan website ini, terdapat beberapa keterbatasan AI sebagai berikut.
1. AI dapat memahami konteks dengan salah (miskonsepsi) karena sejatinya AI memahami konteks dengan mencocokkan definisi kata dengan training, tanpa benar-benar memahami maksud sehingga perlu adanya review dan perbaikan terhadap kode yang dibuat oleh AI.
2. Kurang peka terhadap estetika visual dan pengalaman pengguna riil: AI sering kali menghasilkan kode CSS yang secara teori benar, tetapi secara visual terasa kaku, tidak proporsional, atau menghasilkan layout shift yang mengganggu saat diuji langsung di berbagai ukuran layar. Penyesuaian mikro seperti hierarki tipografi, padding, dan kehalusan transisi tetap memerlukan human touch dan pengujian visual secara manual di peramban.