import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
import skfuzzy.control as ctrl

#crop ds
pd.set_option('display.max_rows', 260)
pd.set_option('display.max_columns', 10)

def fuzzy_rendah(x, b_rendah, b_sedang):
    if x <= b_rendah:
        return 1.0
    elif b_rendah < x < b_sedang:
        return (b_sedang - x) / (b_sedang - b_rendah)
    else:
        return 0.0

def fuzzy_sedang(x, b_rendah, b_sedang, b_tinggi):
    if x <= b_rendah or x >= b_tinggi:
        return 0.0
    elif b_rendah < x <= b_sedang:
        return (x - b_rendah) / (b_sedang - b_rendah)
    elif b_sedang < x < b_tinggi:
        return (b_tinggi - x) / (b_tinggi - b_sedang)

def fuzzy_tinggi(x, b_sedang, b_tinggi):
    if x <= b_sedang:
        return 0.0
    elif b_sedang < x < b_tinggi:
        return (x - b_sedang) / (b_tinggi - b_sedang)
    else:
        return 1.0

def plot_membership(b_rendah, b_sedang, b_tinggi, nama_kriteria):
    x = np.linspace(0, 24 if b_tinggi > 10 else 10, 500)
    y_rendah = [fuzzy_rendah(i, b_rendah, b_sedang) for i in x]
    y_sedang = [fuzzy_sedang(i, b_rendah, b_sedang, b_tinggi) for i in x]
    y_tinggi = [fuzzy_tinggi(i, b_sedang, b_tinggi) for i in x]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(x, y_rendah, label='Rendah', color='green')
    ax.plot(x, y_sedang, label='Sedang', color='orange')
    ax.plot(x, y_tinggi, label='Tinggi', color='red')
    ax.set_title(f"Kurva Keanggotaan {nama_kriteria}")
    ax.set_xlabel("Nilai")
    ax.set_ylabel("Derajat Keanggotaan")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    return fig

st.set_page_config(page_title="SPK Kesehatan Mental Mahasiswa", layout="wide")
st.title("Sistem Pendukung Keputusan: Menentukan Tingkat Kesehatan Mental Mahasiswa")
st.write("Aplikasi analisis tingkat kesehatan mental berbasis Logika Fuzzy Mamdani.")

menu = st.sidebar.selectbox(
    "Navigasi Halaman",
    ["Halaman Data", "Halaman Hitung SPK", "Halaman Profil"]
)

@st.cache_data
def load_local_data():
    try:
        df = pd.read_csv('student_mental_health_burnout_1M.csv')
        df = df[df["study_hours_per_day"] > 0]
        df = df[df["gender"] != "Other"]
        df = df.round(1)
        df_terbatas = df.iloc[:260, :10]
        return df_terbatas
    except FileNotFoundError:
        st.error(
            "Gagal membaca data! Pastikan file "
            "'student_mental_health_burnout_1M.csv' "
            "berada di folder yang sama."
        )
        return None

if 'dataset' not in st.session_state or st.session_state['dataset'] is None:
    st.session_state['dataset'] = load_local_data()

# Halaman Utama (nampilin seluruh data)

if menu == "Halaman Data":
    st.header("Data Seluruh Mahasiswa")

    if st.session_state['dataset'] is not None:
        df_display = st.session_state['dataset']
        st.success(
            f"Berhasil memuat data! "
            f"Ukuran Data Saat Ini: "
            f"{df_display.shape[0]} baris × {df_display.shape[1]} kolom."
        )
        st.subheader("Tampilan Dataset")
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("File CSV belum ditemukan.")


# HALAMAN HITUNG SPK

