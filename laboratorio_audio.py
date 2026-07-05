import sys
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

# Paleta de cores
COR_FUNDO = "#eef1f5"
COR_HEADER = "#2c3e50"
COR_HEADER_TEXTO = "#ffffff"
COR_CARD = "#ffffff"
COR_TEXTO = "#2c3e50"
COR_SUBTEXTO = "#7f8c8d"

# ---------------------------------------------------------
# Controle do gráfico ativo, para permitir atualização
# em tempo real quando os sliders são movidos
# ---------------------------------------------------------
modo_atual = None          # 'fft', 'filtro' ou 'espectrograma'
fig_atual = None
ax_atual = None
canvas_atual = None


def criar_area_grafico():
    """Cria (ou recria) a figura/canvas que será reutilizada pelo modo atual."""
    global fig_atual, ax_atual, canvas_atual
    for widget in frame_resultados.winfo_children():
        widget.destroy()
    fig_atual, ax_atual = plt.subplots(figsize=(5, 3))
    fig_atual.patch.set_facecolor(COR_CARD)
    ax_atual.set_facecolor("#fbfcfd")
    canvas_atual = FigureCanvasTkAgg(fig_atual, master=frame_resultados)
    canvas_atual.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


def obter_sinal_atual():
    """Retorna o sinal a ser usado nos gráficos, conforme o seletor de fonte."""
    if audio is None:
        return None
    if fonte_var.get() == "filtrado":
        cutoff = cutoff_var.get()
        b, a = butter(6, cutoff / (fs / 2), btype="low")
        return lfilter(b, a, audio.flatten())
    return audio.flatten()


def redesenhar():
    """Chamada pelos sliders: redesenha o gráfico atualmente ativo, se houver."""
    if modo_atual == "fft":
        _desenhar_fft()
    elif modo_atual == "filtro":
        _desenhar_filtro()
    elif modo_atual == "espectrograma":
        _desenhar_espectrograma()


