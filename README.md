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

---

### Minggu 2 (Tutorial 02 & Individual Assignment 2)
* Menambahkan model Education pada aplikasi main untuk mencatat riwayat pendidikan secara terstruktur.
* Melakukan migrasi basis data untuk skema model baru serta registrasi model ke antarmuka Django Admin.
* Membuat fungsi view show_education dan template education.html dengan perulangan dinamis serta penanganan kondisi kosong (empty state).
* Menambahkan named route pada main/urls.py dan memperbarui navbar dengan tag {% url %} yang konsisten.
* Mengimplementasikan unit test komprehensif (akses URL & template, rendering data, dan empty state).
* Menambahkan fitur kreativitas berupa mode cetak dokumen (print-friendly stylesheet via @media print) dan penyesuaian tipografi judul kartu.

---

### Tugas 2

1. Alur pemrosesan permintaan (request-response lifecycle) pada arsitektur MVT Django:
* Permintaan Diterima Proyek (urls.py proyek): Ketika pengguna mengakses URL baru (misalnya /education/), peramban mengirimkan HTTP Request ke server. Berkas urls.py pada level proyek menjadi gerbang utama yang memeriksa awalan path URL dan meneruskannya (include) ke berkas rute aplikasi yang bersangkutan.

* Resolusi Rute Aplikasi (urls.py aplikasi): Berkas main/urls.py mencocokkan sisa path URL dengan pola rute yang telah didaftarkan (path('education/', show_education, name='show_education')). Setelah kecocokan ditemukan, Django memanggil fungsi handler yang sesuai pada views.py.

* Pengambilan Data oleh Controller/Logic Layer (views.py & models.py): Fungsi view mengeksekusi logika aplikasi. Di sini, view berinteraksi dengan models.py melalui Django ORM (misalnya memanggil Education.objects.all()) untuk mengambil rekaman data dari database. View kemudian menyusun data tersebut ke dalam sebuah kamus context.

* Penyajian Data pada Presentation Layer (template): View meneruskan data context ke template yang dituju (education.html). Django Template Engine memproses berkas HTML tersebut, mengevaluasi tag logika seperti {% for %}, {% empty %}, serta memformat variabel tanggal menggunakan filter |date.

* Respons ke Peramban: Template yang telah selesai dikompilasi menjadi dokumen HTML utuh dikemas kembali oleh view ke dalam objek HttpResponse, lalu dikirimkan ke peramban pengguna untuk dirender secara visual.

2. Data untuk bagian portofolio baru sebaiknya disimpan dalam model supaya memudahkan proses penambahan dan pemeliharaan data. Jika data hanya ditulis di dalam HTML (hard-coded), perubahan data ke depannya mengharuskan developer untuk mengubah kode HTML, which is bad practice karena seharusnya perubahan data tidak mengharuskan kita untuk mengubah keseluruhan kode. Selain itu, dengan adanya perubahan kode ini, potensi bug muncul menjadi lebih besar. Karena itu, dengan kita menaruh di dalam model, perubahan/penambahan data ke depannya menjadi lebih "safe" dan mudah dilakukan karena kita dapat langsung mengubahnya melalui routing /admin menggunakan kredensial superuser. Selain itu, hal ini juga berkaitan dengan pemisahan tanggung jawab supaya model bertindak sebagai basis data dan template hanya mengurusi tampilan.

3. Fungsi makemigrations bertujuan hanya untuk membuat file migrasi yang berisi perubahan yang dilakukan pada database aplikasi, sedangkan fungsi migrate bertujuan untuk menerapkan file migrasi yang telah dibuat ke dalam database aplikasi, seperti membuat objek atau kolom baru. Karena itu, perubahan skema database yang dilakukan baru bisa digunakan setelah kita menerapkan fungsi migrate. 
**Contoh konkret:** Ketika kita menambahkan model baru seperti `Education`, atau ketika kita mengubah field pada model yang sudah ada (misalnya mengubah tipe data field `started_at` menjadi `DateField` dan menambahkan parameter `null=True, blank=True` pada `ended_at`). Perintah `makemigrations` harus dijalankan terlebih dahulu untuk mencatat perubahan field tersebut ke dalam berkas migrasi, kemudian `migrate` dijalankan agar tabel SQLite benar-benar diperbarui dengan struktur kolom yang baru.

---

## 🤖 Pernyataan Penggunaan AI (AI Disclosure)

Dalam pengerjaan Tugas 2 ini, saya memanfaatkan asisten kecerdasan buatan dengan rincian transparansi sebagai berikut:

* **Alat yang Digunakan:** Google Gemini
* **Strategi Prompting:**
  * Memastikan pemahaman AI dengan memberikan kode yang sudah dibuat sejauh ini.
  * Langsung to-the-point agar tidak menghabiskan banyak token.
* **Bagian Spesifik yang Dibantu:**
  * Memperbaiki footer yang inkonsisten di antara beberapa page.
  * Menambahkan dan memodifikasi model Education dengan ketentuan yang sudah didefinisikan.
  * Membuat dan memodifikasi page `education.html` sesuai dengan ketentuan yang sudah didefinisikan.
  * Menambahkan fitur print (kreativitas) sesuai ketentuan yang diberikan.
