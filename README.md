# DailyLife Manager
A practical Flask + SQLite daily productivity application.

Features:
- Dashboard
- Tasks with priority and completion
- Daily schedule
- Expense tracking
- Goal tracking
- Health-check endpoint
- Pytest automated tests

Run on Windows:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

Open http://localhost:5000
Health: http://localhost:5000/health
Tests: pytest -q

DevOps path: Git/GitHub -> Docker -> Jenkins -> Kubernetes -> SonarQube/Monitoring
