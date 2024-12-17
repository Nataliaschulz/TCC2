# TCC 2 - Análise de Vibração de Mancal de Máquinas Rotativas

Este projeto realiza uma análise de vibração em mancais de máquinas rotativas, utilizando modelos baseados em sinais de aceleração no tempo e no domínio da frequência. O objetivo principal é identificar e comparar condições de funcionamento "Saudável" e com "Falha" por meio de métricas como FFT, Transformada de Hilbert, RMS e PSD.

## Estrutura do Código

O código principal realiza as seguintes etapas:
1. **Carregamento dos Dados:** Leitura de arquivos contendo séries temporais de aceleração.
2. **Processamento dos Dados:** 
   - Transformada de Hilbert para cálculo do envelope do sinal.
   - Cálculo da FFT para identificar frequências predominantes.
   - Filtragem de harmônicas em torno da frequência fundamental e suas múltiplas.
3. **Cálculo de Métricas:**
   - **RMS (Root Mean Square):** Mede a energia do sinal em frequências específicas.
   - **EQM (Erro Quadrático Médio):** Compara a diferença entre espectros de frequência.
   - **MAE (Erro Médio Absoluto):** Outra métrica para comparação de espectros.
4. **Análise Gráfica:**
   - Sinal no tempo.
   - Sinal envelope (Hilbert).
   - FFT (domínio da frequência).
   - PSD (Densidade Espectral de Potência).

## Pré-requisitos

Certifique-se de ter instalado as seguintes dependências no ambiente Python:
- `numpy`
- `plotly`
- `scipy`

Para instalar as dependências, use:
```bash
pip install numpy plotly scipy
