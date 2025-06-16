#Codigo que plota o grafico do sinal no modelo FHF modelo F 
#Gera a base de dados 

import numpy as np
import plotly.graph_objects as go
from scipy.signal import hilbert, welch
from plotly.subplots import make_subplots

# Função para carregar e ajustar dados
def carregar_dados(filename):
    with open(filename, 'r') as file:
        data = file.read().replace(',', '.')
    return np.loadtxt(data.splitlines(), delimiter=None)

# Função para calcular parâmetros
def calcular_parametros(dados, freq_fundamental, harmonicas, harmonicas_negativas, largura_banda, n_hilbert=None, n_fft=None):
    if n_hilbert is None:
        n_hilbert = len(dados)
    if n_fft is None:
        n_fft = len(dados)

    tempo = dados[:, 0]  # Primeira coluna: tempo
    aceleracao = dados[:, 1]  # Segunda coluna: aceleração

    fs = 2048
  
    # Transformada de Hilbert
    hilbert_result = np.abs(hilbert(aceleracao, N=n_hilbert))

    # FFT
    fft_result = np.abs(np.fft.fft(aceleracao, n=n_fft))
    freq_fft = np.fft.fftfreq(n_fft, 1 / fs)

    # FFT dos envelopes
    fft_result_hilbert = np.abs(np.fft.fft(hilbert_result, n=n_fft))
    freq_fft_hilbert = np.fft.fftfreq(n_fft, 1 / fs)

    # Filtrar harmônicas
    def filtrar_harmonicas_fft_espelhado(freq, fft_amplitude, harmonicas, harmonicas_negativas, largura_banda):
        filtro = np.zeros_like(fft_amplitude)
        for harm in harmonicas + harmonicas_negativas:
            banda_inferior = harm - largura_banda / 2
            banda_superior = harm + largura_banda / 2
            indices = (freq >= banda_inferior) & (freq <= banda_superior)
            filtro[indices] = fft_amplitude[indices]
        return filtro

    # Filtrar FFT para harmônicas
    fft_harmonicas_espelhado = filtrar_harmonicas_fft_espelhado(freq_fft, fft_result, harmonicas, harmonicas_negativas, largura_banda)
    fft_harmonicas_hilbert_espelhado = filtrar_harmonicas_fft_espelhado(freq_fft_hilbert, fft_result_hilbert, harmonicas, harmonicas_negativas, largura_banda)

    return tempo, aceleracao, hilbert_result, freq_fft, fft_harmonicas_espelhado, freq_fft_hilbert, fft_harmonicas_hilbert_espelhado

# Função para calcular RMS
def calcular_rms_harmonicas(freq, fft_amplitude, harmonicas, largura_banda):
    rms_total = 0
    for harm in harmonicas:
        banda_inferior = harm - largura_banda / 2
        banda_superior = harm + largura_banda / 2
        indices = (freq >= banda_inferior) & (freq <= banda_superior)
        rms_total += np.sum(fft_amplitude[indices]**2)
    return np.sqrt(rms_total)

# Função para calcular erro quadrático médio (EQM)
def calcular_mae(espectro1, espectro2): # somatorio da diferença ao quadrado / numero de amostras
    soma = np.sum(abs(espectro1 - espectro2))
    print(f' tamanh espectro {len(espectro1)}')
    return soma / len(espectro1)

# Função para calcular erro quadrático médio (EQM)
def calcular_eqm(espectro1, espectro2): # somatorio da diferença ao quadrado / numero de amostras
    soma = np.sum((espectro1 - espectro2)**2)
    return soma / len(espectro1)

# Função para calcular PSD
def calcular_psd(fft_result, fs, n_fft):
    f, psd = welch(fft_result, fs, nperseg=n_fft)
    return f, psd

# Parâmetros das harmônicas
freq_fundamental = 58.6
harmonicas = [freq_fundamental * n for n in range(1, 4)]
harmonicas_negativas = [-freq_fundamental * n for n in range(1, 4)]
largura_banda = 20

n_hilbert = None
n_fft = None

# Carregar dados das duas condições
dados_saude = carregar_dados('base_dados_mancal\semmassa.txt')
dados_falha = carregar_dados('base_dados_mancal\MancalInterno_Desalinhamento_05_3g.txt')

# Calcular parâmetros para os dois casos
param_saude = calcular_parametros(dados_saude, freq_fundamental, harmonicas, harmonicas_negativas, largura_banda, n_hilbert, n_fft)
param_falha = calcular_parametros(dados_falha, freq_fundamental, harmonicas, harmonicas_negativas, largura_banda, n_hilbert, n_fft)