elif menu == "Halaman Hitung SPK":
    st.header("Proses Perhitungan Fuzzy SPK")

    if st.session_state['dataset'] is None:
        st.error("Dataset belum termuat.")
    else:
        df_proses = st.session_state['dataset'].copy()
        all_columns = df_proses.columns.tolist()

        st.subheader("1. Konfigurasi Kriteria & Batas Defuzzifikasi")
        st.write("Pilih kolom kriteria yang sesuai dari dataset Anda.")

        col1, col2, col3 = st.columns(3)

        with col1:
            idx_k1 = all_columns.index("stress_level")
            kriteria_1 = st.selectbox("Stress Level", all_columns, index=idx_k1)
            batas_k1 = st.slider(f"Batas 'Sedang' untuk {kriteria_1}", 1.0, 10.0, 5.0, step=0.1, key="k1")

            idx_k2 = all_columns.index("study_hours_per_day")
            kriteria_2 = st.selectbox("Study Hours", all_columns, index=idx_k2)
            batas_k2 = st.slider(f"Batas 'Sedang' untuk {kriteria_2}", 0.0, 24.0, 8.0, step=1.0, key="k2")

        with col2:
            idx_k3 = all_columns.index("sleep_hours")
            kriteria_3 = st.selectbox("Sleep Hours", all_columns, index=idx_k3)
            batas_k3 = st.slider(f"Batas 'Sedang' untuk {kriteria_3}", 0.0, 24.0, 5.0, step=1.0, key="k3")

            idx_k4 = all_columns.index("exam_pressure")
            kriteria_4 = st.selectbox("Exam Pressure", all_columns, index=idx_k4)
            batas_k4 = st.slider(f"Batas 'Sedang' untuk {kriteria_4}", 1.0, 10.0, 5.0, step=0.1, key="k4")

        with col3:
            idx_k5 = all_columns.index("anxiety_score")
            kriteria_5 = st.selectbox("Anxiety Score", all_columns, index=idx_k5)
            batas_k5 = st.slider(f"Batas 'Sedang' untuk {kriteria_5}", 1.0, 10.0, 5.0, step=0.1, key="k5")

        st.markdown("---")
        st.subheader("2. Visualisasi Kurva Keanggotaan Fuzzy")
        expander_kurva = st.expander("Lihat Grafik Fungsi Keanggotaan Linier Dinamis")

        with expander_kurva:
            c_plot1, c_plot2, c_plot3 = st.columns(3)
            with c_plot1:
                st.pyplot(plot_membership(batas_k1-2, batas_k1, batas_k1+2, kriteria_1))
                st.pyplot(plot_membership(batas_k2-3, batas_k2, batas_k2+3, kriteria_2))
            with c_plot2:
                st.pyplot(plot_membership(batas_k3-2, batas_k3, batas_k3+2, kriteria_3))
                st.pyplot(plot_membership(batas_k4-2, batas_k4, batas_k4+2, kriteria_4))
            with c_plot3:
                st.pyplot(plot_membership(batas_k5-2, batas_k5, batas_k5+2, kriteria_5))

        st.markdown("---")
        st.subheader("3. Eksekusi Sistem")
        st.write(f"Sistem siap memproses {len(df_proses)} data mahasiswa.")

        hitung_button = st.button("Hitung Peringkat Kesehatan Mental", type="primary")

        if hitung_button:
            with st.spinner("Sedang menghitung nilai fuzzy..."):

                # VARIABEL FUZZY

                stress_var   = ctrl.Antecedent(np.arange(0, 11, 1), 'stress')
                study_var    = ctrl.Antecedent(np.arange(0, 25, 1), 'study')
                sleep_var    = ctrl.Antecedent(np.arange(0, 25, 1), 'sleep')
                exam_var     = ctrl.Antecedent(np.arange(0, 11, 1), 'exam')
                anxiety_var  = ctrl.Antecedent(np.arange(0, 11, 1), 'anxiety')
                mental_var   = ctrl.Consequent(np.arange(0, 101, 1), 'mental')

                # FUNGSI KEANGGOTAAN INPUT
                
                stress_var['rendah'] = fuzz.trimf(stress_var.universe, [0, 0, batas_k1])
                stress_var['sedang'] = fuzz.trimf(stress_var.universe, [batas_k1-2, batas_k1, batas_k1+2])
                stress_var['tinggi'] = fuzz.trimf(stress_var.universe, [batas_k1, 10, 10])

                study_var['rendah'] = fuzz.trimf(study_var.universe, [0, 0, batas_k2])
                study_var['sedang'] = fuzz.trimf(study_var.universe, [batas_k2-3, batas_k2, batas_k2+3])
                study_var['tinggi'] = fuzz.trimf(study_var.universe, [batas_k2, 24, 24])

                sleep_var['rendah'] = fuzz.trapmf(sleep_var.universe, [0, 0, batas_k3-3, batas_k3])
                sleep_var['sedang'] = fuzz.trimf(sleep_var.universe, [batas_k3-2, batas_k3, batas_k3+2])
                sleep_var['tinggi'] = fuzz.trimf(sleep_var.universe, [batas_k3, 24, 24])

                exam_var['rendah'] = fuzz.trimf(exam_var.universe, [0, 0, batas_k4])
                exam_var['sedang'] = fuzz.trimf(exam_var.universe, [batas_k4-2, batas_k4, batas_k4+2])
                exam_var['tinggi'] = fuzz.trimf(exam_var.universe, [batas_k4, 10, 10])

                anxiety_var['rendah'] = fuzz.trimf(anxiety_var.universe, [0, 0, batas_k5])
                anxiety_var['sedang'] = fuzz.trimf(anxiety_var.universe, [batas_k5-2, batas_k5, batas_k5+2])
                anxiety_var['tinggi'] = fuzz.trimf(anxiety_var.universe, [batas_k5, 10, 10])

                # FUNGSI KEANGGOTAAN OUTPUT
            
                mental_var['buruk'] = fuzz.trimf(mental_var.universe, [0, 0, 40])
                mental_var['sedang'] = fuzz.trimf(mental_var.universe, [30, 50, 70])
                mental_var['baik']  = fuzz.trimf(mental_var.universe, [70, 100, 100])

                # Logika: setiap rule hanya pakai 2 variabel, 
                # tapi tetep dibaca satu satu terus dibandingin 

                # BURUK  = indikator negatif tinggi
                # SEDANG = campuran / satu tinggi satu rendah
                # BAIK   = indikator positif dominan

                # KONDISI BURUK
                r_buruk_1 = ctrl.Rule(stress_var['tinggi'] & anxiety_var['tinggi'], mental_var['buruk'])
                r_buruk_2 = ctrl.Rule(sleep_var['rendah']  & exam_var['tinggi'],    mental_var['buruk'])
                r_buruk_3 = ctrl.Rule(study_var['tinggi']  & sleep_var['rendah'],   mental_var['buruk'])
                r_buruk_4 = ctrl.Rule(stress_var['tinggi'] & sleep_var['rendah'],   mental_var['buruk'])
                r_buruk_5 = ctrl.Rule(stress_var['tinggi'] & exam_var['tinggi'],    mental_var['buruk'])
                r_buruk_6 = ctrl.Rule(anxiety_var['tinggi'] & exam_var['tinggi'],   mental_var['buruk'])
                r_buruk_7 = ctrl.Rule(sleep_var['rendah']  & stress_var['tinggi'],  mental_var['buruk'])
                r_buruk_8 = ctrl.Rule(sleep_var['rendah']  & anxiety_var['tinggi'], mental_var['buruk'])
                r_buruk_9  = ctrl.Rule(sleep_var['rendah']  & stress_var['sedang'],  mental_var['buruk'])
                r_buruk_10 = ctrl.Rule(sleep_var['rendah']  & exam_var['sedang'],    mental_var['buruk'])

                 # KONDISI SEDANG
                r_sedang_1 = ctrl.Rule(stress_var['sedang']  & anxiety_var['sedang'], mental_var['sedang'])
                r_sedang_2 = ctrl.Rule(study_var['sedang']   & sleep_var['sedang'],   mental_var['sedang'])
                r_sedang_3 = ctrl.Rule(stress_var['tinggi']  & anxiety_var['rendah'], mental_var['sedang'])
                r_sedang_4 = ctrl.Rule(stress_var['rendah']  & anxiety_var['tinggi'], mental_var['sedang'])
                r_sedang_5 = ctrl.Rule(stress_var['sedang']  & sleep_var['sedang'],   mental_var['sedang'])
                r_sedang_6 = ctrl.Rule(exam_var['sedang']    & anxiety_var['sedang'], mental_var['sedang'])
                r_sedang_7 = ctrl.Rule(study_var['tinggi']   & sleep_var['tinggi'],   mental_var['sedang'])

                # KONDISI BAIK
                r_baik_1 = ctrl.Rule(stress_var['rendah'] & anxiety_var['rendah'], mental_var['baik'])
                r_baik_2 = ctrl.Rule(sleep_var['tinggi']  & exam_var['rendah'],    mental_var['baik'])
                r_baik_3 = ctrl.Rule(sleep_var['tinggi']  & stress_var['rendah'],  mental_var['baik'])
                r_baik_4 = ctrl.Rule(sleep_var['tinggi']  & anxiety_var['rendah'], mental_var['baik'])

                mental_ctrl = ctrl.ControlSystem([
                    r_buruk_1, r_buruk_2, r_buruk_3, r_buruk_4, r_buruk_5, r_buruk_6,
                    r_sedang_1, r_sedang_2, r_sedang_3, r_sedang_4, r_sedang_5, r_sedang_6, r_sedang_7,
                    r_baik_1, r_baik_2, r_baik_3, r_baik_4
                ])

                # ITERASI DATA
                
                hasil_skor = []
                status_mental = []

                for index, row in df_proses.iterrows():
                    mental = ctrl.ControlSystemSimulation(mental_ctrl)
                    mental.input['stress']  = float(row[kriteria_1])
                    mental.input['study']   = float(row[kriteria_2])
                    mental.input['sleep']   = float(row[kriteria_3])
                    mental.input['exam']    = float(row[kriteria_4])
                    mental.input['anxiety'] = float(row[kriteria_5])
                    mental.compute()

                    skor_akhir = mental.output['mental']
                    hasil_skor.append(round(skor_akhir, 2))

                    if skor_akhir >= 75:
                        status_mental.append("Stabil")
                    elif 50 <= skor_akhir < 75:
                        status_mental.append("Stres Ringan")
                    elif 30 <= skor_akhir < 50:
                        status_mental.append("Burnout Sedang")
                    else:
                        status_mental.append("Depresi/ Butuh Konseling")

                # TAMPILKAN HASIL
                
                df_proses['Skor Kesehatan Mental'] = hasil_skor
                df_proses['Status Diagnosa'] = status_mental

                df_terurut = df_proses.sort_values(
                    by='Skor Kesehatan Mental', ascending=False
                ).reset_index(drop=True)
                df_terurut.index = df_terurut.index + 1
                df_terurut.index.name = 'Peringkat'

                st.success("Perhitungan Selesai!")
                st.subheader("Tabel Hasil Perangkingan Kesehatan Mental Mahasiswa")
                st.dataframe(df_terurut, use_container_width=True)

                st.subheader("Distribusi Kondisi Kesehatan Mental Mahasiswa")
                status_counts = pd.Series(status_mental).value_counts()
                st.bar_chart(status_counts)

# HALAMAN PROFIL

elif menu == "Halaman Profil":
    st.header("Profil Kelompok")
    st.info("""
    **Anggota Tim:**
    1. Mahendra Rajwaa Putra Pamungkas (NIM 123240039)
    2. Aliza Alfarisi (NIM 123240035)
    """)