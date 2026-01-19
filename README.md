
UrbanInfrastructure is a full-stack web application designed to analyze and recommend urban infrastructure locations based on accessibility, safety, and surrounding facilities.  
It helps identify best zones and risk-prone zones for urban planning and decision-making.


Features
Location-based search (e.g., *Bangalore North*)
Interactive map visualization
Best infrastructure zones recommendation
Danger / risk zone identification
Fast frontend with React + Vite
Backend powered by Python (Flask) with geospatial logic

Tech Stack:
Frontend: React, Vite, JavaScript, CSS, Leaflet / Map-based components
Backend: Python, Flask, Flask-CORS, Geospatial utilities, JSON-based caching

📂 Project Structure
urbaninfra_dashboard/
│
├── backend/
│   ├── app.py
│   ├── cache.py
│   ├── utils_geo.py
│   ├── requirements.txt
│   └── run_backend.bat
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── .gitignore


HOW TO RUN LOCALLY:
Backend Setup (Python):
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py
Backend will run on: http://127.0.0.1:5000

Frontend Setup (React):
cd frontend
npm install
npm run dev
Frontend will run on: http://localhost:5173


Author
Mateena Sadaf
GitHub: [https://github.com/mateenasadaf](https://github.com/mateenasadaf)

