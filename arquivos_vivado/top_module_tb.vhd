library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;
use IEEE.STD_LOGIC_TEXTIO.ALL;

entity top_module_tb is
end top_module_tb;

architecture Behavioral of top_module_tb is

    -- Constants
    constant CLOCK_PERIOD : time := 10 ns;
    constant T_HOLD      : time := 1 ns;

    -- Signals
    signal clk   : STD_LOGIC := '0';
    signal resetn : STD_LOGIC := '0';
    signal m_axis_data_tready : STD_LOGIC := '0';  -- Inicialmente em '0'
    signal m_axis_data_tvalid : STD_LOGIC;
    signal m_axis_data_tdata  : STD_LOGIC_VECTOR(31 downto 0);
    signal m_axis_data_tlast  : STD_LOGIC;
    signal event_frame_started : STD_LOGIC;
    signal event_tlast_unexpected : STD_LOGIC;
    signal event_tlast_missing : STD_LOGIC;
    signal event_status_channel_halt : STD_LOGIC;
    signal event_data_in_channel_halt : STD_LOGIC;
    signal event_data_out_channel_halt : STD_LOGIC;

    -- Signals for FFT configuration and data input
    signal s_axis_config_tdata  : STD_LOGIC_VECTOR(23 downto 0) := (others => '0');
    signal s_axis_config_tvalid : STD_LOGIC := '0';
    signal s_axis_config_tready : STD_LOGIC;
--    signal s_axis_data_tdata    : STD_LOGIC_VECTOR(31 downto 0) := (others => '0');
    signal s_axis_data_tvalid   : STD_LOGIC := '0';
    signal s_axis_data_tready   : STD_LOGIC;
    signal lock   : STD_LOGIC := '0';
    signal s_axis_data_tlast    : STD_LOGIC := '0';

    -- Sinal start
    signal start : STD_LOGIC := '0';  -- Sinal para iniciar a configuração da FFT

    -- File handles
    file input_file : TEXT;
    file output_file : TEXT;

    component top_module
        Port (
            clk   : in  STD_LOGIC;
            resetn : in  STD_LOGIC;
            m_axis_data_tready : in  STD_LOGIC;
            m_axis_data_tvalid : out STD_LOGIC;
            m_axis_data_tdata  : out STD_LOGIC_VECTOR(31 downto 0);
            m_axis_data_tlast  : out STD_LOGIC;
            s_axis_data_tready   : out STD_LOGIC;
            start : in STD_LOGIC  -- Sinal para iniciar a configuração da FFT
        );
    end component;

    function to_hex_string(slv : std_logic_vector) return string is
        variable hex_length : natural := (slv'length + 3) / 4;
        variable result : string(1 to hex_length);
        variable temp : std_logic_vector(3 downto 0);
    begin
        for i in 0 to hex_length - 1 loop
            temp := slv((i * 4) + 3 downto i * 4); -- Extrai 4 bits do vetor slv começando na posição i * 4
            case temp is
                when "0000" => result(hex_length - i) := '0';
                when "0001" => result(hex_length - i) := '1';
                when "0010" => result(hex_length - i) := '2';
                when "0011" => result(hex_length - i) := '3';
                when "0100" => result(hex_length - i) := '4';
                when "0101" => result(hex_length - i) := '5';
                when "0110" => result(hex_length - i) := '6';
                when "0111" => result(hex_length - i) := '7';
                when "1000" => result(hex_length - i) := '8';
                when "1001" => result(hex_length - i) := '9';
                when "1010" => result(hex_length - i) := 'A';
                when "1011" => result(hex_length - i) := 'B';
                when "1100" => result(hex_length - i) := 'C';
                when "1101" => result(hex_length - i) := 'D';
                when "1110" => result(hex_length - i) := 'E';
                when "1111" => result(hex_length - i) := 'F';
                when others => result(hex_length - i) := 'X';
            end case;
        end loop;
        return result;
    end function;

begin

--    clk_process: process
--    begin
--        while now < 50000 ns loop  
--            clk <= '0';
--            wait for CLOCK_PERIOD / 2;
--            clk <= '1';
--            wait for CLOCK_PERIOD / 2;
--        end loop;
--        wait;
--    end process;
    clk <= not clk after 5ns;


    reset_process: process
    begin
        resetn <= '0';  
        wait for 100 ns;
        resetn <= '1';  
        wait;
    end process;


    m_axis_data_tready <= '1' when (m_axis_data_tvalid = '1') else '0';

    -- Instantiate the top_module
    uut: top_module
        Port map (
            clk   => clk,
            resetn => resetn,
            m_axis_data_tready => m_axis_data_tready,
            m_axis_data_tvalid => m_axis_data_tvalid,
            m_axis_data_tdata  => m_axis_data_tdata,
            m_axis_data_tlast  => m_axis_data_tlast,
            s_axis_data_tready   => s_axis_data_tready,
            start => start
        );

    config_process: process
    begin
        report "Entrou na configuracao da fft" severity note;
        wait until resetn = '1';  
        wait for CLOCK_PERIOD;
        start <= '1';
        wait for CLOCK_PERIOD;
        start <= '0';
    end process;


    -- Output process
    output_process: process
        variable output_line : LINE;
        variable output_file_status : FILE_OPEN_STATUS;
    begin
        -- Open the output file
        file_open(output_file_status, output_file, "fft_512_output.txt", WRITE_MODE);
        if output_file_status /= OPEN_OK then
            report "Failed to open output file" severity failure;
        end if;

        -- Wait for valid output data
        wait until m_axis_data_tvalid = '1';

        -- Write output data to the file
        while m_axis_data_tlast = '0' loop --  while m_axis_data_tvalid = '1' loop
            report "Entrou aqui pra escrever os dados txt" severity note;
            write(output_line, to_hex_string(m_axis_data_tdata)); -- Use custom function
            writeline(output_file, output_line);
            wait until rising_edge(clk);
        end loop;

        file_close(output_file);

        wait;
    end process;

end Behavioral;