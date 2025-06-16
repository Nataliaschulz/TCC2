import math

# Função para normalizar os valores
def normalize(values, max_value):
    return [round((2**15 - 32) * (x / max_value)) for x in values]

# Função para converter um número para complemento de dois (16 bits)
def to_complement_of_two(value, bits=16):
    if value < 0:
        value = (1 << bits) + value  # Complemento de dois para negativos
    return value & 0xFFFF  # Garante que o valor esteja dentro de 16 bits

# Função para converter para hexadecimal de 32 bits
def to_32bit_hex(real_part, imag_part):
    # Combina a parte imaginária e real em um número de 32 bits
    combined = (imag_part << 16) | (real_part & 0xFFFF)
    # Formata como hexadecimal de 8 dígitos (32 bits)
    return f"{combined:08X}"

# Ler os dados do arquivo semmassa.txt
with open("semmassa.txt", "r") as file:
    lines = file.readlines()
    # Corrigir a vírgula para ponto e converter os valores para float
    real_parts = [float(line.strip().replace(',', '.')) for line in lines]  # Parte real
    imag_parts = real_parts  # Parte imaginária é igual à parte real (multiplicada por i)

# Calcular o valor máximo absoluto para normalização
max_real = max(abs(min(real_parts)), abs(max(real_parts)))
max_imag = max(abs(min(imag_parts)), abs(max(imag_parts)))
max_value = max(max_real, max_imag)

# Normalizar partes real e imaginária
normalized_real = normalize(real_parts, max_value)
normalized_imag = normalize(imag_parts, max_value)

# Converter para complemento de dois (16 bits)
real_complement = [to_complement_of_two(x) for x in normalized_real]
imag_complement = [to_complement_of_two(x) for x in normalized_imag]

# Converter para hexadecimal de 32 bits e salvar no arquivo saida_VIVADO.txt
with open("saida_VIVADO.txt", "w") as output_file:
    # Escrever os valores normalizados
    for real, imag in zip(real_complement, imag_complement):
        hex_value = to_32bit_hex(real, imag)
        output_file.write(hex_value + "\n")

    # Adicionar zeros até completar 32768 linhas
    lines_written = len(real_complement)  # Linhas já escritas
    target_lines = 32768  # Total de linhas desejadas
    zeros_needed = target_lines - lines_written

    if zeros_needed > 0:
        zero_hex = "00000000\n"  # Representação de 32 bits em hexadecimal + \n
        for _ in range(zeros_needed):
            output_file.write(zero_hex)

print("Processamento concluído. Os dados foram salvos em saida_VIVADO.txt.")
