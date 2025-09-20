from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from typing import Dict, List, Tuple

# Try to import sentence transformers, fallback if not available
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    model = SentenceTransformer("all-MiniLM-L6-v2")
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    model = None

def hard_match_score(resume_text: str, jd_text: str) -> float:
    """
    Calculate exact keyword matching score
    """
    try:
        # Use TfidfVectorizer for better keyword importance
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams
            lowercase=True
        )
        
        # Fit on job description to get relevant terms
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return max(0.0, min(1.0, similarity))
        
    except Exception as e:
        print(f"Error in hard matching: {e}")
        # Fallback to simple word overlap
        jd_words = set(jd_text.lower().split())
        resume_words = set(resume_text.lower().split())
        if len(jd_words) == 0:
            return 0.0
        overlap = len(jd_words.intersection(resume_words))
        return overlap / len(jd_words)

def semantic_match_score(resume_text: str, jd_text: str) -> float:
    """
    Calculate semantic similarity using sentence transformers
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE or model is None:
        # Fallback to TF-IDF based semantic matching
        return tfidf_semantic_match(resume_text, jd_text)
    
    try:
        # Encode both texts
        resume_emb = model.encode(resume_text, convert_to_tensor=True)
        jd_emb = model.encode(jd_text, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = util.cos_sim(resume_emb, jd_emb).item()
        
        return max(0.0, min(1.0, similarity))
        
    except Exception as e:
        print(f"Error in semantic matching: {e}")
        return tfidf_semantic_match(resume_text, jd_text)

def tfidf_semantic_match(resume_text: str, jd_text: str) -> float:
    """
    Fallback semantic matching using TF-IDF
    """
    try:
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            lowercase=True,
            min_df=1
        )
        
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return max(0.0, min(1.0, similarity))
        
    except Exception as e:
        print(f"Error in TF-IDF semantic matching: {e}")
        return 0.0

def section_wise_matching(resume_sections: Dict[str, str], jd_text: str) -> Dict[str, float]:
    """
    Calculate matching scores for different resume sections
    """
    section_scores = {}
    
    for section, content in resume_sections.items():
        if content.strip():
            hard_score = hard_match_score(content, jd_text)
            semantic_score = semantic_match_score(content, jd_text)
            combined_score = (0.6 * hard_score + 0.4 * semantic_score)
            section_scores[section] = combined_score
        else:
            section_scores[section] = 0.0
    
    return section_scores

def skill_frequency_analysis(resume_text: str, jd_text: str, skills_list: List[str]) -> Dict[str, Dict[str, int]]:
    """
    Analyze frequency of skills mentioned in both resume and JD
    """
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    
    skill_analysis = {
        'resume_freq': {},
        'jd_freq': {},
        'skill_importance': {}
    }
    
    for skill in skills_list:
        skill_lower = skill.lower()
        
        # Count occurrences
        resume_count = len(re.findall(r'\b' + re.escape(skill_lower) + r'\b', resume_lower))
        jd_count = len(re.findall(r'\b' + re.escape(skill_lower) + r'\b', jd_lower))
        
        skill_analysis['resume_freq'][skill] = resume_count
        skill_analysis['jd_freq'][skill] = jd_count
        
        # Calculate importance (higher JD frequency = more important)
        skill_analysis['skill_importance'][skill] = jd_count
    
    return skill_analysis

def combined_score(resume_text: str, jd_text: str, weights: Dict[str, float] = None) -> float:
    """
    Calculate combined matching score with configurable weights
    """
    if weights is None:
        weights = {'hard': 0.4, 'semantic': 0.6}
    
    hard_score = hard_match_score(resume_text, jd_text)
    semantic_score = semantic_match_score(resume_text, jd_text)
    
    combined = (weights['hard'] * hard_score + weights['semantic'] * semantic_score)
    
    return round(combined * 100, 2)

def advanced_skill_matching(resume_text: str, jd_text: str, skills_dict: Dict[str, List[str]]) -> Dict[str, any]:
    """
    Advanced skill matching with category-wise analysis
    """
    results = {
        'category_scores': {},
        'matched_skills_by_category': {},
        'missing_skills_by_category': {},
        'skill_coverage': {},
        'overall_score': 0.0
    }
    
    total_score = 0.0
    total_categories = 0
    
    for category, skills in skills_dict.items():
        category_matched = []
        category_missing = []
        category_score = 0.0
        
        for skill in skills:
            skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(skill_pattern, resume_text.lower()):
                category_matched.append(skill)
            elif re.search(skill_pattern, jd_text.lower()):
                category_missing.append(skill)
        
        # Calculate category score
        total_skills_in_jd = len([s for s in skills if re.search(r'\b' + re.escape(s.lower()) + r'\b', jd_text.lower())])
        if total_skills_in_jd > 0:
            category_score = len(category_matched) / total_skills_in_jd
            total_score += category_score
            total_categories += 1
        
        results['category_scores'][category] = round(category_score * 100, 1)
        results['matched_skills_by_category'][category] = category_matched
        results['missing_skills_by_category'][category] = category_missing
        results['skill_coverage'][category] = {
            'matched': len(category_matched),
            'total_required': total_skills_in_jd,
            'coverage_percent': round(category_score * 100, 1) if total_skills_in_jd > 0 else 0
        }
    
    # Calculate overall score
    if total_categories > 0:
        results['overall_score'] = round((total_score / total_categories) * 100, 1)
    
    return results

def get_match_insights(resume_text: str, jd_text: str, skills_dict: Dict[str, List[str]]) -> Dict[str, any]:
    """
    Generate detailed insights about the resume-JD match
    """
    # Basic scores
    hard_score = hard_match_score(resume_text, jd_text)
    semantic_score = semantic_match_score(resume_text, jd_text)
    combined = combined_score(resume_text, jd_text)
    
    # Advanced skill analysis
    skill_analysis = advanced_skill_matching(resume_text, jd_text, skills_dict)
    
    # Text length analysis
    resume_word_count = len(resume_text.split())
    jd_word_count = len(jd_text.split())
    
    # Extract key phrases (most important terms from JD)
    key_phrases = extract_key_phrases(jd_text)
    
    insights = {
        'scores': {
            'hard_match': round(hard_score * 100, 1),
            'semantic_match': round(semantic_score * 100, 1),
            'combined_score': combined,
            'overall_skill_score': skill_analysis['overall_score']
        },
        'skill_analysis': skill_analysis,
        'text_analysis': {
            'resume_word_count': resume_word_count,
            'jd_word_count': jd_word_count,
            'resume_length_score': min(100, (resume_word_count / max(jd_word_count * 0.8, 100)) * 100)
        },
        'key_phrases': key_phrases,
        'recommendations': generate_recommendations(skill_analysis, hard_score, semantic_score)
    }
    
    return insights

def extract_key_phrases(text: str, top_n: int = 10) -> List[str]:
    """
    Extract key phrases from job description
    """
    try:
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(2, 3),
            lowercase=True
        )
        
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        # Get top phrases
        phrase_scores = list(zip(feature_names, scores))
        phrase_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [phrase for phrase, score in phrase_scores[:top_n] if score > 0]
        
    except Exception as e:
        print(f"Error extracting key phrases: {e}")
        return []

def generate_recommendations(skill_analysis: Dict, hard_score: float, semantic_score: float) -> List[str]:
    """
    Generate personalized recommendations based on analysis
    """
    recommendations = []
    
    # Score-based recommendations
    if hard_score < 0.3:
        recommendations.append("Include more specific keywords from the job description in your resume")
    
    if semantic_score < 0.4:
        recommendations.append("Restructure your resume content to better align with the job requirements")
    
    # Skill-based recommendations
    for category, skills in skill_analysis['missing_skills_by_category'].items():
        if skills:
            if category in ['programming', 'data_science']:
                recommendations.append(f"Consider gaining experience in {category} skills: {', '.join(skills[:3])}")
            else:
                recommendations.append(f"Highlight any experience with {category} tools: {', '.join(skills[:2])}")
    
    # Category coverage recommendations
    for category, coverage in skill_analysis['skill_coverage'].items():
        if coverage['coverage_percent'] < 30 and coverage['total_required'] > 0:
            recommendations.append(f"Focus on developing {category} skills as they are important for this role")
    
    return recommendations[:5]  # Return top 5 recommendations