I want to modify the upload_employee features in such a way that following things will be taken care:

- admin will upload an excel file from UI application consisting of following fields:

  - 

  - | Employee ID | Employee First Name | Employee Last Name | Email ID | Project Role | Skill Requirement |
    | ----------- | ------------------- | ------------------ | -------- | ------------ | ----------------- |
    |             |                     |                    |          |              |                   |

- once api will get the file, it will first validate the format of the file

- then extract the content of the file in a dataframe

- according to our database design, it will insert the user information in database like following mapping

  "sso_id": row.get('Employee ID', ''),

  "first_name": row.get('Employee First Name', ''),

​        "last_name": row.get('Employee Last Name', ''),

​        "project_role": row.get('Project Role', ''),

​        "skill_name": row.get('Skill Requirement', '')

- then it will map the Project Role as our database design
- then it will map the skill role as our database design
- then it will proceed for the proficiency evaluation as per the provided rules given in "developer_processing.py"
- after evaluation, it will update the "user_skills" table
- after all these table insertion done, API will return with a summary of all that happened to the UI