----------------------------------------------------------------------------------
-- Company: University of Brasília
-- Engineer: Natália Schulz Teixeira
-- 
-- Create Date: 02/14/2025 03:53:47 PM
-- Module Name: faulty_detection - Behavioral
-- Project Name: Implementação de Modelo para Detecção de Falhas em Máquinas Rotativas com FPGA
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity top_module is
    Port (
        clk   : in  STD_LOGIC;
        resetn : in  STD_LOGIC;
--        m_axis_data_tready : in  STD_LOGIC; -- interno
--        m_axis_data_tvalid : out STD_LOGIC;
--        m_axis_data_tdata  : out STD_LOGIC_VECTOR(31 downto 0);
--        m_axis_data_tlast  : out STD_LOGIC;
--        s_axis_data_tready   : out STD_LOGIC;  -- Alterado para 'out'
        start : in STD_LOGIC;  -- Sinal para iniciar a configuração da FFT
        auxtready : out STD_LOGIC;  -- Sinal auxiliar para tready
        led : out STD_LOGIC  -- Sinal auxiliar para tready
    );
end top_module;

architecture Behavioral of top_module is

    signal s_axis_data_tvalid_int : STD_LOGIC;  -- Sinal interno para tvalid
    signal s_axis_data_tdata_int  : STD_LOGIC_VECTOR(31 downto 0);  -- Sinal interno para tdata
    signal s_axis_data_tlast_int  : STD_LOGIC :='0';  -- Sinal interno para tlast
    signal s_axis_config_tvalid_int  : STD_LOGIC :='0';  -- Sinal interno para tlast
    signal s_axis_data_tready_int : STD_LOGIC;  -- Sinal interno para tready
    signal tlast_memory : STD_LOGIC:='0';  -- Sinal interno para tready
    signal start_int : STD_LOGIC;  -- Sinal interno para start
    
    -- Sinais internos para configuração da FFT
    signal s_axis_config_tdata_int  : STD_LOGIC_VECTOR(31 downto 0);  -- Sinal interno para tdata    signal s_axis_config_tvalid_int : STD_LOGIC;  -- Sinal interno para tvalid
    signal s_axis_config_tready_int : STD_LOGIC;  -- Sinal interno para tready 
    signal config_reg : STD_LOGIC_VECTOR(11 downto 0) := (others => '0');
    signal log2nFFT   : STD_LOGIC_VECTOR(3 downto 0) := (others => '0');
    signal FWD        : STD_LOGIC_VECTOR(4 downto 0) := "10000";  -- FFT
    signal INV        : STD_LOGIC_VECTOR(4 downto 0) := "00000";  -- IFFT 
    
       -- Sinais para configuração da FFT
    signal event_frame_started  : STD_LOGIC;
    signal event_tlast_unexpected  : STD_LOGIC;
    signal event_tlast_missing   : STD_LOGIC;
    signal event_status_channel_halt         : STD_LOGIC;
    signal event_data_in_channel_halt : STD_LOGIC;
    signal event_data_out_channel_halt : STD_LOGIC;
  
      -- Sinais para saida da FFT
    signal m_axis_data_tdata_int : STD_LOGIC_VECTOR(31 downto 0);
    signal m_axis_data_tvalid :  STD_LOGIC;
    signal m_axis_data_tdata  :  STD_LOGIC_VECTOR(31 downto 0);
    signal m_axis_data_tlast  :  STD_LOGIC;
    signal s_axis_data_tready   :  STD_LOGIC;
    signal m_axis_data_tready   :  STD_LOGIC;

    
    -- Sinal para o limiar
    signal threshold : STD_LOGIC_VECTOR(15 downto 0) := x"7FFF"; 
  
    -- Sinais adicionais
    signal lock : STD_LOGIC := '0';  -- Sinal de lock para controle de configuração

    -- Componente datasrc
    component datasrc
        Port (
            clk    : in  STD_LOGIC;
            resetn : in  STD_LOGIC;
            tready : in  STD_LOGIC;
            start : in  STD_LOGIC;
            tvalid : out STD_LOGIC;
            tlast : out STD_LOGIC;
            tdata  : out STD_LOGIC_VECTOR(31 downto 0)
        );
    end component;

    -- Componente FFT (substitua pelo nome correto do seu IP FFT)
    component xfft_0
        Port (
            -- Interface de entrada de dados (S_AXIS_DATA)
            s_axis_data_tdata  : in  STD_LOGIC_VECTOR(31 downto 0);
            s_axis_data_tlast  : in  STD_LOGIC;
            s_axis_data_tready : out STD_LOGIC;
            s_axis_data_tvalid : in  STD_LOGIC;
            s_axis_config_tdata  : in  STD_LOGIC_VECTOR(31 downto 0);
            s_axis_config_tready : out STD_LOGIC;
            s_axis_config_tvalid : in  STD_LOGIC;
            m_axis_data_tdata  : out STD_LOGIC_VECTOR(31 downto 0);
            m_axis_data_tlast  : out STD_LOGIC;
            m_axis_data_tready : in  STD_LOGIC;
            m_axis_data_tvalid : out STD_LOGIC;
            aclk    : in  STD_LOGIC;
            aresetn : in  STD_LOGIC;
            event_frame_started : out STD_LOGIC;
            event_tlast_unexpected : out STD_LOGIC;
            event_tlast_missing : out STD_LOGIC;
            event_status_channel_halt : out STD_LOGIC;
            event_data_in_channel_halt : out STD_LOGIC;
            event_data_out_channel_halt : out STD_LOGIC
        );
    end component;
    
    component faulty_detection is
        Port (
            clk          : in  STD_LOGIC;
            resetn       : in  STD_LOGIC;
            fft_data     : in  STD_LOGIC_VECTOR(31 downto 0);  -- Dados de saída da FFT
            fft_valid    : in  STD_LOGIC;                      -- Sinal de validação dos dados da FFT
            fft_last     : in  STD_LOGIC;                      -- Sinal de último dado da FFT
            led_fault    : out STD_LOGIC;                       -- LED que indica falha
            threshold    : in  STD_LOGIC_VECTOR(15 downto 0)  -- Limiar para detecção de pico
        );
    end component;
    
    component ila_0
        port (
            clk    : in STD_LOGIC;
            probe0 : in STD_LOGIC_VECTOR(31 downto 0);  -- m_axis_data_tdata_int
            probe1 : in STD_LOGIC;                      -- m_axis_data_tvalid_int
            probe2 : in STD_LOGIC;                      -- m_axis_data_tlast_int
            probe3 : in STD_LOGIC                       -- s_axis_data_tready_int
        );
    end component;

