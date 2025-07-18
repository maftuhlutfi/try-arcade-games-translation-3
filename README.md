# CSV Translation Tool

Program Python untuk menerjemahkan file CSV menggunakan ArgosTranslate dengan dukungan HTML dan multiprocessing untuk performa optimal.

## Fitur

- ✅ Translasi menggunakan ArgosTranslate (offline)
- ✅ Dukungan HTML tags dengan translatehtml
- ✅ Multiprocessing untuk memaksimalkan CPU
- ✅ Konfigurasi kolom melalui JSON
- ✅ Output dalam format JSON
- ✅ Progress tracking
- ✅ Error handling

## Instalasi

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Pastikan folder struktur seperti ini:
```
project/
├── input/
│   ├── column_data.json
│   ├── gm_games.csv
│   ├── gm_categories.csv
│   └── ... (file CSV lainnya)
├── main.py
├── requirements.txt
└── README.md
```

## Cara Penggunaan

### 1. Mode Interaktif (Rekomendasi)
```bash
python main.py
# atau
python main.py --interactive
```
Program akan menampilkan menu interaktif untuk:
- Memilih bahasa sumber
- Memilih bahasa tujuan  
- Memilih file CSV yang akan diterjemahkan
- Konfirmasi pengaturan sebelum memulai

### 2. Mode Auto (Cepat)
```bash
python main.py --auto
```
Otomatis menerjemahkan semua file dari English ke Indonesian

### 3. Menerjemahkan semua file CSV (Command Line)
```bash
python main.py --source en --target id
```

### 4. Menerjemahkan ke bahasa tertentu
```bash
python main.py --source en --target es
python main.py --source en --target fr
```

### 5. Menerjemahkan file CSV tertentu
```bash
python main.py --file gm_games.csv
python main.py --file gm_categories.csv --target es
```

### 6. Melihat daftar file CSV yang tersedia
```bash
python main.py --list
```

## Parameter

- `--interactive` / `-i`: Mode interaktif dengan menu (default jika tanpa parameter)
- `--auto` / `-a`: Mode otomatis (en->id, semua file)
- `--source` / `-s`: Kode bahasa sumber
- `--target` / `-t`: Kode bahasa tujuan
- `--file` / `-f`: File CSV tertentu yang akan diterjemahkan
- `--list` / `-l`: Tampilkan daftar file CSV yang tersedia

## Kode Bahasa yang Didukung

- `en`: English
- `id`: Indonesian 
- `es`: Spanish
- `fr`: French
- `de`: German
- `pt`: Portuguese
- `ru`: Russian
- `zh`: Chinese
- `ja`: Japanese
- `ko`: Korean
- `ar`: Arabic
- `hi`: Hindi
- `it`: Italian
- `nl`: Dutch
- `pl`: Polish
- `tr`: Turkish
- Dan bahasa lainnya yang didukung ArgosTranslate

## Output

File hasil terjemahan akan disimpan di:
```
output/
└── [kode-bahasa]/
    ├── gm_games.json
    ├── gm_categories.json
    └── ... (file JSON lainnya)
```

## Konfigurasi Kolom

Edit `input/column_data.json` untuk mengatur kolom mana yang perlu diterjemahkan:

```json
{
  "gm_games.csv": {
    "translate": ["game_name", "description", "instructions"],
    "skip": ["game_id", "image", "category"]
  }
}
```

## Performa

- Program menggunakan semua core CPU yang tersedia
- Batch processing untuk file besar
- Progress tracking real-time
- Automatic HTML detection dan handling
- Emoji protection untuk mempertahankan emoji dalam translasi
- Mendukung emoji composite (keluarga, flags, dll)

## Troubleshooting

1. **Error "Translation package not available"**:
   - Pastikan koneksi internet untuk download package pertama kali
   - Coba bahasa lain yang didukung

2. **Memory error untuk file besar**:
   - Program otomatis mengatur batch size
   - Tutup aplikasi lain untuk mengosongkan RAM

3. **Encoding error**:
   - Program otomatis mencoba encoding latin-1 jika UTF-8 gagal

4. **HTML translation issues**:
   - Program otomatis fallback ke regular translation jika HTML translation gagal
   - HTML detection berdasarkan keberadaan tag `<` dan `>`

5. **Emoji protection issues**:
   - Program menggunakan regex pattern untuk melindungi emoji selama translasi
   - Mendukung emoji composite seperti keluarga (👨‍👩‍👧‍👦), flags, dan ZWJ sequences
   - Jika emoji hilang, coba jalankan ulang translasi

6. **Import errors**:
   - Pastikan semua dependencies terinstall: `pip install -r requirements.txt`

## Contoh Penggunaan

```bash
# Mode interaktif (rekomendasi untuk pemula)
python main.py

# Mode auto - cepat untuk English ke Indonesian
python main.py --auto

# Command line - terjemahkan semua file ke bahasa Indonesia
python main.py --target id

# Terjemahkan hanya gm_games.csv ke bahasa Spanyol  
python main.py --file gm_games.csv --target es

# Lihat file yang tersedia
python main.py --list
```

## Mode Interaktif

Saat menjalankan tanpa parameter, program akan menampilkan:

1. **Menu Bahasa Asal** - Pilih dari 16+ bahasa yang didukung
2. **Menu Bahasa Tujuan** - Pilih bahasa target
3. **Menu File CSV** - Pilih file tertentu atau semua file
4. **Konfirmasi** - Review pengaturan sebelum memulai

Contoh tampilan:
```
🌍 CSV TRANSLATION TOOL
   Powered by ArgosTranslate
============================================================

🔤 PILIH BAHASA ASAL:
----------------------------------------
 1. en - English              2. id - Indonesian
 3. es - Spanish              4. fr - French
 5. de - German               6. pt - Portuguese
...

📁 PILIH FILE CSV UNTUK DITERJEMAHKAN
----------------------------------------
 1. gm_categories.csv
 2. gm_games.csv
 3. gm_tags.csv
 7. Proses SEMUA file
```
