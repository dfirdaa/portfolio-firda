from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from html import escape
import os
import certifi
import pymysql
import cloudinary
import cloudinary.uploader
import resend


# =========================
# Konfigurasi Aplikasi
# =========================
load_dotenv(override=True)
print("DB_NAME TERBACA:", os.getenv("DB_NAME"))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "portfolio_firda_secret_key")

# Konfigurasi Resend
resend.api_key = os.getenv("RESEND_API_KEY")

# Konfigurasi Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


# =========================
# Koneksi Database TiDB
# =========================
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 4000)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"ca": certifi.where()}
    )


# =========================
# Halaman Utama Portfolio
# =========================
@app.route('/')
def home():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM profil LIMIT 1")
    profil = cursor.fetchone()

    cursor.execute("SELECT * FROM skill ORDER BY id ASC")
    skills = cursor.fetchall()

    cursor.execute("SELECT * FROM pengalaman ORDER BY id ASC")
    experiences = cursor.fetchall()

    cursor.execute("SELECT * FROM proyek ORDER BY id ASC")
    projects = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        'index.html',
        profil=profil,
        skills=skills,
        experiences=experiences,
        projects=projects
    )


# =========================
# Contact Form + Resend
# =========================
@app.route('/contact', methods=['POST'])
def contact():
    nama = request.form.get('nama', '').strip()
    email = request.form.get('email', '').strip()
    pesan = request.form.get('pesan', '').strip()

    if not nama or not email or not pesan:
        return redirect(url_for('home') + '#contact')

    # Simpan pesan ke TiDB
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO kontak (nama, email, pesan) VALUES (%s, %s, %s)",
        (nama, email, pesan)
    )

    db.commit()
    cursor.close()
    db.close()

    # Kirim email lewat Resend
    try:
        admin_email = os.getenv("ADMIN_EMAIL")

        if not admin_email:
            print("Email Resend gagal dikirim: ADMIN_EMAIL belum diisi di file .env")
        else:
            nama_safe = escape(nama)
            email_safe = escape(email)
            pesan_safe = escape(pesan).replace("\n", "<br>")

            params = {
                "from": os.getenv(
                    "RESEND_FROM",
                    "Firda Portfolio <onboarding@resend.dev>"
                ),
                "to": [admin_email],
                "subject": f"Pesan Baru dari Portfolio - {nama}",
                "html": f"""
                    <h2>Pesan Baru dari Website Portfolio</h2>

                    <p><strong>Nama:</strong> {nama_safe}</p>
                    <p><strong>Email:</strong> {email_safe}</p>
                    <p><strong>Pesan:</strong></p>
                    <p>{pesan_safe}</p>
                """
            }

            resend.Emails.send(params)

    except Exception as e:
        print("Email Resend gagal dikirim:", e)

    return redirect(url_for('home') + '#contact')


# =========================
# Login Admin
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin'))

        error = "Username atau password salah."

    return render_template('admin/login.html', error=error)


# =========================
# Dashboard Admin
# =========================
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect(url_for('login'))

    return render_template('admin/dashboard.html')


