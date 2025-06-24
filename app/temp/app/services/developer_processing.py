import pandas as pd
from typing import List, Dict, Any
import json

# Ruleset for proficiency levels
def calculate_proficiency(role: str, skill: str) -> List[Dict[str, int]]:
    print(f"Calculating proficiency for role: {role}, skill: {skill}")
    # Handle None, NaN, or non-string inputs
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

        # Convert to array of objects
        return [{"technology": tech, "proficiencyLevel": level} for tech, level in proficiency.items()]
    except Exception as e:
        # Return all skills as 0 in case of error
        return [{"technology": tech, "proficiencyLevel": 0} for tech in ["Angular", "React", ".Net", "SQL", "Postgresql", "AWS", "Python"]]


def process_developers_excel(file_path: str) -> List[Dict[str, Any]]:
    try:
        df = convert_excel_to_dataframe(file_path)
        # Step 1a: Validate required columns
        required_columns = ['Associate Id', 'Associate Name', 'Project Role', 'Skill Requirement']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Error: Missing required columns in Excel file: {', '.join(missing_columns)}"
            return [{"error": error_msg}]
        developers = []
        for idx, row in df.iterrows():
            developer = {
                "associateId": row.get("Associate Id", ""),
                "associateName": row.get("Associate Name", ""),
                "projectRole": row.get("Project Role", ""),
                "skillRequirement": row.get("Skill Requirement", ""),
            }
            try:
                developer["proficiency"] = calculate_proficiency(developer["projectRole"], developer["skillRequirement"])
            except Exception as e:
                developer["proficiency"] = [{"technology": tech, "proficiencyLevel": 0} for tech in ["Angular", "React", ".Net", "SQL", "Postgresql", "AWS", "Python"]]
            developers.append(developer)
        return developers
    except Exception as e:
        # Return a single developer with all skills 0 if the whole process fails
        return [{
            "error": f"Error processing Excel file: {e}",
            "name": "",
            "role": "",
            "skill": "",
            "proficiency": [{"technology": tech, "proficiencyLevel": 0} for tech in ["Angular", "React", ".Net", "SQL", "Postgresql", "AWS", "Python"]]
        }]

def convert_excel_to_dataframe(excel_file_path, sheet_name=0):
    try:
        return pd.read_excel(excel_file_path, sheet_name=sheet_name)
    except FileNotFoundError:
        print(f"Error: The Excel file '{excel_file_path}' was not found. Please check the path.")
        return None
    except ValueError as ve:
        print(f"Error: A sheet with name or index '{sheet_name}' was not found in '{excel_file_path}'. {ve}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

