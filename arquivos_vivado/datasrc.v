`timescale 1ns / 1ps

module datasrc(
    input clk, 
    input start,          // Sinal de start para iniciar a leitura e envio de dados.
    input resetn,
    input tready,
    output tvalid,
    output [31:0] tdata,
    output tlast
);

    parameter infile = "input_sinal_tempo.mem";
    
    reg [31:0] mem[0:32767];  // Memória com 32768 posições (0 a 32767)
    localparam s0 = 'd0;      // Estado inicial (aguardando start).
    localparam s1 = 'd1;      // Estado de leitura e preparação dos dados.
    localparam s2 = 'd2;      // Estado de envio dos dados.
    localparam s3 = 'd3;      // Estado de espera (quando tready = 0).

    reg [2:0] state, n_state;
    reg [14:0] addr, n_addr;  // Endereço de 15 bits para suportar 32768 posições
    reg [31:0] d0, d1, d2, n_d1, n_d2;
    reg valid, n_valid;
    reg tlast_reg;            // Registro para armazenar o valor de tlast

    initial begin
        $readmemh(infile, mem);  // Inicializa a memória com os dados do arquivo
        state = s0;               // Inicializa o estado
        addr = 'd0;               // Inicializa o endereço
        d0 = 'd0;                // Inicializa os registradores de dados
        d1 = 'd0;
        d2 = 'd0;
        valid = 0;               // Inicializa o sinal de validade
        tlast_reg = 0;           // Inicializa tlast_reg
    end

    assign tvalid = valid;
    assign tdata = d2;
    assign tlast = tlast_reg;  // Atribui o valor de tlast_reg ao sinal tlast

    always @(posedge clk) begin 
        if (~resetn) begin
            state <= s0;
            addr <= 'd0;
            d0 <= 'd0;
            d1 <= 'd0;
            d2 <= 'd0;
            valid <= 0;
            tlast_reg <= 0;    // Inicializa tlast_reg com 0
        end else begin
            state <= n_state;
            addr <= n_addr;
            d0 <= mem[n_addr]; // Carrega o próximo dado da memória
            d1 <= n_d1;
            d2 <= n_d2;
            valid <= n_valid;
            tlast_reg <= (n_addr == 32767) ? 1'b1 : 1'b0;  // Atualiza tlast_reg
        end
    end

    always @(*) begin
        // Defaults
        n_d1 = d1;
        n_d2 = d2;
        n_state = state;
        n_addr = addr;
        n_valid = valid;
        
        // Lógica de transição de estados
        case(state)
            s0: begin
                n_addr = 'd0;          // Reinicia o endereço para o início da memória.
                n_valid = 0;           // Desativa o sinal de validade.
                if (start) begin       // Aguarda o sinal de start para prosseguir.
                    n_state = s1;      // Avança para o estado s1.
                end else begin
                    n_state = s0;      // Permanece no estado s0 até que start seja ativado.
                end
            end
            s1: begin
                n_d1 = d0;             // Carrega o próximo dado (d0) em n_d1.
                n_addr = addr + 1;     // Incrementa o endereço para apontar para o próximo dado na memória.
                n_state = s2;          // Define o próximo estado como s2.
                n_valid = 1;           // Ativa o sinal de validade (n_valid = 1).
            end
            s2: begin
                n_d1 = d0;             // Carrega o próximo dado (d0) em n_d1.
                n_d2 = d1;             // Carrega o dado atual (d1) em n_d2 (dado a ser enviado).
                n_valid = 1;           // Mantém o sinal de validade ativo (n_valid = 1).
                if (tready) begin      // Se o receptor estiver pronto (tready = 1):
                    if (addr == 32767) begin // Verifica se o endereço atual é o último (32767).
                        n_state = s0;  // Retorna ao estado inicial após o último dado.
                    end else begin
                        n_addr = addr + 1; // Incrementa o endereço para o próximo dado.
                        n_state = s2;  // Mantém o estado como s2 para enviar o próximo dado.
                    end
                end else begin         // Se o receptor não estiver pronto (tready = 0):
                    n_state = s3;      // Muda para o estado s3 para esperar.
                end
            end
            s3: begin 
                if (tready) begin      // Se o receptor estiver pronto (tready = 1):
                    n_addr = addr + 1; // Incrementa o endereço para o próximo dado.
                    n_state = s2;      // Volta para o estado s2 para enviar o próximo dado.
                end else begin         // Se o receptor não estiver pronto (tready = 0):
                    n_state = s3;      // Permanece no estado s3, esperando.
                end
            end
            default: begin 
                n_state = s0;         // Retorna ao estado inicial s0.
            end
        endcase
    end
endmodule