import os
import random
import pandas as pd
from datetime import datetime, timedelta
from O365 import Account, MSGraphProtocol
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURAÇÕES ---
AZ_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZ_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AZ_TENANT_ID = os.getenv('AZURE_TENANT_ID')
ONEDRIVE_FILE_ID = os.getenv('ONEDRIVE_FILE_ID')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

def run_pipeline(n_linhas=50):
    try:
        # AQUI ESTÁ O SEGREDO: Forçamos o protocolo a usar 'users' em vez de 'me'
        # para garantir que o Azure Application Permissions (Files.ReadWrite.All) funcione
        protocol = MSGraphProtocol(default_resource=f'users/{EMAIL_USER}')
        
        credentials = (AZ_CLIENT_ID, AZ_CLIENT_SECRET)
        account = Account(credentials, tenant_id=AZ_TENANT_ID, protocol=protocol, auth_flow_type='credentials')
        
        if not account.authenticate():
            print("❌ Falha na autenticação.")
            return

        storage = account.storage()
        # Acedemos à drive do utilizador específico
        drive = storage.get_default_drive()
        item = drive.get_item(ONEDRIVE_FILE_ID)
        
        print("⏬ Descarregando ficheiro...")
        content = item.download_contents()
        
        # --- PROCESSAMENTO ---
        df_raw = pd.read_excel(BytesIO(content), sheet_name='Sales_Raw')
        df_prods = pd.read_excel(BytesIO(content), sheet_name='Products')
        df_stores = pd.read_excel(BytesIO(content), sheet_name='Stores')

        last_id = df_raw['TransactionID'].max() if not df_raw.empty else 1000
        hoje = datetime.now()
        new_records = []

        for i in range(1, n_linhas + 1):
            prod = df_prods.sample(1).iloc[0]
            loja = df_stores.sample(1).iloc[0]
            data_str = (hoje - timedelta(days=random.randint(0, 6))).strftime('%Y-%m-%d')
            new_records.append([last_id + i, data_str, loja['Store'], prod['ProductID'], random.randint(1, 5), prod['ListPrice'], 
                               random.choice(['Card', 'Cash', 'MBWay']), f"user_{i}@test.com", "Online"])

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
        enviar_email(len(df_final))
        print(f"✅ Sucesso total!")

    except Exception as e:
        print(f"❌ Erro: {e}")

def enviar_email(total):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    msg['Subject'] = "🚀 Pipeline concluído com sucesso"
    msg.attach(MIMEText(f"O ficheiro foi atualizado. Total de linhas: {total}", 'plain'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

if __name__ == "__main__":
    run_pipeline(50)
