import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/data/resumes.db')

# File upload configuration
UPLOAD_FOLDER = BASE_DIR / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.doc'}

# Server configuration
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
STREAMLIT_PORT = int(os.getenv('STREAMLIT_PORT', 8501))

# Analysis configuration
MATCHING_WEIGHTS = {
    'hard_match': 0.4,
    'semantic_match': 0.6
}

SCORE_THRESHOLDS = {
    'excellent': 80,
    'good': 60,
    'average': 40,
    'poor': 0
}

# Skills configuration - Enhanced with more comprehensive categories
SKILLS_CONFIG = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", 
        "rust", "scala", "r", "matlab", "php", "ruby", "swift", "kotlin"
    ],
    "data_science": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "data analysis", "statistics", "pandas", "numpy", 
        "scikit-learn", "tensorflow", "pytorch", "keras", "opencv", "matplotlib",
        "seaborn", "plotly", "jupyter", "anaconda", "data mining", "predictive modeling"
    ],
    "big_data": [
        "spark", "kafka", "hadoop", "pyspark", "hive", "storm", "flink", 
        "elasticsearch", "solr", "databricks", "snowflake", "redshift",
        "bigquery", "data pipeline", "etl", "data warehouse"
    ],
    "databases": [
        "sql", "mysql", "postgresql", "oracle", "sqlite", "nosql", "mongodb", 
        "cassandra", "redis", "dynamodb", "neo4j", "couchbase", "influxdb"
    ],
    "cloud_platforms": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", 
        "terraform", "ansible", "jenkins", "ci/cd", "devops", "serverless",
        "lambda", "cloud functions", "containerization"
    ],
    "web_technologies": [
        "html", "css", "react", "angular", "vue", "node.js", "express", 
        "django", "flask", "fastapi", "spring", "laravel", "bootstrap", 
        "sass", "less", "webpack", "babel"
    ],
    "mobile_development": [
        "android", "ios", "react native", "flutter", "xamarin", "ionic",
        "swift", "kotlin", "objective-c", "cordova"
    ],
    "tools_and_platforms": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", 
        "slack", "trello", "asana", "linux", "unix", "bash", "powershell",
        "vim", "vscode", "intellij", "eclipse"
    ],
    "business_intelligence": [
        "tableau", "power bi", "qlik", "looker", "excel", "google sheets",
        "business analysis", "data visualization", "dashboard", "reporting"
    ],
    "testing_qa": [
        "selenium", "junit", "testng", "pytest", "jest", "cypress", 
        "postman", "rest assured", "automation testing", "manual testing",
        "load testing", "performance testing", "unit testing"
    ],
    "soft_skills": [
        "communication", "leadership", "teamwork", "problem solving", 
        "analytical thinking", "project management", "agile", "scrum",
        "critical thinking", "time management", "adaptability", "creativity"
    ],
    "certifications": [
        "aws certified", "azure certified", "google certified", "pmp", 
        "scrum master", "comptia", "cisco", "microsoft certified",
        "oracle certified", "mongodb certified"
    ]
}

# UI Configuration
UI_CONFIG = {
    'theme': {
        'primary_color': '#3498db',
        'secondary_color': '#2c3e50',
        'success_color': '#27ae60',
        'warning_color': '#f39c12',
        'danger_color': '#e74c3c'
    },
    'score_colors': {
        'excellent': '#27ae60',  # Green
        'good': '#f39c12',       # Orange
        'average': '#e67e22',    # Dark Orange
        'poor': '#e74c3c'        # Red
    }
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': BASE_DIR / 'logs' / 'app.log'
}

# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# Environment-specific settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
TESTING = os.getenv('TESTING', 'False').lower() == 'true'

# Feature flags
FEATURES = {
    'advanced_matching': True,
    'skill_tracking': True,
    'export_functionality': True,
    'user_authentication': False,  # Future feature
    'batch_processing': False      # Future feature
}