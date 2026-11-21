# DESIGN.md — KartuTa

Arah desain untuk storefront dan dashboard KartuTa. Dokumen ini mengisi bagian **jiwa** (identitas, warna, tipe, ritme). Aturan `antislop` berlaku sebagai filter di atasnya, bukan pengganti.

Dibuat: 2026-11-16
Status: draft v1, diturunkan dari UI yang sudah berjalan di `templates/` dan `static/css/style.css`

---

## 1. Produk & Audiens

**Apa ini:** toko photocard K-Pop official dengan sinkronisasi Virtual Binder digital. Pembeli mengoleksi kartu fisik, lalu koleksinya tercatat di akun.

**Siapa:** kolektor photocard Indonesia, usia 17-28, terbiasa membeli lewat marketplace dan grup fanbase. Mereka sudah tahu istilah *grade*, *toploader*, *unboxing*, *lens*.

**Apa yang mereka nilai:** keaslian yang bisa dibuktikan, kondisi kartu yang presisi, kemasan yang tidak merusak kartu. Bukan diskon, bukan gamifikasi.

**Konsekuensi desain:** katalog harus terasa seperti arsip terkatalogisasi, bukan toko diskon. Foto kartu adalah bukti, jadi ia mendapat ruang paling besar dan latar paling tenang.

---

## 2. Dial

```
ENERGY 2 / RHYTHM 2 / MOTION 1
```

| Dial | Nilai | Alasan satu baris |
|---|---|---|
| **ENERGY** | 2 | Kolektor butuh ketenangan untuk menilai kondisi kartu, tapi toko rilisan baru butuh sedikit momentum. 2 = hadir jelas tanpa berteriak. |
| **RHYTHM** | 2 | Halaman perlu berhenti di antara katalog dan panduan, tapi komposisi dasar tetap konsisten agar arsip terasa satu sistem. |
| **MOTION** | 1 | Tidak ada animasi yang membantu penilaian kondisi kartu. Gerak hanya mengganggu pemeriksaan visual. Hover dan transisi state saja. |

Dial ini mengikat. Kalau sebuah seksi butuh ENERGY 3 untuk bekerja, yang salah adalah seksinya, bukan dialnya.

---

## 3. Tema

**Gelap sebagai default. Alasan:** photocard adalah objek cetak dengan warna jenuh dan tepi putih. Di atas kanvas gelap, tepi kartu terbaca sebagai objek dan warna cetakan tidak tertandingi oleh latar. Ini alasan yang sama dipakai galeri foto dan ruang pamer, bukan "gelap terlihat teknologi".

**Konsekuensi wajib:** karena gelap dipilih, seluruh pasangan teks harus lolos WCAG AA. Lihat bagian 4. Gelap tanpa kontras cukup adalah kegagalan tema, bukan pilihan gaya.

Tidak ada toggle terang/gelap. Tidak dirancang untuk itu, dan tidak akan diklaim sebagai fitur.

---

## 4. Warna

### Kanvas dan permukaan

| Token | Nilai | Pakai |
|---|---|---|
| `canvas` | `#090C12` | Latar halaman |
| `canvas-deep` | `#05070B` | Announcement bar, area paling mundur |
| `surface` | `#111622` | Kartu, panel, tabel |
| `surface-raised` | `#161B26` | Kartu yang bisa diinteraksi, sidebar |
| `border` | `#334155` | Garis pemisah yang masih terlihat |
| `border-soft` | `rgba(255,255,255,0.07)` | Pemisah halus di dalam kartu |

Empat tingkat gelap ini sengaja: kanvas, permukaan, permukaan terangkat, dan area mundur. Perbedaan antar tingkat kecil (sekitar 5-8% luminans) supaya hierarki terbaca tanpa kotak-kotak menonjol.

### Teks

| Token | Nilai | Kontras di `canvas` | Pakai |
|---|---|---|---|
| `text` | `#F8FAFC` | 18.7:1 | Judul, angka penting |
| `text-strong` | `#FFFFFF` | 19.6:1 | Nama produk, harga |
| `text-secondary` | `#94A3B8` | 7.6:1 | Deskripsi, label |
| `text-muted` | `#7C8AA0` | 5.6:1 (5.2:1 di surface) | Meta (tanggal, penulis, SKU) |

**`#64748B` dihentikan** untuk teks apa pun. Rasio 4.11:1 di kanvas dan 3.80:1 di permukaan, gagal AA. Penggantinya `text-muted` di atas.

### Aksen

Satu aksen utama, satu aksen sekunder yang dipakai jauh lebih sedikit:

