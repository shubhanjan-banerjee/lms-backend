import pandas as pd
from typing import List, Dict, Any
import json

def calculate_proficiency(role: str, skill: str) -> List[Dict[str, int]]:
    print(f"--------------------- Calculating proficiency for role: {role}, skill: {skill}")
    import math
    if not isinstance(role, str) or (isinstance(role, float) and math.isnan(role)):
        role = ""
    if not isinstance(skill, str) or (isinstance(skill, float) and math.isnan(skill)):
        skill = ""
    try:
        proficiency = {"Angular": 0, "React": 0, ".Net": 0, "SQL": 0, "Postgresql": 0, "AWS": 0, "Python": 0}

        if "Fullstack Developer" in role or "FSE" in skill:
            proficiency["Angular"] = 2
            proficiency[".Net"] = 3
            proficiency["SQL"] = 3

        for tech in proficiency.keys():
            if tech in role or tech in skill:
                proficiency[tech] = 3

        if "Backend Developer" in role or "Angular" in skill:
            proficiency["Angular"] = 2
            proficiency["SQL"] = max(proficiency["SQL"], 1)

        if "Frontend Developer" in role or "React" in skill:
            proficiency["React"] = 3
            proficiency["SQL"] = max(proficiency["SQL"], 1)

        if "Cloud Architect" in role or "AWS" in skill:
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

def convert_excel_to_dataframe(file_path: str):
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        raise Exception(f"Failed to read Excel file: {str(e)}")

def process_employees_excel_and_insert(file_path: str, db):
    import app.crud.crud as crud
    from sqlalchemy.exc import SQLAlchemyError
    df = convert_excel_to_dataframe(file_path)
    required_columns = [
        'Employee ID', 'Employee First Name', 'Employee Last Name', 'Email ID', 'Project Role', 'Skill Requirement'
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    summary = {"created": [], "updated": [], "errors": []}
    if missing_columns:
        return {"error": f"Missing required columns: {', '.join(missing_columns)}"}
    for _, row in df.iterrows():
        try:
            sso_id = str(row.get('Employee ID', '')).strip()
            first_name = str(row.get('Employee First Name', '')).strip()
            last_name = str(row.get('Employee Last Name', '')).strip()
            email = str(row.get('Email ID', '')).strip()
            project_role_name = str(row.get('Project Role', '')).strip()
            skill_names = str(row.get('Skill Requirement', '')).strip().split(',')
            skill_names = [s.strip() for s in skill_names if s.strip()]
            # Map project role
            project_role = crud.get_project_role_by_name(db, project_role_name)
            if not project_role:
                summary["errors"].append(f"Project role '{project_role_name}' not found for {sso_id}")
                continue
            # Check if user exists
            user = crud.get_user_by_sso_id(db, sso_id)
            if not user:
                user_data = type('UserObj', (), {})()
                user_data.sso_id = sso_id
                user_data.email = email
                user_data.first_name = first_name
                user_data.last_name = last_name
                user_data.password = 'password123'
                user_data.current_project_role_id = project_role.id
                user = crud.create_user_with_role(db, user_data)
                summary["created"].append(sso_id)
            else:
                if user.current_project_role_id != project_role.id:
                    user.current_project_role_id = project_role.id
                    db.add(user)
                    db.commit()
                summary["updated"].append(sso_id)
            # For each skill
            for skill_name in skill_names:
                skill = crud.get_skill_by_name(db, skill_name)
                if not skill:
                    summary["errors"].append(f"Skill '{skill_name}' not found for {sso_id}")
                    continue
                # Proficiency evaluation
                proficiencies = calculate_proficiency(project_role_name, skill_name)
                for prof in proficiencies:
                    if prof["technology"].lower() == skill_name.lower():
                        proficiency_level = crud.get_proficiency_level_by_level(db, prof["proficiencyLevel"])
                        if not proficiency_level:
                            summary["errors"].append(f"Proficiency level '{prof['proficiencyLevel']}' not found for {sso_id}")
                            continue
                        crud.upsert_user_skill(db, user.id, skill.id, proficiency_level.id)
        except SQLAlchemyError as e:
            summary["errors"].append(f"DB error for {sso_id}: {str(e)}")
        except Exception as e:
            summary["errors"].append(f"General error for {sso_id}: {str(e)}")
    return summary
