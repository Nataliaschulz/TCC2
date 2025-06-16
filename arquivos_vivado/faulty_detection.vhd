----------------------------------------------------------------------------------
-- Company: University of Bras�lia
-- Engineer: Nat�lia Schulz Teixeira
-- 
-- Create Date: 02/14/2025 03:53:47 PM
-- Module Name: faulty_detection - Behavioral
-- Project Name: Implementa��o de Modelo para Detec��o de Falhas em M�quinas Rotativas com FPGA
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity faulty_detection is
    Port (
        clk          : in  STD_LOGIC;
        resetn       : in  STD_LOGIC;
        fft_data     : in  STD_LOGIC_VECTOR(31 downto 0);  -- Dados de sa�da da FFT
        fft_valid    : in  STD_LOGIC;                      -- Sinal de valida��o dos dados da FFT
        fft_last     : in  STD_LOGIC;                      -- Sinal de �ltimo dado da FFT
        threshold    : in  STD_LOGIC_VECTOR(15 downto 0);  -- Limiar para detec��o de pico
        led_fault    : out STD_LOGIC                       -- LED que indica falha
    );
end faulty_detection;

architecture Behavioral of faulty_detection is

    -- Constantes para a faixa de frequ�ncia de 22 kHz a 40 kHz
    constant FREQ_LOW  : integer := 22000;  -- 22 kHz
    constant FREQ_HIGH : integer := 40000;  -- 40 kHz

    -- Constante para o tempo de 5 segundos
    constant TIMER_5S  : integer := 500000000;  -- 5 segundos em ciclos de clock (assumindo 100 MHz)

    -- Sinais internos
    signal magnitude  : unsigned(15 downto 0) := (others => '0');  -- Magnitude da frequ�ncia
    signal frequency  : integer := 0;           -- Frequ�ncia atual
    signal fault_flag : STD_LOGIC := '0';       -- Flag para indicar falha
    signal timer      : integer := 0;           -- Contador de tempo
    signal led_state  : STD_LOGIC := '0';       -- Estado do LED
    signal threshold_int    : STD_LOGIC_VECTOR(15 downto 0);  -- Limiar para detec��o de pico

    
begin

    process(clk, resetn)
    begin
        if resetn = '0' then
            magnitude <= (others => '0');
            frequency <= 0;
            fault_flag <= '0';
            led_state <= '0';
            timer <= 0;
        elsif rising_edge(clk) then
            if fft_valid = '1' then
                -- Extrai a magnitude do dado da FFT (assumindo que os 16 bits mais significativos s�o a parte real)
                magnitude <= unsigned(fft_data(31 downto 16));

                -- Verifica se a frequ�ncia atual est� na faixa desejada
                if frequency >= FREQ_LOW and frequency <= FREQ_HIGH then
                    -- Verifica se a magnitude est� acima do limiar
                    if magnitude > unsigned(threshold) then
                        fault_flag <= '1';  -- Ativa a flag de falha
                    end if;
                end if;

                -- Incrementa a frequ�ncia para o pr�ximo dado
                frequency <= frequency + 1;

                -- Reseta a frequ�ncia quando o �ltimo dado � recebido
                if fft_last = '1' then
                    frequency <= 0;
                    if fault_flag = '1' then
                        led_state <= '1';  -- Acende o LED
                        timer <= 0;        -- Reseta o contador de tempo
                    end if;
                    fault_flag <= '0';    -- Reseta a flag de falha
                end if;
            end if;

            -- Controle do tempo que o LED fica aceso
            if led_state = '1' then
                if timer < TIMER_5S then
                    timer <= timer + 1;  -- Incrementa o contador
                else
                    led_state <= '0';   -- Desliga o LED ap�s 5 segundos
                end if;
            end if;
        end if;
    end process;

    -- Atribui o estado do LED ao sinal de sa�da
    led_fault <= led_state;

end Behavioral;