| Token | Nilai | Pakai | Alasan |
|---|---|---|---|
| `accent` | `#8B5CF6` | Satu aksi utama per layar: tombol beli, tautan aktif, fokus | Violet adalah warna album photobook dan lightstick umum di pasar K-Pop Indonesia, jadi terasa milik audiensnya, bukan pilihan model |
| `accent-ink` | `#4C1D95` | Latar tombol dengan teks putih | Varian gelap supaya putih di atasnya lolos 11:1 |
| `signal` | `#10B981` | Status berhasil, stok tersedia, badge terverifikasi | Hijau hanya untuk status, tidak untuk dekorasi |
| `alert` | `#F59E0B` | Peringatan stok menipis, pesanan tertunda | Amber hanya untuk peringatan |

**Magenta `#EC4899` dicabut dari peran aksen.** Sekarang hanya boleh muncul sebagai bagian wordmark "KartuTa" itu sendiri, tidak di tombol, tidak di badge, tidak di garis.

### Aturan pakai

1. Satu aksen per layar. Kalau tombol beli violet dan badge violet dan garis violet, tidak ada yang menonjol.
2. Glow maksimal di satu elemen per layar. Saat ini 31 deklarasi glow, harus turun ke hitungan satu digit.
3. Gradien hanya untuk satu hal: badge wordmark. Selain itu, warna solid.
4. Putih di atas `#8B5CF6` hanya 4.23:1, gagal. Tombol primary memakai `accent-ink` sebagai latar.

---

## 5. Tipografi

| Peran | Keluarga | Ukuran | Alasan |
|---|---|---|---|
| Display | Space Grotesk | 34-56px, weight 800, tracking -0.02em | Geometris dengan detail aneh di `a` dan `g`. Terasa seperti tipografi katalog seni, bukan tipografi SaaS |
| Body | Plus Jakarta Sans | 13-16px, weight 400-600, line-height 1.6-1.85 | Rancangan Indonesia, bentuk huruf terbuka, tetap terbaca di 13px pada layar gelap |

Keduanya dimuat dari Google Fonts. Space Grotesk adalah pilihan sadar untuk display, bukan default: huruf ini punya karakter yang membedakan dari tumpukan Inter/Geist yang dipakai semua template.

### Aturan

1. **Uppercase ber-tracking hanya di satu level:** label seksi kecil (`.protocol-pretitle`, announcement). Maksimal 2 tempat per halaman. Nav link tidak uppercase lagi, karena menu bukan label.
2. **Angka harga memakai `font-variant-numeric: tabular-nums`** supaya kolom harga rata saat dipindai.
3. Berat 800 untuk judul, 600 untuk label, 400 untuk paragraf. Tidak ada 500, tidak ada 700 acak.

---

## 6. Skala Spasi

Basis 4px.

```
4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96
```

| Pakai | Nilai |
|---|---|
| Jarak dalam komponen (ikon ke teks) | 8 |
| Padding kartu | 20-24 |
| Jarak antar kartu | 16 |
| Jarak antar seksi | 64 di desktop, 48 di mobile |
| Jarak judul seksi ke kontennya | 24 |

Spasi antar seksi sengaja jauh lebih besar dari spasi di dalam seksi. Itu satu-satunya cara halaman terbaca sebagai beberapa bagian, bukan satu strip panjang.

---

## 7. Skala Radius

```
4  — badge, kbd, chip kecil
8  — input, tombol, item nav
12 — kartu kecil
16 — kartu utama, panel
```

Tidak ada radius 20, 24, atau 999 kecuali search bar (kapsul) karena bentuknya memang menandakan "kotak isian tunggal di antara tombol", satu-satunya kapsul di halaman.

Tombol tidak kapsul. Kartu tidak kapsul. Badge tidak kapsul.

---

## 8. Kedalaman

Dua tingkat saja:

| Tingkat | Treatment | Pakai |
|---|---|---|
| Datar | `1px solid var(--border-soft)` | Kartu, panel, tabel, semua isi default |
| Terangkat | `0 8px 24px rgba(0,0,0,0.45)` | Hanya elemen yang benar-benar mengapung: navbar sticky, modal, dropdown |

Tidak ada bayangan di kartu katalog. Kartu katalog duduk di halaman, bukan melayang di atasnya.

---

## 9. Ikona

**Emoji tidak dipakai sebagai ikon UI.** Emoji dirender berbeda di setiap sistem operasi, tidak punya berat yang konsisten, dan tidak bisa diwarnai. Pengganti: inline SVG stroke 1.5px, ukuran 16 atau 20, warna `currentColor`.