# =========================
# Kelola Profil
# =========================
@app.route('/admin/profil', methods=['GET', 'POST'])
def admin_profil():
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM profil LIMIT 1")
    profil = cursor.fetchone()

    if request.method == 'POST':
        nama_lengkap = request.form['nama_lengkap']
        nama_panggilan = request.form['nama_panggilan']
        universitas = request.form['universitas']
        fakultas = request.form['fakultas']
        program_studi = request.form['program_studi']
        email = request.form['email']

        foto_file = request.files.get('foto')
        foto_url = profil['foto'] if profil and profil.get('foto') else ''

        if foto_file and foto_file.filename != '':
            upload_result = cloudinary.uploader.upload(
                foto_file,
                folder="portfolio_firda/profil"
            )
            foto_url = upload_result['secure_url']

        if profil:
            cursor.execute(
                """
                UPDATE profil
                SET nama_lengkap=%s,
                    nama_panggilan=%s,
                    universitas=%s,
                    fakultas=%s,
                    program_studi=%s,
                    email=%s,
                    foto=%s
                WHERE id=%s
                """,
                (
                    nama_lengkap,
                    nama_panggilan,
                    universitas,
                    fakultas,
                    program_studi,
                    email,
                    foto_url,
                    profil['id']
                )
            )
        else:
            cursor.execute(
                """
                INSERT INTO profil
                (nama_lengkap, nama_panggilan, universitas, fakultas, program_studi, email, foto)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    nama_lengkap,
                    nama_panggilan,
                    universitas,
                    fakultas,
                    program_studi,
                    email,
                    foto_url
                )
            )

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('admin_profil') + '#profil-form')

    cursor.close()
    db.close()

    return render_template('admin/profil.html', profil=profil)


# =========================
# Kelola Skill
# =========================
@app.route('/admin/skill', methods=['GET', 'POST'])
def admin_skill():
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        nama_skill = request.form['nama_skill']
        persentase = request.form['persentase']

        cursor.execute(
            "INSERT INTO skill (nama_skill, persentase) VALUES (%s, %s)",
            (nama_skill, persentase)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('admin_skill'))

    cursor.execute("SELECT * FROM skill ORDER BY id ASC")
    skills = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin/skill.html', skills=skills)


@app.route('/admin/skill/edit/<int:id>', methods=['GET', 'POST'])
def edit_skill(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        nama_skill = request.form['nama_skill']
        persentase = request.form['persentase']

        cursor.execute(
            "UPDATE skill SET nama_skill=%s, persentase=%s WHERE id=%s",
            (nama_skill, persentase, id)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('admin_skill'))

    cursor.execute("SELECT * FROM skill WHERE id=%s", (id,))
    skill = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('admin/edit_skill.html', skill=skill)


@app.route('/admin/skill/delete/<int:id>', methods=['POST'])
def delete_skill(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM skill WHERE id=%s", (id,))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin_skill'))


# =========================
# Kelola Pengalaman
# =========================
@app.route('/admin/pengalaman', methods=['GET', 'POST'])
def admin_pengalaman():
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        jabatan = request.form['jabatan']
        instansi = request.form['instansi']
        tahun = request.form['tahun']
        deskripsi = request.form['deskripsi']

        cursor.execute(
            """
            INSERT INTO pengalaman (jabatan, instansi, tahun, deskripsi)
            VALUES (%s, %s, %s, %s)
            """,
            (jabatan, instansi, tahun, deskripsi)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('admin_pengalaman'))

    cursor.execute("SELECT * FROM pengalaman ORDER BY id ASC")
    experiences = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin/pengalaman.html', experiences=experiences)


@app.route('/admin/pengalaman/edit/<int:id>', methods=['GET', 'POST'])
def edit_pengalaman(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        jabatan = request.form['jabatan']
        instansi = request.form['instansi']
        tahun = request.form['tahun']
        deskripsi = request.form['deskripsi']

        cursor.execute(
            """
            UPDATE pengalaman
            SET jabatan=%s, instansi=%s, tahun=%s, deskripsi=%s
            WHERE id=%s
            """,
            (jabatan, instansi, tahun, deskripsi, id)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('admin_pengalaman'))

    cursor.execute("SELECT * FROM pengalaman WHERE id=%s", (id,))
    pengalaman = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('admin/edit_pengalaman.html', pengalaman=pengalaman)


@app.route('/admin/pengalaman/delete/<int:id>', methods=['POST'])
def delete_pengalaman(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM pengalaman WHERE id=%s", (id,))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin_pengalaman'))


# =========================
# Kelola Proyek
# =========================
@app.route('/admin/proyek', methods=['GET', 'POST'])
def admin_proyek():
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        nama_proyek = request.form['nama_proyek']
        deskripsi = request.form['deskripsi']
        teknologi = request.form['teknologi']

        gambar_url = request.form.get('gambar', '').strip()

        gambar_file = request.files.get('gambar_file')
        if gambar_file and gambar_file.filename != '':
            upload_result = cloudinary.uploader.upload(
                gambar_file,
                folder="portfolio_firda/proyek"
            )
            gambar_url = upload_result['secure_url']

        cursor.execute(
            """
            INSERT INTO proyek (nama_proyek, gambar, deskripsi, teknologi)
            VALUES (%s, %s, %s, %s)
            """,
            (nama_proyek, gambar_url, deskripsi, teknologi)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('admin_proyek'))

    cursor.execute("SELECT * FROM proyek ORDER BY id ASC")
    projects = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin/proyek.html', projects=projects)


@app.route('/admin/proyek/edit/<int:id>', methods=['GET', 'POST'])
def edit_proyek(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM proyek WHERE id=%s", (id,))
    proyek = cursor.fetchone()

    if not proyek:
        cursor.close()
        db.close()
        return redirect(url_for('admin_proyek'))

    if request.method == 'POST':
        nama_proyek = request.form['nama_proyek']
        deskripsi = request.form['deskripsi']
        teknologi = request.form['teknologi']

        gambar_url = proyek['gambar'] if proyek.get('gambar') else ''

        gambar_file = request.files.get('gambar_file')
        if gambar_file and gambar_file.filename != '':
            upload_result = cloudinary.uploader.upload(
                gambar_file,
                folder="portfolio_firda/proyek"
            )
            gambar_url = upload_result['secure_url']
        else:
            gambar_input = request.form.get('gambar', '').strip()
            if gambar_input:
                gambar_url = gambar_input

        cursor.execute(
            """
            UPDATE proyek
            SET nama_proyek=%s, gambar=%s, deskripsi=%s, teknologi=%s
            WHERE id=%s
            """,
            (nama_proyek, gambar_url, deskripsi, teknologi, id)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('admin_proyek'))

    cursor.close()
    db.close()

    return render_template('admin/edit_proyek.html', proyek=proyek)

@app.route('/admin/proyek/delete/<int:id>', methods=['POST'])
def delete_proyek(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM proyek WHERE id=%s", (id,))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin_proyek'))


# =========================
# Kelola Kontak
# =========================
@app.route('/admin/kontak')
def admin_kontak():
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM kontak ORDER BY id DESC")
    kontak = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin/kontak.html', kontak=kontak)


@app.route('/admin/kontak/delete/<int:id>', methods=['POST'])
def delete_kontak(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM kontak WHERE id=%s", (id,))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin_kontak'))


# =========================
# Logout Admin
# =========================
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))


# =========================
# Menjalankan Flask
# =========================
if __name__ == '__main__':
    app.run(debug=True)