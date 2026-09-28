import re
import json
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Make the model configurable. Llama3 is a solid default.
OLLAMA_MODEL = "qwen2.5:14b"

# Initialize Ollama
llm = OllamaLLM(model=OLLAMA_MODEL)

def summarize_cv(cv_text: str) -> str:
    """Uses the LLM to extract key skills and experience from the CV."""
    prompt = PromptTemplate.from_template(
        "You are an expert HR recruiter. Analyze the following CV and extract the core skills, years of experience, and ideal roles for this candidate.\n"
        "CV TEXT:\n{cv_text}\n\n"
        "SUMMARY:"
    )
    chain = prompt | llm
    return chain.invoke({"cv_text": cv_text})

def analyze_cv_for_params(cv_text: str) -> dict:
    """Uses the LLM to extract recommended roles, location, and summary."""
    prompt = PromptTemplate.from_template(
        "You are an expert HR recruiter. Analyze the following CV.\n"
        "1. Recommend 3 to 5 specific job titles (roles) this person should apply for.\n"
        "2. Extract the location or city where this person lives/works. If not found, use 'Buenos Aires, Argentina'.\n"
        "3. Provide a brief 3-sentence summary of their core skills.\n\n"
        "CV TEXT:\n{cv_text}\n\n"
        "Respond ONLY in valid JSON format like this:\n"
        "{{\"roles\": [\"Data Engineer\", \"Python Developer\"], \"location\": \"Capital Federal, Argentina\", \"summary\": \"Has 5 years of Python...\"}}"
    )
    chain = prompt | llm
    result_text = chain.invoke({"cv_text": cv_text})
    
    try:
        match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(result_text)
    except Exception as e:
        print(f"Error parsing LLM response for analyze_cv: {result_text}")
        return {
            "roles": ["IT Specialist", "Developer"],
            "location": "Buenos Aires, Argentina",
            "summary": "Experienced IT professional."
        }

def score_job(cv_summary: str, job_title: str, job_description: str) -> dict:
    """Scores a job description based on the CV summary."""
    prompt = PromptTemplate.from_template(
        "You are an expert HR recruiter evaluating a candidate's fit for a job.\n"
        "CANDIDATE SUMMARY:\n{cv_summary}\n\n"
        "JOB TITLE: {job_title}\n"
        "JOB DESCRIPTION:\n{job_description}\n\n"
        "Evaluate how well the candidate fits this job on a scale of 0 to 100. "
        "Also provide a one-sentence explanation.\n"
        "Respond ONLY in valid JSON format like this:\n"
        "{{\"score\": 85, \"explanation\": \"Strong match because...\"}}"
    )
    chain = prompt | llm
    result_text = chain.invoke({
        "cv_summary": cv_summary,
        "job_title": job_title,
        "job_description": job_description
    })
    
    # Try to parse the JSON
    try:
        # Simple extraction in case LLM added markdown backticks
        match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(result_text)
    except Exception as e:
        print(f"Error parsing LLM response: {result_text}")
        return {"score": 0, "explanation": "Failed to parse evaluation."}
