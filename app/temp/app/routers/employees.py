from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.employee import Employee
from app.services.developer_processing import calculate_proficiency, process_developers_excel
from fastapi.responses import JSONResponse
import logging

router = APIRouter()

# Sample in-memory storage
data_store = {}

# for employee in mock_employees:
#     data_store[employee.empId] = employee

@router.post("/employees/")
def create_employee(employee: Employee):
    if employee.empId in data_store:
        raise HTTPException(status_code=400, detail="Employee already exists")
    data_store[employee.empId] = employee
    return {"message": "Employee created", "employee": employee}

@router.get("/employees/{employee_id}")
def read_employee(employee_id: int):
    employee = data_store.get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.get("/employees/")
def read_all_employees():
    employees = list(data_store.values())
    enriched_employees = []
    for emp in employees:
        emp_dict = {
            "associateId": emp.associateId,
            "associateName": emp.associateName,
            "projectRole": emp.projectRole,
            "skillRequirement": emp.skillRequirement,
            "proficiency": calculate_proficiency(emp.projectRole, emp.skillRequirement)
        }
        enriched_employees.append(emp_dict)
    return enriched_employees

@router.post("/employees/upload/")
def upload_employees(file: UploadFile = File(...)):
    import tempfile
    import shutil
    logger = logging.getLogger("uvicorn.error")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        employees = process_developers_excel(tmp_path)
        # If error key is present in the first element, return error message with 400 status
        if isinstance(employees, list) and employees and isinstance(employees[0], dict) and employees[0].get("error"):
            logger.error(f"Excel processing error: {employees[0]['error']}")
            return JSONResponse(status_code=400, content={"error": employees[0]["error"]})
        return employees
    except Exception as e:
        logger.exception(f"File upload failed: {str(e)}")
        return JSONResponse(status_code=400, content={"error": f"File upload failed: {str(e)}"})