# Calcular PSD para ambos os modelos
f_psd_saude, psd_saude = calcular_psd(param_saude[4], 2048, n_fft)
f_psd_falha, psd_falha = calcular_psd(param_falha[4], 2048, n_fft)
f_psd_hilbert_saude, psd_hilbert_saude = calcular_psd(param_saude[6], 2048, n_fft)
f_psd_hilbert_falha, psd_hilbert_falha = calcular_psd(param_falha[6], 2048, n_fft)

# Calcular RMS
rms_saude = calcular_rms_harmonicas(param_saude[3], param_saude[4], harmonicas, largura_banda)
rms_falha = calcular_rms_harmonicas(param_falha[3], param_falha[4], harmonicas, largura_banda)
rms_saude_hilbert = calcular_rms_harmonicas(param_saude[5], param_saude[6], harmonicas, largura_banda)
rms_falha_hilbert = calcular_rms_harmonicas(param_falha[5], param_falha[6], harmonicas, largura_banda)

# Calcular EQM entre espectros
eqm_f = calcular_eqm(param_falha[4], param_saude[4])
eqm_fhf = calcular_eqm(param_falha[6], param_saude[6])

eq_mae_f = calcular_mae(param_falha[4], param_saude[4])
eq_mae_fhf = calcular_mae(param_falha[6], param_saude[6])

# Printar resultados de RMS e EQM
print(f'RMS Saudável (Modelo F): {rms_saude}')
print(f'RMS Falha (Modelo F): {rms_falha}')
print(f'RMS Saudável (Modelo FHF): {rms_saude_hilbert}')
print(f'RMS Falha (Modelo FHF): {rms_falha_hilbert}')

print(f'\nEQM entre os espectros do Modelo F (Saudável vs Falha): {eqm_f}')
print(f'EQM entre os espectros do Modelo FHF (Saudável vs Falha): {eqm_fhf}')

print(f'\nMAE entre os espectros do Modelo F (Saudável vs Falha): {eq_mae_f}')
print(f'MAE entre os espectros do Modelo FHF (Saudável vs Falha): {eq_mae_fhf}')

# Criar subplots
fig = make_subplots(rows=5, cols=1, vertical_spacing=0.1)

# Títulos das séries
titulos = [
    "SINAL NO TEMPO",
    "SINAL ENVELOPE DE HILBERT",
    "FFT MODELO F",
    "FFT MODELO FHF",
    "DENSIDADE ESPECTRAL DE POTÊNCIA (PSD)"
]

# Adicionar gráficos
for i, (titulo, dados_saude_plot, dados_falha_plot) in enumerate(zip(
    titulos,
    [
        (param_saude[0], param_saude[1]),  # Aceleração no tempo
        (param_saude[0], param_saude[2]),  # Envelope de Hilbert
        (param_saude[3][(param_saude[3] >= 0) & (param_saude[3] <= 300)], 
         param_saude[4][(param_saude[3] >= 0) & (param_saude[3] <= 300)]),  # FFT
        (param_saude[5][(param_saude[5] >= 0) & (param_saude[5] <= 300)], 
         param_saude[6][(param_saude[5] >= 0) & (param_saude[5] <= 300)]),   # FFT + Hilbert
        (f_psd_saude, psd_saude),  # PSD (Modelo F)
        (f_psd_falha, psd_falha),  # PSD (Modelo F)
        (f_psd_hilbert_saude, psd_hilbert_saude),  # PSD (Modelo FHF)
        (f_psd_hilbert_falha, psd_hilbert_falha)   # PSD (Modelo FHF)
    ],
    [
        (param_falha[0], param_falha[1]),  # Aceleração no tempo (com falha)
        (param_falha[0], param_falha[2]),  # Envelope de Hilbert (com falha)
        (param_falha[3][(param_falha[3] >= 0) & (param_falha[3] <= 300)], 
         param_falha[4][(param_falha[3] >= 0) & (param_falha[3] <= 300)]),  # FFT (com falha)
        (param_falha[5][(param_falha[5] >= 0) & (param_falha[5] <= 300)], 
         param_falha[6][(param_falha[5] >= 0) & (param_falha[5] <= 300)]),   # FFT + Hilbert (com falha)
        (f_psd_hilbert_saude, psd_hilbert_saude),  # PSD (Modelo FHF, saudável)
        (f_psd_hilbert_falha, psd_hilbert_falha)   # PSD (Modelo FHF, falha)
    ]
), start=1):
    fig.add_trace(go.Scatter(x=dados_falha_plot[0], y=dados_falha_plot[1], mode='lines',
                             name=f'Falha: {titulo}', line=dict(color='red')), row=i, col=1)
    fig.add_trace(go.Scatter(x=dados_saude_plot[0], y=dados_saude_plot[1], mode='lines',
                             name=f'Saudável: {titulo}', line=dict(color='blue')), row=i, col=1)
   

# Atualizar gráficos e exibir
fig.update_layout(title="Comparação: Saudável vs Falha", height=1000, width=800, plot_bgcolor='white', paper_bgcolor='white')
fig.show()
