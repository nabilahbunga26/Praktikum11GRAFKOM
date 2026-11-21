# P10 — UV-Mapped PBR Asset: Kampus Sekolah

**Mata kuliah:** EF234504 — Grafika Komputer  
**Praktikum:** Pertemuan 10 — Blender Materials, UV & Texturing  
**Blender:** 5.2 LTS  
**Nama / kelompok:** `[ISI NAMA DAN KELOMPOK SEBELUM DIKUMPULKAN]`
**NRP:** `[ISI NRP SEBELUM DIKUMPULKAN]`
**Asset utama:** `SCH_Building` — model gedung sekolah dari scene P09/P10  

> Isi identitas kelompok dan pastikan ulang aturan lisensi aset sebelum mengunggah repo. Folder ini adalah paket P10 mandiri; file P10 dan P11 sumber di folder induk tidak ditimpa.

## Hasil dan struktur paket

```text
P10_Kelompok_Sekolah_UV_PBR/
├── P10_Kelompok_Sekolah_UV_PBR.blend
├── P10_Kelompok_Sekolah_UV_PBR_UV_Mapping.blend
├── README.md
├── build_p10_uv_pbr.py
├── make_p10_evidence.py
├── uv_layout_data.json
├── assets/
│   └── Wooden_Crate_01/wooden_crate_01_2k.blend
├── textures/
│   ├── School_Building/       # lima map sekolah yang diekstrak dari image packed
│   ├── School_Bus/
│   ├── School_Students/
│   └── Wooden_Crate_01/
└── screenshots/               # bukti proses UV, PBR, eksperimen, dan render
```

File revisi yang menampilkan alur Mapping adalah `P10_Kelompok_Sekolah_UV_PBR_UV_Mapping.blend` di folder ini. Gedung sekolah tetap hero subject di scene kampus. Bus, lapangan olahraga, lapangan upacara, playground, kantin, peti PBR, dan dua siswa tetap menjadi elemen pendukung. Bus tetap di depan dan playground menapak di ground.

File `.blend` membawa image resource yang dipakai oleh scene dalam kondisi packed. Salinan map juga tersedia dalam folder `textures/` agar dapat diperiksa atau diedit. File `assets/Wooden_Crate_01/wooden_crate_01_2k.blend` menyertakan model PBR eksternal yang digunakan. README ini mencatat bahwa map bus yang tersedia adalah map pengganti lokal, bukan tekstur sumber bus yang tidak ikut dalam file model.

Gambar close-up adalah render bukti dari Blender. Gambar UV layout/node graph dan contact sheet eksperimen disusun dari koordinat UV, koneksi node, serta render hasil file `.blend`; diagram bukan tangkapan literal seluruh antarmuka Blender. Jika dosen mensyaratkan screenshot aplikasi, buka scene di Blender dan ambil screenshot UV Editor/Shader Editor untuk melengkapi bukti tersebut.

## Asset dan pemeriksaan geometry

Asset utama adalah bangunan hard-surface bergaya low-poly. Geometry mendefinisikan bentuk dan siluet; material/texture mendefinisikan warna, roughness, karakter metal, detail normal, dan emission.

Audit pada `SCH_Building` sebelum UV study:

| Pemeriksaan | Hasil |
|---|---:|
| Scale object | `(1, 1, 1)` |
| Vertices / edges / faces | `597 / 925 / 396` |
| Ngons | `0` |
| Coincident vertices pada toleransi `0.00001 m` | `0` |
| Boundary edges | `335` |

Model adalah susunan shell arsitektural, bukan satu solid tertutup. Boundary edge pada bawah/ujung komponen tidak otomatis dianggap lubang yang harus ditutup; gabungkan atau tutup hanya jika memang cacat pada bagian tersebut. Hindari **Merge by Distance** secara membabi buta pada sambungan panel yang sengaja terpisah.

### Audit yang dapat diulang di Blender

1. Pilih `SCH_Building`; di Object Mode lihat **Item → Transform**. Scale sekarang sudah `(1, 1, 1)`. Jika membuat perubahan skala, gunakan `Ctrl+A` → **Scale** sebelum unwrap.
2. `Tab` → Edit Mode, `A`, lalu `F3` → **Merge by Distance** hanya sebagai pemeriksaan. Verifikasi jumlah vertex yang dilaporkan sebelum menghapus apa pun.
3. `F3` → **Select Non Manifold** untuk meninjau boundary/non-manifold. Tinjau tiap seleksi karena edge terbuka memang ada pada shell bangunan.
4. `F3` → **Select Faces by Sides**, atur `Number of Vertices > 4` untuk memeriksa ngon. Audit menghasilkan nol ngon.
5. Untuk normals, pilih face lalu `Shift+N` (**Recalculate Outside**) hanya pada komponen tertutup yang memang terbukti terbalik. Aktifkan **Viewport Overlays → Face Orientation**: biru menghadap luar dan merah sisi belakang. Bangunan memiliki shell terbuka, jadi jangan membalik semua face sekaligus tanpa memeriksa komponen dan tampilan material.

