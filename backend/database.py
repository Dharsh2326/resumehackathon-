from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Text, DateTime, MetaData, Boolean
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import json
import os

# Create database directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Database connection
DATABASE_URL = "sqlite:///data/resumes.db"
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()

# Enhanced resumes table with more fields
resumes_table = Table(
    "resumes", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("candidate_name", String(255)),
    Column("resume_filename", String(255)),
    Column("jd_filename", String(255)),
    Column("overall_score", Float),
    Column("hard_match_score", Float),
    Column("semantic_match_score", Float),
    Column("verdict", String(50)),
    Column("matched_skills", Text),  # JSON string
    Column("missing_skills", Text),  # JSON string
    Column("improvement_plan", Text),  # JSON string
    Column("skill_categories", Text),  # JSON string
    Column("analysis_timestamp", DateTime, default=datetime.utcnow),
    Column("resume_word_count", Integer),
    Column("jd_word_count", Integer),
    Column("is_archived", Boolean, default=False),
    Column("notes", Text)
)

# Skills tracking table
skills_table = Table(
    "skills_tracking", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("skill_name", String(100)),
    Column("skill_category", String(50)),
    Column("frequency_in_jds", Integer, default=0),
    Column("frequency_in_resumes", Integer, default=0),
    Column("last_seen", DateTime, default=datetime.utcnow)
)

# Analysis sessions table for tracking multiple analyses
sessions_table = Table(
    "analysis_sessions", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("session_name", String(255)),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("total_analyses", Integer, default=0),
    Column("avg_score", Float, default=0.0),
    Column("is_active", Boolean, default=True)
)

# Create all tables
try:
    metadata.create_all(engine)
    print("Database tables created successfully")
except SQLAlchemyError as e:
    print(f"Error creating database tables: {e}")

