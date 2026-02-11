import sqlite3
import hashlib
import requests
import json
import pandas as pd
from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import random

# --- CONFIGURAÇÕES ---
DB_NAME = "hospital_santa_clara.db"
URL_ALVO = "https://genhealthtech.streamlit.app/"

# --- FUNÇÕES DE APOIO (MANTIDAS DO SEU CÓDIGO) ---

def criar_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS pacientes (id_paciente INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL,data_nascimento DATETIME, hash_identificacao TEXT UNIQUE)')
        cursor.execute('CREATE TABLE IF NOT EXISTS triagens (id_triagem INTEGER PRIMARY KEY AUTOINCREMENT, id_paciente INTEGER, data_hora DATETIME DEFAULT CURRENT_TIMESTAMP, temperatura REAL, sat_o2 INTEGER, sintomas TEXT, classificacao_cor TEXT, classificacao_palavra TEXT, tempo REAL, erro_sensor BOOLEAN, FOREIGN KEY (id_paciente) REFERENCES pacientes (id_paciente))')
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao criar DB: {e}")

def gerar_hash(nome):
    return hashlib.sha256(nome.encode()).hexdigest()[:10].upper()

def classificar_manchester(sinais, queixa):
    temp = sinais.get('temp', 0)
    sat = sinais.get('sat_o2', 100)
    queixa_lower = str(queixa).lower()
    if sat < 90 or temp > 39.5 or any(p in queixa_lower for p in ["infarto", "desmaio", "coracao", "parada cardiorrespiratoria", "insuficiencia respiratoria", "choque", 
                                                                  "inconsciencia", "crise convulsiva", "hemorragia massiva", "trauma grave", "dor no peito intensa", "paralisia subita",
                                                                    "obstrucao de vias aereas", "cianose", "coma"]):
        return "Vermelho"
    elif temp > 38.5 or any(p in queixa_lower for p in ["falta de ar", "peito", "sangue","dor severa", "arritmia", "falta de ar", "dispneia", "alteracao do estado mental",
                                                         "febre muito alta", "cefaleia subita", "dor abdominal intensa", "fratura exposta", "queimadura grave", "sangramento moderado", 
                                                         "vomito persistente", "fraqueza extrema"]):
        return "Laranja"
    elif temp > 37.5 or any(p in queixa_lower for p in ["dor moderada", "vomitos", "diarreia", "febre", "desidratacao", "trauma leve", 
                                                        "sinais de infeccao", "crise de hipertensao", "desorientacao leve", 
                                                        "dor lombar aguda", "asma moderada", "reacao alergica leve"]):
        return "Amarelo"
    else:
        return "Verde"


def num_aleatorio(sinais, queixa):

    temp = sinais.get('temp', 0)
    sat = sinais.get('sat_o2', 100)
    minutos = str(queixa).lower()
    if sat < 90 or temp > 39.5 or any(p in minutos for p in ["infarto", "desmaio", "coracao", "parada cardiorrespiratoria", "insuficiencia respiratoria", "choque", 
                                                                  "inconsciencia", "crise convulsiva", "hemorragia massiva", "trauma grave", "dor no peito intensa", "paralisia subita",
                                                                    "obstrucao de vias aereas", "cianose", "coma"]):
        return round(random.uniform(0, 2), 0)
    elif temp > 38.5 or any(p in minutos for p in ["falta de ar", "peito", "sangue","dor severa", "arritmia", "falta de ar", "dispneia", "alteracao do estado mental",
                                                         "febre muito alta", "cefaleia subita", "dor abdominal intensa", "fratura exposta", "queimadura grave", "sangramento moderado", 
                                                         "vomito persistente", "fraqueza extrema"]):
        return  round(random.uniform(0, 10), 0)
    elif temp > 37.5 or any(p in minutos for p in ["dor moderada", "vomitos", "diarreia", "febre", "desidratacao", "trauma leve", 
                                                        "sinais de infeccao", "crise de hipertensao", "desorientacao leve", 
                                                        "dor lombar aguda", "asma moderada", "reacao alergica leve"]):
        return round(random.uniform(0, 60), 0)
    else:
        return round(random.uniform(0, 120), 0)
    
def palavra2(sinais, queixa):

    temp = sinais.get('temp', 0)
    sat = sinais.get('sat_o2', 100)
    minutos = str(queixa).lower()
    if sat < 90 or temp > 39.5 or any(p in minutos for p in ["infarto", "desmaio", "coracao", "parada cardiorrespiratoria", "insuficiencia respiratoria", "choque", 
                                                                  "inconsciencia", "crise convulsiva", "hemorragia massiva", "trauma grave", "dor no peito intensa", "paralisia subita",
                                                                    "obstrucao de vias aereas", "cianose", "coma"]):
        return "Emergência"
    elif temp > 38.5 or any(p in minutos for p in ["falta de ar", "peito", "sangue","dor severa", "arritmia", "falta de ar", "dispneia", "alteracao do estado mental",
                                                         "febre muito alta", "cefaleia subita", "dor abdominal intensa", "fratura exposta", "queimadura grave", "sangramento moderado", 
                                                         "vomito persistente", "fraqueza extrema"]):
        return  "Muito Urgente"
    elif temp > 37.5 or any(p in minutos for p in ["dor moderada", "vomitos", "diarreia", "febre", "desidratacao", "trauma leve", 
                                                        "sinais de infeccao", "crise de hipertensao", "desorientacao leve", 
                                                        "dor lombar aguda", "asma moderada", "reacao alergica leve"]):
        return "Urgente"
    else:
        return "Pouco Urgente"

