import numpy as np
import plotly.graph_objects as go
from scipy.signal import hilbert
from plotly.subplots import make_subplots

# Função para carregar e ajustar dados
def carregar_dados(filename):
    with open(filename, 'r') as file:
        data = file.read().replace(',', '.')
    return np.loadtxt(data.splitlines(), delimiter=None)

# Carregar os dados do arquivo txt
dados = carregar_dados('MancalInterno_Atual_SemMassa.txt')

# Separar as colunas em tempo e aceleração
tempo = dados[:, 0]  # Primeira coluna: tempo
aceleracao = dados[:, 1]  # Segunda coluna: aceleração

# Calcular a taxa de amostragem
fs = 1 / np.mean(np.diff(tempo))
if fs <= 0:
    raise ValueError(f"A taxa de amostragem calculada é inválida: {fs}")

# Transformada de Hilbert
hilbert_result = np.abs(hilbert(aceleracao))

# FFT dos sinais
fft_result = np.abs(np.fft.fft(aceleracao))
freq_fft = np.fft.fftfreq(len(aceleracao), 1 / fs)

# Filtrar apenas as frequências positivas
fft_result = fft_result[freq_fft >= 0]
freq_fft = freq_fft[freq_fft >= 0]


# Definir frequência fundamental e harmônicas
freq_fundamental = 58.6  # Primeira harmônica (Hz)
harmonicas = [freq_fundamental * n for n in range(1, 4)]  # 1ª, 2ª e 3ª harmônicas
largura_banda = 20  # Largura de banda para cada harmônica

# Função para filtrar as regiões das harmônicas
def filtrar_harmonicas(freq, fft_amplitude, harmonicas, largura_banda):
    filtro = np.zeros_like(fft_amplitude)
    for harm in harmonicas:
        banda_inferior = harm - largura_banda / 2
        banda_superior = harm + largura_banda / 2
        indices = (freq >= banda_inferior) & (freq <= banda_superior)
        filtro[indices] = fft_amplitude[indices]
    return filtro

# Filtrar FFT para harmônicas
fft_harmonicas = filtrar_harmonicas(freq_fft, fft_result, harmonicas, largura_banda)

# Criar subplots
fig = make_subplots(rows=3, cols=1, vertical_spacing=0.1)

# Adicionar gráficos
fig.add_trace(go.Scatter(x=tempo, y=aceleracao, mode='lines', name='Aceleração', line=dict(color='blue')), row=1, col=1)
fig.add_trace(go.Scatter(x=tempo, y=hilbert_result, mode='lines', name='Envelope de Hilbert', line=dict(color='orange')), row=2, col=1)
fig.add_trace(go.Scatter(x=freq_fft, y=fft_harmonicas, mode='lines', name='Harmônicas (FFT)', line=dict(color='green')), row=3, col=1)

# Configuração de eixos e layout
fig.update_yaxes(title_text="Aceleração (m/s²)", row=1, col=1)
fig.update_yaxes(title_text="Envelope de Hilbert", row=2, col=1)
fig.update_yaxes(title_text="Amplitude FFT (Harmônicas)", row=3, col=1, range=[0, max(fft_harmonicas) * 1.1])
fig.update_xaxes(title_text="Tempo (s)", row=1, col=1)
fig.update_xaxes(title_text="Tempo (s)", row=2, col=1)
fig.update_xaxes(title_text="Frequência (Hz)", row=3, col=1)

fig.update_layout(
    title="Análise de Sinais com Foco nas Harmônicas",
    height=900,
    width=800,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Exibindo o gráfico
fig.show()

# Servir o arquivo HTML localmente
import http.server
import socketserver
import threading

# Função para servir o arquivo HTML
def serve_html():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
        print(f"Serving at http://127.0.0.1:{PORT}")
        httpd.serve_forever()

# Iniciar o servidor HTML em uma thread separada
server_thread = threading.Thread(target=serve_html)
server_thread.start()

# Exibindo a URL para acessar o arquivo HTML
print("Para visualizar os gráficos, acesse: http://127.0.0.1:8000/graficos_com_titulos.html")
