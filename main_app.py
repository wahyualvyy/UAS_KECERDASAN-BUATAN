import tkinter as tk
from tkinter import ttk, messagebox
import csv
import datetime
from chatbot import GeminiChatbot

gad7_questions = {
    "cemas": "Dalam 2 minggu terakhir, seberapa sering Anda merasa\n cemas atau gelisah?",
    "tidak_bisa_kontrol_khawatir": "Dalam 2 minggu terakhir, seberapa sering \n Anda merasa sulit mengendalikan rasa khawatir?",
    "khawatir_berlebihan": "Apakah Anda merasa khawatir berlebihan terhadap berbagai hal?",
    "sulit_relaks": "Apakah Anda kesulitan untuk rileks?",
    "gelisah": "Apakah Anda merasa gelisah, seperti tidak bisa diam?",
    "mudah_tersinggung": "Apakah Anda merasa mudah tersinggung atau marah?",
    "takut_hal_buruk": "Apakah Anda takut terjadi sesuatu yang buruk?",
}

phq9_questions = {
    "tidak_berminat": "Apakah Anda merasa tidak berminat atau tidak \n bergairah terhadap aktivitas sehari-hari?",
    "sedih": "Apakah Anda merasa sedih, murung, atau putus asa?",
    "sulit_tidur": "Apakah Anda kesulitan tidur atau terlalu banyak tidur?",
    "lelah": "Apakah Anda merasa lelah atau tidak bertenaga?",
    "nafsu_makan": "Apakah nafsu makan Anda menurun atau meningkat drastis?",
    "merasa_gagal": "Apakah Anda merasa bahwa Anda telah mengecewakan \n diri sendiri atau keluarga?",
    "sulit_konsentrasi": "Apakah Anda sulit berkonsentrasi pada sesuatu, \n seperti membaca atau menonton TV?",
    "gerak_lambat": "Apakah orang lain memperhatikan bahwa Anda bergerak \n atau berbicara lebih lambat dari biasanya?",
    "pikiran_bunuh_diri": "Apakah Anda pernah berpikir lebih baik mati \n atau menyakiti diri sendiri?",
}

CSV_FILE = "mental_health_results.csv"

