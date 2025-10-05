import sys
import json
import re
import os

def clean_text(txt):
    """Convert text to lowercase and remove special characters"""
    txt = txt.lower()
    txt = re.sub(r'[^a-z0-9\s]', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt)
    return txt.strip()

def analyze_resume(resume_txt, job):
    """Analyze resume and find matching skills"""
    
    # Load job requirements from JSON file
    current_dir = os.path.dirname(os.path.abspath(_file_))
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
        if skill.lower() in cleaned_resume:
            present.append(skill)
        else:
            missing.append(skill)
    
    # Return only present and missing skills
    return {
        "present_skills": present,
        "missing_skills": missing
    }

if _name_ == "_main_":
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
