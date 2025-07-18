# chatbot.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import requests
import re

API_KEY = "AIzaSyBCoY8_frkzfnG9xQfZOR9FxRQ8DU1pnD4"  
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

class GeminiChatbot(tk.Frame):  # Tetap menggunakan Frame untuk Chatbot
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(side="right", fill="both", expand=True)  # Tempatkan chatbot di sisi kanan

        self.configure(bg="#f9f9f9")

        # Style UI
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry", font=("Segoe UI", 10))

        # Tampilan obrolan
        self.chat_display = scrolledtext.ScrolledText(self, height=18, width=78, state='disabled',
        bg="#FFFFFF", fg="#222222", font=("Segoe UI", 10))
        self.chat_display.pack(pady=(10, 5), padx=10)

        # Input pengguna
        input_frame = ttk.Frame(self)
        input_frame.pack(padx=10, pady=10, fill='x')

        self.user_input = ttk.Entry(input_frame, width=70)
        self.user_input.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_button = ttk.Button(input_frame, text="Kirim", command=self.send_message)
        self.send_button.pack(side='right')

        # Remove the protocol line since `self.protocol()` is not valid for `Frame`
        # self.protocol("WM_DELETE_WINDOW", self.close)

    def send_message(self):
        user_msg = self.user_input.get().strip()
        if not user_msg:
            return
        self.user_input.delete(0, 'end')
        self._append_chat(f"🧑 Anda: {user_msg}\n")

        threading.Thread(target=self.call_gemini_api, args=(user_msg,), daemon=True).start()

    def call_gemini_api(self, user_msg):
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": user_msg}
                    ]
                }
            ]
        }
        
        print(f"Sending request to Gemini API with message: {user_msg}")  # Cek apakah request dikirim dengan benar

        try:
            response = requests.post(API_URL, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            bot_reply = self._clean_markdown(raw_text)
            print(f"API response: {bot_reply}")  # Menampilkan respons dari API di console
        except Exception as e:
            bot_reply = f"❌ Error saat memanggil Gemini API:\n{e}"
            print(f"Error calling Gemini API: {e}")  # Menampilkan error jika ada masalah

        self._append_chat(f"🤖 Chatbot: {bot_reply}\n")

    def _clean_markdown(self, text):
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        return text

    def _append_chat(self, text):
        self.chat_display.config(state='normal')
        self.chat_display.insert('end', text + "\n")
        self.chat_display.see('end')
        self.chat_display.config(state='disabled')
        
    def send_message_to_bot(self, message):
        # Menampilkan pesan ke chatbot dan memulai request API
        self._append_chat(f"🧑 Anda: {message}\n")
        threading.Thread(target=self.call_gemini_api, args=(message,), daemon=True).start()


    def close(self):
        self.destroy()  # Menutup jendela chatbot saat ditutup
