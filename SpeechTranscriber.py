import tkinter as tk
from tkinter import messagebox, scrolledtext
import pyaudio
import wave
import speech_recognition as sr
import threading
from pydub import AudioSegment

class SpeechTranscriberApp:
    def __init__(self, master):
        self.master = master
        master.title("Speech Transcriber")
        master.geometry("600x500")
        master.configure(bg="#f0f0f0")

        self.label = tk.Label(master, text="Premi 'Registra' per iniziare a registrare:", bg="#f0f0f0", font=("Arial", 12))
        self.label.pack(pady=10)

        self.record_button = tk.Button(master, text="Registra", command=self.toggle_recording, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.record_button.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=50, height=10, font=("Arial", 10))
        self.text_area.pack(padx=10, pady=10)

        self.is_recording = False
        self.audio_filename = "recorded_audio.wav"

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.record_button.config(text="Ferma Registrazione")
            threading.Thread(target=self.record_audio_thread).start()
        else:
            self.is_recording = False
            self.record_button.config(text="Registra")

    def record_audio_thread(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        frames = []
        print("Registrazione in corso...")
        while self.is_recording:
            data = stream.read(1024)
            frames.append(data)
        print("Registrazione terminata.")
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.audio_filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

        print("Convertendo l'audio registrato in testo...")
        text = self.audio_to_text(self.audio_filename)
        self.display_text(text)

    def audio_to_text(self, filename):
        wav_filename = "temp_audio.wav"
        if filename.lower().endswith(('.wav', '.aiff', '.aif', '.flac')):
            wav_filename = filename
        else:
            try:
                audio = AudioSegment.from_file(filename)
                audio.export(wav_filename, format="wav")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile convertire l'audio: {e}")
                return "Errore di conversione"

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_filename) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="it-IT")
                return text
            except sr.UnknownValueError:
                return "Google Speech Recognition non è riuscito a capire l'audio."
            except sr.RequestError as e:
                return f"Impossibile richiedere risultati dal servizio Google Speech Recognition; {e}"

    def display_text(self, text):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text)
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        print("Testo copiato negli appunti.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechTranscriberApp(root)
    root.mainloop()
