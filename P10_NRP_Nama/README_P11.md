# P11 — Lighting, Camera & Rendering

**Mata kuliah:** EF234504 — Grafika Komputer  
**Praktikum:** Pertemuan 11  
**Blender:** 5.2.0 LTS  
**Nama:** isi nama mahasiswa  
**NRP:** isi NRP  
**Nama asset:** Kampus Sekolah — scene P10 dengan lighting, camera, environment, dan render P11

> Identitas belum diberikan, jadi kolom Nama/NRP sengaja dibiarkan untuk diisi sebelum pengumpulan. Folder ini adalah salinan P11; file P10 sumber tidak ditimpa.

## Isi folder

```text
P11_Kelompok_Sekolah_Kampus/
├── P11_Kelompok_Sekolah_Kampus.blend
├── build_p11.py
├── README.md
├── environment/
│   └── studio_small_08_1k.hdr
├── textures/
│   ├── School_Bus/
│   ├── School_Students/
│   └── Wooden_Crate_01/
└── renders/
    ├── hero_final.png
    ├── render_eevee.png
    ├── render_cycles.png
    ├── render_metrics.csv
    └── ...render studi lainnya
```

File `.blend` mengemas semua image yang digunakan (73/73 image terpaket), termasuk HDRI. Folder `textures/` dan `environment/` juga disertakan sebagai salinan sumber yang mudah diperiksa. File final dibuka ulang dengan Blender 5.2.0 tanpa texture missing. Playground menapak pada permukaan ground (`Z minimum = 0`); bus diletakkan di depan tanpa menimpa lapangan upacara atau playground.

## Scene P10 yang digunakan

Scene P10 dipakai sebagai aset dasar, bukan dibuat ulang. Gedung sekolah tetap menjadi hero subject; lapangan olahraga, lapangan upacara, playground, kantin, bus, siswa, dan aset peti PBR menjadi konteks kampus. `ENV_Ground` adalah ground yang menerima bayangan dan menjadi referensi ruang. Kamera akhir memakai komposisi kampus lebar dengan ruang kosong di langit dan foreground.

File sumber bus dari proyek sendiri adalah `schollbus.blend`. Mesh dan enam material slot aslinya dipertahankan. Image `T_Bus_*` yang dirujuk file sumber tidak tersedia, jadi node material PBR bus diisi map pengganti yang sudah disertakan di `textures/School_Bus/`; map ini bukan tekstur asli yang hilang. Aset siswa diadaptasi dari Universal Base Characters Quaternius dan geometri seragam merupakan tambahan proyek. Wooden Crate 01 dari Poly Haven dan asset PBR sekolah dari P10 tetap ada dalam scene.

### Sumber aset dan lisensi

