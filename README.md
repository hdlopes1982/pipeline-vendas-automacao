# Automated Data Pipeline: Python | GitHub Actions | Power BI

This project demonstrates a fully automated end-to-end data ecosystem, from synthetic data generation to real-time Business Intelligence visualization.

##  Tech Stack
- **Language:** Python (Pandas, Openpyxl, XlsxWriter)
- **Automation:** GitHub Actions (CI/CD)
- **Storage:** GitHub Repository (as a flat-file database)
- **Communication:** SMTP / Gmail API (HTML Reports)
- **Visualization:** Power BI (Web/API Integration)

##  How it Works
1.  **Data Generation:** A Python script runs weekly to simulate realistic sales transactions, maintaining referential integrity between Product and Store tables.
2.  **Orchestration:** GitHub Actions triggers the environment every Monday at 08:30 AM. It executes the script, updates the `Base_Vendas.xlsx` file, and performs a Git commit/push back to the repository.
3.  **Smart Alerting:** Upon success, the system sends a professional HTML-formatted email report with key ingestion metrics.
4.  **BI Integration:** Power BI Service connects to the GitHub Raw URL via a secure API connection, enabling scheduled refreshes and automated dashboard updates.

##  Business Value
This solution eliminates manual data entry and repetitive cleaning tasks. By using GitHub as a lightweight data versioning tool, the dashboard remains updated without any human intervention, ensuring data-driven decisions are made on the most recent information.

##  Project Structure
- `script_vendas.py`: Main logic for data generation and email reporting.
- `Base_Vendas.xlsx`: The project's data source.
- `.github/workflows/main.yml`: Workflow configuration for automation.

##  How to Setup

To replicate this pipeline, follow these steps:

### 1. Prerequisites
- A **GitHub** account.
- A **Gmail** account (with an [App Password](https://support.google.com/accounts/answer/185833) generated).
- **Power BI Desktop** installed.

### 2. Environment Secrets
In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add the following secrets:
- `EMAIL_USER`: Your Gmail address.
- `EMAIL_PASS`: Your 16-character App Password.

### 3. Local Configuration
1. Clone this repository.
2. Install dependencies: `pip install pandas openpyxl xlsxwriter`.
3. Run the script locally once to ensure connection: `python script_vendas.py`.

### 4. Power BI Integration
1. Open the `.pbix` file (or create a new one).
2. Use the **Web** connector with the **Raw URL** of your `Base_Vendas.xlsx`.
3. Set the privacy level to **Public** or **Organizational** in the Power BI Service settings to enable scheduled refresh.

---
##  License
This project is for educational purposes. Feel free to fork and adapt it for your own automation needs!

---
*Note: This project was developed as a technical showcase. Power BI automatic refresh is active during the Pro Trial period.*
