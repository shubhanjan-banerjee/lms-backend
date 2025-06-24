import pandas as pd
from typing import List, Dict, Any
import json

def calculate_proficiency(role: str, skill: str) -> List[Dict[str, int]]:
    print(f"Calculating proficiency for role: {role}, skill: {skill}")
    import math
    if not isinstance(role, str) or (isinstance(role, float) and math.isnan(role)):
        role = ""
    if not isinstance(skill, str) or (isinstance(skill, float) and math.isnan(skill)):
        skill = ""
    try:
        proficiency = {"Angular": 0, "React": 0, ".Net": 0, "SQL": 0, "Postgresql": 0, "AWS": 0, "Python": 0}

        if "Full Stack" in role or "FSE" in skill:
            proficiency["Angular"] = 2
            proficiency[".Net"] = 3
            proficiency["SQL"] = 3

        for tech in proficiency.keys():
            if tech in role or tech in skill:
                proficiency[tech] = 3

        if "Angular" in role or "Angular" in skill:
            proficiency["Angular"] = 3
            proficiency["SQL"] = max(proficiency["SQL"], 1)

        if "React" in role or "React" in skill:
            proficiency["React"] = 3
            proficiency["SQL"] = max(proficiency["SQL"], 1)

        if "AWS" in role or "AWS" in skill:
            proficiency["AWS"] = 2

        if "Lead" in role or "Senior" in role or "Sr." in role:
            for tech in proficiency.keys():
                if proficiency[tech] < 3:
                    proficiency[tech] += 1

        for tech in proficiency.keys():
            if proficiency[tech] > 3:
                proficiency[tech] = 3

        return [{"technology": tech, "proficiencyLevel": level} for tech, level in proficiency.items()]
    except Exception as e:
        return [{"technology": tech, "proficiencyLevel": 0} for tech in ["Angular", "React", ".Net", "SQL", "Postgresql", "AWS", "Python"]]

def process_developers_excel(file_path: str) -> List[Dict[str, Any]]:
    try:
        df = convert_excel_to_dataframe(file_path)
        required_columns = ['Associate Id', 'Associate Name', 'Project Role', 'Skill Requirement']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Error: Missing required columns in Excel file: {', '.join(missing_columns)}"
            return [{"error": error_msg}]
        employees = []
        for _, row in df.iterrows():
            emp = {
                "associateId": row.get('Associate Id', ''),
                "associateName": row.get('Associate Name', ''),
                "projectRole": row.get('Project Role', ''),
                "skillRequirement": row.get('Skill Requirement', ''),
                "proficiency": calculate_proficiency(row.get('Project Role', ''), row.get('Skill Requirement', ''))
            }
            employees.append(emp)
        return employees
    except Exception as e:
        return [{"error": str(e)}]

def convert_excel_to_dataframe(file_path: str):
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        raise Exception(f"Failed to read Excel file: {str(e)}")