## UV Map produksi dan UV study

Material tekstur sekolah menggunakan UV atlas 2K yang telah ada di layer `UVMap`. Layer tersebut **dipertahankan** karena mengubah koordinat produksi tanpa bake ulang akan memindahkan jendela, papan nama, dan tekstur lain. `MAT_School_Building` secara eksplisit membaca `UVMap`.

Sebagai hasil tugas P10, mesh memiliki layer tambahan `P10_Manual_Unwrap` dengan seam manual dan hasil unwrap yang dapat dibuka di UV Editor. Layer study ini tidak menggantikan atlas produksi. Object menyimpan seam flags dan custom property yang menerangkan strategi seam. Saat memakai materi checker, node UV diarahkan sementara ke `P10_Manual_Unwrap`; material produksi tetap pada `UVMap`.

### Strategi seam dan UV Island

- Strategi utama: tandai batas shell terbuka dan edge dengan perubahan sudut antar-face sekurangnya `45°`; total `777` edge ditandai.
- Seam mengikuti sudut arsitektural, pertemuan atap/dinding, underside, dan batas panel. Fasad utama tidak dibelah melintasi bidang datar; garis seam yang terlihat berada pada perubahan bentuk/trim yang sudah terbaca secara visual.
- Jalankan `A` → `U` → **Unwrap** (Conformal untuk studi ini). Hasil utama memiliki `247` UV islands yang dihitung dari sambungan UV aktual antar-face.
- Island besar terutama menampung bidang fasad, dinding, dan bidang atap; strip kecil menampung lis/trim; island bulat dan kecil menampung detail clock, panel, atau elemen dekoratif.

`02_marked_seams.png` menunjukkan edge seam pada asset. `03_initial_unwrap.png` memperlihatkan layout awal sebelum normalisasi skala/packing. Eksperimen seam alternatif dan Smart UV ada di `14_unwrap_seam_comparison.png`:

| Metode | Seam / island | Hasil dan keputusan |
|---|---:|---|
| Seam manual: boundary + hard edge `45°` | 777 seam / 247 island; 5.012 s | Dipilih. Mengikuti perubahan bentuk, layout mudah dibaca, dan checker dapat diperiksa per area. |
| Seam manual: boundary-only | 335 seam / 76 island; 3.757 s | Lebih sedikit island, tetapi Blender melaporkan 2 dari 66 island solver tidak terselesaikan. Peta juga lebih sulit dikontrol pada bidang arsitektur yang saling bertemu; tidak dipilih untuk hasil utama. |
| Smart UV Project | 260 island; 0.012 s | Cepat sebagai baseline, namun memecah permukaan berdasarkan sudut otomatis dan memberi kontrol lebih rendah terhadap lokasi seam serta orientasi island. |

Waktu adalah pengukuran operasi UV di mesin ini dan dapat berubah menurut hardware. Jumlah island adalah jumlah chart UV yang terhubung, bukan jumlah object. Karena model terdiri dari beberapa shell, sejumlah island kecil memang wajar.

### Checker, texel density, packing, dan overlap

1. `04_checker_test.png` memakai Checker Texture dengan UV `P10_Manual_Unwrap`. Checker pada bidang yang melengkung/menyempit membantu menemukan perubahan bentuk dan skala.
2. `14_checker_stretched.png` menunjukkan eksperimen distorsi buatan dengan UV diperlebar pada satu sumbu. Checker tampak berubah proporsi; UV study produksi tidak diubah oleh eksperimen ini.
3. Setelah seam diperbaiki, gunakan UV Editor → **Average Islands Scale**, lalu **Pack Islands** dengan margin `0.006` pada UV 0–1 (sekitar 12 px pada texture 2K). Tujuannya adalah kepadatan texel relatif konsisten, ruang cukup untuk mipmap/bake, dan pemakaian ruang yang efisien.
4. `05_final_uv_layout.png` menunjukkan hasil packing. Seluruh UV berada di tile 0–1; tidak ada face dengan area UV nol.
5. Validasi pasangan segitiga antar-island pada layout akhir menemukan **0 cross-island overlap**. Layout di-pack otomatis; tidak ada intentional overlap yang digunakan.