# ---------------------------------------------------------
# Funções de desenho (atualizam o eixo existente, sem recriar a figura)
# ---------------------------------------------------------
def _desenhar_fft():
    sinal = obter_sinal_atual()
    if sinal is None:
        return
    N = len(sinal)
    yf = fft(sinal)
    xf = fftfreq(N, 1 / fs)
    ax_atual.clear()
    ax_atual.plot(xf[:N // 2], np.abs(yf[:N // 2]), color="#2980b9", linewidth=1.2)
    titulo = "FFT do Áudio Filtrado" if fonte_var.get() == "filtrado" else "FFT do Áudio Original"
    ax_atual.set_title(titulo, fontsize=11, fontweight="bold", color=COR_TEXTO)
    ax_atual.set_xlabel("Frequência (Hz)")
    ax_atual.set_ylabel("Magnitude")
    ax_atual.grid(alpha=0.25)
    fig_atual.tight_layout()
    canvas_atual.draw_idle()


def _desenhar_filtro():
    global audio_filtrado
    if audio is None:
        return
    cutoff = cutoff_var.get()
    b, a = butter(6, cutoff / (fs / 2), btype="low")
    audio_filtrado = lfilter(b, a, audio.flatten())
    ax_atual.clear()
    ax_atual.plot(audio_filtrado, color="#27ae60", linewidth=1.0)
    ax_atual.set_title(f"Áudio Filtrado - Passa Baixa ({cutoff} Hz)", fontsize=11, fontweight="bold", color=COR_TEXTO)
    ax_atual.set_xlabel("Amostras")
    ax_atual.set_ylabel("Amplitude")
    ax_atual.grid(alpha=0.25)
    fig_atual.tight_layout()
    canvas_atual.draw_idle()


def _desenhar_espectrograma():
    sinal = obter_sinal_atual()
    if sinal is None:
        return
    ax_atual.clear()
    ax_atual.specgram(sinal, Fs=fs, cmap="viridis")
    titulo = "Espectrograma do Áudio Filtrado" if fonte_var.get() == "filtrado" else "Espectrograma do Áudio Original"
    ax_atual.set_title(titulo, fontsize=11, fontweight="bold", color=COR_TEXTO)
    ax_atual.set_xlabel("Tempo (s)")
    ax_atual.set_ylabel("Frequência (Hz)")
    fig_atual.tight_layout()
    canvas_atual.draw_idle()


# ---------------------------------------------------------
# Funções principais (chamadas pelos botões)
# ---------------------------------------------------------
def gravar_audio():
    global audio
    duracao = duracao_var.get()
    modal = tk.Toplevel(janela)
    modal.title("Gravação em andamento")
    modal.configure(bg=COR_CARD)
    modal.resizable(False, False)
    tk.Label(modal, text=f"🎙️  Gravando áudio por {duracao} segundos...",
             bg=COR_CARD, fg=COR_TEXTO, font=("Segoe UI", 11)).pack(padx=30, pady=25)
    modal.transient(janela)
    modal.grab_set()
    janela.update()
    audio = sd.rec(int(duracao * fs), samplerate=fs, channels=1)
    sd.wait()
    modal.destroy()
    messagebox.showinfo("Concluído", "Gravação finalizada!")


def aplicar_filtro_passa_baixa():
    global modo_atual
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    modo_atual = "filtro"
    criar_area_grafico()
    _desenhar_filtro()


def aplicar_fft():
    global modo_atual
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    modo_atual = "fft"
    criar_area_grafico()
    _desenhar_fft()


def mostrar_espectrograma():
    global modo_atual
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    modo_atual = "espectrograma"
    criar_area_grafico()
    _desenhar_espectrograma()


def ouvir_audio():
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    sd.play(audio.flatten(), fs)
    sd.wait()


def ouvir_audio_filtrado():
    """CORRIGIDO: sempre recalcula o filtro com o corte atual do slider,
    não importa em qual tela (fft/filtro/espectrograma) você esteja."""
    global audio_filtrado
    if audio is None:
        messagebox.showerror("Erro", "Nenhum áudio gravado!")
        return
    cutoff = cutoff_var.get()
    b, a = butter(6, cutoff / (fs / 2), btype="low")
    audio_filtrado = lfilter(b, a, audio.flatten())
    sd.play(audio_filtrado, fs)
    sd.wait()


# ---------------------------------------------------------
# Interface gráfica
# ---------------------------------------------------------
janela = tk.Tk()
janela.title("Mini Laboratório de Áudio em Tempo Real")
janela.geometry("1050x650")
janela.configure(bg=COR_FUNDO)

# Estilo ttk
style = ttk.Style()
style.theme_use("clam")

style.configure("TFrame", background=COR_FUNDO)
style.configure("Card.TFrame", background=COR_CARD)

style.configure("TButton",
                font=("Segoe UI", 10, "bold"),
                foreground="white",
                background="#16a085",
                borderwidth=0,
                padding=8)
style.map("TButton", background=[("active", "#13876f")])

style.configure("Record.TButton", background="#e74c3c")
style.map("Record.TButton", background=[("active", "#c0392b")])

style.configure("Play.TButton", background="#3498db")
style.map("Play.TButton", background=[("active", "#2980b9")])

style.configure("TLabelframe", background=COR_CARD, borderwidth=0, relief="flat")
style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), foreground=COR_HEADER, background=COR_CARD)

style.configure("TLabel", font=("Segoe UI", 10), foreground=COR_TEXTO, background=COR_CARD)
style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=COR_HEADER_TEXTO, background=COR_HEADER)
style.configure("Sub.TLabel", font=("Segoe UI", 9), foreground=COR_SUBTEXTO, background=COR_CARD)
style.configure("Value.TLabel", font=("Segoe UI", 10, "bold"), foreground="#16a085", background=COR_CARD)

style.configure("TScale", background=COR_CARD)
style.configure("TRadiobutton", background=COR_CARD, font=("Segoe UI", 10))
style.configure("TLabelframe.Label", background=COR_CARD)

# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------
frame_header = tk.Frame(janela, bg=COR_HEADER, height=60)
frame_header.grid(row=0, column=0, columnspan=2, sticky="nsew")
ttk.Label(frame_header, text="🎧  Mini Laboratório de Áudio em Tempo Real", style="Header.TLabel") \
    .pack(padx=20, pady=14, anchor="w")

# Configuração grid
janela.columnconfigure(0, weight=1)
janela.columnconfigure(1, weight=2)
janela.rowconfigure(1, weight=1)

# Coluna esquerda (Laboratório) - com scroll não é necessário, cabe tudo
frame_lab = ttk.Frame(janela, padding=(15, 15))
frame_lab.grid(row=1, column=0, sticky="nsew")

# ---- Card: Gravação ----
lf_gravacao = ttk.LabelFrame(frame_lab, text="🎙️  Gravação", padding=15)
lf_gravacao.pack(fill="x", pady=(0, 12))

