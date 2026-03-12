name: Weekly Sales Ingestion
on:
  schedule:
    - cron: '30 8 * * 1' # Segundas-feiras às 08:30 UTC
  workflow_dispatch: # Permite correr manualmente para testar

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install pandas openpyxl O365 xlsxwriter
      - name: Execute Script
        env:
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          ONEDRIVE_FILE_ID: ${{ secrets.ONEDRIVE_FILE_ID }}
          EMAIL_USER: ${{ secrets.EMAIL_USER }}
          EMAIL_PASS: ${{ secrets.EMAIL_PASS }}
        run: python main.py
