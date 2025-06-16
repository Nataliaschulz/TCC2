clear all; close all; clc;

% Definir a frequência de amostragem
T = 10; % Duração do sinal (s)
Fs = 2048; % Frequência de amostragem (deve ser >= 2 * Fmax)
rot_maq = 3520; % Rotação da máquina em RPM

% Denominação de tempo e amplitude (mm/s²)
bal = load('MancalInterno_Desalinhamento_05_8g_1.txt');
t = bal(:,1); % Tempo
amp_a = bal(:,2) - mean(bal(:,2)); % Eliminar ruído DC

L = length(t); % Número total de amostras

% Eliminar resíduo DC da aceleração
dc_a = dsp.DCBlocker('Algorithm', 'FIR');
amp_a_eliminardc = dc_a(amp_a);

% Integração para obter a velocidade
amp_v = cumtrapz(t, amp_a_eliminardc) * 1000;
amp_v = amp_v - mean(amp_v);

% Eliminar resíduo DC da velocidade
dc_v = dsp.DCBlocker('Algorithm', 'FIR');
amp_v_eliminardc = dc_v(amp_v);

% Filtro passa-banda (harmônicos 1 a 3)
amp_v_bandpass = bandpass(amp_v_eliminardc, [58.6 176.01], Fs, 'ImpulseResponse', 'fir', 'Steepness', 0.96);

% Filtros para remover bandas específicas
amp_v_bandstop1 = bandstop(amp_v_bandpass, [58.9 117.3], Fs, 'ImpulseResponse', 'fir', 'Steepness', 0.95);
amp_v_bandstop2 = bandstop(amp_v_bandstop1, [117.8 176.3], Fs, 'ImpulseResponse', 'fir', 'Steepness', 0.95);

% Calcular RMS da velocidade
rms_v = rms(amp_v_bandstop2);

% Transformada de Fourier
fft_v = fft(amp_v_bandstop2);
fft_v2 = abs(fft_v / L);
fft_v1 = fft_v2(1:L/2+1); % Spectrum unilateral
fft_v1(2:end-1) = 2 * fft_v1(2:end-1);
fv = Fs * (0:(L/2)) / L; % Domínio da frequência

% Frequências dos harmônicos
freq_maq = rot_maq / 60;
freq_inicial_H1 = freq_maq - 0.8; freq_final_H1 = freq_maq + 0.5;
freq_inicial_H2 = (freq_maq * 2) - 0.8; freq_final_H2 = (freq_maq * 2) + 0.5;
freq_inicial_H3 = (freq_maq * 3) - 0.8; freq_final_H3 = (freq_maq * 3) + 0.5;

% Inicializar variáveis de harmônicos
H1 = 0; freq_H1 = 0;
H2 = 0; freq_H2 = 0;
H3 = 0; freq_H3 = 0;

% Encontrar amplitudes máximas nos harmônicos
for i = 1:length(fv)
    if fv(i) >= freq_inicial_H1 && fv(i) <= freq_final_H1
        if fft_v1(i) > H1
            H1 = fft_v1(i);
            freq_H1 = fv(i);
        end
    end
    if fv(i) >= freq_inicial_H2 && fv(i) <= freq_final_H2
        if fft_v1(i) > H2
            H2 = fft_v1(i);
            freq_H2 = fv(i);
        end
    end
    if fv(i) >= freq_inicial_H3 && fv(i) <= freq_final_H3
        if fft_v1(i) > H3
            H3 = fft_v1(i);
            freq_H3 = fv(i);
        end
    end
end

% Razões dos harmônicos
HS = H1 + H2 + H3;
R1 = (H1 / HS) * 100;
R2 = (H2 / HS) * 100;
R3 = (H3 / HS) * 100;

% Criar sistema Fuzzy
fis = newfis('idendes');

% Variáveis de entrada
fis = addvar(fis, 'input', 'RMS', [0 1]);
fis = addvar(fis, 'input', 'R1', [0 100]);
fis = addvar(fis, 'input', 'R2', [0 100]);
fis = addvar(fis, 'input', 'R3', [0 100]);

% Variáveis de saída
fis = addvar(fis, 'output', 'Desbalanceamento', [0 100]);

% Adicionar funções de pertinência
fis = addmf(fis, 'input', 1, 'P', 'trapmf', [-0.2 0 0.133 0.259]);
fis = addmf(fis, 'input', 1, 'M', 'trimf', [0.133 0.259 0.346]);
fis = addmf(fis, 'input', 1, 'A', 'trimf', [0.259 0.346 0.432]);
fis = addmf(fis, 'input', 1, 'MA', 'trapmf', [0.346 0.432 1 2]);

fis = addmf(fis, 'output', 1, 'Inexistente', 'trimf', [-1 0 25]);
fis = addmf(fis, 'output', 1, 'Tolerável', 'trimf', [25 37.5 50]);
fis = addmf(fis, 'output', 1, 'Alto', 'trimf', [50 62.5 75]);
fis = addmf(fis, 'output', 1, 'Perigoso', 'trimf', [75 100 101]);

% Adicionar regras
regras = [1 3 1 1 1 1 1; 2 3 1 1 2 1 1; 3 3 1 1 3 1 1; 4 3 1 1 4 1 1; 1 2 1 1 1 1 1; 
        2 2 1 1 2 1 1; 3 2 1 1 3 1 1; 4 2 1 1 4 1 1; 0 3 3 3 1 1 1; 
        0 3 3 2 1 1 1; 0 3 3 1 1 1 1;0 3 2 3 1 1 1; 0 3 2 2 1 1 1; 0 3 2 1 1 1 1; 
        0 3 1 3 1 1 1; 0 3 1 2 1 1 1; 0 2 3 3 1 1 1; 0 2 3 2 1 1 1; 0 2 3 1 1 1 1; 
        0 2 2 3 1 1 1; 0 2 2 2 1 1 1; 0 2 2 1 1 1 1; 0 2 1 3 1 1 1; 0 2 1 2 1 1 1; 
        0 1 3 3 1 1 1; 0 1 3 2 1 1 1; 0 1 3 1 1 1 1; 0 1 2 3 1 1 1; 0 1 2 2 1 1 1;
        0 1 2 1 1 1 1; 0 1 1 3 1 1 1; 0 1 1 2 1 1 1];

fis = addRule(fis, regras);

% Avaliar sistema fuzzy
desbalanceamento = evalfis(fis, [rms_v R1 R2 R3]);

% Plotar resultados
figure(1);
plotfis(fis);
figure(2);
plotmf(fis, 'input', 1);
figure(3);
plotmf(fis, 'input', 2);
figure(4);
plotmf(fis, 'output', 1);
