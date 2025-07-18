# run.py
import tkinter as tk
from main_app import MentalHealthApp
from chatbot import GeminiChatbot

class MainApp:
    def __init__(self):
        # Gawe jendela utama
        self.root = tk.Tk()
        self.root.geometry("1000x500")  # Ukuran jendela
        self.root.title("Sistem Pakar Kesehatan Mental")

        # Frame kiwa kanggo aplikasi skrining mental
        self.left_frame = tk.Frame(self.root, width=350)  # Ukuran kiwa tetep
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Pasang aplikasi skrining mental nang kiwa
        self.mental_health_app = MentalHealthApp(self.left_frame)

        # Frame tengen kanggo chatbot
        self.right_frame = tk.Frame(self.root)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Pasang chatbot nang tengen
        self.chatbot_window = GeminiChatbot(self.right_frame)

        # Atur pembagian kolom: kiwa tetep, tengen ngisi sisa
        self.root.grid_columnconfigure(0, weight=0, minsize=350)  # Kiwa: tetep 350px
        self.root.grid_columnconfigure(1, weight=1)  # Tengen: sisa ruang

        # Mungkir aplikasi
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
