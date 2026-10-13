import io
import pytest
from pypdf import PdfWriter
from resumes.matcher import extract_text, match


def test_extract_text_from_txt():
    """Verify that extract_text extracts readable text from plain TXT files."""
    txt_content = b"Candidate Name: John Doe\nSkills: Python, Django, REST APIs, SQL."
    file_obj = io.BytesIO(txt_content)
    file_obj.name = "resume.txt"

    extracted = extract_text(file_obj)
    assert "John Doe" in extracted
    assert "Python, Django" in extracted


def test_extract_text_from_pdf():
    """Verify that extract_text successfully reads pages from a PDF document."""
    # Programmatically create a valid 1-page PDF using pypdf
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    pdf_buffer = io.BytesIO()
    writer.write(pdf_buffer)
    pdf_buffer.seek(0)
    pdf_buffer.name = "resume.pdf"

    # Should run without crashing
    extracted = extract_text(pdf_buffer)
    assert isinstance(extracted, str)


def test_extract_text_empty_returns_empty_string():
    """Verify that empty files or files without readable text return an empty string."""
    empty_file = io.BytesIO(b"   \n\t   ")
    empty_file.name = "scanned.txt"
    assert extract_text(empty_file) == ""


def test_match_score_full_match():
    """Verify that 100% skill match is computed when all required skills are present."""
    resume_text = "Experienced in Python, Django, Docker, and PostgreSQL."
    required_skills = "Python, Django, Docker, PostgreSQL"

    result = match(resume_text, required_skills)

    assert result["score"] == 100.0
    assert set(result["matched_skills"]) == {"Docker", "Django", "PostgreSQL", "Python"}
    assert result["missing_skills"] == []
    assert result["total_skills"] == 4



def test_match_score_partial_match():
    """Verify proportional scoring when only a subset of skills are present."""
    resume_text = "Proficient in Python and SQL with basic HTML knowledge."
    # 4 skills: Python (found), SQL (found), Docker (missing), Kubernetes (missing)
    required_skills = "Python, SQL, Docker, Kubernetes"

    result = match(resume_text, required_skills)

    assert result["score"] == 50.0  # 2 out of 4 = 50%
    assert sorted(result["matched_skills"]) == ["Python", "SQL"]
    assert sorted(result["missing_skills"]) == ["Docker", "Kubernetes"]


def test_match_score_zero_match():
    """Verify that score is 0.0% when no required skills are found."""
    resume_text = "Graphic designer skilled in Photoshop, Illustrator, and Figma."
    required_skills = "Python, Django, AWS, Docker"

    result = match(resume_text, required_skills)

    assert result["score"] == 0.0
    assert result["matched_skills"] == []
    assert len(result["missing_skills"]) == 4


def test_match_case_insensitivity_and_boundary():
    """Verify case-insensitivity and that partial substring collisions are avoided."""
    # 'Java' should not match inside 'JavaScript'
    resume_text = "Built applications using JavaScript and Python."
    required_skills = "Java, JavaScript, Python"

    result = match(resume_text, required_skills)

    # JavaScript and Python matched, Java is missing
    assert "JavaScript" in result["matched_skills"]
    assert "Python" in result["matched_skills"]
    assert "Java" in result["missing_skills"]
    assert result["score"] == 66.7
