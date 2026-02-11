# 🏥 Smart Triage System (STS) - Automação de Triagem Hospitalar

**Status:** ✅ Concluído | **Nível:** Pleno | **Sprint:** 1 Semana

## 🔎 Visão Geral
Este projeto soluciona o problema de superlotação em prontos-socorros automatizando a triagem de pacientes. O sistema utiliza Python para capturar dados em tempo real, processar informações clínicas conforme o **Protocolo de Manchester** e integrar os resultados com um Dashboard no Power BI.

O objetivo é garantir que casos graves sejam priorizados, eliminando falhas manuais e agilizando o atendimento.

---

## 👥 Desenvolvedores
Projeto desenvolvido em grupo pela equipe:
* **Kamilly da Silva Araujo** (Power BI, Dashboard, Documentação e Publicação no GitHub)
* **Batista Dala Catumba** (Python, Lógica de Classificação e Integração com SQLite)
* **Marina Pocheca Matos** (Apresentação Final e Comunicação dos Resultados)

---

## 🔄 Fluxo do Projeto (Pipeline)
1.  **Monitoramento:** O script Python (com Playwright) vigia o totem de autoatendimento web 24/7.
2.  **Detecção:** Identifica novos registros de pacientes instantaneamente.
3.  **Ingestão:** Captura os dados brutos em formato JSON.
4.  **Processamento (ETL):** Realiza a validação dos dados e tratamento de erros.
5.  **Classificação:** Aplica a lógica do *Protocolo de Manchester* (Sinais Vitais + Sintomas).
6.  **Armazenamento:** Salva o histórico em banco de dados SQL (SQLite).
7.  **Analytics:** Gera automaticamente um arquivo CSV conectado ao Power BI.

---

## ⚙️ Tecnologias Utilizadas
* **Python 3.12+** (Linguagem Principal)
* **Playwright** (Automação de Navegador/Scraping)
* **Pandas** (Manipulação de Dados)
* **SQLite** (Banco de Dados Relacional)
* **Power BI** (Dashboard e Business Intelligence)
* **Streamlit** (Interface Web do Totem) -> [https://genhealthtech.streamlit.app/]

---

## 🧠 Regras de Negócio (Protocolo de Manchester)
A classificação de risco é feita automaticamente pelo script:

* 🔴 **Vermelho (Emergência):** Sat O2 < 90%, Temp > 39.5°C ou palavras-chave críticas (ex: "infarto").
* 🟠 **Laranja (Muito Urgente):** Temp > 38.5°C ou palavras-chave como "falta de ar".
* 🟡 **Amarelo (Urgente):** Temp > 37.5°C ou pressão alta.
* 🟢 **Verde (Pouco Urgente):** Casos leves e sem risco imediato.

---

## ▶️ Como Executar o Projeto

Siga os passos abaixo para rodar a automação na sua máquina:

### 1. Preparação
Certifique-se de ter o [Python](https://www.python.org/) e o [Git](https://git-scm.com/) instalados.

```bash
# Clone este repositório
git clone [https://github.com/kamilly-araujo/smart-triage-system.git]
cd smart-triage-system
```

### 2. Instalação das Dependências
Instale as bibliotecas listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Configuração do Navegador
Instale os binários do Playwright (necessário para o robô funcionar):

```bash
playwright install
```

### 4. Execução
Rode o script principal:

```bash
python worker1.py
```

**Nota:** Uma janela do navegador será aberta para monitorar o totem.  
Mantenha-a aberta para que o sistema continue capturando dados.  
O arquivo `output_hospital_santa_clara.csv` será atualizado automaticamente na pasta do projeto.

Para encerrar o monitoramento, pressione Ctrl + C no terminal.

