import google.generativeai as genai
import json
import re
import os

# AWS k liye environment variable wala tareeqa hi best hai
api_key = os.environ.get('GEMINI_API_KEY')

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set!")

genai.configure(api_key=api_key)

def split_full_name(full_name):
    """Splits full name into First, Middle, and Last Name."""
    name_parts = full_name.split()
    first_name = name_parts[0] if len(name_parts) > 0 else ""
    middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
    last_name = name_parts[-1] if len(name_parts) > 1 else ""
    return first_name, middle_name, last_name

def ats_extractor(resume_text):
    prompt = """
    Extract the following details from the resume in **valid JSON format only**:
    {
      "Full Name": "",
      "Email ID": "",
      "Phone Number": "",
      "Location": "",
      "LinkedIn ID": "",
      "GitHub Portfolio": "",
      "Summary": "",
      "Education": [
        {
          "Degree": "",
          "Institution": "",
          "Year": ""
        }
      ],
      "Employment Details": [
        {
          "Designation": "",
          "Duration": "",
          "Organization": ""
        }
      ],
      "Technical Skills": ["Skill1", "Skill2", "Skill3"],
      "Soft Skills": ["Skill1", "Skill2", "Skill3"]
    }

    - **Return only valid JSON**.
    - **Do not include any explanations or markdown formatting**.
    - If a field (like "GitHub Portfolio") is not found, return an empty string "" or empty list [].
    - For "Education", extract all degrees.
    - For "Location", extract the City and Country.
    """

    model = genai.GenerativeModel('models/gemini-2.5-flash') 
    response = model.generate_content([prompt, resume_text])

    raw_text = response.text.strip()
    cleaned_json = re.sub(r"```json\n|\n```", "", raw_text).strip()

    try:
        parsed_data = json.loads(cleaned_json)

        if isinstance(parsed_data, str):
            parsed_data = json.loads(parsed_data)

        # Process full name
        first_name, middle_name, last_name = split_full_name(parsed_data.get("Full Name", "Not Provided"))
        
        # Technical skills ko string banayein (database k liye behtar hai)
        technical_skills = ", ".join(parsed_data.get("Technical Skills", []))

        # Naya, behtar output
        formatted_output = {
            "First Name": first_name,
            "Middle Name": middle_name,
            "Last Name": last_name,
            "Email ID": parsed_data.get("Email ID", ""),
            "Phone Number": parsed_data.get("Phone Number", ""),
            "Location": parsed_data.get("Location", ""),
            "GitHub Portfolio": parsed_data.get("GitHub Portfolio", ""),
            "LinkedIn ID": parsed_data.get("LinkedIn ID", ""),
            "Summary": parsed_data.get("Summary", ""),
            "Education": parsed_data.get("Education", []),
            "Employment Details": parsed_data.get("Employment Details", []),
            "Technical Skills": technical_skills,
            "Soft Skills": parsed_data.get("Soft Skills", []) 
        }

        return formatted_output

    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_response": raw_text}
