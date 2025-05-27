# Odoo 17 Development Setup

Setup pengembangan Odoo 17 dengan Docker Compose.

## Struktur Folder

```
odoo17/
├── addons/                  # Folder untuk modul custom
│   └── custom_module/       # Contoh modul custom
│       ├── models/          # Model Python
│       ├── views/           # Tampilan XML
│       ├── __init__.py      # File inisialisasi
│       └── __manifest__.py  # Manifest modul
├── config/                  # Konfigurasi Odoo
│   └── odoo.conf            # File konfigurasi Odoo
└── docker-compose.yml       # File Docker Compose
```

## Cara Menjalankan

1. Pastikan Docker dan Docker Compose sudah terinstal
2. Jalankan perintah berikut di terminal:

```bash
docker-compose up -d
```

3. Akses Odoo melalui browser di http://localhost:8069

## Pengembangan Modul Custom

1. Buat modul baru di folder `addons/`
2. Instal modul melalui antarmuka Odoo
3. Kembangkan fitur sesuai kebutuhan

## Konfigurasi Database

- Username: odoo
- Password: odoo
- Database: postgres

## Catatan

- Password admin default: admin (dapat diubah di odoo.conf)
- Mode pengembangan diaktifkan
- Port default: 8069