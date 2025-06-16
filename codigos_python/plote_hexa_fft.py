import numpy as np
import matplotlib.pyplot as plt

# Função para ler os valores hexadecimais do arquivo e extrair a parte real
def ler_arquivo_txt(nome_arquivo):
    dados_32_bits = []
    
    # Ler o arquivo e armazenar os dados hexadecimais
    with open(nome_arquivo, 'r') as file:
        for linha in file:
            # Remover espaços em branco e quebras de linha
            linha = linha.strip()
            if linha:
                # Converter de hexadecimal para inteiro
                try:
                    valor_hex = int(linha, 16)
                    if valor_hex < 0 or valor_hex > 0xFFFFFFFF:
                        raise ValueError("Valor fora do intervalo de 32 bits.")
                    dados_32_bits.append(valor_hex)
                except ValueError as e:
                    print(f"Erro ao converter a linha '{linha}': {e}")
                    continue
    
    # Converter os dados para um numpy array de 32 bits (somente valores válidos)
    dados_32_bits = np.array(dados_32_bits, dtype=np.uint32)
    
    # Extrair a parte real (16 bits menos significativos)
    parte_real = (dados_32_bits & 0xFFFF).astype(np.int16)
    
    return parte_real

# Função para exportar os valores de intensidade da FFT em decimal
def exportar_fft_decimal(fft_senoide, nome_arquivo_saida):
    # Calcular a magnitude da FFT
    magnitude_fft = np.abs(fft_senoide)
    
    # Salvar os valores de magnitude em um arquivo de texto
    with open(nome_arquivo_saida, 'w') as file:
        for mag in magnitude_fft:
            file.write(f"{mag:.6f}\n")  # Formato: magnitude (decimal)
    print(f"Valores de intensidade da FFT exportados para {nome_arquivo_saida}")

# Nome do arquivo de entrada
nome_arquivo = 'saida_VIVADO.txt'

# Ler os dados do arquivo
parte_real = ler_arquivo_txt(nome_arquivo)

# Verificar se há dados suficientes para o cálculo da FFT
if len(parte_real) < 2:
    print("Não há dados suficientes para realizar a FFT.")
else:
    # Plotar a FFT
    n_samples = len(parte_real)
    fs = 2048  # Frequência de amostragem (Hz), ajustada conforme o sinal original
    frequencias = np.fft.fftfreq(n_samples, 1/fs)
    fft_senoide = np.fft.fft(parte_real)

    # Plotar o espectro de frequências completo (positivo e negativo)
    plt.figure(figsize=(10, 6))
    plt.plot(frequencias, np.abs(fft_senoide))  # Plota todas as frequências
    plt.title('Espectro de Frequência da Senoide (FFT Completa)')
    plt.xlabel('Frequência [Hz]')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()

    # Exportar os valores de intensidade da FFT em decimal
    nome_arquivo_saida = 'fft_intensidade.txt'
    exportar_fft_decimal(fft_senoide, nome_arquivo_saida)