begin

    -- Instanciação do datasrc
    datasrc_inst : datasrc
        Port map (
            clk    => clk,
            start => start_int,
            resetn => resetn,
            tready => s_axis_data_tready_int,  -- Conecta ao sinal interno tready
            tvalid => s_axis_data_tvalid_int,  -- Conecta ao sinal interno tvalid
            tdata  => s_axis_data_tdata_int,    -- Conecta ao sinal interno tdata
            tlast => tlast_memory
        );

    -- Instanciação do FFT IP
    xfft_0_inst : xfft_0
        Port map (
            -- Interface de entrada de dados
            s_axis_data_tdata  => s_axis_data_tdata_int,  -- Conecta ao sinal interno tdata
            s_axis_data_tlast  => s_axis_data_tlast_int,  -- Conecta ao sinal interno tlast
            s_axis_data_tready => s_axis_data_tready,  -- Conecta ao sinal interno tready
            s_axis_data_tvalid => s_axis_data_tvalid_int,  -- Conecta ao sinal interno tvalid
            s_axis_config_tdata  => s_axis_config_tdata_int,  -- Conecta ao sinal interno tdata
            s_axis_config_tready => s_axis_config_tready_int,  -- Conecta ao sinal interno tready
            s_axis_config_tvalid => s_axis_config_tvalid_int,  -- Conecta ao sinal interno tvalid
            m_axis_data_tdata  => m_axis_data_tdata,
            m_axis_data_tlast  => m_axis_data_tlast,
            m_axis_data_tready => m_axis_data_tready,
            m_axis_data_tvalid => m_axis_data_tvalid,
            aclk    => clk,
            aresetn => resetn,
            event_frame_started => event_frame_started,
            event_tlast_unexpected => event_tlast_unexpected,
            event_tlast_missing => event_tlast_missing,
            event_status_channel_halt => event_status_channel_halt,
            event_data_in_channel_halt => event_data_in_channel_halt,
            event_data_out_channel_halt => event_data_out_channel_halt
        );
        
--        -- Instanciação do indicador de falha
        faulty_detection_inst : faulty_detection
            Port map (
                clk       => clk,
                resetn    => resetn,
                fft_data  => m_axis_data_tdata,
                fft_valid => m_axis_data_tvalid,
                fft_last  => m_axis_data_tlast,
                threshold => threshold,
                led_fault => led  -- Conecte ao pino do LED no top level
             );
             
        ila_inst : ila_0
            port map (
                clk    => clk,
                probe0 => m_axis_data_tdata_int,  -- Conecte ao sinal intermediário
                probe1 => m_axis_data_tvalid,
                probe2 => m_axis_data_tlast,
                probe3 => s_axis_data_tready_int
        );

    -- Conecta o sinal interno tready ao sinal de saída
--    s_axis_data_tready <= s_axis_data_tready_int;
    
    start_int <= start;
  
    process(clk, resetn)
    begin
        if resetn = '0' then
            auxtready <= '0';
            lock <= '0';
            s_axis_config_tdata_int <= (others => '0');
            s_axis_config_tvalid_int <= '0';
            s_axis_data_tlast_int <= '0';
        elsif rising_edge(clk) then
            s_axis_config_tvalid_int <= '0';
--            if start_int = '1' and s_axis_config_tready_int = '1' and lock = '0' then
            if start_int = '1' and lock = '0' then
                s_axis_config_tdata_int <= "00000000" & "000" & "10101010101010" & FWD & "01111"; -- 010101010101010100001110 -- 24 bits tirei um zero de 000110101010
                s_axis_config_tvalid_int <= '1';
                lock <= '1';
            end if;

            if lock = '1' then
                s_axis_data_tready_int <= '1';
                auxtready <= '1';
            end if;

--            if s_axis_data_tlast_int = '1' then
            if tlast_memory = '1' then
                s_axis_data_tready_int <= '0';
                lock <= '0';
            end if;
        end if;
    end process;

end Behavioral;