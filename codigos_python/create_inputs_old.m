%%
% Prof. Daniel Muñoz Arboleda
% UnB/FCTE
% 22 january, 2025
%
% Description:
% Create an input signal, apply FFT and create input file for testbench. 
% This signal can be injected in a FFT IP-core from AMD-Xilinx 
% The scrip also reads the FFT output and compares with the expected out.
%
%%
% Define your signal or function in the time domain 
close all;
clear all;
clc;
create_file=1; % 1:write_inputs; 0:otherwise
decode_result=0; %1:decode fpga result; 0: do not decode

fs = 2048; % sample frequency (Hz)
num_samples = 32768; % signal size in samples (256, 512, 1024, etc)
%t = linspace(0, 2*pi, 512);  % Time vector 
t = 0:1/fs:num_samples/fs-(1/fs); % span time vector 
%x = sin(2*pi*5*t) + 1i*cos(2*pi*10*t);  % Example signal with both real and imaginary components 
xRe = sin(2*pi*60*t);    % signal at \z
xIm = cos(2*pi*102*t);    % signal at 10 Hz
x = xRe + 1i*xIm; % Example signal with both real and imaginary components 

%ler o input e gerar a fft esperada
 %file_input = fopen('input_ip.txt','r');
% input_ip = textread('input_ip.txt', '%s');

% Compute the Fourier transform 
%fft_input = fft(input_ip); 
% Take the real and imaginary parts of the Fourier transform 
%yRe_input = real(fft_input); 
%yIm_input = imag(fft_input); 

%figure; 
%subplot(2,1,1); 
%plot(t, fft_input); 
%xlabel('Time'); 
%ylabel('Real part'); 
%title('Real part of signal in time domain'); 
%%%% 

%ler o output do vivado e plotar a fft gerada
 %file_output = fopen('output_ip.txt','r');
 %output_ip = textread('output_ip.txt', '%s');

%yRe_input = real(output_ip); 
%yIm_input = imag(output_ip); 

%figure; 
%subplot(2,1,1); 
%plot(t, output_ip); 
%xlabel('Time'); 
%ylabel('Real part'); 
%title('Real part of signal in time domain'); 
%%%% 


figure; 
subplot(2,1,1); 
plot(t, xRe); 
xlabel('Time'); 
ylabel('Real part'); 
title('Real part of signal in time domain'); 
subplot(2,1,2); 
plot(t, xIm); 
xlabel('Time'); 
ylabel('Imaginary part'); 
title('Imaginary part of signal in time domain'); 

% Compute the Fourier transform 
y = fft(x); 
% Take the real and imaginary parts of the Fourier transform 
yRe = real(y); 
yIm = imag(y); 

% Plot the real and imaginary parts 
n = length(x);          % number of samples
f = (0:n-1)*(fs/n);     % frequency range
faxis = fs*(0:1/(n-1):1);
figure; 
subplot(2,1,1); 
plot(f, yRe); 
xlabel('Freq'); 
ylabel('Real part'); 
title('Real part of Fourier Transform'); 
subplot(2,1,2); 
plot(f, yIm); 
xlabel('Freq'); 
ylabel('Imaginary part'); 
title('Imaginary part of Fourier Transform'); 

if create_file==1
    file = fopen('fft_512_input.txt','w');
    xRe_int16 = round((2^15-32)*(xRe/max(xRe)));
    xIm_int16 = round((2^15-32)*(xIm/max(xIm)));
    for i=1:n
        fprintf(file,'%d\n',xRe_int16(i));   
        fprintf(file,'%d\n',xIm_int16(i));   
    end
    fclose(file);
    file = fopen('fft_512_expected_output.txt','w');
    yRe_int16 = round((2^15-32)*(yRe/max(yRe)));
    yIm_int16 = round((2^15-32)*(yIm/max(yIm)));
    for i=1:n
        fprintf(file,'%d\n',yRe_int16(i));   
        fprintf(file,'%d\n',yIm_int16(i));   
    end
    fclose(file);    
end

if decode_result == 1
    hw_out_str=textread('fft_512_out.txt', '%s');
    sw_out_str=textread('fft_512_expected_output.txt', '%s');
    hw_out = cellfun(@str2num,hw_out_str)/(2^15-32);
    sw_out = cellfun(@str2num,sw_out_str)/(2^15-32);
    yRe_hw = zeros(1,n);
    yIm_hw = zeros(1,n);
    yRe_sw = zeros(1,n);
    yIm_sw = zeros(1,n);
    k=length(sw_out);
    
    for i=1:n
        yRe_hw(n+1-i) = hw_out(2*i-1);  % output in reverse order 
        yRe_sw(i) = sw_out(2*i-1);
        yIm_hw(n+1-i) = hw_out(2*i);    % output in reverse order 
        yIm_sw(i) = sw_out(2*i);
    end
    yhw = yRe_hw.^2 + yIm_hw.^2; 
    ysw = yRe_sw.^2 + yIm_sw.^2;
    
    yhw = 10*log(yhw/max(yhw));
    ysw = 10*log(ysw/max(ysw));
    figure; 
    plot(faxis/2, yRe_hw,'-k'); % IP-core applied a scaling factor of 2
    hold on
    plot(faxis, yRe_sw,'-r'); 
    xlabel('Freq'); 
    ylabel('dB'); 
    title('Real part of Fourier Transform'); 
    

end