* **Log Obrolan / Riwayat:** [Tautan log chat atau ringkasan obrolan](https://share.gemini.google/8nUDy99tvKM2)

### Analisis Kritis Keterbatasan AI & Perbaikan Manual
Meskipun AI mempermudah saya dalam pembuatan website ini, terdapat keterbatasan AI, yaitu AI mungkin memahami maksud saya dengan salah sehingga diperlukan adanya pengecekan lagi by human supaya menjamin apa yang kita inginkan itu benar-benar dimengerti oleh AI. Kemudian, perlu adanya perbaikan yang dilakukan baik secara mandiri ataupun request kepada AI.

---

### Minggu 3 (Tutorial 03 & Individual Assignment 3)
* Mengimplementasikan fitur formulir menggunakan ModelForm untuk melakukan penambahan data (Create) dan pengeditan data (Update) secara dinamis.
* Menerapkan pengiriman data (data delivery) dengan membuat endpoint yang mengembalikan data dalam format JSON atau XML.
* Membuat fungsi view khusus yang mengimplementasikan metode pengubahan, penghapusan, dan pengembalian respons menggunakan objek HttpResponse.
* Memperbarui antarmuka pengguna dengan mengintegrasikan modal hapus interaktif dan memanfaatkan base.html sebagai kerangka utama (skeleton) menggunakan tag {% extends %}.

---

### Tugas 3

1. Alasan menggunakan ModelForm adalah karena kita menerapkan prinsip DRY (Don't Repeat Yourself) dengan menghubungkan secara langsung atribut pada model database menjadi elemen input form HTML. Kita tidak perlu menulis tag input HTML secara manual, memvalidasi tipe data satu per satu secara manual, atau mengekstrak data dari request.POST secara manual untuk menyimpannya ke database. ModelForm secara otomatis men-generate struktur form yang sesuai dengan model, menangani validasi bawaan, dan memiliki metode save() untuk langsung menyimpan atau memperbarui data. Kemudian, alasan wajibnya {% csrf_token %} adalah token CSRF (Cross-Site Request Forgery) adalah fitur keamanan krusial yang diwajibkan oleh Django pada setiap form dengan metode POST. Token ini berbentuk string rahasia dan unik yang dibuat oleh server. Fungsinya adalah untuk memastikan bahwa permintaan (request) yang memanipulasi data (tambah/edit/hapus) benar-benar berasal dari halaman web aplikasi kita sendiri, bukan dari situs peretas yang mencoba meniru sesi (session) pengguna yang sah.

2. JSON (JavaScript Object Notation) lebih disukai karena strukturnya jauh lebih ringan, ringkas, dan mudah dibaca oleh manusia dibandingkan XML. XML memerlukan penulisan tag pembuka dan penutup (verbose) yang membuat ukuran dokumen membengkak. Karena ukurannya yang lebih kecil, transmisi data JSON melalui jaringan menjadi lebih cepat. Selain itu, JSON berasal dari sintaks objek JavaScript, sehingga memiliki integrasi bawaan (native) yang sangat mulus dengan frontend modern (seperti Vanilla JS, React, Vue), membuat proses parsing data menjadi instan tanpa memerlukan perangkat lunak tambahan yang kompleks.

3.
* Alur Pengembalian Data:
1. Client meminta (request) akses ke URL endpoint JSON (misalnya /api/experience/).
2. Router di urls.py mencocokkan URL dan meneruskan permintaan ke fungsi view terkait.
3. Di dalam view, Django ORM melakukan query ke database dan mengembalikan kumpulan data berupa objek Python kompleks (QuerySet).
4. Fungsi view memanggil serializer untuk mengubah QuerySet tersebut menjadi string berformat JSON.
5. String JSON tersebut dikemas ke dalam objek HttpResponse dengan header content_type="application/json" dan dikirimkan kembali sebagai balasan (response) ke client.

* Tujuan serialization adalah karena protokol HTTP hanya dapat mengirimkan dan menerima teks atau byte stream. Objek model Django (QuerySet) adalah tipe data kompleks di Python yang berisi referensi memori dan metode spesifik yang tidak dapat dipahami oleh jaringan atau client. Proses serialization berfungsi sebagai penerjemah yang memecah (mengekstrak) nilai-nilai dari objek kompleks tersebut, lalu mengubahnya menjadi format teks standar (JSON/XML) agar bisa ditransmisikan lewat HTTP dan direkonstruksi kembali oleh peramban pengguna.

---

## 🤖 Pernyataan Penggunaan AI (AI Disclosure)

Dalam pengerjaan Tugas 3 ini, saya memanfaatkan asisten kecerdasan buatan dengan rincian transparansi sebagai berikut:

* **Alat yang Digunakan:** Google Gemini
* **Strategi Prompting:**
  * Memastikan pemahaman AI dengan memberikan kode yang sudah dibuat sejauh ini.
  * Langsung to-the-point agar tidak menghabiskan banyak token.
* **Bagian Spesifik yang Dibantu:**
  * Menambahkan fitur, seperti create, read, update, dan delete untuk model Education.
  * Memodifikasi halaman tampilan Education supaya memiliki fitur create, update, dan delete.
* **Log Obrolan / Riwayat:** [Tautan log chat atau ringkasan obrolan](https://share.gemini.google/6WKWUn6rLnLt)

### Analisis Kritis Keterbatasan AI & Perbaikan Manual
Meskipun AI sangat membantu, terutama dalam mempercepat proses debugging tampilan CSS dan menjelaskan logika backend Django, saya menemukan beberapa keterbatasan. AI tidak selalu memiliki konteks menyeluruh tentang proyek saya kecuali saya secara spesifik menyalin kodenya (misalnya saat terjadi bentrok struktur class pada HTML Education dan Experience). Oleh karena itu, saya tetap harus menganalisis letak elemen secara manual dan tidak bisa sekadar melakukan copy-paste. Selain itu, AI terkadang menyarankan implementasi fitur tambahan yang melenceng dari spesifikasi atau batasan tugas dasar, sehingga saya sebagai developer harus tetap memfilter dan memutuskan saran mana yang benar-benar esensial dan aman untuk diimplementasikan tanpa merusak aplikasi.
