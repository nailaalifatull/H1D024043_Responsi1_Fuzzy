# MoodSync — Sistem Pendukung Keputusan Fuzzy Mamdani

Sistem ini merupakan implementasi Logika Fuzzy menggunakan metode Mamdani untuk memberikan rekomendasi aktivitas relaksasi berdasarkan tingkat minat seseorang terhadap **Olahraga** dan **Musik**.

## Identitas Mahasiswa

- **Nama**: Naila Alifatul
- **NIM**: H1D024043
- **Shift Baru**: Shift D
- **Shift KRS**: Shift H

---

## Penjelasan Sistem

### 1. Variabel Fuzzy
Sistem memiliki dua input dan satu output:
- **Input 1: Olahraga** (Skala 0–100)
- **Input 2: Musik** (Skala 0–100)
- **Output: Rekomendasi** (Skala 0–100)

### 2. Fungsi Keanggotaan 
Sistem menggunakan dua jenis fungsi keanggotaan:

#### Fungsi Trapesium
Digunakan untuk kategori di ujung (Rendah dan Tinggi).

#### Fungsi Segitiga 
Digunakan untuk kategori di tengah (Sedang/Netral).

**Himpunan Fuzzy:**
- **Rendah**: Trapesium(0, 0, 30, 45)
- **Sedang**: Segitiga(25, 50, 75)
- **Tinggi**: Trapesium(55, 70, 100, 100)

---

### 3. Rule Base (Aturan Mamdani)
Terdapat 9 aturan dasar yang digunakan untuk menentukan hasil inferensi:

| No | Olahraga | Musik | Output (Rekomendasi) |
|----|----------|-------|----------------------|
| 1  | Rendah   | Rendah | Kurang Disarankan    |
| 2  | Rendah   | Sedang | Disarankan           |
| 3  | Rendah   | Tinggi | Sangat Disarankan    |
| 4  | Sedang   | Rendah | Disarankan           |
| 5  | Sedang   | Sedang | Netral               |
| 6  | Sedang   | Tinggi | Disarankan           |
| 7  | Tinggi   | Rendah | Sangat Disarankan    |
| 8  | Tinggi   | Sedang | Disarankan           |
| 9  | Tinggi   | Tinggi | Sangat Disarankan    |

---

### 4. Mekanisme Inferensi
Sistem menggunakan metode **Mamdani**:
1. **Fuzzifikasi**: Mengubah input crisp menjadi derajat keanggotaan.
2. **Implikasi**: Menggunakan operator **MIN** (Minimum) untuk menentukan kekuatan setiap aturan ($\alpha$-predikat).
3. **Agregasi**: Menggunakan operator **MAX** (Maximum) untuk menggabungkan seluruh hasil output dari aturan yang aktif.

---

### 5. Defuzzifikasi
Metode yang digunakan adalah **Centroid**. 
Di mana nilai crisp akhir yang akan menentukan kategori rekomendasi.
