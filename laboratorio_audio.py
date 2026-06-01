import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy.fft import fft, fftfreq
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fs = 44100
audio = None
audio_filtrado = None

# Funções principais
def gravar_audio():
    global audio
    duracao = duracao_var.get()
    modal = tk.Toplevel(janela)
    modal.title("Gravação em andamento")
    tk.Label(modal, text=f"Gravando áudio por {duracao} segundos...").pack(padx=20, pady=20)
    modal.transient(janela)
    modal.grab_set()
    janela.update()
    audio = sd.rec(int(duracao * fs), samplerate=fs, channels=1)
    sd.wait()
    modal.destroy()
    messagebox.showinfo("Concluído", "Gravação finalizada!")

def aplicar_filtro_passa_baixa():
    global audio_filtrado
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    cutoff = cutoff_var.get()
    b, a = butter(6, cutoff / (fs / 2), btype='low')
    audio_filtrado = lfilter(b, a, audio.flatten())
    fig, ax = plt.subplots(figsize=(5,3))
    ax.plot(audio_filtrado)
    ax.set_title(f"Áudio Filtrado - Passa Baixa ({cutoff} Hz)")
    ax.set_xlabel("Amostras")
    ax.set_ylabel("Amplitude")
    mostrar_grafico(fig)

def aplicar_fft():
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    N = len(audio)
    yf = fft(audio.flatten())
    xf = fftfreq(N, 1/fs)
    fig, ax = plt.subplots(figsize=(5,3))
    ax.plot(xf[:N//2], np.abs(yf[:N//2]))
    ax.set_title("FFT do Áudio")
    ax.set_xlabel("Frequência (Hz)")
    ax.set_ylabel("Magnitude")
    mostrar_grafico(fig)

def mostrar_espectrograma():
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    fig, ax = plt.subplots(figsize=(5,3))
    ax.specgram(audio.flatten(), Fs=fs, cmap='viridis')
    ax.set_title("Espectrograma do Áudio")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Frequência (Hz)")
    mostrar_grafico(fig)

def ouvir_audio():
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    sd.play(audio.flatten(), fs)
    sd.wait()

def ouvir_audio_filtrado():
    if audio_filtrado is None:
        messagebox.showerror("Erro", "Nenhum áudio filtrado! Execute o filtro primeiro.")
        return
    sd.play(audio_filtrado, fs)
    sd.wait()

# Função para mostrar gráfico na coluna da direita
def mostrar_grafico(fig):
    for widget in frame_resultados.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_resultados)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# Interface gráfica
janela = tk.Tk()
janela.title("Mini Laboratório de Áudio em Tempo Real")
janela.geometry("1000x600")

# Estilo ttk
style = ttk.Style()
style.theme_use("clam")

style.configure("TButton",
                font=("Arial", 11, "bold"),
                foreground="white",
                background="#4CAF50",
                padding=6)
style.map("TButton",
          background=[("active", "#45a049")])

style.configure("Record.TButton", background="#e74c3c", foreground="white")
style.map("Record.TButton", background=[("active", "#c0392b")])

style.configure("Play.TButton", background="#3498db", foreground="white")
style.map("Play.TButton", background=[("active", "#2980b9")])

style.configure("TLabelframe", background="#f9f9f9")
style.configure("TLabelframe.Label", font=("Arial", 12, "bold"), foreground="#333")

style.configure("TLabel", font=("Arial", 11), foreground="#222")

# Configuração grid
janela.columnconfigure(0, weight=1)
janela.columnconfigure(1, weight=2)
janela.rowconfigure(0, weight=1)

# Coluna esquerda (Laboratório)
frame_lab = ttk.Frame(janela)
frame_lab.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

ttk.Label(frame_lab, text="🎙️ Laboratório de Áudio", font=("Arial", 14, "bold")).pack(pady=10)

# Gravação
duracao_var = tk.IntVar(value=3)
def atualizar_duracao(val):
    duracao_label.config(text=f"{int(float(val))} s")

ttk.Label(frame_lab, text="Duração da Gravação (s)").pack()
duracao_slider = ttk.Scale(frame_lab, from_=1, to=10, orient="horizontal",
                           variable=duracao_var, command=atualizar_duracao)
duracao_slider.pack(pady=5)
duracao_label = ttk.Label(frame_lab, text=f"{duracao_var.get()} s")
duracao_label.pack()

ttk.Button(frame_lab, text="🎙️ Gravar Áudio", style="Record.TButton", command=gravar_audio).pack(pady=5)
ttk.Button(frame_lab, text="🎧 Ouvir Áudio Gravado", style="Play.TButton", command=ouvir_audio).pack(pady=5)

# Processamento
cutoff_var = tk.IntVar(value=1000)
def atualizar_cutoff(val):
    cutoff_label.config(text=f"{int(float(val))} Hz")

ttk.Label(frame_lab, text="Frequência de Corte (Hz)").pack()
cutoff_slider = ttk.Scale(frame_lab, from_=100, to=5000, orient="horizontal",
                          variable=cutoff_var, command=atualizar_cutoff)
cutoff_slider.pack(pady=5)
cutoff_label = ttk.Label(frame_lab, text=f"{cutoff_var.get()} Hz")
cutoff_label.pack()

ttk.Button(frame_lab, text="📊 Mostrar FFT", command=aplicar_fft).pack(pady=5)
ttk.Button(frame_lab, text="🔉 Aplicar Filtro Passa-Baixa", command=aplicar_filtro_passa_baixa).pack(pady=5)
ttk.Button(frame_lab, text="🌈 Mostrar Espectrograma", command=mostrar_espectrograma).pack(pady=5)

# Audição
ttk.Button(frame_lab, text="🎧 Ouvir Áudio Filtrado", style="Play.TButton", command=ouvir_audio_filtrado).pack(pady=5)

# Coluna direita (Resultados)
frame_resultados = ttk.LabelFrame(janela, text="Resultados")
frame_resultados.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

janela.mainloop()