duracao_var = tk.IntVar(value=3)


def atualizar_duracao(val):
    duracao_label.config(text=f"{int(float(val))} s")


ttk.Label(lf_gravacao, text="Duração da gravação").pack(anchor="w")
duracao_slider = ttk.Scale(lf_gravacao, from_=1, to=10, orient="horizontal",
                            variable=duracao_var, command=atualizar_duracao)
duracao_slider.pack(fill="x", pady=(4, 2))
duracao_label = ttk.Label(lf_gravacao, text=f"{duracao_var.get()} s", style="Value.TLabel")
duracao_label.pack(anchor="e")

ttk.Button(lf_gravacao, text="🎙️  Gravar Áudio", style="Record.TButton",
           command=gravar_audio).pack(fill="x", pady=(10, 4))
ttk.Button(lf_gravacao, text="🎧  Ouvir Áudio Gravado", style="Play.TButton",
           command=ouvir_audio).pack(fill="x")

# ---- Card: Processamento ----
lf_proc = ttk.LabelFrame(frame_lab, text="🎚️  Processamento", padding=15)
lf_proc.pack(fill="x", pady=(0, 12))

cutoff_var = tk.IntVar(value=1000)


def atualizar_cutoff(val):
    cutoff_label.config(text=f"{int(float(val))} Hz")
    redesenhar()


ttk.Label(lf_proc, text="Frequência de corte (filtro passa-baixa)").pack(anchor="w")
cutoff_slider = ttk.Scale(lf_proc, from_=100, to=5000, orient="horizontal",
                           variable=cutoff_var, command=atualizar_cutoff)
cutoff_slider.pack(fill="x", pady=(4, 2))
cutoff_label = ttk.Label(lf_proc, text=f"{cutoff_var.get()} Hz", style="Value.TLabel")
cutoff_label.pack(anchor="e")

ttk.Separator(lf_proc, orient="horizontal").pack(fill="x", pady=10)

ttk.Label(lf_proc, text="Fonte para FFT / Espectrograma").pack(anchor="w")
fonte_var = tk.StringVar(value="original")
frame_fonte = ttk.Frame(lf_proc, style="Card.TFrame")
frame_fonte.pack(anchor="w", pady=(4, 8))
ttk.Radiobutton(frame_fonte, text="Original", variable=fonte_var,
                value="original", command=redesenhar).pack(side="left", padx=(0, 15))
ttk.Radiobutton(frame_fonte, text="Filtrado", variable=fonte_var,
                value="filtrado", command=redesenhar).pack(side="left")

ttk.Button(lf_proc, text="📊  Mostrar FFT", command=aplicar_fft).pack(fill="x", pady=3)
ttk.Button(lf_proc, text="🔉  Aplicar Filtro Passa-Baixa", command=aplicar_filtro_passa_baixa).pack(fill="x", pady=3)
ttk.Button(lf_proc, text="🌈  Mostrar Espectrograma", command=mostrar_espectrograma).pack(fill="x", pady=3)

# ---- Card: Áudição ----
lf_audicao = ttk.LabelFrame(frame_lab, text="🔊  Áudição", padding=15)
lf_audicao.pack(fill="x")

ttk.Button(lf_audicao, text="🎧  Ouvir Áudio Filtrado", style="Play.TButton",
           command=ouvir_audio_filtrado).pack(fill="x")
ttk.Label(lf_audicao, text="Sempre usa o corte atual do slider acima.",
          style="Sub.TLabel").pack(anchor="w", pady=(6, 0))

# Coluna direita (Resultados)
frame_resultados = tk.Frame(janela, bg=COR_CARD, highlightbackground="#dcdfe3", highlightthickness=1)
frame_resultados.grid(row=1, column=1, sticky="nsew", padx=(0, 15), pady=15)

placeholder = ttk.Label(frame_resultados, text="Os gráficos aparecerão aqui",
                         style="Sub.TLabel", background=COR_CARD)
placeholder.place(relx=0.5, rely=0.5, anchor="center")


# ---------------------------------------------------------
# Encerramento limpo ao fechar a janela (botão X)
# ---------------------------------------------------------
def ao_fechar():
    try:
        sd.stop()
    except Exception:
        pass
    try:
        plt.close("all")
    except Exception:
        pass
    janela.quit()
    janela.destroy()
    sys.exit(0)


janela.protocol("WM_DELETE_WINDOW", ao_fechar)

janela.mainloop()