Satu pengecualian: `👤` pada tombol akun diganti SVG siluet, bukan dipertahankan.

Ikon hanya dipakai kalau ia mempercepat pemindaian. Label teks yang jelas lebih baik daripada ikon yang perlu ditebak.

---

## 10. Gerak

Karena MOTION 1:

| Boleh | Tidak boleh |
|---|---|
| Transisi hover 150-180ms | Animasi masuk saat scroll |
| Perubahan border dan warna saat fokus | Parallax, pin, choreography |
| Buka/tutup panel | Apa pun yang berjalan otomatis |
| Perpindahan slide hero oleh pengguna | Slide hero yang berganti sendiri |

Semua transisi dibungkus `@media (prefers-reduced-motion: reduce)` untuk dimatikan.

---

## 11. Komposisi per Seksi

Halaman depan tidak boleh memakai satu pola berulang. Urutan dan bentuknya:

| Seksi | Bentuk | Alasan |
|---|---|---|
| Hero | Dua kartu asimetris, kiri teks, kanan slide | Bedanya ukuran menyatakan mana yang menjelaskan dan mana yang memamerkan |
| Jaminan | Satu baris tipis, tiga poin, tanpa kotak | Ini penguat, bukan konten. Kotak akan memberinya bobot yang tidak ia punya |
| Katalog | Grid kartu seragam 2:3 | Keseragaman di sini benar: semua produk setara, dan mata perlu membandingkan bentuk yang sama |
| Protokol kemasan | Satu blok teks lebar dengan empat langkah bernomor garis | Proses, bukan fitur. Tidak perlu kartu |
| Panduan | Dua kolom teks, bukan grid kartu | Artikel dibaca, bukan dipindai seperti produk |

Kalau satu seksi terasa kosong, perbaiki dengan ukuran, spasi, atau bobot huruf. Bukan dengan menambah kotak.

---

## 12. Yang Dilarang di Proyek Ini

Daftar ini spesifik untuk KartuTa, diturunkan dari apa yang sudah salah sekali:

1. Gradien ungu ke magenta pada elemen apa pun selain wordmark.
2. Glow pada lebih dari satu elemen per layar.
3. Emoji sebagai ikon navigasi atau label tombol.
4. `#64748B` untuk teks.
5. Putih di atas `#8B5CF6` untuk teks tombol.
6. Uppercase ber-tracking pada nav link.
7. Radius kapsul pada tombol, kartu, atau badge.
8. Input pencarian yang `readonly` tapi terlihat bisa diketik.
9. Bayangan pada kartu katalog.
10. Angka atau klaim tanpa sumber.

---

## 13. Cara Memakai Dokumen Ini

1. Baca dial di bagian 2 sebelum mengubah apa pun.
2. Ambil warna dari tabel bagian 4, bukan dari color picker.
3. Kalau butuh nilai yang tidak ada di sini, tambahkan ke dokumen ini dulu, dengan alasannya, baru pakai.
4. Kalau sebuah keputusan tidak bisa dijelaskan dalam satu baris, keputusan itu belum siap dipakai.

Audit kondisi saat ini: `anti-slop/audit-001-2026-11-16.md`
---

## 14. Struktur Beranda (Batch 4)

Setiap seksi punya bentuk berbeda. Tidak ada judul tengah + grid kartu identik berulang.

| Seksi | Bentuk | Alasan |
|---|---|---|
| Hero | Grid asimetris 1.35 : 0.85, kiri teks, kanan slide | Satu fokus, tidak ada badge di atas H1 |
| Jaminan | 4 kolom teks dipisah garis vertikal, tanpa kotak ikon | Ikon kotak identik tidak membedakan isi; teks yang membedakan |
| Etalase | Judul kiri + hitungan kanan, grid kartu 2:3 | Rasio photocard, itu inti produknya |
| Protokol kemasan | Daftar bernomor 01-04, satu kolom | Urutan lapisan memang berurutan; kartu 4 kolom menyembunyikan urutan itu |
| Artikel | Baris editorial: judul + ringkasan kiri, meta kanan, garis pemisah | Artikel dibaca, bukan dipamerkan sebagai kartu |
| Mitra ekspedisi | Satu baris nama + jenis, rata kiri | Bukti, bukan pita dekorasi di tengah |

Jarak antar seksi: 36 / 64 / 72 / 88 / 56 px. Jarak tidak seragam karena tiap seksi punya bobot berbeda.
