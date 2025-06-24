from pydantic import BaseModel

class Employee(BaseModel):
    associateId: str
    associateName: str
    projectRole: str
    skillRequirement: str
    
