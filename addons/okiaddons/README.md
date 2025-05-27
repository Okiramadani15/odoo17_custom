# Oki Addons

Modul custom dengan fitur-fitur berikut:

## Fitur

### 1. Sales Order Customization
- Division field (SQA, GLN, BTV, BVG)
- Customer filtering berdasarkan division
- Pickup Method (Delivery atau Take in Plant)
- Credit limit warning
- Overdue invoice warning

### 2. Customer Division
- Satu customer dapat memiliki beberapa division
- Setiap division memiliki pricelist tersendiri
- Credit limit per division
- Sales person per division

### 3. Stock Inventory Report
- Report stock inventory dengan rentang waktu tertentu
- Menampilkan saldo awal, total masuk, total keluar, dan saldo akhir
- Filter berdasarkan lokasi

## Jawaban Soal 3

### Kebutuhan Server Berdasarkan Concurrent User

Untuk menentukan kebutuhan server berdasarkan jumlah concurrent user pengguna Odoo, beberapa faktor yang perlu dipertimbangkan:

1. **RAM**: 
   - Base: 2GB untuk sistem + 2GB untuk PostgreSQL
   - Per user: ~100-150MB per concurrent user
   - Contoh: Untuk 50 concurrent user, dibutuhkan minimal 2GB + 2GB + (50 * 150MB) = ~11.5GB RAM

2. **CPU**:
   - Base: 2 core untuk sistem dan PostgreSQL
   - Per user: ~0.05-0.1 core per concurrent user
   - Contoh: Untuk 50 concurrent user, dibutuhkan minimal 2 + (50 * 0.1) = ~7 core

3. **Storage**:
   - Base: 20GB untuk OS + 20GB untuk Odoo
   - Database: Tergantung jumlah transaksi, biasanya 10-50GB
   - File storage: Tergantung penggunaan, biasanya 50-200GB

4. **Bandwidth**:
   - Per user: ~50-100 Kbps per concurrent user
   - Contoh: Untuk 50 concurrent user, dibutuhkan minimal 50 * 100 Kbps = 5 Mbps

### Pemisahan Aplikasi dan Database

Odoo dapat berjalan dengan baik dalam satu server yang sama untuk aplikasi dan database, terutama untuk implementasi skala kecil hingga menengah. Namun, untuk implementasi skala besar atau dengan kebutuhan performa tinggi, pemisahan server aplikasi dan database memiliki beberapa keuntungan:

1. **Keuntungan pemisahan server**:
   - Skalabilitas yang lebih baik (dapat menambah server aplikasi secara horizontal)
   - Performa database yang lebih baik karena resource tidak terbagi
   - Keamanan yang lebih baik dengan isolasi database
   - Maintenance yang lebih mudah (dapat melakukan update aplikasi tanpa mengganggu database)

2. **Kapan sebaiknya menggunakan satu server**:
   - Implementasi skala kecil (<20 concurrent user)
   - Budget terbatas
   - Kompleksitas operasional yang ingin diminimalkan

3. **Kapan sebaiknya memisahkan server**:
   - Implementasi skala besar (>50 concurrent user)
   - Kebutuhan high availability
   - Transaksi yang sangat tinggi
   - Kebutuhan performa yang tinggi

Kesimpulannya, Odoo dapat berjalan maksimal di satu server untuk implementasi skala kecil hingga menengah, tetapi untuk implementasi skala besar atau dengan kebutuhan performa tinggi, pemisahan server aplikasi dan database sangat direkomendasikan.