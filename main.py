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
AZ_CREDENTIALS = (os.getenv('AZURE_CLIENT_ID'), os.getenv('AZURE_CLIENT_SECRET'))
AZ_TENANT_ID = os.getenv('AZURE_TENANT_ID')
ONEDRIVE_FILE_ID = os.getenv('ONEDRIVE_FILE_ID')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
LINK_DASHBOARD = "https://app.powerbi.com/" 

def run_pipeline(n_linhas=50):
    try:
        # 1. AUTENTICAÇÃO
        account = Account(AZ_CREDENTIALS, tenant_id=AZ_TENANT_ID, auth_flow_type='credentials')
        if not account.authenticate(): 
            print("❌ Erro na autenticação Azure")
            return
        
        # 2. DOWNLOAD
        item = account.storage().get_default_drive().get_item(ONEDRIVE_FILE_ID)
        content = item.download_contents()
        
        # 3. PROCESSAMENTO
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
            
            seed = random.random()
            if seed < 0.05:
                p_id = "P99"; u_price = None; criticos += 1
            elif seed < 0.15:
                u_price = f"€{u_price}"; qualidade += 1
                
            email_val = f"user_{random.randint(100,999)}@gmail.com"
            if random.random() < 0.10: 
                email_val = ""; qualidade += 1

            new_records.append([last_id + i, data_str, loja['Store'], p_id, random.randint(1, 5), u_price, 
                               random.choice(['Card', 'Cash', 'MBWay']), email_val, "Online"])

        df_final = pd.concat([df_raw, pd.DataFrame(new_records, columns=df_raw.columns)], ignore_index=True)

        # 4. UPLOAD
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, sheet_name='Sales_Raw', index=False)
            df_prods.to_excel(writer, sheet_name='Products', index=False)
            df_stores.to_excel(writer, sheet_name='Stores', index=False)
        
        item.update_contents(output.getvalue())

        # 5. EMAIL
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER
        msg['Subject'] = f"🚀 GitHub Actions: Ingestão Concluída"
        msg.attach(MIMEText(f"Sucesso!\nNovas vendas: {n_linhas}\nTotal: {len(df_final)}\nCríticos: {criticos}\nQualidade: {qualidade}", 'plain'))
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            
        print(f"✅ Sucesso! Total na base: {len(df_final)}")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    run_pipeline(50)
