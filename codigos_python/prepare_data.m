%%
% Prof. Daniel Muñoz Arboleda
% UnB/FCTE
% 22 janeiro, 2025
%
% Descrição:
% Cria um sinal de entrada, aplica a FFT e cria um arquivo de entrada para o testbench.
% Este sinal pode ser injetado em um IP-core FFT da AMD-Xilinx.
% O script também lê a saída da FFT e compara com a saída esperada.
%
%%
% Define o sinal ou função no domínio do tempo
close all;
clear all;
clc;

create_file = 0; % 1: escreve os arquivos de entrada; 0: caso contrário
decode_result = 1; % 1: decodifica o resultado do FPGA; 0: não decodifica

fs = 2048; % frequência de amostragem (Hz)

% Lê o sinal do arquivo saida_VIVADO.txt (valores hexadecimais)
fileID = fopen('saida_VIVADO.txt', 'r');
hexData = textscan(fileID, '%s'); % Lê os valores hexadecimais como strings
fclose(fileID);

% Converte os valores hexadecimais para decimais
signal_data = hex2dec(hexData{1});


% Separa as partes real e imaginária do sinal
xRe = signal_data(1:2:end); % Parte real do sinal (amostras ímpares)
xIm = signal_data(2:2:end); % Parte imaginária do sinal (amostras pares)

% Verifica se o número de amostras é par
if length(xRe) ~= length(xIm)
    error('O número de amostras para parte real e imaginária não é igual.');
end

% Ajusta o vetor de tempo com base no número de amostras reais
t = 0:1/fs:(length(xRe)/fs)-(1/fs); % Vetor de tempo

% Sinal complexo
x = xRe + 1i*xIm;

% Plota as partes real e imaginária do sinal no domínio do tempo
figure; 
subplot(2,1,1); 
plot(t, xRe); 
xlabel('Tempo'); 
ylabel('Parte Real'); 
title('Parte Real do Sinal no Domínio do Tempo'); 
subplot(2,1,2); 
plot(t, xIm); 
xlabel('Tempo'); 
ylabel('Parte Imaginária'); 
title('Parte Imaginária do Sinal no Domínio do Tempo'); 

% Calcula a Transformada de Fourier
y = fft(x); 
% Extrai as partes real e imaginária da Transformada de Fourier
yRe = real(y); 
yIm = imag(y); 

% Plota as partes real e imaginária da Transformada de Fourier
n = length(x); % número de amostras
f = (0:n-1)*(fs/n); % faixa de frequência
faxis = fs*(0:1/(n-1):1);

figure; 
subplot(2,1,1); 
plot(f, yRe); 
xlabel('Frequência'); 
ylabel('Parte Real'); 
title('Parte Real da Transformada de Fourier'); 
subplot(2,1,2); 
plot(f, yIm); 
xlabel('Frequência'); 
ylabel('Parte Imaginária'); 
title('Parte Imaginária da Transformada de Fourier'); 

% Cria arquivos de entrada para o testbench, se necessário


% Decodifica o resultado do FPGA, se necessário
if decode_result == 1
    hw_out_str = textread('fft_512_output.txt', '%s');
    sw_out_str = textread('saida_.txt', '%s');
    hw_out = cellfun(@str2num, hw_out_str)/(2^15-32); % Converte para valores decimais
    sw_out = cellfun(@str2num, sw_out_str)/(2^15-32); % Converte para valores decimais

    % Separa as partes real e imaginária da saída do FPGA
    yRe_hw = hw_out(1:2:end); % Parte real (amostras ímpares)
    yIm_hw = hw_out(2:2:end); % Parte imaginária (amostras pares)

    % Separa as partes real e imaginária da saída esperada
    yRe_sw = sw_out(1:2:end); % Parte real (amostras ímpares)
    yIm_sw = sw_out(2:2:end); % Parte imaginária (amostras pares)

    % Calcula a magnitude da FFT (saída do FPGA)
    yhw = sqrt(yRe_hw.^2 + yIm_hw.^2); % Magnitude

    % Calcula a magnitude da FFT (saída esperada)
    ysw = sqrt(yRe.^2 + yIm.^2); % Magnitude

    % Normaliza e converte para dB
    yhw = 10*log10(yhw/max(yhw));
    ysw = 10*log10(ysw/max(ysw));

    % Ajusta o vetor de frequência para o tamanho correto
    faxis = fs*(0:1/(length(yhw)-1):1);

    % Plota os resultados
    figure; 
    plot(faxis, yhw, '-k'); % Saída do FPGA
    hold on
    plot(faxis, ysw, '-r'); % Saída esperada
    xlabel('Frequência (Hz)'); 
    ylabel('Magnitude (dB)'); 
    title('Magnitude da Transformada de Fourier'); 
    legend('Saída do FPGA', 'Saída Esperada');
end