| Aset | Sumber | Lisensi / catatan |
|---|---|---|
| HDRI `studio_small_08_1k.hdr` | [Poly Haven — Studio Small 08](https://polyhaven.com/a/studio_small_08) oleh Sergej Majboroda | [CC0](https://polyhaven.com/license); penggunaan dan atribusi diperbolehkan, kredit dicantumkan sebagai praktik baik. |
| Wooden Crate 01 | [Poly Haven](https://polyhaven.com/a/wooden_crate_01), James Ray Cock | CC0; map PBR ada di `textures/Wooden_Crate_01/`. |
| Karakter laki-laki/perempuan | [Quaternius — Universal Base Characters Kit](https://quaternius.com/packs/universalbasecharacters.html) | Halaman aset Standard menyatakan CC0 untuk proyek personal, edukasi, dan komersial. Ikuti lisensi yang menyertai versi aset saat diunduh. |
| Bus sekolah | `schollbus.blend`, file milik proyek | Model dan slot material asli dipakai. Map fallback lokal diberi label/didokumentasikan. |
| Gedung sekolah, lapangan, kantin, playground | File proyek P09/P10 | Aset yang sudah tersedia dalam proyek. |

## Lighting

### Empat jenis lampu

Empat lampu studi tersedia sebagai `TEST_Point`, `TEST_Sun`, `TEST_Spot`, dan `TEST_Area`. Tiap studi render memakai kamera, komposisi, material, dan HDRI redup yang sama; hanya lampu uji yang dinyalakan.

| Jenis | Setup studi | Karakter yang diuji | Bukti |
|---|---|---|---|
| Point | 2.200 W; posisi lokal di depan-samping; radius 0,08 m vs 2 m | Memancar ke semua arah dari satu titik; radius lebih besar melembutkan bayangan. | [point](renders/light_point.png), [radius kecil](renders/point_radius_small.png), [radius besar](renders/point_radius_large.png) |
| Sun | Strength 2; angle 1° vs 30°; arah diubah dengan rotasi | Cahaya directional yang sejajar; lokasi bukan pengendali arah utamanya; angle besar melembutkan shadow. | [sun](renders/light_sun.png), [angle kecil](renders/sun_angle_small.png), [angle besar](renders/sun_angle_large.png) |
| Spot | 4.000 W; cone 60°; blend 0,05 vs 0,85 | Cahaya berbentuk cone yang berguna untuk focal/dramatic lighting; blend tinggi melembutkan batas cone. | [spot](renders/light_spot.png), [blend rendah](renders/spot_blend_low.png), [blend tinggi](renders/spot_blend_high.png) |
| Area | 18.000 W; size 2 m vs 18 m | Sumber luas seperti softbox; area lebih besar menghasilkan transisi shadow dan highlight lebih lembut. | [area](renders/light_area.png), [size kecil](renders/area_size_small.png), [size besar](renders/area_size_large.png) |

### Setup three-point final

| Lampu | Posisi kira-kira | Power | Ukuran | Fungsi |
|---|---:|---:|---:|---|
| `Key_Light` | `(-22, -18, 28)` | 22.000 W | 15 m | Area utama dari depan-kiri dan atas; membentuk volume serta bayangan. |
| `Fill_Light` | `(20, -7, 20)` | 8.500 W | 18 m | Mengisi sisi gelap secara lebih lembut dan tetap mempertahankan kontras. |
| `Rim_Light` | `(-1, 20, 24)` | 14.500 W | 12 m | Back/side light untuk memisahkan siluet dari latar. |

Setup final memakai key hangat ringan, fill biru netral, dan rim hangat. Fill lebih lemah daripada Key agar bayangan tidak hilang. Studi rasio membandingkan Fill sekitar 95%, 48%, dan 18% dari Key; versi seimbang dipilih untuk hero. Rim OFF/ON dan render three-point tersedia di [folder renders](renders/).

## Camera dan komposisi

- `Hero_Camera`: 50 mm, elevated three-quarter view; komposisi utama berpusat pada gedung, sementara jalan masuk menjadi leading line menuju pintu sekolah.
- Resolusi hero: 1440 × 900. Hero memakai Cycles, 64 samples, denoising aktif, AgX, dan DOF halus.
- DOF memakai `DOF_Focus_School` sebagai Focus Object. Hero menggunakan f/11 agar sekolah tajam dan area kampus masih terbaca. Perbandingan DOF OFF dan f/3,5 ada di [dof_off](renders/dof_off.png) dan [dof_on](renders/dof_on.png).
- `Detail_Camera` memberi close-up alternatif ke bus; hasilnya ada di [detail_camera](renders/detail_camera.png).
- Komposisi terpusat dibandingkan dengan alternatif rule-of-thirds/negative-space: [center](renders/composition_center.png) dan [alternative](renders/composition_rule_of_thirds.png).
- Angle dibandingkan dengan kamera eye-level, low, dan high: [eye-level](renders/angle_eye_level.png), [low](renders/angle_low.png), [high](renders/angle_high.png).
- Focal length 24/50/85 mm dibandingkan dengan kamera yang dipindahkan untuk menjaga ukuran sekolah relatif serupa: [24 mm](renders/focal_24.png), [50 mm](renders/focal_50.png), [85 mm](renders/focal_85.png). 24 mm memberi perspektif lebih lebar, 50 mm lebih moderat, dan 85 mm lebih terkompresi dengan sudut pandang sempit.

## HDRI / environment

HDRI 1K Poly Haven dipasang pada World Shader: `Texture Coordinate → Mapping → Environment Texture → Background → World Output`. Mapping mengubah rotasi Z untuk uji 0° dan 90°; nilai Strength final 0,28. `Light Path` mencampur HDRI sebagai sumber pencahayaan/refleksi dengan background abu-abu netral khusus camera ray, supaya pantulan environment bekerja tanpa mengganggu latar render. Tiga lampu studio melengkapi HDRI untuk mengontrol focal point. Perbandingan orientasi: [HDRI studio](renders/hdri_studio.png), [HDRI diputar 90°](renders/hdri_rotation_90.png).

## EEVEE, Cycles, sampling, dan denoising

| Render | Engine | Resolusi | Setting | Waktu render pada mesin ini |
|---|---|---:|---|---:|
| [EEVEE](renders/render_eevee.png) | EEVEE | 1280 × 720 | setup, camera, HDRI sama dengan pembanding Cycles | lihat `render_metrics.csv` |
| [Cycles](renders/render_cycles.png) | Cycles | 1280 × 720 | 32 samples, denoising ON | lihat `render_metrics.csv` |
| [Hero final](renders/hero_final.png) | Cycles | 1440 × 900 | 64 samples, denoising ON, AgX | lihat `render_metrics.csv` |

Perbandingan engine menjaga scene, camera, material, HDRI, lighting, dan resolusi sama; yang diubah adalah render engine dan setting engine. EEVEE dipakai untuk iterasi cepat, sedangkan Cycles memberi pencahayaan tidak langsung dan respons shadow yang lebih fisikal dengan waktu render lebih tinggi.

Sampling study memakai 8, 24, dan 64 samples pada 640 × 360 tanpa denoising agar perubahan noise mudah dibandingkan: [8](renders/sampling_08.png), [24](renders/sampling_24.png), [64](renders/sampling_64.png). Denoising diuji pada 16 samples yang sama: [OFF](renders/denoise_off.png), [ON](renders/denoise_on.png). `renders/render_metrics.csv` mencatat engine, resolusi, samples, denoising, dan waktu render terukur untuk setiap render. Waktu adalah pengukuran lokal dan bergantung pada perangkat.

## Challenge yang dikerjakan

1. **Dramatic lighting:** Key 26.000 W, Fill 2.200 W, Rim 15.500 W; meningkatkan contrast dan tetap mengarahkan perhatian ke sekolah. [Render](renders/challenge_dramatic.png)
2. **Soft studio lighting:** Key/Fill memakai area besar dengan Fill lebih kuat, Rim lembut; menghasilkan bayangan dan highlight yang lebih halus. [Render](renders/challenge_soft_studio.png)
3. **Two-camera story:** `Hero_Camera` untuk kampus utuh dan `Detail_Camera` untuk bus dengan DOF. [Detail render](renders/detail_camera.png)
4. **HDRI + artistic lighting:** HDRI digabungkan dengan Key/Fill/Rim; rotasi environment dievaluasi sebelum memilih 0°. [Render rotasi](renders/hdri_rotation_90.png)

## Indeks dokumentasi wajib

| Dokumentasi | File |
|---|---|
| Point Light | [light_point.png](renders/light_point.png) |
| Sun Light | [light_sun.png](renders/light_sun.png) |
| Spot Light | [light_spot.png](renders/light_spot.png) |
| Area Light | [light_area.png](renders/light_area.png) |
| Three-point lighting | [three_point.png](renders/three_point.png) |
| Center composition | [composition_center.png](renders/composition_center.png) |
| Alternative composition | [composition_rule_of_thirds.png](renders/composition_rule_of_thirds.png) |
| Camera angles | [eye-level](renders/angle_eye_level.png), [low](renders/angle_low.png), [high](renders/angle_high.png) |
| Focal length | [24 mm](renders/focal_24.png), [50 mm](renders/focal_50.png), [85 mm](renders/focal_85.png) |
| DOF | [OFF](renders/dof_off.png), [ON](renders/dof_on.png) |
| HDRI dan rotation | [0°](renders/hdri_studio.png), [90°](renders/hdri_rotation_90.png) |
| EEVEE / Cycles | [EEVEE](renders/render_eevee.png), [Cycles](renders/render_cycles.png) |
| Sampling / denoising | [8/24/64 samples](renders/sampling_08.png), [denoise OFF](renders/denoise_off.png), [ON](renders/denoise_on.png) |
| Final hero | [hero_final.png](renders/hero_final.png) |

## Checklist pengumpulan

- [x] File P11 tersimpan terpisah dari P10.
- [x] Asset P10, ground, material, dan tekstur digunakan; semua 73 image pada `.blend` terpaket.
- [x] Point, Sun, Spot, Area, soft source radius/angle/blend/size diuji.
- [x] Three-point: Key, Fill, Rim; rasio Fill dan Rim OFF/ON diuji.
- [x] Center/alternative composition, tiga camera angle, focal length 24/50/85 mm, dan DOF dibandingkan.
- [x] HDRI terpasang, Strength dicatat, orientasi 0°/90° diuji dan dipadukan dengan lampu studio.
- [x] EEVEE, Cycles, sampling 8/24/64, denoising OFF/ON, dan metadata waktu render tersedia.
- [x] EEVEE vs Cycles memakai komposisi dan resolusi yang sama.
- [x] Lebih dari dua challenge dan final hero render tersedia.
- [x] README dan folder `environment/`, `textures/`, `renders/` tersedia.

## Refleksi praktikum

1. Area Light paling cocok untuk setup product-style ini karena ukuran sumber dapat dipakai untuk mengendalikan softness tanpa menghilangkan bentuk sekolah.
2. Key membangun arah dan volume, Fill menjaga detail pada sisi bayangan, dan Rim membantu memisahkan silhouette dari bukit/latar.
3. Elevated three-quarter view paling informatif: fasad sekolah terbaca sekaligus lapangan dan bus masih terlihat.
4. Focal length 50 mm dipilih untuk hero karena perspektifnya moderat dan dapat menampilkan kampus dengan distorsi yang terkendali.
5. DOF diarahkan ke sekolah; f/11 pada hero hanya memberi blur halus agar elemen kampus lain tetap terbaca, sedangkan f/3,5 dipakai untuk demonstrasi efek yang lebih nyata.
6. HDRI memberi iluminasi dan pantulan lingkungan; memutarnya mengubah pola highlight, sehingga Strength ditahan dan Area Light dipakai untuk mengontrol fokus.
7. EEVEE menghasilkan iterasi yang jauh lebih cepat, sedangkan Cycles membutuhkan waktu lebih lama tetapi memberi respons indirect light dan shadow lebih meyakinkan.
8. Kenaikan samples mengurangi noise tetapi menambah waktu; denoising mempercepat hasil bersih, meskipun detail halus tetap perlu samples yang memadai.
9. Perubahan paling penting adalah menyeimbangkan komposisi dan rasio Key/Fill/Rim, bukan sekadar menaikkan seluruh daya lampu.

## Pertanyaan pemahaman

| Pertanyaan | Jawaban ringkas |
|---|---|
| Apa fungsi lighting? Mengapa model bagus dapat terlihat datar? | Lighting mengungkap bentuk, material, volume, depth, dan bayangan. Model tampak datar jika arah/kontras cahaya tidak memberi petunjuk volume, misalnya Key dan Fill frontal serta hampir sama kuat. |
| Apa fungsi camera? | Memilih apa yang terlihat, posisi pandang, perspektif, komposisi, dan ruang negatif; camera adalah alat komunikasi visual, bukan sekadar alat mengambil gambar. |
| Apa karakter Point Light? Parameter utama dan pengaruh Radius? | Cahaya lokal memancar ke semua arah. Power, color, location, dan radius mengatur hasil; radius kecil menghasilkan bayangan lebih tajam, radius besar lebih lembut. |
| Apa karakter Sun Light? Mengapa Rotation penting dan apa pengaruh Angle? | Sun mensimulasikan sumber jauh dengan sinar hampir sejajar; rotasi menentukan arah datang cahaya/bayangan, sedangkan Angle kecil membuat shadow tajam dan angle besar melembutkannya. |
| Apa karakter Spot Light? Fungsi Spot Size dan Blend? | Spot menghasilkan cone terarah untuk accent atau focal pool. Size mengatur lebar cone; Blend mengatur kelembutan transisi di batas cone. |
| Apa karakter Area Light dan mengapa cocok untuk product render? | Area menyerupai softbox sehingga highlight dan shadow dapat dikontrol dengan baik; ukuran lebih besar memberi transisi cahaya/bayangan yang lebih lembut. |
| Apa lima aspek evaluasi light? | Direction, intensity/power, color, softness, dan contrast. |
| Apa itu three-point lighting? | Setup Key, Fill, dan Rim/Back yang masing-masing membentuk subject, mengontrol kontras, dan memisahkan silhouette. |
| Apa fungsi Key, Fill, dan Rim? Mengapa Fill biasanya lebih lemah dari Key? | Key menentukan bentuk utama; Fill membuka detail shadow tanpa menghapusnya; Rim memberi edge separation. Fill lebih lemah supaya depth dan contrast tetap terasa. |
| Apa itu camera composition dan negative space? | Composition adalah susunan subject dalam frame. Negative space ialah ruang kosong yang sengaja disisakan agar subject punya ruang bernapas dan hierarki jelas. |
| Apa itu rule of thirds? | Pembagian frame menjadi 3×3; subject/focal point ditempatkan dekat garis atau titik potong agar komposisi terasa dinamis. |
| Kapan center composition cocok? | Untuk subject simetris, presentasi formal/teknis, atau product hero yang membutuhkan stabilitas dan fokus langsung. |
| Bagaimana low angle dan high angle memengaruhi persepsi? | Low angle membuat subject terasa lebih dominan/tinggi; high angle memperlihatkan permukaan atas dan konteks layout serta mengurangi kesan dominan. |
| Apa itu focal length? | Panjang fokus lensa yang mengubah field of view dan karakter perspektif. |
| Apa karakter focal length wide, 35–50 mm, dan 85 mm ke atas? | Wide seperti 24 mm memberi FOV luas dan perspektif lebih kuat; 35–50 mm lebih moderat/natural; 85 mm+ lebih sempit dan mengompresi kedalaman. |
| Mengapa posisi camera harus disesuaikan saat membandingkan focal length? | Agar ukuran subject dalam frame mendekati sama; jika posisi tetap, perubahan FOV mengubah ukuran framing sekaligus sehingga perbandingan perspektif tidak adil. |
| Apa itu Depth of Field? | Rentang jarak yang terlihat tajam; objek di luar fokus menjadi blur. |
| Apa fungsi Focus Object/Distance? | Menentukan bidang/jarak yang harus tajam dan memudahkan kontrol fokus secara eksplisit. |
| Apa pengaruh F-stop kecil dan besar? | F-stop kecil memberi DOF dangkal/blur lebih kuat; f-stop besar memberi rentang fokus lebih luas. |
| Apa itu HDRI dan Image-Based Lighting? | HDRI menyimpan informasi lingkungan/high dynamic range; IBL menggunakan citra environment untuk menerangi scene dan memberi pantulan. |
| Mengapa HDRI memengaruhi reflection dan perlu diputar? | Peta HDRI berisi sumber terang dan bentuk environment; rotasi menggeser highlight/reflection serta arah cahaya yang diterima material. |
| Mengapa HDRI boleh digabungkan dengan light tambahan? | HDRI memberi respons lingkungan alami; lampu tambahan memberi kontrol artistik atas key, fill, rim, dan hierarki visual. |
| Apa karakter EEVEE? | Render real-time/raster yang responsif dan cocok untuk preview serta iterasi cepat. |
| Apa karakter Cycles dan path tracing? | Cycles mengikuti lintasan cahaya secara sampling untuk indirect light, shadow, dan reflection lebih fisikal; biaya render umumnya lebih tinggi. |
| Apa itu sampling? Hubungannya dengan noise dan render time? | Sampling adalah jumlah estimasi/pengambilan kontribusi cahaya; lebih banyak samples cenderung mengurangi noise tetapi memperpanjang render. |
| Apa fungsi denoising dan apa batasannya? | Memperkirakan/mengurangi noise dari render sampel rendah; bukan pengganti lighting baik atau samples memadai, dan bisa menghilangkan detail bila input terlalu noisy. |
| Mengapa rendering bersifat iteratif? | Karena komposisi, pencahayaan, material, fokus, dan biaya render saling memengaruhi; render-test-inspect-adjust mengisolasi perubahan dan memperbaiki masalah bertahap. |
| Kapan memilih EEVEE dan kapan Cycles? | EEVEE untuk preview, layout, dan iterasi cepat; Cycles untuk hasil akhir yang memerlukan indirect light/reflection lebih fisikal, dengan kompromi waktu dan hardware. |

## Pertanyaan analisis

| Kasus | Analisis |
|---|---|
| A — Key dan Fill frontal dengan intensitas hampir sama membuat asset datar. | Arah cahaya kurang membentuk volume dan Fill menghapus kontras. Pindahkan Key ke samping/atas, turunkan Fill, lalu gunakan Rim seperlunya. |
| B — Mengapa Area lebih besar melembutkan product render? | Sumber tampak menempati sudut lebih besar dari subject, sehingga shadow boundary menjadi lebih lebar dan transisi highlight lebih gradual. |
| C — Apa yang terjadi jika Fill lebih kuat daripada Key? | Contrast turun, arah cahaya utama menjadi tidak jelas, dan scene berisiko tampak flat. |
| D — Mengapa Rim membantu bila tonal subject/background berdekatan? | Edge highlight memberi pemisahan luminance/color pada silhouette yang selain itu akan menyatu dengan latar. |
| E — Mengapa perbandingan 24 mm dan 85 mm tidak adil bila camera tidak dipindah? | FOV dan ukuran subject di frame berubah besar; camera perlu dipindahkan agar framing sebanding dan efek perspektif dapat dinilai. |
| F — Mengapa DOF sangat dangkal tidak selalu profesional? | Blur berlebihan dapat menyembunyikan detail penting, membuat skala kampus tidak terbaca, atau terlihat sebagai efek tanpa tujuan. |
| G — Mengapa rotasi HDRI dapat mengubah metal secara drastis? | Material metal merefleksikan environment dengan kuat; rotasi memindahkan sumber terang/gelap yang dipantulkan. |
| H — Mengapa EEVEE tetap berguna bila final memakai Cycles? | EEVEE memberi feedback komposisi dan pencahayaan dengan cepat sebelum render final yang lebih mahal. |
| I — Mengapa menaikkan samples bukan satu-satunya perbaikan noise? | Scene terlalu gelap, light placement, pantulan glossy, dan jumlah cahaya yang masuk sampel juga penyebab noise; perbaiki sumber masalah dan gunakan denoising terkontrol. |
| J — Mengapa hero image merupakan gabungan asset, material, lighting, camera, dan engine? | Tiap bagian menentukan bentuk, respons permukaan, hierarki visual, perspektif, dan cara estimasi cahaya; hasil tidak ditentukan oleh satu tombol render saja. |

## Membuka ulang / regenerasi

1. Buka `P11_Kelompok_Sekolah_Kampus.blend` dengan Blender 5.2 atau versi kompatibel.
2. Untuk menghasilkan ulang studi dan render, jalankan `build_p11.py` dari Blender dengan file P11 tersebut aktif. Skrip menulis hasil ke `renders/`, memperbarui CSV waktu, mengemas image, lalu menyimpan file P11.
3. Sebelum mengumpulkan, isi nama dan NRP, lalu cek kembali README dan render hero. Waktu render pada CSV berlaku untuk mesin tempat skrip dijalankan dan dapat berbeda di perangkat lain.