class MentalHealthApp:
    def __init__(self, master=None):
        self.master = master
        self.create_widgets()  # Langsung panggil untuk tampilkan input nama

        self.nama = ""
        self.current_part = "nama"  # Pastikan langsung ke input nama
        self.gad7_keys = list(gad7_questions.keys())
        self.phq9_keys = list(phq9_questions.keys())

        self.gad7_score = 0
        self.phq9_score = 0

        self.question_index = 0
        self.answers_gad7 = [-1] * len(self.gad7_keys)
        self.answers_phq9 = [-1] * len(self.phq9_keys)


    def create_widgets(self):
        # Membersihkan widget lama
        for widget in self.master.winfo_children():
            widget.destroy()

        # Menampilkan Label untuk input nama
        self.label = ttk.Label(self.master, text="Masukkan Nama Anda:", font=('Arial', 15, 'bold'), anchor="center", justify='center')
        self.label.pack(pady=20)

        # Membuat Entry untuk nama
        self.entry = ttk.Entry(self.master, font=("Arial", 14), width=40)
        self.entry.pack(pady=5)

        # Tombol untuk lanjutkan
        self.next_button = ttk.Button(self.master, text="Selanjutnya", command=self.next_step)
        self.next_button.pack(pady=20)
    
        self.current_part = "nama"

    def start_test(self):
        self.start_test_button.destroy()
        self.start_chatbot_button.destroy()
        self.label.config(text="Masukkan Nama Anda:")

        self.entry = ttk.Entry(self.master, font=("Arial", 14), width=40)
        self.entry.pack(pady=5)

        self.prev_button = ttk.Button(self.master, text="Sebelumnya", command=self.prev_step)
        self.prev_button.pack(side='left', padx=20, pady=20)
        self.prev_button.state(['disabled'])

        self.next_button = ttk.Button(self.master, text="Mulai", command=self.next_step)
        self.next_button.pack(side='right', padx=20, pady=20)

        self.current_part = "nama"

    def next_step(self):
        if self.current_part == "nama":
            self.nama = self.entry.get().strip()
            if not self.nama:
                messagebox.showwarning("Input error", "Nama tidak boleh kosong!")
                return

            self.entry.pack_forget()
            self.next_button.config(text="Selanjutnya")
            self.label.config(text=f"Hai, {self.nama}! Jawablah pertanyaan berikut:")
            self.current_part = "gad7"
            self.question_index = 0
            self.gad7_score = 0
            self.show_question()
            self.prev_button.state(['disabled'])

        elif self.current_part == "gad7":
            if not self.save_answer():
                return
            self.question_index += 1
            if self.question_index < len(self.gad7_keys):
                self.show_question()
                self.prev_button.state(['!disabled'])
            else:
                self.current_part = "phq9"
                self.question_index = 0
                self.phq9_score = 0
                self.show_question()
                self.prev_button.state(['!disabled'])
                self.send_result_to_chatbot(f"Skor GAD-7: {self.gad7_score} → Kecemasan Berat\nSkor PHQ-9: {self.phq9_score} → Depresi Berat")

        elif self.current_part == "phq9":
            if not self.save_answer():
                return
            self.question_index += 1
            if self.question_index < len(self.phq9_keys):
                self.show_question()
                self.prev_button.state(['!disabled'])
            else:
                self.current_part = "hasil"
                self.show_result()
                self.prev_button.state(['disabled'])

    def prev_step(self):
        if self.current_part == "gad7":
            if self.question_index == 0:
                self.current_part = "nama"
                self.prev_button.state(['disabled'])
                self.next_button.config(text="Mulai")
                self.label.config(text="Masukkan Nama Anda:")
                self.entry.pack(pady=5)
                self.entry.delete(0, 'end')
                if hasattr(self, 'radio_buttons'):
                    for rb in self.radio_buttons:
                        rb.destroy()
                return
            else:
                self.question_index -= 1
                self.show_question()
                if self.question_index == 0:
                    self.prev_button.state(['disabled'])

        elif self.current_part == "phq9":
            if self.question_index == 0:
                self.current_part = "gad7"
                self.question_index = len(self.gad7_keys) - 1
                self.show_question()
                self.prev_button.state(['!disabled'])
            else:
                self.question_index -= 1
                self.show_question()
                if self.question_index == 0:
                    self.prev_button.state(['disabled'])

        elif self.current_part == "hasil":
            self.current_part = "phq9"
            self.question_index = len(self.phq9_keys) - 1
            self.show_question()
            self.next_button.config(text="Selanjutnya", command=self.next_step)
            self.prev_button.state(['!disabled'])
            if hasattr(self, 'retry_button'):
                self.retry_button.destroy()

    def show_question(self):
        if self.current_part == "gad7":
            key = self.gad7_keys[self.question_index]
            question = gad7_questions[key]
            answer = self.answers_gad7[self.question_index]
        elif self.current_part == "phq9":
            key = self.phq9_keys[self.question_index]
            question = phq9_questions[key]
            answer = self.answers_phq9[self.question_index]
        else:
            question = ""
            answer = -1

        self.label.config(text=question)

        if hasattr(self, 'var'):
            self.var.set(answer)
        else:
            self.var = tk.IntVar(value=answer)

        if hasattr(self, 'radio_buttons'):
            for rb in self.radio_buttons:
                rb.destroy()

        self.radio_buttons = []
        options = [("0 = Tidak Pernah", 0), ("1 = Kadang-kadang", 1), ("2 = Sering", 2), ("3 = Hampir setiap hari", 3)]
        for text, val in options:
            rb = ttk.Radiobutton(self.master, text=text, variable=self.var, value=val)
            rb.pack(anchor='w', padx=30)
            self.radio_buttons.append(rb)

        self.next_button.config(text="Selanjutnya", command=self.next_step)
        self.next_button.state(['!disabled'])

    def save_answer(self):
        if self.var.get() == -1:
            messagebox.showwarning("Input error", "Silakan pilih jawaban sebelum melanjutkan!")
            return False

        answer_score = self.var.get()
        if self.current_part == "gad7":
            self.answers_gad7[self.question_index] = answer_score
        elif self.current_part == "phq9":
            self.answers_phq9[self.question_index] = answer_score
        return True

    def calculate_scores(self):
        self.gad7_score = sum([ans if ans != -1 else 0 for ans in self.answers_gad7])
        self.phq9_score = sum([ans if ans != -1 else 0 for ans in self.answers_phq9])

    def interpret_score(self, score, jenis):
        if jenis == 'GAD-7':
            if score <= 4:
                return "Kecemasan minimal"
            elif 5 <= score <= 9:
                return "Kecemasan ringan"
            elif 10 <= score <= 14:
                return "Kecemasan sedang"
            else:
                return "Kecemasan berat"
        elif jenis == 'PHQ-9':
            if score <= 4:
                return "Depresi minimal"
            elif 5 <= score <= 9:
                return "Depresi ringan"
            elif 10 <= score <= 14:
                return "Depresi sedang"
            else:
                return "Depresi berat"


    def show_result(self):
        self.calculate_scores()
        gad_result, phq_result = self.forward_chaining()  # <-- Menggunakan forward chaining

        result_text = (
            f"Hasil Skrining Mental untuk {self.nama}:\n\n"
            f"Skor GAD-7: {self.gad7_score} → {gad_result}\n"
            f"Skor PHQ-9: {self.phq9_score} → {phq_result}\n\n"
            "📝 Catatan:\n"
            "Hasil ini adalah indikasi awal, bukan diagnosis klinis.\n"
            "Jika gejala berlanjut, konsultasikan dengan profesional kesehatan mental."
        )

        self.label.config(text=result_text)

        for rb in self.radio_buttons:
            rb.destroy()

        self.prev_button.state(['disabled'])
        
        # Automatically send the result to the chatbot
        self.send_result_to_chatbot(result_text)

        self.next_button.config(text="Mulai Chatbot", command=self.start_chatbot)
        self.next_button.state(['!disabled'])

        self.retry_button = ttk.Button(self.master, text="Ulangi Tes", command=self.reset_app)
        self.retry_button.pack(pady=10)

        self.save_to_csv(gad_result, phq_result)

    def send_result_to_chatbot(self, result_text):
        # Mengirim hasil tes ke chatbot
        print(f"Sending result to chatbot: {result_text}")
        self.chatbot_window.send_message_to_bot(result_text)

    def reset_app(self):
        if hasattr(self, 'retry_button'):
            self.retry_button.destroy()

        self.nama = ""
        self.current_part = "menu"
        self.question_index = 0
        self.gad7_score = 0
        self.phq9_score = 0
        self.answers_gad7 = [-1] * len(self.gad7_keys)
        self.answers_phq9 = [-1] * len(self.phq9_keys)

        for widget in self.master.winfo_children():
            widget.destroy()

        self.create_widgets()

    

    def save_to_csv(self, gad_result, phq_result):
        header = ['Waktu', 'Nama', 'Skor GAD-7', 'Interpretasi GAD-7', 'Skor PHQ-9', 'Interpretasi PHQ-9']
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [now, self.nama, self.gad7_score, gad_result, self.phq9_score, phq_result]

        try:
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                file.seek(0, 2)
                if file.tell() == 0:
                    writer.writerow(header)
                writer.writerow(data)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan hasil: {e}")

    def start_chatbot(self):
        # Panggil window chatbot Gemini dari file chatbot.py
        GeminiChatbot(self.master)
        
    def forward_chaining(self):
        fakta = {
            'gad_score': self.gad7_score,
            'phq_score': self.phq9_score
        }

        aturan = [
            (lambda f: f['gad_score'] <= 4, 'Kecemasan minimal'),
            (lambda f: 5 <= f['gad_score'] <= 9, 'Kecemasan ringan'),
            (lambda f: 10 <= f['gad_score'] <= 14, 'Kecemasan sedang'),
            (lambda f: f['gad_score'] > 14, 'Kecemasan berat'),

            (lambda f: f['phq_score'] <= 4, 'Depresi minimal'),
            (lambda f: 5 <= f['phq_score'] <= 9, 'Depresi ringan'),
            (lambda f: 10 <= f['phq_score'] <= 14, 'Depresi sedang'),
            (lambda f: f['phq_score'] > 14, 'Depresi berat'),
        ]

        hasil = []
        for kondisi, kesimpulan in aturan:
            if kondisi(fakta):
                hasil.append(kesimpulan)

        # Mengembalikan hasil sesuai urutan: GAD dan PHQ
        gad_result = next((r for r in hasil if 'Kecemasan' in r), 'Tidak diketahui')
        phq_result = next((r for r in hasil if 'Depresi' in r), 'Tidak diketahui')
        return gad_result, phq_result

if __name__ == "__main__":
    root = tk.Tk()
    app = MentalHealthApp(root)
    root.mainloop()
