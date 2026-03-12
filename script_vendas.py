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
            new_records.append([
                last_id + i, data_str, loja['Store'], prod['ProductID'], 
                random.randint(1, 5), prod['ListPrice'], 
                random.choice(['Card', 'Cash', 'MBWay']), f"user_{random.randint(100,999)}@test.com", "Online"
            ])

        df_final = pd.concat([df_raw, pd.DataFrame(new_records, columns=df_raw.columns)], ignore_index=True)

        # 3. Salvar o ficheiro localmente
        with pd.ExcelWriter(FILE_NAME, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, sheet_name='Sales_Raw', index=False)
            df_prods.to_excel(writer, sheet_name='Products', index=False)
            df_stores.to_excel(writer, sheet_name='Stores', index=False)
        
        print(f"✅ Ficheiro atualizado localmente. Total: {len(df_final)} linhas.")

        # 4. Enviar Email formatado (HTML)
        # Simulamos alguns valores de qualidade apenas para o visual do email
        enviar_email(total=len(df_final), adicionadas=n_linhas)

    except Exception as e:
        print(f"❌ Erro: {e}")

def enviar_email(total, adicionadas):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    msg['Subject'] = f"🚀 Relatório de Vendas: {datetime.now().strftime('%d/%m/%Y')}"

    # Template HTML elegante
    html = f"""
    <html>
      <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border: 1px solid #e0e0e0;">
          
          <div style="background-color: #2e7d32; padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Automação Concluída</h1>
          </div>

          <div style="padding: 30px;">
            <p style="font-size: 16px;">Olá,</p>
            <p style="font-size: 16px;">O pipeline semanal de vendas foi executado com sucesso no <b>GitHub Actions</b>. Os novos dados já foram injetados no Excel.</p>
            
            <div style="background-color: #f1f8e9; border-radius: 8px; padding: 20px; margin: 25px 0;">
              <table style="width: 100%; border-collapse: collapse;">
                <tr>
                  <td style="padding: 10px 0; border-bottom: 1px solid #c8e6c9;"><b>Status:</b></td>
                  <td style="text-align: right; padding: 10px 0; border-bottom: 1px solid #c8e6c9; color: #2e7d32; font-weight: bold;">Sucesso ✅</td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; border-bottom: 1px solid #c8e6c9;"><b>Novos Registos:</b></td>
                  <td style="text-align: right; padding: 10px 0; border-bottom: 1px solid #c8e6c9;">+ {adicionadas}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 0;"><b>Total na Base:</b></td>
                  <td style="text-align: right; padding: 10px 0; font-weight: bold; font-size: 18px;">{total}</td>
                </tr>
              </table>
            </div>

            <div style="text-align: center; margin-top: 30px;">
              <a href="https://app.powerbi.com/" 
                 style="background-color: #2e7d32; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                 Abrir Power BI Online
              </a>
            </div>
          </div>

          <div style="background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #777;">
            Pipeline automatizado via Python & GitHub Actions<br>
            © {datetime.now().year} Data Analytics Project
          </div>
        </div>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print("📧 Email enviado com sucesso!")
    except Exception as e:
        print(f"⚠️ Falha ao enviar email: {e}")

if __name__ == "__main__":
    run_pipeline(50)
