 # Resume Relevance Check Hackathon Project

## 📄 Problem Statement
At Innomatics Research Labs, resume evaluation is currently **manual, inconsistent, and time-consuming**. Every week, the placement team across Hyderabad, Bangalore, Pune, and Delhi NCR receives 18–20 job requirements, with each posting attracting thousands of applications.  
Currently, recruiters and mentors manually review resumes, matching them against job descriptions (JD). This leads to:  
- Delays in shortlisting candidates.  
- Inconsistent judgments, as evaluators may interpret role requirements differently.  
- High workload for placement staff, reducing their ability to focus on interview prep and student guidance.  

With hiring companies expecting fast and high-quality shortlists, there is a **pressing need for an automated system** that can scale, be consistent, and provide actionable feedback to students.  

**This project automates the process to:**  
- Evaluate resume relevance to a job description.  
- Highlight matched and missing skills.  
- Provide actionable improvement suggestions.  
- Track analysis history with statistics and top candidates.

---

## 🛠️ Tools & Technologies
- **Frontend:** Streamlit  
- **Backend:** Flask (Deployed on Render)  
- **Language:** Python   
- **Deployment:** Streamlit Cloud (frontend), Render (backend)  

---
## Approach 

This project is designed as a **web-based Resume Relevance Checker** with a frontend and backend:

### Frontend
- Built using **Streamlit**.
- Allows users to **upload resume and job description files** (PDF, DOCX, TXT).
- Sends files to the backend for analysis.
- Displays results including:
  - Resume relevance score
  - Matched skills
  - Missing skills
  - Improvement suggestions
  - Verdict (e.g., Excellent, Good, Average, Poor)
- Provides a **dashboard** to track:
  - Analysis history
  - Score trends
  - Top-performing candidates

### Backend
- Hosted on **Render** (cloud deployment).
- Exposes a `/match` **API endpoint**.
- Processes uploaded files and calculates:
  - **Resume relevance score**
  - Matched and missing skills
  - Improvement suggestions
  - Verdict
- Returns results as **JSON** to the frontend.

### Workflow
1. User uploads a resume and job description via the Streamlit frontend.
2. Frontend sends the files to the backend API using an HTTP POST request.
3. Backend analyzes the documents and returns the results.
4. Frontend displays the results in an interactive interface and updates the dashboard/history.

### Features
- Fast and automated resume evaluation.
- Clear visualization of matched and missing skills.
- Actionable improvement suggestions for candidates.
- Persistent analysis history and statistics.


## 💡 Project Overview
1. Users upload a **resume** and **job description**.  
2. Backend processes files: extracts text, matches skills, calculates a score, and generates suggestions.  
3. Frontend displays:  
   - Score percentage  
   - Matched / missing skills  
   - Top improvement suggestions  
   - Dashboard with history & analytics  

---

## ⚙️ Installation & Setup
1. **Clone the repository**:
bash
git clone https://github.com/YOUR_USERNAME/resume-relevance-check.git
cd resume-relevance-check
Install dependencies:
pip install -r requirements.txt
Run frontend locally:
cd frontend
streamlit run app.py
Open browser and navigate to the app (default: http://localhost:8501)
---

🎯 Usage

Upload a resume (PDF, DOCX, TXT).

Upload a job description (PDF, DOCX, TXT).

Click Analyze Resume Match.

View results:

Score

Matched / Missing Skills

Improvement Suggestions

Access Dashboard to see history, top candidates, and score trends.
---
## 🚀 Live Demo
- **Frontend (Streamlit App):** https://5z8xusbxc99z6gp9hdtkmp.streamlit.app/
- **Backend (Render API):** https://resume-relevance-check-hackthon.onrender.com/

