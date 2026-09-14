# Figma Anima Pro Interceptor

Repositori ini berisi skrip automasi proxy interceptor berbasis **mitmproxy** untuk memodifikasi response API dari **Anima App** (`api.animaapp.com`) dan **Stigg Entitlements** (`edge.api.stigg.io`) secara lokal. Skrip ini meng-override batasan akun (plan, kuota export, screen limit, dan fitur eksperimental) menjadi status **Business / Unlimited** pada plugin Figma Anima.

---

## 📋 Daftar Isi

- [Fitur & Kemampuan](#-fitur--kemampuan)
- [Prasyarat Sistem](#-prasyarat-sistem)
- [Instalasi](#-instalasi)
- [Konfigurasi Sertifikat SSL (Penting)](#-konfigurasi-sertifikat-ssl-penting)
- [Cara Penggunaan](#-cara-penggunaan)
- [Detail Modifikasi API](#-detail-modifikasi-api)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#-disclaimer)

---

## ✨ Fitur & Kemampuan

Skrip [`modify_anima.py`](modify_anima.py) melakukan inspeksi dan transformasi payload JSON pada lalu lintas HTTP/HTTPS secara real-time:

- **Plan Upgrade:** Mengubah status plan akun dan tim menjadi `Business`.
- **Admin & Permissions:** Mengaktifkan flag `is_admin: true`, `is_in_paying_team: true`, dan `access_level: owner`.
- **Unlimited Usage & Limits:** Menghapus batas kuota dengan menaikkan limit hingga `99999` (screens, Storybook components, active projects, dan dev-mode exports).
- **Entitlements Bypass:** Mengaktifkan semua izin fitur (`is_granted: true`, `hasUnlimitedUsage: true`, `hasSoftLimit: false`, `accessDeniedReason: null`).
- **Fitur Eksperimental:** Memaksa aktivasi semua toggle eksperimen pada endpoint `/users/me`.
- **Project Unlock:** Membuka status proyek (`is_locked: false`, `is_archived: false`).

---

## 💻 Prasyarat Sistem

1. **Sistem Operasi:** Windows 10 / 11.
2. **Python:** Versi 3.9+ (Opsional jika menginstal mitmproxy executable).
3. **Mitmproxy:** Versi 9.x atau 10.x+.
4. **Figma Desktop App** atau Browser (Chrome / Edge / Firefox).

---

## 🚀 Instalasi

### 1. Install mitmproxy

Pilih salah satu metode instalasi mitmproxy di Windows:

#### Opsi A: Menggunakan `pip` (Python)

```bash
pip install mitmproxy
```

#### Opsi B: Menggunakan `winget`

```bash
winget install mitmproxy.mitmproxy
```

#### Opsi C: Menggunakan `choco` (Chocolatey)

```bash
choco install mitmproxy
```

Atau unduh installer resmi standalone langsung dari situs [mitmproxy.org](https://mitmproxy.org/).

---

## 🔒 Konfigurasi Sertifikat SSL (Penting)

Karena Anima berkomunikasi melalui protokol HTTPS, sertifikat root CA mitmproxy wajib diinstal ke sistem Windows:

1. Jalankan mitmproxy satu kali di terminal (`mitmproxy` atau `mitmweb`) agar file sertifikat dibuat di direktori profil pengguna.
2. Buka folder sertifikat:
   ```text
   %USERPROFILE%\.mitmproxy
   ```
3. Klik dua kali pada file `mitmproxy-ca-cert.cer` atau `mitmproxy-ca-cert.p12`.
4. Pilih **Install Certificate...** ➔ **Local Machine** (atau Current User).
5. Pilih **Place all certificates in the following store** ➔ Klik **Browse**.
6. Pilih **Trusted Root Certification Authorities** (Otoritas Sertifikasi Akar Tepercaya).
7. Klik **Next** lalu **Finish** hingga muncul notifikasi sukses.

> **Tips:** Anda juga bisa membuka browser saat proxy aktif dan mengunjungi [http://mitm.it](http://mitm.it) untuk mengunduh dan menginstal sertifikat secara langsung.

---

## 🛠️ Cara Penggunaan

### 1. Konfigurasi Manual Proxy Windows

1. Buka **Settings** di Windows (`Win + I`).
2. Masuk ke **Network & internet** ➔ **Proxy**.
3. Pada bagian **Manual proxy setup**, klik **Set up** / **Edit**.
4. Aktifkan **Use a proxy server**:
   - **Proxy IP address:** `127.0.0.1`
   - **Port:** `8080`
5. Klik **Save**.

---

### 2. Menjalankan Interceptor

Buka Command Prompt atau PowerShell di folder project:

#### Opsi 1: Menjalankan dengan Tampilan Web UI (Rekomendasi)

```cmd
mitmweb -s modify_anima.py
```

_Antarmuka Web UI akan otomatis terbuka di `http://127.0.0.1:8081` untuk memantau request dan response yang dimodifikasi._

#### Opsi 2: Menjalankan di Terminal (CLI Mode)

```cmd
mitmproxy -s modify_anima.py
```

---

### 3. Buka Figma & Gunakan Plugin Anima

1. Buka aplikasi **Figma Desktop** atau browser.
2. Buka plugin **Anima** (Anima for Figma).
3. Akun dan fitur akan otomatis terdeteksi dengan status **Business Plan** dengan limit tak terbatas.

---

## 🔍 Detail Modifikasi API

Skrip menyaring dan memodifikasi endpoint berikut:

| Endpoint Target           | Host                | Modifikasi Utama                                                                     |
| :------------------------ | :------------------ | :----------------------------------------------------------------------------------- |
| `/v2/users/me`            | `api.animaapp.com`  | `plan="Business"`, `is_in_paying_team=True`, `is_admin=True`, eksperimen aktif       |
| `/v2/team_memberships`    | `api.animaapp.com`  | `team_plan="Business"`, `access_level="owner"`, limit screens & components = `99999` |
| `/v2/projects/`           | `api.animaapp.com`  | `is_locked=False`, `is_archived=False`                                               |
| `/v2/.../entitlements`    | `api.animaapp.com`  | `is_granted=True`, `limit=99999.0`, `usage=0.0`                                      |
| `entitlements-state.json` | `edge.api.stigg.io` | `usageLimit=99999`, `hasUnlimitedUsage=True`, `isGranted=True`                       |

---

## ❓ Troubleshooting

| Kendala                                                  | Solusi                                                                                                                                                                                      |
| :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Koneksi internet terputus saat proxy aktif**           | Pastikan `mitmproxy` / `mitmweb` sudah berjalan di terminal sebelum proxy diaktifkan.                                                                                                       |
| **Error SSL / Security Warning pada Figma atau Browser** | Sertifikat CA mitmproxy belum diinstal ke folder _Trusted Root Certification Authorities_. Ulangi langkah di bagian [Konfigurasi Sertifikat](#-konfigurasi-sertifikat-ssl-penting).         |
| **Fitur Anima tidak berubah**                            | Buka `http://127.0.0.1:8081`, cari request ke `api.animaapp.com` atau `edge.api.stigg.io`, dan pastikan status response termodifikasi. Muat ulang (restart / reload) plugin Anima di Figma. |
| **Port 8080 bentrok / sudah digunakan**                  | Jalankan dengan port lain, contoh: `mitmweb -p 8888 -s modify_anima.py`, lalu sesuaikan port di pengaturan proxy Windows.                                                                   |

---

## ⚠️ Disclaimer

Project ini dibuat hanya untuk **tujuan riset, edukasi, dan pengujian lokal (debugging network traffic)**. Pengembang tidak bertanggung jawab atas penyalahgunaan skrip ini di luar lingkungan pengujian pribadi.
