import os
import random
import pandas as pd
from datetime import datetime, timedelta
from O365 import Account
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURAÇÕES ---
# IMPORTANTE: Agora usamos o ID e o SECRET mas com um fluxo simplificado
AZ_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZ_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AZ_TENANT_ID = os.getenv('AZURE_TENANT_ID')
ONEDRIVE_FILE_ID = os.getenv('ONEDRIVE_FILE_ID')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

def run_pipeline(n_linhas=50):
    try:
        credentials = (AZ_CLIENT_ID, AZ_CLIENT_SECRET)
        # Usamos o protocolo básico sem prefixos 'me' ou 'users' para evitar o erro de SPO
        account = Account(credentials, tenant_id=AZ_TENANT_ID, auth_flow_type='credentials')
        
        if not account.authenticate():
            print("❌ Falha na autenticação.")
            return

        # Aceder diretamente via Drive ID (o ID que tiraste do link)
        storage = account.storage()
        # Tentativa de acesso direto ao item para ignorar verificação de licença do Tenant
        item = storage.get_drive_item(ONEDRIVE_FILE_ID)
        
        print("⏬ Descarregando ficheiro...")
        content = item.download_contents()
        
        # --- PROCESSAMENTO (Igual ao anterior) ---
        df_raw = pd.read_excel(BytesIO(content), sheet_name='Sales_Raw')
        df_prods = pd.read_excel(BytesIO(content), sheet_name='Products')
        df_stores = pd.read_excel(BytesIO(content), sheet_name='Stores')

        last_id = df_raw['TransactionID'].max() if not df_raw.empty else 1000
        hoje = datetime.now()
        criticos, qualidade, new_records = 0, 0, []

        for i in range(1, n_linhas + 1):
            prod = df_prods.sample(1).iloc[0]
            loja = df_stores.sample(1).iloc[0]
            data_str = (hoje - timedelta(days=random.randint(0, 6))).strftime('%Y-%m-%d')
            p_id, u_price = prod['ProductID'], prod['ListPrice']
            
            if random.random() < 0.05:
                p_id = "P99"; u_price = None; criticos += 1
            elif random.random() < 0.15:
                u_price = f"€{u_price}"; qualidade += 1
                
            email_val = f"user_{random.randint(100,999)}@gmail.com"
            if random.random() < 0.10: email_val = ""; qualidade += 1

            new_records.append([last_id + i, data_str, loja['Store'], p_id, random.randint(1, 5), u_price, 
                               random.choice(['Card', 'Cash', 'MBWay']), email_val, "Online"])

        df_final = pd.concat([df_raw, pd.DataFrame(new_records, columns=df_raw.columns)], ignore_index=True)

        # --- UPLOAD ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, sheet_name='Sales_Raw', index=False)
            df_prods.to_excel(writer, sheet_name='Products', index=False)
            df_stores.to_excel(writer, sheet_name='Stores', index=False)
        
        print("⬆️ Atualizando ficheiro...")
        item.update_contents(output.getvalue())

        # --- EMAIL ---
        enviar_email(n_linhas, criticos, qualidade, len(df_final))
        print("✅ Pipeline concluído!")

    except Exception as e:
        print(f"❌ Erro: {e}")

def enviar_email(n, crit, qual, total):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    msg['Subject'] = "🚀 Ingestão de Dados Concluída"
    corpo = f"Sucesso!\nNovas linhas: {n}\nTotal: {total}\nErros Críticos: {crit}\nQualidade: {qual}"
    msg.attach(MIMEText(corpo, 'plain'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

if __name__ == "__main__":
    run_pipeline(50)
