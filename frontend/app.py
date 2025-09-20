import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import time

st.set_page_config(page_title="Resume Relevance Check", layout="wide", initial_sidebar_state="expanded")

# ===========================
# Custom CSS - Dark Theme Compatible
# ===========================
st.markdown("""
    <style>
        .title { 
            text-align: center; 
            font-size: 36px; 
            font-weight: bold; 
            color: #2c3e50;
            margin-bottom: 30px;
        }
        
        .section-header { 
            font-size: 22px; 
            font-weight: 600; 
            margin-top: 20px; 
            color: #34495e; 
        }
        
        .card { 
            background: linear-gradient(145deg, #f8f9fa, #e9ecef);
            padding: 20px; 
            border-radius: 15px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.1); 
            margin-bottom: 20px; 
            color: #2c3e50 !important;
            border-left: 4px solid #3498db;
        }
        
        .dark-card {
            background: linear-gradient(145deg, #2c3e50, #34495e) !important;
            color: #ecf0f1 !important;
            border-left: 4px solid #3498db;
        }
        
        .circle-score { 
            width: 160px; 
            height: 160px; 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            font-size: 36px; 
            font-weight: bold; 
            color: white; 
            margin: 20px auto; 
            box-shadow: 0px 8px 20px rgba(0,0,0,0.2);
            position: relative;
        }
        
        .skill-tag {
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            margin: 3px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .matched-skill-tag {
            background: #27ae60 !important;
        }
        
        .improvement-item {
            background: #f8f9fa;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            color: #2c3e50 !important;
        }
        
        .priority-high { border-left-color: #e74c3c; }
        .priority-medium { border-left-color: #f39c12; }
        .priority-low { border-left-color: #3498db; }
        
        .stats-container {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        
        .stat-box {
            text-align: center;
            padding: 15px;
            background: linear-gradient(145deg, #3498db, #2980b9);
            color: white;
            border-radius: 10px;
            min-width: 120px;
        }
        
        .reset-btn { 
            margin-top: 20px; 
            background: #e74c3c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        
        /* Dark theme overrides */
        @media (prefers-color-scheme: dark) {
            .card {
                background: linear-gradient(145deg, #2c3e50, #34495e) !important;
                color: #ecf0f1 !important;
            }
            .improvement-item {
                background: #34495e !important;
                color: #ecf0f1 !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# ===========================
# State Management - Initialize properly
# ===========================
def initialize_session_state():
    if "results" not in st.session_state:
        st.session_state.results = []
    if "detail_result" not in st.session_state:
        st.session_state.detail_result = None
    if "analysis_done" not in st.session_state:
        st.session_state.analysis_done = False
    if "current_files" not in st.session_state:
        st.session_state.current_files = {"resume": None, "jd": None}
    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = 0
    if "reset_trigger" not in st.session_state:
        st.session_state.reset_trigger = False

initialize_session_state()

# ===========================
# Helper Functions
# ===========================
def reset_analysis():
    """Reset all analysis data and file uploads"""
    st.session_state.detail_result = None
    st.session_state.analysis_done = False
    st.session_state.current_files = {"resume": None, "jd": None}
    # Increment the key to force file uploader widgets to reset
    st.session_state.file_uploader_key += 1
    st.session_state.reset_trigger = True
    # Clear file uploader widgets by rerunning
    st.rerun()

def force_reset_file_uploaders():
    """Force reset file uploaders by clearing cache"""
    # Clear Streamlit's file uploader cache
    st.cache_data.clear()
    # Reset file uploader keys
    st.session_state.file_uploader_key += 1
    # Clear current files
    st.session_state.current_files = {"resume": None, "jd": None}

def extract_candidate_name_from_filename(filename):
    """Fallback: Extract candidate name from resume filename"""
    if not filename or filename == "Unknown":
        return "Unknown Candidate"
    
    # Remove file extension
    name = filename.rsplit('.', 1)[0]
    
    # Clean up common resume filename patterns
    cleanup_words = ['resume', 'cv', 'curriculum', 'vitae', '_', '-', 'final', 'updated', 'new', 'latest']
    
    # Split by common separators and clean
    parts = name.replace('_', ' ').replace('-', ' ').split()
    cleaned_parts = []
    
    for part in parts:
        if part.lower() not in cleanup_words and len(part) > 1:
            cleaned_parts.append(part.title())
    
    if cleaned_parts:
        candidate_name = ' '.join(cleaned_parts[:3])  # Take first 3 meaningful parts
    else:
        candidate_name = name.replace('_', ' ').replace('-', ' ').title()
    
    return candidate_name if len(candidate_name) > 0 else "Unknown Candidate"

def save_result_to_history(result):
    """Save analysis result to session history"""
    if result and result not in st.session_state.results:
        result_with_timestamp = result.copy()
        result_with_timestamp["analysis_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Candidate name is now included in the backend response
        if not result_with_timestamp.get("candidate_name"):
            # Fallback to filename extraction for legacy results
            resume_filename = result.get("resume_filename", "Unknown")
            result_with_timestamp["candidate_name"] = extract_candidate_name_from_filename(resume_filename)
        
        st.session_state.results.append(result_with_timestamp)

def get_score_color(score):
    """Get color based on score"""
    if score >= 80:
        return "#27ae60"  # Green
    elif score >= 60:
        return "#f39c12"  # Orange
    elif score >= 40:
        return "#e67e22"  # Dark Orange
    else:
        return "#e74c3c"  # Red

# ===========================
# App Title
# ===========================
st.markdown('<div class="title">📄 Resume Relevance Check</div>', unsafe_allow_html=True)

# ===========================
# Navigation - Removed Detailed Report
# ===========================
page = st.sidebar.radio("Navigate", ["🏠 Home", "📈 Dashboard"], key="navigation")

# ===========================
# Home Page
# ===========================
if page == "🏠 Home":
    st.markdown('<p class="section-header">Upload Resume and Job Description</p>', unsafe_allow_html=True)
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Resume Upload")
        uploaded_resume = st.file_uploader(
            "Choose resume file", 
            type=["pdf", "docx", "txt"], 
            key=f"resume_uploader_{st.session_state.file_uploader_key}",
            help="Supported formats: PDF, DOCX, TXT"
        )
        if uploaded_resume:
            st.success(f"✅ Resume uploaded: {uploaded_resume.name}")
            st.session_state.current_files["resume"] = uploaded_resume
        elif st.session_state.reset_trigger:
            # Clear the file from session state after reset
            st.session_state.current_files["resume"] = None
    
    with col2:
        st.subheader("📋 Job Description Upload")
        uploaded_jd = st.file_uploader(
            "Choose job description file", 
            type=["pdf", "docx", "txt"], 
            key=f"jd_uploader_{st.session_state.file_uploader_key}",
            help="Supported formats: PDF, DOCX, TXT"
        )
        if uploaded_jd:
            st.success(f"✅ Job Description uploaded: {uploaded_jd.name}")
            st.session_state.current_files["jd"] = uploaded_jd
        elif st.session_state.reset_trigger:
            # Clear the file from session state after reset
            st.session_state.current_files["jd"] = None
    
    # Reset the trigger after handling
    if st.session_state.reset_trigger:
        st.session_state.reset_trigger = False
    
    # Analysis button
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        if st.button("🔍 Analyze Resume Match", type="primary", use_container_width=True):
            if st.session_state.current_files["resume"] and st.session_state.current_files["jd"]:
                with st.spinner("📄 Analyzing resume match..."):
                    try:
                        # Reset file pointers
                        st.session_state.current_files["resume"].seek(0)
                        st.session_state.current_files["jd"].seek(0)
                        
                        files = {
                            "resume": st.session_state.current_files["resume"],
                            "jd": st.session_state.current_files["jd"]
                        }
                        
                        response = requests.post("http://127.0.0.1:5000/match", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.detail_result = result
                            st.session_state.analysis_done = True
                            
                            # Save to history
                            save_result_to_history(result)
                            
                            st.success("✅ Analysis completed successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {response.json().get('error', 'Unknown error')}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to backend server. Please make sure it's running.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please upload both resume and job description files.")
    
    # Display results if analysis is done
    if st.session_state.analysis_done and st.session_state.detail_result:
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        result = st.session_state.detail_result
        
        # Score circle
        score = result["score"]
        color = get_score_color(score)
        
        st.markdown(f"""
            <div class="circle-score" style="background: linear-gradient(135deg, {color}, {color}dd);">
                {score}%
            </div>
        """, unsafe_allow_html=True)
        
        # Verdict and stats
        verdict = result.get("verdict", "Unknown")
        st.markdown(f"<h2 style='text-align: center; color: {color};'>Suitability: {verdict}</h2>", unsafe_allow_html=True)
        
        # Stats
        matched_count = len(result.get("matched_skills", []))
        total_count = result.get("total_skills_required", 0)
        missing_count = len(result.get("missing_skills", []))
        
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-box">
                <h3>{matched_count}</h3>
                <p>Skills Matched</p>
            </div>
            <div class="stat-box" style="background: linear-gradient(145deg, #e74c3c, #c0392b);">
                <h3>{missing_count}</h3>
                <p>Skills Missing</p>
            </div>
            <div class="stat-box" style="background: linear-gradient(145deg, #9b59b6, #8e44ad);">
                <h3>{total_count}</h3>
                <p>Total Required</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Skills display
        if result.get("matched_skills"):
            st.markdown('<div class="card"><b>✅ Matched Skills:</b><br><br>', unsafe_allow_html=True)
            skills_html = ""
            for skill in result["matched_skills"]:
                skills_html += f'<span class="skill-tag matched-skill-tag">{skill.title()}</span>'
            st.markdown(skills_html + '</div>', unsafe_allow_html=True)
        
        if result.get("missing_skills"):
            st.markdown('<div class="card"><b>❌ Missing Skills:</b><br><br>', unsafe_allow_html=True)
            skills_html = ""
            for skill in result["missing_skills"]:
                skills_html += f'<span class="skill-tag">{skill.title()}</span>'
            st.markdown(skills_html + '</div>', unsafe_allow_html=True)
        
        # Improvement suggestions
        improvement_plan = result.get("improvement_plan", [])
        if improvement_plan:
            st.markdown('<div class="card"><b>🎯 Top Improvement Suggestions:</b></div>', unsafe_allow_html=True)
            
            # Show top 3 high priority suggestions
            high_priority = [item for item in improvement_plan if item.get("priority") == "High"][:3]
            for item in high_priority:
                st.markdown(f"""
                <div class="improvement-item priority-high">
                    <h4>🎯 {item['skill']} ({item.get('category', 'General')})</h4>
                    <p>{item['suggestion']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Reset button - Always show for better UX
    st.markdown("<br>", unsafe_allow_html=True)
    col_reset1, col_reset2, col_reset3 = st.columns([1, 2, 1])
    with col_reset2:
        # Show different button text based on state
        button_text = "🔄 Reset & Upload New Files" if st.session_state.analysis_done else "🗑️ Clear Uploaded Files"
        button_disabled = not (st.session_state.current_files["resume"] or st.session_state.current_files["jd"] or st.session_state.analysis_done)
        
        if st.button(button_text, type="secondary", use_container_width=True, key="reset_button", disabled=button_disabled):
            # Force clear everything
            force_reset_file_uploaders()
            reset_analysis()
            st.success("✅ All files cleared! Ready for new uploads.")
            
    # Show current file status
    if st.session_state.current_files["resume"] or st.session_state.current_files["jd"]:
        st.markdown("---")
        st.markdown("**📁 Current Files:**")
        if st.session_state.current_files["resume"]:
            st.markdown(f"📄 Resume: `{st.session_state.current_files['resume'].name}`")
        if st.session_state.current_files["jd"]:
            st.markdown(f"📋 Job Description: `{st.session_state.current_files['jd'].name}`")

# ===========================
# Dashboard Page
# ===========================
elif page == "📈 Dashboard":
    st.markdown('<p class="section-header">📊 Analysis Dashboard</p>', unsafe_allow_html=True)
    
    if st.session_state.results:
        # Summary statistics
        df = pd.DataFrame(st.session_state.results)
        
        # Ensure candidate_name column exists and is properly populated
        if 'candidate_name' not in df.columns or df['candidate_name'].isna().any():
            # For existing results without candidate names, try to extract from backend if possible
            for idx, row in df.iterrows():
                if pd.isna(row.get('candidate_name')) or row.get('candidate_name') == 'Unknown Candidate':
                    # Use filename as fallback since we can't re-process the original file
                    df.at[idx, 'candidate_name'] = extract_candidate_name_from_filename(row.get('resume_filename', 'Unknown'))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Analyses", len(df))
        with col2:
            avg_score = df['score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}%")
        with col3:
            high_scores = len(df[df['score'] >= 70])
            st.metric("High Scores", f"{high_scores}")
        with col4:
            recent_score = df.iloc[-1]['score'] if not df.empty else 0
            st.metric("Latest Score", f"{recent_score}%")
        
        # Top candidates section
        st.markdown("### 🏆 Top Performing Candidates")
        if len(df) >= 3:
            top_candidates = df.nlargest(3, 'score')[['candidate_name', 'score', 'verdict', 'analysis_time']]
            
            cols = st.columns(3)
            for idx, (_, candidate) in enumerate(top_candidates.iterrows()):
                with cols[idx]:
                    rank_emoji = ["🥇", "🥈", "🥉"][idx]
                    st.markdown(f"""
                    <div style="
                        padding: 15px; 
                        border-radius: 10px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-align: center;
                        margin: 5px 0;
                    ">
                        <h3>{rank_emoji} Rank {idx + 1}</h3>
                        <h4>{candidate['candidate_name']}</h4>
                        <h2>{candidate['score']}%</h2>
                        <p>{candidate['verdict']}</p>
                        <small>{candidate['analysis_time']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Need at least 3 analyses to show top candidates")
        
        # Results table
        st.markdown("### 📋 Analysis History")
        
        # Prepare display dataframe
        display_df = df[['analysis_time', 'candidate_name', 'resume_filename', 'score', 'verdict', 'skills_matched', 'total_skills_required']].copy()
        display_df.columns = ['Analysis Time', 'Candidate', 'Resume File', 'Score (%)', 'Verdict', 'Skills Matched', 'Total Required']
        
        # Format the data for better display
        display_df['Resume File'] = display_df['Resume File'].apply(lambda x: x if len(str(x)) <= 25 else str(x)[:22] + "...")
        display_df['Candidate'] = display_df['Candidate'].apply(lambda x: x if len(str(x)) <= 20 else str(x)[:17] + "...")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score (%)": st.column_config.ProgressColumn(
                    "Score (%)",
                    help="Resume match percentage",
                    min_value=0,
                    max_value=100,
                ),
                "Analysis Time": st.column_config.DatetimeColumn(
                    "Analysis Time",
                    format="DD/MM/YY HH:mm",
                ),
            }
        )
        
        # Score distribution chart
        if len(df) > 1:
            st.markdown("### 📈 Score Trend")
            st.line_chart(df.set_index('analysis_time')['score'])
        
        # Detailed analysis section
        st.markdown("### 🔍 Detailed Analysis View")
        
        # Allow user to select a specific analysis to view details
        if len(df) > 0:
            analysis_options = []
            for idx, row in df.iterrows():
                candidate = row.get('candidate_name', 'Unknown')
                score = row.get('score', 0)
                analysis_time = row.get('analysis_time', 'Unknown')
                analysis_options.append(f"{candidate} - {score}% ({analysis_time})")
            
            selected_analysis = st.selectbox(
                "Select analysis to view details:",
                options=range(len(analysis_options)),
                format_func=lambda x: analysis_options[x],
                key="analysis_selector"
            )
            
            if selected_analysis is not None:
                selected_row = df.iloc[selected_analysis]
                
                # Display detailed info in expandable sections
                with st.expander("📄 Analysis Details", expanded=False):
                    col_detail1, col_detail2 = st.columns(2)
                    
                    with col_detail1:
                        st.markdown(f"**👤 Candidate:** {selected_row.get('candidate_name', 'Unknown')}")
                        st.markdown(f"**📄 Resume:** {selected_row.get('resume_filename', 'Unknown')}")
                        st.markdown(f"**📋 Job Description:** {selected_row.get('jd_filename', 'Unknown')}")
                        st.markdown(f"**📅 Analysis Date:** {selected_row.get('analysis_time', 'Unknown')}")
                    
                    with col_detail2:
                        st.markdown(f"**🎯 Score:** {selected_row.get('score', 0)}%")
                        st.markdown(f"**📊 Verdict:** {selected_row.get('verdict', 'Unknown')}")
                        st.markdown(f"**✅ Skills Matched:** {selected_row.get('skills_matched', 0)}")
                        st.markdown(f"**📋 Total Required:** {selected_row.get('total_skills_required', 0)}")
                
                # Show matched and missing skills if available
                if selected_row.get('matched_skills'):
                    with st.expander("✅ Matched Skills", expanded=False):
                        matched_skills = selected_row.get('matched_skills', [])
                        if matched_skills:
                            skills_text = " • ".join([f"`{skill}`" for skill in matched_skills])
                            st.markdown(skills_text)
                        else:
                            st.info("No matched skills recorded")
                
                if selected_row.get('missing_skills'):
                    with st.expander("❌ Missing Skills", expanded=False):
                        missing_skills = selected_row.get('missing_skills', [])
                        if missing_skills:
                            skills_text = " • ".join([f"`{skill}`" for skill in missing_skills])
                            st.markdown(skills_text)
                        else:
                            st.info("No missing skills recorded")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.results = []
            st.rerun()
            
    else:
        st.info("📊 No analysis data available yet.")
        st.markdown("""
        <div class="card">
            <h3>Welcome to the Dashboard!</h3>
            <p>This dashboard will show your analysis history and statistics once you start analyzing resumes.</p>
            <p>Go to the Home page to upload and analyze your first resume.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Placeholder image
        st.image("https://img.freepik.com/free-vector/recruitment-concept-illustration_114360-3704.jpg", 
                width=400, caption="Start analyzing resumes to see your dashboard")

# ===========================
# Sidebar Info
# ===========================
with st.sidebar:
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This tool helps you:
    - 📊 Analyze resume-job match
    - 🎯 Identify skill gaps
    - 💡 Get improvement suggestions
    - 📈 Track your progress
    """)
    
    if st.session_state.analysis_done:
        st.markdown("---")
        st.markdown("### 📢 Quick Stats")
        result = st.session_state.detail_result
        if result:
            st.metric("Current Score", f"{result['score']}%")
            st.metric("Missing Skills", len(result.get('missing_skills', [])))
            st.metric("Matched Skills", len(result.get('matched_skills', [])))
            
            # Show current file names
            st.markdown("---")
            st.markdown("### 📁 Current Analysis")
            if result.get('resume_filename'):
                resume_name = result['resume_filename']
                if len(resume_name) > 20:
                    resume_name = resume_name[:17] + "..."
                st.markdown(f"📄 **Resume:** {resume_name}")
                
                # Show extracted candidate name
                candidate_name = extract_candidate_name_from_filename(result['resume_filename'])
                st.markdown(f"👤 **Candidate:** {candidate_name}")
            if result.get('jd_filename'):
                jd_name = result['jd_filename']
                if len(jd_name) > 20:
                    jd_name = jd_name[:17] + "..."
                st.markdown(f"📋 **Job Desc:** {jd_name}")
   