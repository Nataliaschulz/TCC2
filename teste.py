import numpy as np
import plotly.graph_objects as go
from scipy.signal import butter, filtfilt, hilbert
from plotly.subplots import make_subplots

# Definição dos parâmetros do sinal
fs = 20E3  # Taxa de amostragem (Hz)
Np = 13  # Número de dentes no pinhão
Ng = 35  # Número de dentes na engrenagem
fPin = 22.5  # Frequência do eixo do pinhão (Hz)
fGear = fPin * Np / Ng  # Frequência do eixo da engrenagem (Hz)
fMesh = fPin * Np  # Frequência da engrenagem (Hz)
t = np.arange(0, 20, 1 / fs)
vfIn = 0.4 * np.sin(2 * np.pi * fPin * t)  # Forma de onda do pinhão
vfOut = 0.2 * np.sin(2 * np.pi * fGear * t)  # Forma de onda da engrenagem
vMesh = np.sin(2 * np.pi * fMesh * t)  # Forma de onda da engrenagem
vNoFault = vfIn + vfOut + vMesh
vNoFaultNoisy = vNoFault + np.random.randn(len(t)) / 5

# Criando bandas laterais
SideBands = np.arange(-3, 4)
SideBandAmp = [0.02, 0.1, 0.4, 0, 0.4, 0.1, 0.02]  # Amplitudes das bandas laterais
SideBandFreq = fMesh + SideBands * fPin  # Frequências das bandas laterais
vSideBands = np.dot(SideBandAmp, np.sin(2 * np.pi * np.outer(SideBandFreq, t)))

# Adicionando bandas laterais ao sinal com falha
vPinFaultNoisy = vNoFaultNoisy + vSideBands

# Aplicando filtro passa-baixa
fc = 2000  # Frequência de corte do filtro passa-baixa
b, a = butter(6, fc / (fs / 2), 'low')
vNoFaultFiltered = filtfilt(b, a, vNoFaultNoisy)
vFaultFiltered = filtfilt(b, a, vPinFaultNoisy)

# Calculando FFT dos sinais filtrados
fft_no_fault_result = np.abs(np.fft.fft(vNoFaultFiltered))
fft_fault_result = np.abs(np.fft.fft(vFaultFiltered))

# Frequências para a primeira FFT
freq_no_fault = np.fft.fftfreq(len(vNoFaultFiltered), 1 / fs)
# Frequências para a segunda FFT
freq_fault = np.fft.fftfreq(len(vFaultFiltered), 1 / fs)

# Aplicando transformada de Hilbert
hilbert_no_fault_result = np.abs(hilbert(vNoFaultFiltered))
hilbert_fault_result = np.abs(hilbert(vFaultFiltered))

# Calculando FFT dos sinais após a transformada de Hilbert
fft_hilbert_no_fault_result = np.abs(np.fft.fft(hilbert_no_fault_result))
fft_hilbert_fault_result = np.abs(np.fft.fft(hilbert_fault_result))

# Frequências para a terceira FFT
freq_hilbert_no_fault = np.fft.fftfreq(len(hilbert_no_fault_result), 1 / fs)
# Frequências para a quarta FFT
freq_hilbert_fault = np.fft.fftfreq(len(hilbert_fault_result), 1 / fs)

# Criando subplots com 5 linhas e 1 coluna
fig = make_subplots(rows=5, cols=1, vertical_spacing=0.1)

# Adicionando cada gráfico em um subplot diferente
fig.add_trace(go.Scatter(x=t, y=vPinFaultNoisy, mode='lines', name='Com Falha', line=dict(color='red')), row=1, col=1)
fig.add_trace(go.Scatter(x=t, y=vNoFaultNoisy, mode='lines', name='Sem Falha', line=dict(color='blue', dash='dot')), row=1, col=1)

fig.add_trace(go.Scatter(x=t, y=vFaultFiltered, mode='lines', name='Com Falha', line=dict(color='red')), row=2, col=1)
fig.add_trace(go.Scatter(x=t, y=vNoFaultFiltered, mode='lines', name='Sem Falha', line=dict(color='blue', dash='dot')), row=2, col=1)

