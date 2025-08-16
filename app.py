# Resume Matcher Application

from flask import Flask, render_template, request
import re
import PyPDF2

app = Flask(__name__)

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def extract_keywords(text):
    common_words = {"in", "of", "for", "and", "the", "to", "a", "is", "on", "with", "as", "at", "by", "an", "be", "it", "this", "or", "that", "which", "from", "not", "are", "was", "were", "has", "have"}
    words = set(clean_text(text).split())
    return words - common_words

def compare_keywords(resume_text, job_text):
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_text)
    matched_keywords = resume_keywords & job_keywords
    missing_keywords = job_keywords - resume_keywords
    match_percentage = round((len(matched_keywords) / len(job_keywords)) * 100) if job_keywords else 0
    
    if match_percentage >= 80:
        match_label, match_class = "Excellent", "match-excellent"
    elif match_percentage >= 50:
        match_label, match_class = "Good", "match-good"
    else:
        match_label, match_class = "Average", "match-average"
    
    return matched_keywords, missing_keywords, match_percentage, match_label, match_class

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        resume_text = ""
        if 'resume_file' in request.files:
            pdf_file = request.files['resume_file']
            if pdf_file.filename.endswith('.pdf'):
                resume_text = extract_text_from_pdf(pdf_file)
        if request.form['resume_txt']:
            resume_text += request.form['resume_txt']
        job_text = request.form['job_txt']
        
        matched_keywords, missing_keywords, match_percentage, match_label, match_class = compare_keywords(resume_text, job_text)
        
        highlighted_resume = re.sub(f'({"|".join(matched_keywords)})', r'<mark>\1</mark>', resume_text, flags=re.IGNORECASE)
        
        return render_template('index.html', matched_keywords=matched_keywords, missing_keywords=missing_keywords,
                               match_percentage=match_percentage, match_label=match_label, match_class=match_class,
                               highlighted_resume=highlighted_resume, resume_text=resume_text, job_text=job_text)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)