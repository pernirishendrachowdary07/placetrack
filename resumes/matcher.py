"""
matcher.py - Resume Parsing and Skill Matching Engine
Extracts readable text from PDF/TXT documents and computes match scores,
matched skills, and missing skills against job requirements.
"""
import os
import re
from pypdf import PdfReader


def extract_text(file_obj_or_path):
    """
    Extract readable text from a PDF or plain TXT file.
    
    Returns:
        str: Clean extracted text, or empty string if no readable text is found
             (e.g., in scanned/image-only PDFs).
    """
    text_content = []

    # Identify filename for extension checking
    if hasattr(file_obj_or_path, 'name'):
        filename = file_obj_or_path.name
    else:
        filename = str(file_obj_or_path)

    ext = os.path.splitext(filename)[1].lower()

    if ext == '.pdf':
        try:
            # Ensure file pointer is at the beginning
            if hasattr(file_obj_or_path, 'seek'):
                file_obj_or_path.seek(0)

            reader = PdfReader(file_obj_or_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        except Exception:
            return ""

    elif ext == '.txt':
        try:
            if hasattr(file_obj_or_path, 'seek'):
                file_obj_or_path.seek(0)
                raw_bytes = file_obj_or_path.read()
                if isinstance(raw_bytes, bytes):
                    text_content.append(raw_bytes.decode('utf-8', errors='ignore'))
                else:
                    text_content.append(str(raw_bytes))
            else:
                with open(file_obj_or_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content.append(f.read())
        except Exception:
            return ""

    full_text = "\n".join(text_content).strip()
    return full_text


def match(resume_text, job_skills_or_text):
    """
    Calculate compatibility between candidate resume and job required skills.
    
    Args:
        resume_text (str): Plain text from candidate resume.
        job_skills_or_text (str): Comma-separated required skills or job text.
        
    Returns:
        dict: {
            'score': float,              # Match percentage (0.0 to 100.0)
            'matched_skills': list[str], # Skills present in resume
            'missing_skills': list[str], # Skills absent from resume
            'total_skills': int
        }
    """
    if not resume_text or not job_skills_or_text:
        return {
            'score': 0.0,
            'matched_skills': [],
            'missing_skills': [],
            'total_skills': 0,
        }

    # Extract required skills list (handles comma or semicolon separation)
    raw_skills = re.split(r'[,;]+', job_skills_or_text)
    skills = [s.strip() for s in raw_skills if s.strip()]

    if not skills:
        return {
            'score': 0.0,
            'matched_skills': [],
            'missing_skills': [],
            'total_skills': 0,
        }

    resume_lower = resume_text.lower()
    matched_skills = []
    missing_skills = []

    for skill in skills:
        # Match using word boundaries to avoid partial substring false-positives (e.g. 'c' inside 'cloud')
        # For multi-word or special chars like C++, C#, .NET:
        clean_skill = skill.lower()
        # Word boundary pattern if skill is alphanumeric
        if re.match(r'^[a-zA-Z0-9\s]+$', clean_skill):
            pattern = r'\b' + re.escape(clean_skill) + r'\b'
        else:
            pattern = re.escape(clean_skill)

        if re.search(pattern, resume_lower):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    total = len(skills)
    match_ratio = len(matched_skills) / total if total > 0 else 0.0
    score = round(match_ratio * 100.0, 1)

    return {
        'score': score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'total_skills': total,
    }
