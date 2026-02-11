AI-First CRM: HCP Interaction Manager
Life Sciences Agentic Workflow (Task 1 & 2)
A full-stack application designed for Medical Science Liaisons (MSLs) to log, search, and manage Healthcare Professional (HCP) interactions using an Agentic AI Bridge. This project replaces traditional manual data entry with a conversational interface that ensures data integrity and QMS compliance.

Features
•	Conversational Logging: AI extracts HCP names, meeting summaries, and next steps directly from chat.
•	Agentic Reasoning: Powered by LangGraph and Llama-3.3 for intelligent tool-calling.
•	Real-time State Sync: Frontend fields auto-fill via Redux based on AI analysis.
•	Persistence: Fully integrated with a PostgreSQL database for long-term data storage.
•	Sentiment Analysis: Automatic tone detection (Positive, Neutral, Concerned) for every interaction.

Tech Stack
•	Frontend: React, Redux Toolkit, Axios, CSS3.
•	Backend: FastAPI (Python 3.10+).
•	AI Orchestration: LangGraph, LangChain, Groq (Llama-3.3-70b).
•	Database: PostgreSQL with SQLAlchemy ORM.

Project Structure

hcp_crm_project/
├── backend/
│   ├── main.py              # FastAPI server & LangGraph logic
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Template for API keys
├── hcp-frontend/
│   ├── src/
│   │   ├── App.js           # Main UI logic
│   │   └── store.js         # Redux state management
│   ├── package.json         # Node dependencies
│   └── public/
└── README.md

Setup & Installation
1. Database Setup
Ensure you have PostgreSQL installed and running. Create a database named hcp_crm_db:
SQL
CREATE DATABASE hcp_crm_db;
2. Backend Setup
1.	Navigate to the backend folder.
2.	Create a virtual environment: python -m venv venv.
3.	Activate it: source venv/bin/activate (Mac) or venv\Scripts\activate (Windows).
4.	Install dependencies: pip install -r requirements.txt.
5.	Create a .env file and add your key: GROQ_API_KEY=your_key_here.
6.	Run the server: python main.py.
3. Frontend Setup
1.	Navigate to the hcp-frontend folder.
2.	Install packages: npm install.
3.	Start the app: npm start.

Security & QMS Compliance
•	Environment Variables: Sensitive API keys are managed via .env files and excluded from version control via .gitignore.
•	Data Integrity: The system uses a "Human-in-the-loop" design, allowing users to verify and manually edit AI-extracted data before saving it to the database.
•	Audit Readiness: Every interaction is timestamped and stored in a structured format, meeting Life Sciences regulatory standards for transparency.

Submission Videos
•	Task 1 (Technical Demo): https://drive.google.com/file/d/1oE-6-G1bCv2zoxnNZtzV6aTyTaOHXCeZ/view?usp=drive_link
•	Task 2 (Business & QMS Presentation): https://drive.google.com/file/d/1Q9RSVpIJZ_haibAa-jjNPZEjedarSXpV/view?usp=drive_link

Developed by: Vishal Tiwari

