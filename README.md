# Last Mile SLA Intelligence - Geografia

## Como rodar

1. Extraia o ZIP.
2. Coloque a planilha Excel na mesma pasta do `app.py`.
   - Recomendado: `dashboard_base_com_geografia.xlsx`
   - O app também aceita upload manual pela tela.
3. Instale as dependências:
```bash
python -m pip install -r requirements.txt
```
4. Rode:
```bash
python -m streamlit run app.py
```

## Principais melhorias

- Filtro global de `geografia_comercial`.
- Geografia adicionada nas principais análises.
- NS geral = Antecipado + No Prazo.
- Cores condicionais para desempenho:
  - Verde: performance muito alta.
  - Azul: boa performance.
  - Amarelo: atenção.
  - Vermelho: risco.
- Correção e padronização de Modal: COURIER, RODO, MICRO.
