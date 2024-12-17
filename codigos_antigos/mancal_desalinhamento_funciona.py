import numpy as np
import plotly.graph_objects as go
from scipy.signal import hilbert
from plotly.subplots import make_subplots

# Função para exportar dados para um arquivo .txt
def exportar_dados(filename, x, y, is_failed):
    """
    Exporta os dados x e y para um arquivo .txt.
    
    :param filename: Nome do arquivo de saída.
    :param x: Dados do eixo x.
    :param y: Dados do eixo y.
    :param is_failed: Dado que representa se é um dado com falha (Com_Falha=True, Sem_Falha=False):
    """
    with open(filename, 'w') as file:
        file.write("@RELATION ROLAMENTO\n@ATTRIBUTE AC numeric\n")
        file.write("@ATTRIBUTE AC-intensidade numeric\n@ATTRIBUTE Classe {'0','1'}\n@data\n")

        for xi, yi in zip(x, y):
            if xi <=300.0:
                file.write(f"{xi},{yi},{int(is_failed)}\n")
    print(f"Dados exportados para {filename}")


# Função para carregar e ajustar dados
def carregar_dados(filename):
    with open(filename, 'r') as file:
        data = file.read().replace(',', '.')
    return np.loadtxt(data.splitlines(), delimiter=None)

# Carregar os dados do arquivo txt
dados = carregar_dados('semmassa.txt')

# Separar as colunas em tempo e aceleração
tempo = dados[:, 0]  # Primeira coluna: tempo
aceleracao = dados[:, 1]  # Segunda coluna: aceleração

# Calcular a taxa de amostragem
fs = 2048

#1 / np.mean(np.diff(tempo))
#if fs <= 0:
 #   raise ValueError(f"A taxa de amostragem calculada é inválida: {fs}")

# Transformada de Hilbert
hilbert_result = np.abs(hilbert(aceleracao))

# FFT dos sinais
fft_result = np.abs(np.fft.fft(aceleracao))
freq_fft = np.fft.fftfreq(len(aceleracao), 1 / fs)

# FFT dos sinais
fft_result_hilbert = np.abs(np.fft.fft(hilbert_result))
freq_fft_hilbert = np.fft.fftfreq(len(hilbert_result), 1 / fs)

# Definir frequência fundamental e harmônicas
freq_fundamental = 58.6  # Primeira harmônica (Hz)
harmonicas = [freq_fundamental * n for n in range(1, 4)]  # 1ª, 2ª e 3ª harmônicas
harmonicas_negativas = [-freq_fundamental * n for n in range(1, 4)]  # Harmônicas negativas (espelhadas)
largura_banda = 20  # Largura de banda para cada harmônica

# Função para filtrar as regiões das harmônicas (incluindo frequências negativas)
def filtrar_harmonicas_fft_espelhado(freq, fft_amplitude, harmonicas, harmonicas_negativas, largura_banda):
    filtro = np.zeros_like(fft_amplitude)
    
    # Filtrar para frequências positivas
    for harm in harmonicas:
        banda_inferior = harm - largura_banda / 2
        banda_superior = harm + largura_banda / 2
        indices = (freq >= banda_inferior) & (freq <= banda_superior)
        filtro[indices] = fft_amplitude[indices]
    
    # Filtrar para frequências negativas (espelhadas)
    for harm_neg in harmonicas_negativas:
        banda_inferior = harm_neg - largura_banda / 2
        banda_superior = harm_neg + largura_banda / 2
        indices = (freq >= banda_inferior) & (freq <= banda_superior)
        filtro[indices] = fft_amplitude[indices]
    
    return filtro

# Filtrar FFT para harmônicas (positivas e negativas)
fft_harmonicas_espelhado = filtrar_harmonicas_fft_espelhado(
    freq_fft, fft_result, harmonicas, harmonicas_negativas, largura_banda
)

fft_harmonicas_hilbert_espelhado = filtrar_harmonicas_fft_espelhado(
    freq_fft_hilbert, fft_result_hilbert, harmonicas, harmonicas_negativas, largura_banda
)

# Adicionar ao gráfico para exibir as frequências espelhadas
fig = make_subplots(rows=4, cols=1, vertical_spacing=0.1)

# Adicionar gráficos
fig.add_trace(go.Scatter(x=tempo, y=aceleracao, mode='lines', name='Aceleração', line=dict(color='blue')), row=1, col=1)
fig.add_trace(go.Scatter(x=tempo, y=hilbert_result, mode='lines', name='Envelope de Hilbert', line=dict(color='orange')), row=2, col=1)
fig.add_trace(go.Scatter(x=freq_fft, y=fft_harmonicas_espelhado, mode='lines', name='Harmônicas (FFT Espelhado)', line=dict(color='green')), row=3, col=1)
fig.add_trace(go.Scatter(x=freq_fft_hilbert, y=fft_harmonicas_hilbert_espelhado, mode='lines', name='Harmônicas (FFT + Hilbert Espelhado)', line=dict(color='black')), row=4, col=1)

# Configuração de eixos e layout
fig.update_yaxes(title_text="Aceleração (m/s²)", row=1, col=1)
fig.update_yaxes(title_text="Envelope de Hilbert", row=2, col=1)
fig.update_yaxes(title_text="Modelo F", row=3, col=1, range=[0, max(fft_harmonicas_espelhado) * 1.1])
fig.update_xaxes(title_text="Tempo (s)", row=1, col=1)
fig.update_xaxes(title_text="Tempo (s)", row=2, col=1)
fig.update_xaxes(title_text="Frequência (Hz)", row=3, col=1)
fig.update_yaxes(title_text="Modelo FHF", row=4, col=1, range=[0, max(fft_harmonicas_hilbert_espelhado) * 1.1])
fig.update_xaxes(title_text="Frequência (Hz)", row=4, col=1)

# Exportar os dados dos gráficos para arquivos .txt
exportar_dados('F_Model__Health_200.txt', freq_fft, fft_harmonicas_espelhado, is_failed=False)
exportar_dados('FHF_Model_Health_200.txt', freq_fft_hilbert, fft_harmonicas_hilbert_espelhado, is_failed=False)

fig.update_layout(
    title="Análise de Sinais com Foco nas Harmônicas (Espelhadas)",
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