Perbandingan initial/final menunjukkan bahwa penataan ulang island dan Average Islands Scale menghasilkan texel density yang lebih konsisten. Fasad tidak dibesarkan secara terpisah pada UV study; resolusi detail fasad yang dipakai scene berasal dari atlas produksi 2K.

## Material PBR gedung sekolah

`MAT_School_Building` memakai Principled BSDF. `06_principled_node_graph.png` adalah diagram node yang dibuat dari dan diverifikasi terhadap koneksi material di `.blend`. Saat membuka file, susunan node aslinya dapat dilihat di Shader Editor.

| Image Texture | Color Space | Koneksi |
|---|---|---|
| `School_BaseColor.png` | sRGB | Principled **Base Color** |
| `School_Roughness.png` | Non-Color | Principled **Roughness** |
| `School_Metallic.png` | Non-Color | Principled **Metallic** |
| `School_Normal.png` (OpenGL tangent) | Non-Color | **Normal Map** (Tangent) → Principled **Normal** |
| `School_Emission.png` | sRGB | Principled **Emission Color** |

Map sekolah diekstrak dari image yang telah packed di file sumber. File gambar tersedia di `textures/School_Building/`. Base Color memakai sRGB karena menyimpan warna tampilan. Roughness, Metallic, dan Normal adalah data shading sehingga harus Non-Color. Emission map menyimpan aksen berwarna dan menggunakan sRGB. Tidak ada AO map khusus untuk gedung sekolah.

### QA material dan portability

- `07_pbr_texture_maps.png` memperlihatkan semua map sekolah.
- `08_normal_off.png` / `09_normal_on.png` membandingkan normal detail. Normal map mengubah shading, bukan silhouette geometry.
- `20_normal_strength_low.png` / `21_normal_strength_high.png` membandingkan strength `0.2` dan `1.5`; nilai terlalu tinggi dapat membuat relief terlihat berlebihan. Material produksi memakai strength `0.8`.
- `24_emission_low.png` / `25_emission_high.png` menguji emission strength `0.2` dan `5.0`; material scene memakai emission sebagai aksen pada clock, bukan sumber penerangan utama.
- `10_final_material.png` adalah tampilan akhir asset di bawah lighting render. Scene kampus lengkap ada di `13_campus_final_render.png`.
- File `.blend` menyimpan semua image resource sebagai packed. Folder map tetap disertakan sebagai salinan eksplisit. File dibuka ulang dengan Blender 5.2 untuk memeriksa map dan material.

## Eksplorasi asset eksternal PBR

### Wooden Crate 01 — Poly Haven

Model external crate hadir dalam scene kampus dan disalin ke `assets/Wooden_Crate_01/`.