# --- FUNÇÃO DE PROCESSAMENTO INDIVIDUAL ---

def processar_novo_link(url_json):
    """Esta função faz todo o ciclo para UM único link detectado"""
    try:
        print(f"\n👦🏻 Um novo paciente foi cadastrado!\n🚀 Processando link detectado: {url_json}")
        res = requests.get(url_json, timeout=10)
        
        if res.status_code == 200:
            dados_brutos = res.json()
            if isinstance(dados_brutos, str):
                dados_historicos = [json.loads(dados_brutos)]
            elif isinstance(dados_brutos, dict):
                dados_historicos = [dados_brutos]
            else:
                dados_historicos = dados_brutos

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            for registro in dados_historicos:
                paciente = registro.get('paciente', {})
                clinico = registro.get('dados_clinicos', {})
                sinais = clinico.get('sinais_vitais', {})
                sintomas = clinico.get('queixa_principal', 'Não informado')

                temp_lida = sinais.get('temperatura', 0.0)
                sat_lida = sinais.get('saturacao_o2', 100)
                erro_detectado = (temp_lida == 0.0 or temp_lida is None)
                temp_final = 36.5 if erro_detectado else temp_lida

                nome_original = paciente.get('nome_completo', 'Desconhecido')
                hash_id = gerar_hash(nome_original)

                cursor.execute('INSERT OR IGNORE INTO pacientes (nome, hash_identificacao) VALUES (?, ?)', (nome_original, hash_id))
                cursor.execute('SELECT id_paciente FROM pacientes WHERE hash_identificacao = ?', (hash_id,))
                id_p = cursor.fetchone()[0]

                cor = classificar_manchester({'temp': temp_final, 'sat_o2': sat_lida}, sintomas)
                time = num_aleatorio({'temp': temp_final, 'sat_o2': sat_lida}, sintomas)
                palavra=palavra2({'temp': temp_final, 'sat_o2': sat_lida}, sintomas)

                cursor.execute('''
                    INSERT INTO triagens (id_paciente, temperatura, sat_o2, sintomas, classificacao_cor,classificacao_palavra, tempo, erro_sensor)
                    VALUES (?, ?, ?, ?, ?, ?, ?,?)
                ''', (id_p, temp_final, sat_lida, sintomas, cor, palavra, time, erro_detectado))

            conn.commit()
            conn.close()
            print(f"✅ Novo Paciente inserido no Banco de Dados! ({datetime.now().strftime('%H:%M:%S')})")
            
            # Atualiza o CSV para o Power BI automaticamente
            gerar_csv_powerbi()
            
        else:
            print(f"⚠️ Erro ao baixar JSON: Status {res.status_code}")
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")

def gerar_csv_powerbi():
    try:
        conn = sqlite3.connect(DB_NAME)
        query = '''
        SELECT t.data_hora, p.hash_identificacao AS ID_Paciente, t.classificacao_cor, t.classificacao_palavra, t.tempo, 
               t.sintomas, t.temperatura, t.sat_o2, t.erro_sensor
        FROM triagens t JOIN pacientes p ON t.id_paciente = p.id_paciente
        '''
        df = pd.read_sql_query(query, conn)
        df.to_csv('output_hospital_santa_clara.csv', index=False, encoding='utf-8-sig')
        conn.close()
        print("📊 CSV 'output_hospital_santa_clara.csv' atualizado.")
    except Exception as e:
        print(f"❌ Erro ao gerar CSV: {e}")

# --- MONITORAMENTO EM TEMPO REAL COM PLAYWRIGHT ---

def monitorar_e_processar_em_tempo_real():
    criar_db()
    
    with sync_playwright() as p:
        print(f"🌐 Abrindo monitoramento no site: {URL_ALVO}")
        browser = p.chromium.launch(headless=False) # Mantenha False para ver o site operando
        page = browser.new_page()

        # ESSA É A CHAVE: O evento 'request' chama a função de processamento na hora!
        def handle_request(request):
            url = request.url
            if "https://genhealthtech.streamlit.app/~/+/media/"  in url:
                # Dispara o processamento sem interromper o monitoramento
                processar_novo_link(url)

        page.on("request", handle_request)

        page.goto(URL_ALVO, wait_until="networkidle")

        print("⏳ Monitorando o site em tempo real. Pressione Ctrl+C para parar.")
        
        # Mantém o navegador aberto "infinitamente" ou por um tempo muito longo
        # Enquanto ele estiver aberto, cada novo JSON detectado disparará o processamento
        try:
            page.wait_for_timeout(9999999) # Tempo estendido para monitoramento contínuo
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento encerrado pelo usuário.")
        finally:
            browser.close()


if __name__ == "__main__":
    monitorar_e_processar_em_tempo_real()