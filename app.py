import streamlit as st
import fitz  # PyMuPDF
import spacy
from spacy.matcher import Matcher
import requests
import json
import time

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Expanded lists of keywords
skills_list = [
    "Python", "Java", "C++", "Machine Learning", "Deep Learning", "NLP", "Data Analysis", "SQL", "AWS", "Docker",
    "JavaScript", "React", "Node.js", "Angular", "Vue.js", "HTML", "CSS", "Ruby", "Rails", "PHP", "Swift", "Kotlin",
    "Android", "iOS", "Flutter", "Django", "Flask", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "Scikit-learn", "Keras", "Hadoop", "Spark", "Tableau", "Power BI", "Excel", "Git", "GitHub", "Bitbucket", "Jira",
    "Agile", "Scrum", "Kanban", "Project Management", "Leadership", "Team Management", "Communication", "Problem Solving",
    "Critical Thinking", "Creativity", "Innovation", "Adaptability", "Time Management", "Attention to Detail"
]

education_keywords = [
    "Bachelor", "Master", "B.Sc", "M.Sc", "PhD", "University", "College", "School", "Institute", "Degree", "Diploma",
    "Certification", "Course", "Training", "Program", "Graduate", "Postgraduate", "Doctorate"
]

experience_keywords = [
    "experience", "worked", "developed", "managed", "led", "internship", "intern", "project", "role", "position",
    "responsibility", "achievement", "accomplishment", "challenge", "solution", "strategy", "initiative", "leadership",
    "team", "collaboration", "communication", "problem-solving", "critical thinking", "creativity", "innovation",
    "adaptability", "time management", "attention to detail"
]

def extract_text_from_pdf(pdf_file):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def extract_skills(doc):
    skills = set()
    for token in doc:
        if token.text in skills_list:
            skills.add(token.text)
    return list(skills)

def extract_education(doc):
    education = []
    for sent in doc.sents:
        if any(keyword in sent.text for keyword in education_keywords):
            education.append(sent.text.strip())
    return education

def extract_experience(doc):
    experience = []
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in experience_keywords):
            experience.append(sent.text.strip())
    return experience

def call_ai_api(skills):
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyBL0CVjzkwFZwtWltrSoqydeDUv4wEYuT8"
    prompt = f"Hi GPT, I am working on improving my resume and would appreciate your help. Current skills: {', '.join(skills)}. Tell me more to improve it."
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    response = requests.post(api_url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to get response from AI API: {response.status_code}")
        return None

def suggest_improvements(skills, education, experience):
    suggestions = []
    
    # Show a spinner while waiting for the API response
    with st.spinner("Generating a curated response for you..."):
        # Call AI API for suggestions
        ai_response = call_ai_api(skills)
        
        # If API response is successful, add AI suggestions
        if ai_response and 'candidates' in ai_response and ai_response['candidates']:
            ai_suggestions = ai_response['candidates'][0]['content']['parts'][0]['text']
            suggestions.append(ai_suggestions)
        else:
            # Fallback to hardcoded suggestions if API fails
            suggestions.append("Consider adding more relevant skills to your resume. Aim for at least 10 key skills.")
            suggestions.append("Include your educational background. This includes degrees, certifications, and relevant courses.")
            suggestions.append("Add your work experience or internships. Highlight key roles, responsibilities, and achievements.")
            suggestions.append("Python is a highly sought skill; consider adding it if applicable.")
            suggestions.append("SQL is a valuable skill; consider adding it if applicable.")
            suggestions.append("Data Analysis is a sought-after skill; consider adding it if applicable.")
            suggestions.append("Machine Learning is a growing field; consider adding it if applicable.")
    
    return suggestions

def main():
    st.title("Resume Parser & Enhancer")
    st.write("Upload your resume PDF to extract key information and get improvement suggestions.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        text = extract_text_from_pdf(uploaded_file)
        if text:
            st.write("Text extracted successfully!")
            doc = nlp(text)
            st.write("NLP processing done!")

            st.header("Extracted Information")
            skills = extract_skills(doc)
            education = extract_education(doc)
            experience = extract_experience(doc)

            st.subheader("Skills")
            st.write(skills if skills else "No skills found.")

            st.subheader("Education")
            for edu in education:
                st.write(f"- {edu}")

            st.subheader("Experience")
            for exp in experience:
                st.write(f"- {exp}")

            st.header("Suggestions")
            suggestions = suggest_improvements(skills, education, experience)
            if suggestions:
                for suggestion in suggestions:
                    st.write(f"- {suggestion}")
            else:
                st.write("Your resume looks good!")
        else:
            st.error("Failed to extract text from the uploaded PDF.")

if __name__ == "__main__":
    main()