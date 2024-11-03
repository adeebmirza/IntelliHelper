import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import docx
import re
import PyPDF2
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")

# Parse resume from different formats (PDF, DOCX, Text)
def parse_resume(resume_file):
    resume_text = ""
    if resume_file.filename.endswith('.docx'):
        doc = docx.Document(resume_file)
        resume_text = '\n'.join([para.text for para in doc.paragraphs])
    elif resume_file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(resume_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            resume_text += page.extract_text()
    else:
        resume_text = resume_file.read().decode('utf-8')
    
    return resume_text

# Helper function: normalize text
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text

# Extract key information from both resume and job description
def extract_keywords(text):
    doc = nlp(text)
    keywords = []

    # Extract noun chunks (phrases), entities, and verbs (actions)
    keywords.extend([chunk.text for chunk in doc.noun_chunks])
    keywords.extend([ent.text for ent in doc.ents])  # Named entities (skills, organizations, etc.)
    keywords.extend([token.text for token in doc if token.pos_ == 'VERB'])  # Extract verbs (actions)
    
    return ' '.join(keywords)
'''
# Function to boost certain critical keywords (like required skills)
def boost_critical_keywords(job_description, resume_text):
    critical_keywords = ['python', 'sql', 'machine learning', 'aws', 'docker', 'git']  # Example critical skills
    boost_factor = 1.5
    
    job_desc_normalized = normalize_text(job_description)
    resume_text_normalized = normalize_text(resume_text)
    
    for keyword in critical_keywords:
        if keyword in job_desc_normalized and keyword in resume_text_normalized:
            return boost_factor  # Increase similarity score if key skills match
    return 1  # No boost if no critical skill match
'''
# Update calculate_ats_score function to return more detailed feedback
def calculate_ats_score(resume_text, job_description):
    # Normalize text to ensure uniform comparison
    resume_text = normalize_text(resume_text)
    job_description = normalize_text(job_description)
    
    # Extract keywords
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)
    
    # Use TF-IDF to compare text similarity
    vectorizer = TfidfVectorizer().fit_transform([resume_keywords, job_keywords])
    vectors = vectorizer.toarray()
    
    cosine_sim = cosine_similarity(vectors)
    similarity_score = cosine_sim[0][1] * 100  # Base score


# Changed Item by Anas Ahmad as of (28/10/24)
    # Prepare detailed feedback
    feedback = {
        "score": round(similarity_score, 2),
        "keywords_matched": len(set(resume_keywords.split()).intersection(set(job_keywords.split()))),
        "total_keywords": len(set(job_keywords.split())),
        "recommendations": []
    }

    # Add recommendations based on the score
    if feedback["score"] < 60:
        feedback["recommendations"].append("Consider adding more relevant keywords from the job description to improve your resume's visibility to applicant tracking systems (ATS). Focus on including industry-specific terms and phrases that match the skills and qualifications outlined in the job listing. Additionally, make sure your experience section highlights measurable achievements that demonstrate your capabilities.")
    elif feedback["score"] < 80:
        feedback["recommendations"].append("Your resume is decent but can be improved with specific examples. Try to quantify your achievements where possible (e.g., 'increased sales by 20% over six months') and provide context for your roles. This can help potential employers better understand your impact in previous positions. Also, ensure that your skills section aligns closely with those mentioned in the job description to enhance relevance.")
    else:
        feedback["recommendations"].append("Great job! Your resume is well-tailored for this position. To take it to the next level, consider personalizing your summary or objective statement to reflect your enthusiasm for the role and how your unique skills can contribute to the company's goals. You might also want to include links to your professional online presence, such as a LinkedIn profile or a personal portfolio, to provide further insight into your qualifications.")

    return feedback  # Return score and feedback details