import os

# Nome do arquivo de entrada (hexadecimal)
# arquivo_entrada = r'D:/UNB/TCC2_organizado/saida_da_senoide_ip.txt'  # Usando string raw
# OU, se o arquivo estiver na mesma pasta que o script:
arquivo_entrada = 'saida_da_senoide_ip.txt'

# Nome do arquivo de saída (decimal)
arquivo_saida = 'saida_ip_decimal_HW.txt'

# Verifica se o arquivo de entrada existe
if not os.path.exists(arquivo_entrada):
    print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
    print(f"Diretório atual: {os.getcwd()}")
else:
    try:
        # Abre o arquivo de entrada para leitura e o arquivo de saída para escrita
        with open(arquivo_entrada, 'r') as entrada, open(arquivo_saida, 'w') as saida:
            # Itera sobre cada linha do arquivo de entrada
            for linha in entrada:
                # Remove espaços em branco e quebras de linha
                linha = linha.strip()
                
                # Converte o valor hexadecimal para decimal
                try:
                    valor_decimal = int(linha, 16)
                except ValueError:
                    print(f"Erro: A linha '{linha}' não é um valor hexadecimal válido.")
                    continue  # Pula para a próxima linha
                
                # Escreve o valor decimal no arquivo de saída
                saida.write(f"{valor_decimal}\n")

        print(f"Conversão concluída! Valores decimais salvos em {arquivo_saida}.")
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}")