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
    
    reg [31:0] mem[0:32767];  // Mem�ria com 32768 posi��es (0 a 32767)
    localparam s0 = 'd0;      // Estado inicial (aguardando start).
    localparam s1 = 'd1;      // Estado de leitura e prepara��o dos dados.
    localparam s2 = 'd2;      // Estado de envio dos dados.
    localparam s3 = 'd3;      // Estado de espera (quando tready = 0).

    reg [2:0] state, n_state;
    reg [14:0] addr, n_addr;  // Endere�o de 15 bits para suportar 32768 posi��es
    reg [31:0] d0, d1, d2, n_d1, n_d2;
    reg valid, n_valid;
    reg tlast_reg;            // Registro para armazenar o valor de tlast

    initial begin
        $readmemh(infile, mem);  // Inicializa a mem�ria com os dados do arquivo
        state = s0;               // Inicializa o estado
        addr = 'd0;               // Inicializa o endere�o
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
            d0 <= mem[n_addr]; // Carrega o pr�ximo dado da mem�ria
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
        
        // L�gica de transi��o de estados
        case(state)
            s0: begin
                n_addr = 'd0;          // Reinicia o endere�o para o in�cio da mem�ria.
                n_valid = 0;           // Desativa o sinal de validade.
                if (start) begin       // Aguarda o sinal de start para prosseguir.
                    n_state = s1;      // Avan�a para o estado s1.
                end else begin
                    n_state = s0;      // Permanece no estado s0 at� que start seja ativado.
                end
            end
            s1: begin
                n_d1 = d0;             // Carrega o pr�ximo dado (d0) em n_d1.
                n_addr = addr + 1;     // Incrementa o endere�o para apontar para o pr�ximo dado na mem�ria.
                n_state = s2;          // Define o pr�ximo estado como s2.
                n_valid = 1;           // Ativa o sinal de validade (n_valid = 1).
            end
            s2: begin
                n_d1 = d0;             // Carrega o pr�ximo dado (d0) em n_d1.
                n_d2 = d1;             // Carrega o dado atual (d1) em n_d2 (dado a ser enviado).
                n_valid = 1;           // Mant�m o sinal de validade ativo (n_valid = 1).
                if (tready) begin      // Se o receptor estiver pronto (tready = 1):
                    if (addr == 32767) begin // Verifica se o endere�o atual � o �ltimo (32767).
                        n_state = s0;  // Retorna ao estado inicial ap�s o �ltimo dado.
                    end else begin
                        n_addr = addr + 1; // Incrementa o endere�o para o pr�ximo dado.
                        n_state = s2;  // Mant�m o estado como s2 para enviar o pr�ximo dado.
                    end
                end else begin         // Se o receptor n�o estiver pronto (tready = 0):
                    n_state = s3;      // Muda para o estado s3 para esperar.
                end
            end
            s3: begin 
                if (tready) begin      // Se o receptor estiver pronto (tready = 1):
                    n_addr = addr + 1; // Incrementa o endere�o para o pr�ximo dado.
                    n_state = s2;      // Volta para o estado s2 para enviar o pr�ximo dado.
                end else begin         // Se o receptor n�o estiver pronto (tready = 0):
                    n_state = s3;      // Permanece no estado s3, esperando.
                end
            end
            default: begin 
                n_state = s0;         // Retorna ao estado inicial s0.
            end
        endcase
    end
endmodule