- Sumber: [Poly Haven — Wooden Crate 01](https://polyhaven.com/a/wooden_crate_01), model oleh James Ray Cock.
- Lisensi: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Kredit tetap dicantumkan sebagai atribusi praktik baik.
- Perbandingan sebelum/sesudah PBR: `11_wooden_crate_pbr_comparison.png`.

| Map 2K | Color Space | Penggunaan |
|---|---|---|
| `wooden_crate_01_diff_2k.jpg` | sRGB | Base Color, dikombinasi AO secara halus |
| `wooden_crate_01_rough_2k.jpg` | Non-Color | Roughness |
| `wooden_crate_01_metal_2k.jpg` | Non-Color | Metallic; membedakan hardware metal dari kayu painted/non-metal |
| `wooden_crate_01_nor_gl_2k.jpg` | Non-Color | Normal Map tangent/OpenGL |
| `wooden_crate_01_ao_2k.jpg` | Non-Color | AO untuk contact/celah, dicampur halus ke Base Color |

Model sumber tidak menyediakan emission map; emission tidak dipaksakan pada crate. Node material `PBR_Wooden_Crate_01_CC0` memakai UV model sumber, Principled BSDF, Normal Map node Strength `0.8`, dan AO Multiply factor `0.7`.

### Karakter, lapangan, dan bus

- Karakter laki-laki/perempuan: [Quaternius Universal Base Characters](https://quaternius.com/packs/universalbasecharacters.html), versi Standard; halaman/lisensi aset menyatakan CC0, periksa kembali lisensi yang menyertai unduhan. Ringkasan map karakter dan perbandingan ada di `12_students_pbr_before_after.png`.
- Lapangan, lapangan upacara, playground, kantin, sekolah, dan bus berasal dari file project P09/P10. Bus pengguna berasal dari `schollbus.blend`.
- File sumber bus merujuk map `T_Bus_*` yang tidak tersedia. Slot material dan node shader aslinya dipertahankan; body diberi map fallback lokal yang disertakan di `textures/School_Bus/`. Map ini bukan tekstur sumber asli. Kekurangan tersebut tidak disamarkan sebagai tekstur PBR resmi bus.

## Dua atau lebih challenge

1. **Multi-material / Metal + painted surface:** Wooden Crate menggunakan map Metallic PBR untuk hardware metal dan bidang kayu non-metal. Bandingkan `11_wooden_crate_pbr_comparison.png`.
2. **Custom emission mask:** emission mask sekolah membatasi emisi pada detail clock, bukan seluruh fasad. Map terlihat di `07_pbr_texture_maps.png`; hasil akhir dan uji strength ditunjukkan pada `10_final_material.png`, `24_emission_low.png`, dan `25_emission_high.png`.
3. **Normal detail dan custom roughness variation:** map memberikan detail shading serta perubahan respons highlight tanpa menambah geometri; uji Normal dan Roughness tersedia di screenshot eksperimen.

## Catatan hasil eksperimen wajib

Semua variasi material memakai duplikat mesh sementara dengan kamera dan tiga sumber Area Light yang sama; mesh/material produksi tidak diubah. Ringkasan visual ada di `15_required_experiments.png`.

| No. | Eksperimen | Bukti | Hasil |
|---:|---|---|---|
| 1 | Dua strategi seam manual | `14_unwrap_seam_comparison.png` | Boundary-only mempertahankan island solver yang belum terpecahkan; tambahan seam hard edge memberi kontrol yang lebih baik. |
| 2 | Manual Unwrap vs Smart UV | `14_unwrap_seam_comparison.png` | Manual menghasilkan 247 island yang mengikuti struktur; Smart UV 260 island dengan keputusan pemotongan otomatis. |
| 3 | Checker distortion | `04_checker_test.png`, `14_checker_stretched.png` | UV skala satu sumbu membuat checker memanjang; kemudian pengujian diisolasi pada duplicate dan UV utama dipertahankan. |
| 4 | Texel density | `03_initial_unwrap.png`, `05_final_uv_layout.png` | Average Islands Scale menormalkan detail relatif sebelum packing. |
| 5 | Margin | `05_final_uv_layout.png` | Pack margin `0.006` memberi jarak antarpulau; layout berada di tile 0–1 tanpa overlap terukur. |
| 6 | Base Color solid vs map | `15_basecolor_solid.png`, `10_final_material.png` | Map menambahkan informasi fasad/window/logo yang tidak dapat diwakili solid color tunggal. |
| 7 | Roughness | `16_roughness_0_1.png`, `17_roughness_0_9.png`, `07_pbr_texture_maps.png` | Nilai 0.1 lebih licin/berkilau; 0.9 lebih menyebarkan highlight. Map memberi variasi per texel. |
| 8 | Metallic | `18_metallic_0.png`, `19_metallic_1.png`, `07_pbr_texture_maps.png` | Nilai 0 non-metal; nilai 1 merespons environment sebagai metal. Map mempertahankan material cat/non-metal sekolah dengan aksen metal yang terbatas. |
| 9 | Color Space roughness | `22_roughness_srgb_test.png`, `23_roughness_noncolor_test.png` | sRGB mengubah interpretasi angka data; Non-Color dipulihkan sebagai setelan yang benar. |
| 10 | Normal Map OFF/ON | `08_normal_off.png`, `09_normal_on.png` | Relief shading berubah, tetapi bentuk siluet tidak berubah. |
| 11 | Normal strength | `20_normal_strength_low.png`, `09_normal_on.png`, `21_normal_strength_high.png` | Strength rendah lebih halus; tinggi lebih kuat namun dapat tampak berlebihan. Produksi memakai 0.8. |
| 12 | Emission strength | `24_emission_low.png`, `25_emission_high.png` | Strength tinggi lebih menonjol; aksen akhir dijaga agar tidak mendominasi material. |

## Refleksi singkat

Bagian tersulit adalah menyeimbangkan seam yang cukup untuk membuka sudut atap, trim, dan fasad tanpa membuat layout tidak terbaca. Checker menunjukkan hubungan langsung antara perubahan bentuk UV dan pola pada surface; karena itu distortion diperbaiki dengan UV/seam, bukan dengan mengganti texture. Average Islands Scale membantu mempertahankan detail yang relatif konsisten, lalu margin `0.006` mencegah island terlalu rapat. Base Color menyimpan warna visual, sedangkan Roughness dan Metallic mengatur respons shading per area. Normal Map memberi detail shading tanpa mengubah silhouette. Emission dipakai selektif sebagai aksen clock agar tetap mendukung hierarki visual sekolah.

## Pertanyaan pemahaman dan analisis

| Pertanyaan inti | Jawaban |
|---|---|
| Apa hubungan geometry, material, texture, dan hasil visual? | Geometry membentuk siluet/volume; material menentukan model respons cahaya; texture memberi nilai Base Color dan data surface per UV texel. |
| Apa fungsi UV, seam, unwrap, dan island? | UV memetakan surface 3D ke koordinat U/V 2D; seam menentukan tempat mesh dibuka; unwrap membentuk island; layout menentukan lokasi dan kepadatan texture. |
| Apa itu distortion dan bagaimana checker membantu? | Distortion adalah perubahan skala/proporsi texel pada surface. Checker yang tidak seragam mengungkap stretching/compression agar seam/unwrap bisa diperbaiki. |
| Apa itu texel density dan kapan boleh tidak seragam? | Banyaknya texel per satuan luas surface. Jaga relatif seragam untuk aset umum; beri kepadatan lebih pada hero detail hanya bila disengaja dan dibuktikan. |
| Kapan overlap UV dapat diterima? | Hanya untuk permukaan identik yang sengaja berbagi texture; bukan untuk bagian unik sekolah yang memerlukan detail berbeda. |
| Manual Unwrap vs Smart UV? | Manual memberi kendali atas seam dan orientasi; Smart UV lebih cepat sebagai baseline tetapi cenderung membuat chart lebih banyak/otomatis. |
| Mengapa Base Color sRGB sedangkan Roughness/Metallic/Normal Non-Color? | Base Color adalah warna yang dikodekan sRGB; map data berisi nilai numerik untuk shading sehingga transformasi gamma warna tidak boleh diterapkan. |
| Apa fungsi Normal Map dan mengapa perlu node Normal Map? | Mengubah normal shading tangent-space secara terkontrol; tidak mengubah geometri/siluet dan harus melalui Normal Map node. |
| Mengapa wooden crate tidak boleh dibuat metal hanya agar reflektif? | Metallic menentukan kelas permukaan dan refleksi Fresnel; kayu tetap non-metal, sementara hardware metal dibedakan oleh Metallic map. |
| Mengapa PBR asset masih perlu lighting yang baik? | Map menentukan respons permukaan, tetapi cahaya/environment menyediakan pantulan, highlight, shadow, dan petunjuk bentuk yang membuat respons PBR terlihat. |

## Checklist pengumpulan

- [x] Folder P10 mandiri berisi file `.blend`, `textures/`, `screenshots/`, README, dan asset PBR eksternal.
- [x] Model utama terverifikasi scale/topologi dan memiliki seam flags serta manual unwrap.
- [x] UV study dipisahkan dari UV atlas produksi.
- [x] Checker test, distortion terkontrol, texel-density adjustment, packing margin, bounds, dan overlap diperiksa.
- [x] Principled BSDF tersambung ke Base Color, Roughness, Metallic, Normal Map, dan Emission.
- [x] sRGB/Non-Color diperiksa pada node image.
- [x] Dua challenge atau lebih dan eksperimen pembanding terdokumentasi.
- [x] Map packed ke `.blend`, salinan texture dan screenshot tersedia.
- [ ] Isi Nama/NRP/kelompok sebelum mengumpulkan.
- [ ] Unggah folder ini ke repository GitHub (bukan ZIP), lalu uji file `.blend` dari hasil clone/download repository.

## Rebuild

`build_p10_uv_pbr.py` membuat ulang file Blender dan render eksperimen dengan Blender 5.2, termasuk node Mapping pada material bertekstur. Script memakai `P10_Kelompok_Sekolah_Kampus.blend` di folder induk sebagai sumber; `make_p10_evidence.py` memakai Pillow untuk menyusun bukti UV/node-map dari data UV dan render. Untuk repo mandiri, file hasil `.blend` dan aset yang tercantum di atas adalah deliverable; script rebuild memerlukan source scene P10 di folder induk.

## Lampiran Pertemuan 11 — Lighting, Camera & Rendering

Paket ini juga menyertakan hasil Pertemuan 11 tanpa mengganti file P10:

- `P11_Kelompok_Sekolah_Kampus.blend`
- `build_p11.py`
- `README_P11.md`
- `environment/studio_small_08_1k.hdr`
- `renders/` berisi render hero, four-light study, three-point, camera/DOF, HDRI, EEVEE/Cycles, sampling, dan denoising
- `textures/` berisi resource PBR pendukung scene P11

Dokumentasi lengkap lighting dan rendering ada pada [README_P11.md](README_P11.md). Sebelum dikumpulkan, lengkapi Nama dan NRP pada kedua README.
