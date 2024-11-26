import numpy as np
import plotly.graph_objects as go
from scipy.signal import butter, filtfilt, hilbert
from plotly.subplots import make_subplots

# Função para ler o arquivo e substituir vírgulas por pontos
def carregar_dados(filename):
    with open(filename, 'r') as file:
        data = file.read().replace(',', '.')
    with open('MancalInterno_Atual_SemMassa.txt', 'w') as temp_file:
        temp_file.write(data)
    return np.loadtxt('MancalInterno_Atual_SemMassa.txt')

# Carregar os dados do arquivo txt
dados = carregar_dados('MancalInterno_Atual_SemMassa.txt')

# Separar as colunas em tempo e aceleração
tempo = dados[:, 0]  # Agora a primeira coluna é tempo
aceleracao = dados[:, 1]  # A segunda coluna é aceleração

# Definir a taxa de amostragem estimada com base nos dados filtrados
fs = 1 / np.mean(np.diff(tempo))  # Taxa de amostragem

# Verificar se a taxa de amostragem é válida
if fs <= 0:
    raise ValueError(f"A taxa de amostragem calculada é inválida: {fs}")


# Aplicando transformada de Hilbert
hilbert_result = np.abs(hilbert(aceleracao))

# Calculando FFT dos sinais filtrados
fft_result = np.abs(np.fft.fft(aceleracao))
freq_fft = np.fft.fftfreq(len(aceleracao), 1 / fs)

# Calculando FFT após a transformada de Hilbert
fft_hilbert_result = np.abs(np.fft.fft(hilbert_result))
freq_hilbert_fft = np.fft.fftfreq(len(hilbert_result), 1 / fs)

# Criando subplots com 4 linhas e 1 coluna
fig = make_subplots(rows=4, cols=1, vertical_spacing=0.1)

# Adicionando gráficos
fig.add_trace(go.Scatter(x=tempo, y=aceleracao, mode='lines', name='Aceleração Filtrada', line=dict(color='blue', width=2)), row=1, col=1)
fig.add_trace(go.Scatter(x=tempo, y=hilbert_result, mode='lines', name='Envelope de Hilbert', line=dict(color='orange', width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=freq_fft, y=fft_result, mode='lines', name='FFT', line=dict(color='green', width=2)), row=3, col=1)
fig.add_trace(go.Scatter(x=freq_hilbert_fft, y=fft_hilbert_result, mode='lines', name='FFT Hilbert', line=dict(color='red', width=2)), row=4, col=1)

# Ajustar eixos
fig.update_yaxes(title_text="Aceleração Filtrada (m/s²)", row=1, col=1)
fig.update_yaxes(title_text="Envelope de Hilbert", row=2, col=1)
fig.update_yaxes(title_text="Amplitude (FFT)", row=3, col=1, range=[0, 20000])  # Limite de 0 a 20k para FFT
fig.update_yaxes(title_text="Amplitude (FFT Hilbert)", row=4, col=1, range=[0, 20000])  # Limite de 0 a 20k para FFT Hilbert

# Adicionando títulos e rótulos dos eixos
fig.update_xaxes(title_text="Tempo (s)", row=1, col=1)
fig.update_xaxes(title_text="Tempo (s)", row=2, col=1)
fig.update_xaxes(title_text="Frequência (Hz)", row=3, col=1)
fig.update_xaxes(title_text="Frequência (Hz)", row=4, col=1)

# Ajustar layout
fig.update_layout(
    title="Análise de Sinais com e sem Falha",
    height=1000,
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
