import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft

# Nome do arquivo de entrada (hexadecimal)
arquivo_entrada = 'senoide_60hz_hex.txt'

# Nome do arquivo de saída (intensidades da FFT)
arquivo_saida = 'saida_fft_intensidades_SW.txt'

# Lista para armazenar os valores decimais
valores_decimais = []

# Abre o arquivo de entrada para leitura
with open(arquivo_entrada, 'r') as entrada:
    # Itera sobre cada linha do arquivo de entrada
    for linha in entrada:
        # Remove espaços em branco e quebras de linha
        linha = linha.strip()
        
        # Pega apenas os 4 últimos caracteres hexadecimais
        linha = linha[-4:]
        
        # Converte o valor hexadecimal para decimal
        valor_decimal = int(linha, 16)
        
        # Adiciona o valor decimal à lista
        valores_decimais.append(valor_decimal)

# Converte a lista de valores decimais para um array numpy
valores_decimais = np.array(valores_decimais)

# Calcula a FFT dos valores decimais
fft_resultado = fft(valores_decimais)

# Calcula as intensidades (módulos) da FFT
intensidades_fft = np.abs(fft_resultado)

# Abre o arquivo de saída para escrita
with open(arquivo_saida, 'w') as saida:
    # Escreve as intensidades da FFT no arquivo de saída
    for intensidade in intensidades_fft:
        saida.write(f"{intensidade}\n")

print(f"FFT concluída! Intensidades salvas em {arquivo_saida}.")

# Plotagem das intensidades da FFT
plt.figure(figsize=(10, 6))
plt.plot(intensidades_fft, label='Intensidades da FFT')
plt.title('Espectro de Frequência (Intensidades da FFT)')
plt.xlabel('Índice de Frequência')
plt.ylabel('Intensidade (Magnitude)')
plt.grid()
plt.legend()
plt.show()