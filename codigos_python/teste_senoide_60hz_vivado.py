import numpy as np
import matplotlib.pyplot as plt

# Parâmetros da senoide
fs = 1000  # Frequência de amostragem (Hz)
f_senoide = 60  # Frequência da senoide (Hz)
n_samples = 32768  # Número de amostras (32768 amostras)

# Gerar a senoide
t = np.linspace(0, n_samples / fs, n_samples, endpoint=False)  # Vetor de tempo
senoide = np.sin(2 * np.pi * f_senoide * t)  # Sinal senoide

# Transformar a senoide para variar entre 0 e 1
senoide_positiva = (senoide + 1) / 2  # Agora varia entre 0 e 1

# Escalonar para o intervalo de 16 bits (0 a 65535)
parte_real = (senoide_positiva * (2**16 - 1)).astype(np.uint16)

# Parte imaginária (16 bits mais significativos, pode ser zero para uma senoide real)
parte_imaginaria = np.zeros_like(parte_real)  # Parte imaginária é zero

# Combinar parte real e imaginária em um único vetor de 32 bits
dados_32_bits = (parte_imaginaria.astype(np.uint32) << 16) | (parte_real.astype(np.uint32) & 0xFFFF)

# Exportar para arquivo TXT em formato hexadecimal
with open('senoide_60hz_hex.txt', 'w') as txtfile:
    for valor in dados_32_bits:
        # Escrever cada valor de 32 bits em formato hexadecimal
        txtfile.write(f'{valor:08X}\n')  # Formato hexadecimal de 8 dígitos (32 bits)

# Plotar a forma de onda no tempo
plt.figure(figsize=(10, 6))
plt.plot(t, senoide_positiva, label='Senoide 60Hz (0 a 1)')
plt.title('Forma de Onda no Tempo (Senoide de 60Hz)')
plt.xlabel('Tempo [s]')
plt.ylabel('Amplitude')
plt.grid(True)
plt.legend()
plt.show()

# Calcular a FFT
fft_senoide = np.fft.fft(senoide_positiva)

# Reorganizar as frequências para incluir a parte negativa
fft_senoide_shifted = np.fft.fftshift(fft_senoide)
frequencias = np.fft.fftfreq(n_samples, 1/fs)
frequencias_shifted = np.fft.fftshift(frequencias)

# Plotar a FFT com a parte negativa das frequências
plt.figure(figsize=(10, 6))
plt.plot(frequencias_shifted, np.abs(fft_senoide_shifted))
plt.title('Espectro de Frequência da Senoide (FFT com Frequências Negativas)')
plt.xlabel('Frequência [Hz]')
plt.ylabel('Magnitude')
plt.grid(True)
plt.show()