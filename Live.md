# Liquidity Risk Inference Engine

🚀 **Live Production Application:** [[LIVE DASHBOARD](https://sba-risk-engine.onrender.com/)]
*(Note: This application is deployed on serverless cloud infrastructure. Please allow 45-60 seconds for the initial "cold start" boot-up).*

## 📊 Executive Summary
This project is an end-to-end Machine Learning web application designed to assess capital liquidity and default risk for commercial loans. Moving beyond static analysis, this tool deploys a live **XGBoost classification engine** wrapped in an interactive, off-white enterprise dashboard, allowing stakeholders to run dynamic scenario simulations based on loan term, requested capital, macroeconomic CPI, and geographic jurisdiction.

## 🏗️ System Architecture: Zero-Disk Pipeline
This application operates on a strict **zero-disk architecture**. No local CSVs or static files are stored in the repository. 
1. **Data Ingestion:** Live data is queried directly from a secure PostgreSQL vault (`powerbi_historical_view`) hosted on **Supabase**.
2. **Inference Engine:** A pre-trained XGBoost model evaluates user inputs against historical risk patterns, achieving robust predictive accuracy.
3. **Frontend Delivery:** Built with **Plotly Dash**, the UI operates entirely in-memory, rendering a clean, responsive canvas without heavy client-side processing.
4. **CI/CD Deployment:** The pipeline is version-controlled via Git and continuously deployed via **Render**.

## 💻 Tech Stack
* **Machine Learning:** `xgboost`, `scikit-learn`, `pandas`
* **Cloud Database:** `Supabase`, `PostgreSQL`, `SQLAlchemy`, `psycopg2`
* **Frontend/UI:** `Plotly Dash`, `HTML/CSS` (Flexbox canvas)
* **Deployment & DevOps:** `Render`, `Gunicorn`, `Git/GitHub`, `python-dotenv`

## 📈 Key Business Features
* **Algorithmic Risk Scoring (PD):** A forward-looking predictive widget that instantly outputs a Probability of Default (PD) via a dynamic gauge chart.
* **Macro Portfolio Analytics:** Backward-looking analytics detailing total capital exposure, historical loss, and average amortization terms.
* **Geospatial & Sector Risk:** Interactive chloropleth mapping and horizontal bar charting to isolate the top 10 highest-risk industries and state-level default concentrations.

## ⚙️ Local Development Setup
To run this pipeline locally on your machine:

1. Clone the repository:
   ```bash
   git clone [https://github.com/YourUsername/sba-risk-pipeline.git](https://github.com/YourUsername/sba-risk-pipeline.git)