fig.add_trace(go.Scatter(x=t, y=hilbert_fault_result, mode='lines', name='Com Falha', line=dict(color='red')), row=3, col=1)
fig.add_trace(go.Scatter(x=t, y=hilbert_no_fault_result, mode='lines', name='Sem Falha', line=dict(color='blue', dash='dot')), row=3, col=1)

fig.add_trace(go.Scatter(x=freq_fault, y=fft_fault_result, mode='lines', name='Com Falha', line=dict(color='red')), row=4, col=1)
fig.add_trace(go.Scatter(x=freq_no_fault, y=fft_no_fault_result, mode='lines', name='Sem Falha', line=dict(color='blue', dash='dot')), row=4, col=1)

fig.add_trace(go.Scatter(x=freq_hilbert_fault, y=fft_hilbert_fault_result, mode='lines', name='Com Falha', line=dict(color='red')), row=5, col=1)
fig.add_trace(go.Scatter(x=freq_hilbert_no_fault, y=fft_hilbert_no_fault_result, mode='lines', name='Sem Falha', line=dict(color='blue', dash='dot')), row=5, col=1)

# Adicionando títulos e rótulos dos eixos
fig.update_yaxes(title_text="Amplitude", tickfont=dict(size=16), titlefont=dict(size=16), row=1, col=1, showgrid=True, zeroline=True, showline=True)
fig.update_yaxes(title_text="Amplitude", tickfont=dict(size=16), titlefont=dict(size=16), row=2, col=1, showgrid=True, zeroline=True, showline=True)
fig.update_yaxes(title_text="Hilbert", tickfont=dict(size=16), titlefont=dict(size=16), row=3, col=1, showgrid=True, zeroline=True, showline=True)
fig.update_yaxes(title_text="FFT", tickfont=dict(size=16), titlefont=dict(size=16), row=4, col=1, showgrid=True, zeroline=True, showline=True)
fig.update_yaxes(title_text="FFT + Hilbert", tickfont=dict(size=16), titlefont=dict(size=16), row=5, col=1, showgrid=True, zeroline=True, showline=True)

fig.update_xaxes(title_text="Frequency (Hz)", tickfont=dict(size=16), titlefont=dict(size=16), tickvals=np.arange(np.min(freq_hilbert_no_fault), np.max(freq_hilbert_no_fault) + 1, 50), row=5, col=1, showgrid=True, zeroline=True, showline=True)
fig.update_xaxes(title_text="Frequency (Hz)", tickfont=dict(size=16), titlefont=dict(size=16), tickvals=np.arange(np.min(freq_no_fault), np.max(freq_no_fault) + 1, 50), row=4, col=1, showgrid=True, zeroline=True, showline=True)
fig.update_xaxes(title_text="Time (s)", tickfont=dict(size=16), titlefont=dict(size=16), tickvals=np.arange(np.min(t), np.max(t) + 1, 0.05), row=3, col=1, showgrid=True, zeroline=True, showline=True)
fig.update_xaxes(title_text="Time (s)", tickfont=dict(size=16), titlefont=dict(size=16), tickvals=np.arange(np.min(t), np.max(t) + 1, 0.05), row=2, col=1, showgrid=True, zeroline=True, showline=True)
fig.update_xaxes(title_text="Time (s)", tickfont=dict(size=16), titlefont=dict(size=16), tickvals=np.arange(np.min(t), np.max(t) + 1, 0.5), row=1, col=1, showgrid=True, zeroline=True, showline=True)

# Definindo o fundo branco
fig.update_layout(
    title="Análise de Sinais com e sem Falha",
    height=2000,
    width=1000,
    plot_bgcolor='white',  # Fundo do gráfico
    paper_bgcolor='white'  # Fundo ao redor do gráfico
)

# Salvar o gráfico em um arquivo HTML
fig.write_html("graficos_com_titulos.html")

# Exibindo o endereço IP para acessar o arquivo HTML
import http.server
import socketserver
import threading

# Function to serve the HTML file
def serve_html():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
        print(f"Serving at http://127.0.0.1:{PORT}")
        httpd.serve_forever()

# Start serving the HTML file in a separate thread
server_thread = threading.Thread(target=serve_html)
server_thread.start()

# Print the URL to access the HTML file
print("Para visualizar os gráficos, acesse: http://127.0.0.1:8000/graficos_com_titulos.html")
