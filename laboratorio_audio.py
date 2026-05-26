import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy.fft import fft, fftfreq

# Configurações globais
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
    concluido = tk.Toplevel(janela)
    concluido.title("Concluído")
    tk.Label(concluido, text="Gravação finalizada!").pack(padx=20, pady=20)
    concluido.after(1500, concluido.destroy)

def visualizar_sinal():
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    plt.figure("Sinal no Tempo")
    plt.plot(audio)
    plt.title("Sinal no Tempo")
    plt.xlabel("Amostras")
    plt.ylabel("Amplitude")
    plt.show()

def aplicar_filtro_passa_baixa():
    global audio_filtrado
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    cutoff = cutoff_var.get()
    b, a = butter(6, cutoff / (fs / 2), btype='low')
    audio_filtrado = lfilter(b, a, audio.flatten())
    plt.figure("Áudio Filtrado - Passa Baixa")
    plt.plot(audio_filtrado)
    plt.title(f"Áudio Filtrado - Passa Baixa (corte {cutoff} Hz)")
    plt.xlabel("Amostras")
    plt.ylabel("Amplitude")
    plt.show()

def aplicar_fft():
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    N = len(audio)
    yf = fft(audio.flatten())
    xf = fftfreq(N, 1/fs)
    plt.figure("FFT do Áudio")
    plt.plot(xf[:N//2], np.abs(yf[:N//2]))
    plt.title("FFT do Áudio")
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Magnitude")
    plt.show()

def mostrar_espectrograma():
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    plt.figure("Espectrograma")
    plt.specgram(audio.flatten(), Fs=fs, cmap='viridis')
    plt.title("Espectrograma do Áudio")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Frequência (Hz)")
    plt.colorbar(label="Intensidade")
    plt.show()

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

# Interface gráfica
janela = tk.Tk()
janela.title("Mini Laboratório de Áudio em Tempo Real")
janela.geometry("600x600")

style = ttk.Style()
style.theme_use("clam")

ttk.Label(janela, text="🎙️ Mini Laboratório de Áudio em Tempo Real", font=("Arial", 14, "bold")).pack(pady=10)

# Frame Gravação
frame_gravacao = ttk.LabelFrame(janela, text="Gravação")
frame_gravacao.pack(fill="x", padx=10, pady=10)

duracao_var = tk.IntVar(value=3)
def atualizar_duracao(val): duracao_label.config(text=f"{int(float(val))} s")
ttk.Label(frame_gravacao, text="Duração da Gravação (s)").pack()
duracao_slider = ttk.Scale(frame_gravacao, from_=1, to=10, orient="horizontal", variable=duracao_var, command=atualizar_duracao)
duracao_slider.pack(pady=5)
duracao_label = ttk.Label(frame_gravacao, text=f"{duracao_var.get()} s")
duracao_label.pack()
ttk.Button(frame_gravacao, text="🎙️ Gravar Áudio", command=gravar_audio).pack(pady=5)
ttk.Button(frame_gravacao, text="🎧 Ouvir Áudio Gravado", command=ouvir_audio).pack(pady=5)

# Frame Processamento
frame_proc = ttk.LabelFrame(janela, text="Processamento")
frame_proc.pack(fill="x", padx=10, pady=10)

cutoff_var = tk.IntVar(value=1000)
def atualizar_cutoff(val): cutoff_label.config(text=f"{int(float(val))} Hz")
ttk.Label(frame_proc, text="Frequência de Corte (Hz)").pack()
cutoff_slider = ttk.Scale(frame_proc, from_=100, to=5000, orient="horizontal", variable=cutoff_var, command=atualizar_cutoff)
cutoff_slider.pack(pady=5)
cutoff_label = ttk.Label(frame_proc, text=f"{cutoff_var.get()} Hz")
cutoff_label.pack()

ttk.Button(frame_proc, text="📊 Mostrar FFT", command=aplicar_fft).pack(pady=5)
ttk.Button(frame_proc, text="🔉 Aplicar Filtro Passa-Baixa", command=aplicar_filtro_passa_baixa).pack(pady=5)
ttk.Button(frame_proc, text="🌈 Mostrar Espectrograma", command=mostrar_espectrograma).pack(pady=5)

# Frame Audição
frame_audicao = ttk.LabelFrame(janela, text="Audição")
frame_audicao.pack(fill="x", padx=10, pady=10)
ttk.Button(frame_audicao, text="🎧 Ouvir Áudio Filtrado", command=ouvir_audio_filtrado).pack(pady=5)

janela.mainloop()
