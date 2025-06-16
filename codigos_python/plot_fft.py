import numpy as np
import matplotlib.pyplot as plt

# Função para ler e converter valores hexadecimais
def ler_arquivo_hex(nome_arquivo):
    with open(nome_arquivo, 'r') as file:
        linhas = file.readlines()
    # Converte cada valor hexadecimal para decimal
    dados = [int(linha.strip(), 16) for linha in linhas]
    return np.array(dados, dtype=float)

# Caminho do arquivo
nome_arquivo = r'D:\UNB\TCC2_ORGANIZADO\saida_VIVADO.txt'

# Ler os dados de aceleração
dados = ler_arquivo_hex(nome_arquivo)

# Verificar se há dados suficientes para o cálculo da FFT
if len(dados) < 2:
    print("Não há dados suficientes para realizar a FFT.")
else:
    # Frequência de amostragem (ajuste conforme necessário)
    fs = 1000  # Frequência de amostragem em Hz
    
    # Calcular a FFT
    n_samples = len(dados)
    frequencias = np.fft.fftfreq(n_samples, 1/fs)  # Frequências (positivas e negativas)
    fft_dados = np.fft.fft(dados)  # FFT do sinal de aceleração

    # Remover a frequência em 0 Hz (componente DC)
    fft_dados[frequencias == 0] = 0  # Define o valor da FFT em 0 Hz como zero

    # Plotar o espectro de frequências completo (incluindo frequências negativas)
    plt.figure(figsize=(10, 6))
    plt.plot(frequencias, np.abs(fft_dados))  # Plota todas as frequências
    plt.title('Espectro de Frequência da Aceleração (FFT Completa)')
    plt.xlabel('Frequência [Hz]')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()