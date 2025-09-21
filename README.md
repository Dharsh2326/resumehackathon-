 # Automated Resume Relevance Check System 

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
- **DataBase:** SQLite
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
- **Database:** SQLite

# ⚙️ Installation & Setup

#### Clone the repository
git clone https://github.com/Dharsh2326/resumehackathon.git

#### Go into the cloned folder
cd resumehackathon

#### Install dependencies
pip install -r requirements.txt

#### Run frontend locally
cd frontend
streamlit run app.py

#### Open browser at
http://localhost:8501

## 🎯 Usage

1. **Upload a Resume**  
   - Supported formats: PDF, DOCX, TXT.  
   - Click the **Upload Resume** button and select your file.  

2. **Upload a Job Description**  
   - Supported formats: PDF, DOCX, TXT.  
   - Click the **Upload Job Description** button and select the file.  

3. **Analyze Resume Match**  
   - Click the **Analyze** button.  
   - The system will send your files to the backend API for processing.  

4. **View Results**  
   - **Resume Relevance Score** (percentage)  
   - **Matched Skills** – skills from the JD found in the resume  
   - **Missing Skills** – skills required but not found in the resume  
   - **Improvement Suggestions** – actionable tips for the candidate  
   - **Verdict** – e.g., Excellent, Good, Average, Poor  

5. **Dashboard & History**  
   - Track multiple candidates’ analysis history.  
   - See top-performing candidates and score trends over time.

---
## 🚀 Live Demo
- **Frontend (Streamlit App):** https://5z8xusbxc99z6gp9hdtkmp.streamlit.app/
- **Backend (Render API):** https://resume-relevance-check-hackthon.onrender.com/
---
