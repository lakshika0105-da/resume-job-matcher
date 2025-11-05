#this is wo latest claude wala code
#THIS IS THE RUNNNNN WALAA CODDEEE FINALL AFTER AFTERRR AFTERR
import sys
import json
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(txt):
    """Convert text to lowercase and remove special characters"""
    txt = txt.lower()
    txt = re.sub(r'[^a-z0-9\s]', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt)
    return txt.strip()

def check_skill_in_resume(skill, resume_text):
    """
    Check if a skill exists in resume with common variations
    """
    resume_lower = resume_text.lower()
    skill_lower = skill.lower()
    
    # Direct match
    if skill_lower in resume_lower:
        return True
    
    # Check common variations
    variations = {
        'javascript': ['js', 'javascript'],
        'python': ['python', 'python3'],
        'react': ['react', 'reactjs'],
        'node.js': ['node', 'nodejs'],
        'html': ['html', 'html5'],
        'css': ['css', 'css3']
    }
    
    if skill_lower in variations:
        for variant in variations[skill_lower]:
            if variant in resume_lower:
                return True
    
    return False

def calculate_ml_score(resume_text, job_requirements):
    """
    MACHINE LEARNING PART:
    Uses TF-IDF Vectorization and Cosine Similarity
    Compares resume text with job requirements text
    """
    # TEXT 1: Clean resume text
    cleaned_resume = clean_text(resume_text)
    
    # TEXT 2: Combine all job requirements into one text
    required_skills = ' '.join(job_requirements['skills'])
    required_keywords = ' '.join(job_requirements.get('keywords', []))
    requirements_text = clean_text(required_skills + ' ' + required_keywords)
    
    try:
        # Convert both texts to numerical vectors using TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([cleaned_resume, requirements_text])
        
        # Calculate Cosine Similarity (angle between vectors)
        similarity_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        # Convert to percentage
        ml_match_percentage = round(similarity_score * 100, 2)
        
        return ml_match_percentage
        
    except Exception as e:
        return 0.0

def analyze_resume(resume_txt, job):
    """Main function: Analyze resume using ML and skill matching"""
    
    # Load job requirements from JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(current_dir, 'job_requirements.json')
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
    except Exception as e:
        return {"error": f"Could not load job requirements: {str(e)}"}
    
    # Check if job role exists
    if job not in job_data:
        return {"error": f"Job role '{job}' not found"}
    
    requirements = job_data[job]
    cleaned_resume = clean_text(resume_txt)
    
    # Get required skills for the job
    skills_list = requirements['skills']
    
    # Find which skills are present and which are missing
    present = []
    missing = []
    
    for skill in skills_list:
        if check_skill_in_resume(skill, cleaned_resume):
            present.append(skill)
        else:
            missing.append(skill)
    
    # Calculate skill match percentage
    total_skills = len(skills_list)
    found_skills = len(present)
    skill_match = round((found_skills / total_skills * 100), 2) if total_skills > 0 else 0
    
    # ML ALGORITHM: Calculate similarity using TF-IDF + Cosine Similarity
    ml_score = calculate_ml_score(resume_txt, requirements)
    
    # Combined final score (weighted average)
    # 60% from skill matching + 40% from ML algorithm
    final_score = round((skill_match * 0.6) + (ml_score * 0.4), 2)
    
    # Return complete results
    return {
        "present_skills": present,
        "missing_skills": missing,
        "skill_match_percentage": skill_match,
        "ml_similarity_score": ml_score,
        "final_match_score": final_score,
        "skills_count": {
            "found": found_skills,
            "total": total_skills
        }
    }

if __name__ == "__main__":
    # Check if correct arguments are provided
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Usage: python script.py <resume_text> <job_role>"}))
        sys.exit(1)
    
    resume_text = sys.argv[1]
    job_role = sys.argv[2]
    
    # Analyze the resume
    result = analyze_resume(resume_text, job_role)
    
    # Print result as JSON
    print(json.dumps(result, indent=4, ensure_ascii=False))

    
