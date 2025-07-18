# LLM‑Finance Analyzer & Dashboard

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-orange)

Automatize a **classificação de transações bancárias** com Large Language Models (LLM) da **Groq** e visualize tudo num **dashboard interativo (Streamlit)** em apenas dois comandos.

---

## ✨ Principais Recursos

| Pilar | Valor para o negócio |
|-------|---------------------|
| **Classificação inteligente** | Reduz horas de trabalho manual e minimiza erros na categorização de despesas |
| **Visual Analytics** | Facilita decisões de custo × receita com gráficos de tendência e métricas resumidas |
| **Arquitetura modular** | Permite adicionar novos extratores de PDF, LLMs ou painéis sem reescrever o core |
| **Rate limiting automático** | Otimiza custos de API (paga ou gratuita) |

---

## 📂 Estrutura do Projeto

```text
.
├── extratos/                 # PDFs do banco
├── templates/                # Prompts & categorias customizadas
├── finances.csv              # Saída padrão (transações + categoria)
├── main.py                   # **Fase 1:** Classificação CLI
├── dash.py                   # **Fase 2:** Dashboard Streamlit
├── pdf_to_pandas.py          # Parser de extratos em PDF (testado apenas com o Itaú)
├── expense_classifier.py     # Classe de interface com LLM
├── financial_tab.py          # Componentes específicos da análise financeira avançada
├── config.py | template_manager.py
└── requirements.txt
```

---

## ⚡️ Instalação Rápida

```bash
# 1. Clone e entre no diretório
git clone https://github.com/lukemariano/llm-finance-analyzer.git
cd llm-finance-analyzer

# 2. (Opcional) Crie um ambiente virtual e instale dependências
python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip3 install -r requirements.txt

# 3. Configure variáveis de ambiente
cp .env.example .env && nano .env
```

---

## 🏃‍♂️ Execução em 2 Passos

| Passo | Comando | O que acontece? |
|-------|---------|-----------------|
| **1. Classificar** | `python3 main.py` | Gera/atualiza `finances.csv` com a coluna `category` |
| **2. Visualizar** | `streamlit run dash.py` | Abre o dashboard em <http://localhost:8501> |

> Use `python3 main.py -h` para listar todas as opções (template, rate limit, diretórios, etc.).

---

## 🔧 Configuração (.env)

```env
# --- Groq ---
GROQ_API_KEY=YOUR_KEY_HERE
LLM_MODEL=llama3-70b-8192          # opcional

# --- Rate Limiting ---
USE_RATE_LIMIT=true
RATE_LIMIT_BATCH_SIZE=30
RATE_LIMIT_SLEEP_TIME=60

# --- Arquivos & Diretórios ---
EXTRATOS_DIR=extratos
OUTPUT_FILE=finances.csv
TEMPLATE_FILE=templates/default_template.txt
CATEGORIES_FILE=templates/categories.json
```

---

## 🖼️ Screenshots

<p align="center">
  <img src="docs/img/dashboard_overview.png" width="700">
  <br><em>Visão geral dos gastos por categoria e tendência temporal.</em>
</p>

---

## 🗂️ APIs Internas (exemplo)

```python
from expense_classifier import ExpenseClassifier
from config import Config
import pandas as pd

cfg = Config()
clf = ExpenseClassifier(cfg)

df = pd.read_csv("extratos/meu_banco.csv")
resultado = clf.process_dataframe(df)
```

---

## ❓ FAQ & Troubleshooting

| Erro/Sintoma | Possível causa | Solução rápida |
|--------------|----------------|----------------|
| `GROQ_API_KEY not found` | `.env` ausente ou variável incorreta | `cp .env.example .env` e preencha corretamente |
| Classificações inesperadas | Template genérico demais | Ajuste `templates/categories.json` ou `default_template.txt` |
| Rate limit atingido | Plano gratuito Groq | Mantenha `USE_RATE_LIMIT=true` ou migre para plano pago |

---

## 📄 Licença

Distribuído sob licença **MIT** – veja `LICENSE`.

---

### Roadmap Futuro

- [ ] Possibilitar importar extratos pela UI
- [ ] Deploy 1‑click no Streamlit Community Cloud
- [ ] Suporte a múltiplas contas bancárias