class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.metadata = metadata
    
    def save_analysis_result(self, result_data):
        """Save analysis result to database"""
        try:
            with self.engine.connect() as conn:
                # Prepare data for insertion
                insert_data = {
                    'candidate_name': result_data.get('candidate_name', 'Unknown'),
                    'resume_filename': result_data.get('resume_filename', ''),
                    'jd_filename': result_data.get('jd_filename', ''),
                    'overall_score': result_data.get('score', 0),
                    'hard_match_score': result_data.get('hard_score', 0),
                    'semantic_match_score': result_data.get('semantic_score', 0),
                    'verdict': result_data.get('verdict', ''),
                    'matched_skills': json.dumps(result_data.get('matched_skills', [])),
                    'missing_skills': json.dumps(result_data.get('missing_skills', [])),
                    'improvement_plan': json.dumps(result_data.get('improvement_plan', [])),
                    'skill_categories': json.dumps(result_data.get('skill_categories', {})),
                    'resume_word_count': result_data.get('resume_word_count', 0),
                    'jd_word_count': result_data.get('jd_word_count', 0),
                    'notes': result_data.get('notes', '')
                }
                
                result = conn.execute(resumes_table.insert().values(**insert_data))
                conn.commit()
                return result.inserted_primary_key[0]
                
        except SQLAlchemyError as e:
            print(f"Error saving analysis result: {e}")
            return None
    
    def get_analysis_history(self, limit=50, archived=False):
        """Get analysis history from database"""
        try:
            with self.engine.connect() as conn:
                query = resumes_table.select().where(
                    resumes_table.c.is_archived == archived
                ).order_by(resumes_table.c.analysis_timestamp.desc()).limit(limit)
                
                result = conn.execute(query)
                
                history = []
                for row in result:
                    row_dict = dict(row._mapping)
                    # Parse JSON fields
                    row_dict['matched_skills'] = json.loads(row_dict['matched_skills'] or '[]')
                    row_dict['missing_skills'] = json.loads(row_dict['missing_skills'] or '[]')
                    row_dict['improvement_plan'] = json.loads(row_dict['improvement_plan'] or '[]')
                    row_dict['skill_categories'] = json.loads(row_dict['skill_categories'] or '{}')
                    history.append(row_dict)
                
                return history
                
        except SQLAlchemyError as e:
            print(f"Error retrieving analysis history: {e}")
            return []
    
    def get_analysis_statistics(self):
        """Get overall statistics"""
        try:
            with self.engine.connect() as conn:
                # Basic stats
                from sqlalchemy import func
                
                stats_query = conn.execute(
                    resumes_table.select().with_only_columns([
                        func.count(resumes_table.c.id).label('total_analyses'),
                        func.avg(resumes_table.c.overall_score).label('avg_score'),
                        func.max(resumes_table.c.overall_score).label('max_score'),
                        func.min(resumes_table.c.overall_score).label('min_score')
                    ]).where(resumes_table.c.is_archived == False)
                ).fetchone()
                
                if stats_query:
                    stats = dict(stats_query._mapping)
                    stats['avg_score'] = round(stats['avg_score'] or 0, 2)
                else:
                    stats = {
                        'total_analyses': 0,
                        'avg_score': 0,
                        'max_score': 0,
                        'min_score': 0
                    }
                
                # Score distribution
                score_ranges = {
                    'excellent': 0,  # 80+
                    'good': 0,       # 60-79
                    'average': 0,    # 40-59
                    'poor': 0        # <40
                }
                
                score_query = conn.execute(
                    resumes_table.select().with_only_columns([
                        resumes_table.c.overall_score
                    ]).where(resumes_table.c.is_archived == False)
                )
                
                for row in score_query:
                    score = row[0] or 0
                    if score >= 80:
                        score_ranges['excellent'] += 1
                    elif score >= 60:
                        score_ranges['good'] += 1
                    elif score >= 40:
                        score_ranges['average'] += 1
                    else:
                        score_ranges['poor'] += 1
                
                stats['score_distribution'] = score_ranges
                
                return stats
                
        except SQLAlchemyError as e:
            print(f"Error retrieving statistics: {e}")
            return {
                'total_analyses': 0,
                'avg_score': 0,
                'max_score': 0,
                'min_score': 0,
                'score_distribution': {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
            }
    
    def update_skills_tracking(self, jd_skills, resume_skills):
        """Update skills frequency tracking"""
        try:
            with self.engine.connect() as conn:
                # Update JD skills
                for skill in jd_skills:
                    # Check if skill exists
                    existing = conn.execute(
                        skills_table.select().where(skills_table.c.skill_name == skill)
                    ).fetchone()
                    
                    if existing:
                        # Update frequency
                        conn.execute(
                            skills_table.update().where(
                                skills_table.c.skill_name == skill
                            ).values(
                                frequency_in_jds=existing.frequency_in_jds + 1,
                                last_seen=datetime.utcnow()
                            )
                        )
                    else:
                        # Insert new skill
                        conn.execute(
                            skills_table.insert().values(
                                skill_name=skill,
                                skill_category='unknown',
                                frequency_in_jds=1,
                                frequency_in_resumes=0
                            )
                        )
                
                # Update resume skills
                for skill in resume_skills:
                    existing = conn.execute(
                        skills_table.select().where(skills_table.c.skill_name == skill)
                    ).fetchone()
                    
                    if existing:
                        conn.execute(
                            skills_table.update().where(
                                skills_table.c.skill_name == skill
                            ).values(
                                frequency_in_resumes=existing.frequency_in_resumes + 1,
                                last_seen=datetime.utcnow()
                            )
                        )
                    else:
                        conn.execute(
                            skills_table.insert().values(
                                skill_name=skill,
                                skill_category='unknown',
                                frequency_in_jds=0,
                                frequency_in_resumes=1
                            )
                        )
                
                conn.commit()
                
        except SQLAlchemyError as e:
            print(f"Error updating skills tracking: {e}")
    
    def get_trending_skills(self, limit=20):
        """Get most frequently requested skills"""
        try:
            with self.engine.connect() as conn:
                query = skills_table.select().order_by(
                    skills_table.c.frequency_in_jds.desc()
                ).limit(limit)
                
                result = conn.execute(query)
                return [dict(row._mapping) for row in result]
                
        except SQLAlchemyError as e:
            print(f"Error retrieving trending skills: {e}")
            return []
    
    def archive_analysis(self, analysis_id):
        """Archive an analysis"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    resumes_table.update().where(
                        resumes_table.c.id == analysis_id
                    ).values(is_archived=True)
                )
                conn.commit()
                return True
                
        except SQLAlchemyError as e:
            print(f"Error archiving analysis: {e}")
            return False
    
    def delete_analysis(self, analysis_id):
        """Permanently delete an analysis"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    resumes_table.delete().where(
                        resumes_table.c.id == analysis_id
                    )
                )
                conn.commit()
                return True
                
        except SQLAlchemyError as e:
            print(f"Error deleting analysis: {e}")
            return False
    
    def clear_all_data(self, confirm=False):
        """Clear all data from tables (use with caution)"""
        if not confirm:
            return False
            
        try:
            with self.engine.connect() as conn:
                conn.execute(resumes_table.delete())
                conn.execute(skills_table.delete())
                conn.execute(sessions_table.delete())
                conn.commit()
                return True
                
        except SQLAlchemyError as e:
            print(f"Error clearing data: {e}")
            return False
    
    def export_data(self, format='json'):
        """Export all data in specified format"""
        try:
            data = {
                'analyses': self.get_analysis_history(limit=1000),
                'statistics': self.get_analysis_statistics(),
                'trending_skills': self.get_trending_skills(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            if format == 'json':
                return json.dumps(data, indent=2, default=str)
            else:
                return data
                
        except Exception as e:
            print(f"Error exporting data: {e}")
            return None

# Initialize database manager
db_manager = DatabaseManager()

# Utility functions for backward compatibility
def save_result(result_data):
    """Save analysis result - backward compatible function"""
    return db_manager.save_analysis_result(result_data)

def get_history(limit=50):
    """Get analysis history - backward compatible function"""
    return db_manager.get_analysis_history(limit=limit)

def get_stats():
    """Get statistics - backward compatible function"""
    return db_manager.get_analysis_statistics()