-- =====================================================
-- DATABASE PORTFOLIO WEB
-- NIM  : 682024014
-- NAMA : DEWI FIRDA AMALIA
-- =====================================================

CREATE DATABASE IF NOT EXISTS portfolio_db;

USE portfolio_db;

-- Hapus tabel lama jika sudah ada
DROP TABLE IF EXISTS kontak;
DROP TABLE IF EXISTS proyek;
DROP TABLE IF EXISTS pengalaman;
DROP TABLE IF EXISTS skill;
DROP TABLE IF EXISTS profil;
DROP TABLE IF EXISTS admin;

-- =====================================================
-- TABEL ADMIN
-- =====================================================
CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- =====================================================
-- TABEL PROFIL
-- =====================================================
CREATE TABLE profil (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_lengkap VARCHAR(150),
    nama_panggilan VARCHAR(100),
    universitas VARCHAR(150),
    fakultas VARCHAR(150),
    program_studi VARCHAR(150),
    email VARCHAR(150),
    foto VARCHAR(255)
);

-- =====================================================
-- TABEL SKILL
-- =====================================================
CREATE TABLE skill (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_skill VARCHAR(100) NOT NULL,
    persentase INT NOT NULL
);

-- =====================================================
-- TABEL PENGALAMAN
-- =====================================================
CREATE TABLE pengalaman (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jabatan VARCHAR(150) NOT NULL,
    instansi VARCHAR(150) NOT NULL,
    tahun VARCHAR(100),
    deskripsi TEXT
);

-- =====================================================
-- TABEL PROYEK
-- =====================================================
CREATE TABLE proyek (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_proyek VARCHAR(150) NOT NULL,
    gambar VARCHAR(255),
    deskripsi TEXT,
    teknologi VARCHAR(255)
);

-- =====================================================
-- TABEL KONTAK
-- =====================================================
CREATE TABLE kontak (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    pesan TEXT,
    tanggal DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- DATA ADMIN
-- =====================================================
INSERT INTO admin (username, password) VALUES
('admin', 'admin123');

-- =====================================================
-- DATA PROFIL
-- =====================================================
INSERT INTO profil (
    nama_lengkap,
    nama_panggilan,
    universitas,
    fakultas,
    program_studi,
    email,
    foto
) VALUES (
    'Dewi Firda Amalia',
    'Firda',
    'Universitas Kristen Satya Wacana',
    'Fakultas Teknologi Informasi',
    'Sistem Informasi',
    'isi_email_kamu@gmail.com',
    ''
);

-- =====================================================
-- DATA SKILL
-- =====================================================
INSERT INTO skill (nama_skill, persentase) VALUES
('Java', 85),
('Python', 80),
('MySQL', 85);

-- =====================================================
-- DATA PENGALAMAN
-- =====================================================
INSERT INTO pengalaman (jabatan, instansi, tahun, deskripsi) VALUES
('SMK Negeri 1 Tengaran', 'Rekayasa Perangkat Lunak', '2021 - 2024', 'Menempuh pendidikan pada jurusan Rekayasa Perangkat Lunak.'),
('Mahasiswa Sistem Informasi', 'Universitas Kristen Satya Wacana', '2024 - Sekarang', 'Mahasiswa Fakultas Teknologi Informasi Program Studi Sistem Informasi.'),
('Panitia LDKM FTI Gelombang 1', 'Fakultas Teknologi Informasi UKSW', '2026', 'Berpartisipasi sebagai panitia dalam kegiatan Latihan Dasar Kepemimpinan Mahasiswa.');

-- =====================================================
-- DATA PROYEK
-- =====================================================
INSERT INTO proyek (nama_proyek, gambar, deskripsi, teknologi) VALUES
(
    'Sistem Manajemen Perpustakaan',
    '',
    'Aplikasi desktop berbasis Java yang digunakan untuk mengelola data buku, anggota, peminjaman, pengembalian, serta laporan data perpustakaan.',
    'Java, MySQL, Apache NetBeans, XAMPP'
);

-- =====================================================
-- DATA KONTAK CONTOH
-- =====================================================
INSERT INTO kontak (nama, email, pesan) VALUES
('Test Resend', 'test@gmail.com', 'Halo, ini tes pesan dari website portfolio.');