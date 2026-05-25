import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy.fft import fft, fftfreq

# Configurações globais
fs = 44100  # taxa de amostragem
audio = None
audio_filtrado = None

# Função para gravar áudio
def gravar_audio():
    global audio
    duracao = duracao_var.get()  # pega o valor do slider

    # Criar janela modal temporária
    modal = tk.Toplevel(janela)
    modal.title("Gravação em andamento")
    tk.Label(modal, text=f"Gravando áudio por {duracao} segundos...").pack(padx=20, pady=20)

    modal.transient(janela)
    modal.grab_set()
    janela.update()

    # Gravação
    audio = sd.rec(int(duracao * fs), samplerate=fs, channels=1)
    sd.wait()

    # Fecha automaticamente ao terminar
    modal.destroy()

    # Mensagem rápida de conclusão
    concluido = tk.Toplevel(janela)
    concluido.title("Concluído")
    tk.Label(concluido, text="Gravação finalizada!").pack(padx=20, pady=20)
    concluido.after(1500, concluido.destroy)

# Função para visualizar sinal no tempo
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

# Função para aplicar filtro passa-baixa
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

# Função para FFT
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

# Função para espectrograma
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

# Função para executar processamento escolhido
def executar():
    escolha = opcao.get()
    if escolha == "FFT":
        aplicar_fft()
    elif escolha == "Filtro":
        aplicar_filtro_passa_baixa()
    elif escolha == "Espectrograma":
        mostrar_espectrograma()
    else:
        messagebox.showwarning("Aviso", "Selecione uma opção de processamento!")

# Função para ouvir áudio original
def ouvir_audio():
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    sd.play(audio.flatten(), fs)
    sd.wait()

# Função para ouvir áudio filtrado
def ouvir_audio_filtrado():
    if audio_filtrado is None:
        messagebox.showerror("Erro", "Nenhum áudio filtrado! Execute o filtro primeiro.")
        return
    sd.play(audio_filtrado, fs)
    sd.wait()

# Interface gráfica
janela = tk.Tk()
janela.title("Mini Laboratório de Áudio em Tempo Real")
janela.geometry("500x600")

# Variáveis globais ajustáveis
cutoff_var = tk.IntVar(value=1000)
duracao_var = tk.IntVar(value=3)

ttk.Label(janela, text="Mini Laboratório de Áudio em Tempo Real", font=("Arial", 12, "bold")).pack(pady=10)

# Slider de duração da gravação
def atualizar_duracao(val):
    duracao_label.config(text=f"{int(float(val))} s")

ttk.Label(janela, text="Duração da Gravação (s)").pack()
duracao_slider = ttk.Scale(janela, from_=1, to=10, orient="horizontal", variable=duracao_var, command=atualizar_duracao)
duracao_slider.pack(pady=5)
duracao_label = ttk.Label(janela, text=f"{duracao_var.get()} s")
duracao_label.pack()

ttk.Button(janela, text="Gravar Áudio", command=gravar_audio).pack(pady=5)
ttk.Button(janela, text="Ouvir Áudio Gravado", command=ouvir_audio).pack(pady=5)
ttk.Button(janela, text="Visualizar Sinal no Tempo", command=visualizar_sinal).pack(pady=5)

# Slider de frequência de corte
def atualizar_cutoff(val):
    cutoff_label.config(text=f"{int(float(val))} Hz")

ttk.Label(janela, text="Frequência de Corte (Hz)").pack()
cutoff_slider = ttk.Scale(janela, from_=100, to=5000, orient="horizontal", variable=cutoff_var, command=atualizar_cutoff)
cutoff_slider.pack(pady=5)
cutoff_label = ttk.Label(janela, text=f"{cutoff_var.get()} Hz")
cutoff_label.pack()

ttk.Label(janela, text="Processamento:", font=("Arial", 10, "bold")).pack(pady=10)
opcao = tk.StringVar()
ttk.Radiobutton(janela, text="FFT", variable=opcao, value="FFT").pack()
ttk.Radiobutton(janela, text="Aplicar Filtro - Passa Baixa", variable=opcao, value="Filtro").pack()
ttk.Radiobutton(janela, text="Mostrar Espectrograma", variable=opcao, value="Espectrograma").pack()

ttk.Button(janela, text="Executar Resultados", command=executar).pack(pady=15)
ttk.Button(janela, text="Ouvir Áudio Filtrado", command=ouvir_audio_filtrado).pack(pady=5)

janela.mainloop()
