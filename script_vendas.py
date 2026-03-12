import os
import random
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Nome do ficheiro que tem de estar na raiz do teu GitHub
FILE_NAME = "Base_Vendas.xlsx"
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

def run_pipeline(n_linhas=50):
    try:
        print(f"📂 Lendo ficheiro local: {FILE_NAME}")
        
        # 1. Ler o ficheiro que já está no repositório
        df_raw = pd.read_excel(FILE_NAME, sheet_name='Sales_Raw')
        df_prods = pd.read_excel(FILE_NAME, sheet_name='Products')
        df_stores = pd.read_excel(FILE_NAME, sheet_name='Stores')

        # 2. Gerar novos dados
        last_id = df_raw['TransactionID'].max() if not df_raw.empty else 1000
        hoje = datetime.now()
        new_records = []

        for i in range(1, n_linhas + 1):
            prod = df_prods.sample(1).iloc[0]
            loja = df_stores.sample(1).iloc[0]
            data_str = (hoje - timedelta(days=random.randint(0, 6))).strftime('%Y-%m-%d')
            new_records.append([last_id + i, data_str, loja['Store'], prod['ProductID'], 
                               random.randint(1, 5), prod['ListPrice'], 
                               random.choice(['Card', 'Cash', 'MBWay']), f"user_{i}@test.com", "Online"])

        df_final = pd.concat([df_raw, pd.DataFrame(new_records, columns=df_raw.columns)], ignore_index=True)

        # 3. Salvar o ficheiro localmente (o GitHub Action fará o resto)
        with pd.ExcelWriter(FILE_NAME, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, sheet_name='Sales_Raw', index=False)
            df_prods.to_excel(writer, sheet_name='Products', index=False)
            df_stores.to_excel(writer, sheet_name='Stores', index=False)
        
        print(f"✅ Ficheiro atualizado localmente. Total: {len(df_final)} linhas.")

        # 4. Enviar Email
        enviar_email(len(df_final))

    except Exception as e:
        print(f"❌ Erro: {e}")

def enviar_email(total):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    msg['Subject'] = "🚀 GitHub Actions: Dados Atualizados no Repositório"
    msg.attach(MIMEText(f"O pipeline correu. O Excel no GitHub agora tem {total} linhas.", 'plain'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

if __name__ == "__main__":
    run_pipeline(50)
