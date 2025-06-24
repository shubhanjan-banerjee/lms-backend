# Project: Account-Specific Learning Management System (LMS) - Backend API Development

## Overall Goal

Develop a robust, scalable, and secure backend API for the Account-Specific Learning Management System. This API will handle data persistence (MySQL), business logic, skill gap calculations, learning recommendations, and serve data to the frontend.

## Development Environment

- **IDE:** VS Code
- **AI Tool:** GitHub Copilot Agent
- **Backend Framework:** Python (FastAPI) - Preferred for performance, modern features, and automatic OpenAPI documentation.
- **Database:** MySQL
- **ORM:** SQLAlchemy (for database interactions)
- **Database Connector:** `mysql-connector-python` or `pymysql`
- **Authentication:** JWT (JSON Web Tokens) for API security, with a placeholder for future SSO integration.
- **Excel Processing:** `pandas` library for handling Excel file uploads.

## Detailed Development Plan for GitHub Copilot Agent

---

### **General Instructions for Copilot Agent:**

1. **Modular Design:** Organize code into logical modules (e.g., `main.py` for FastAPI app/routes, `models.py` for SQLAlchemy models, `schemas.py` for Pydantic models, `crud.py` for database operations, `utils.py` for helper functions like Excel parsing).
2. **Dependencies:** Use FastAPI's dependency injection extensively, especially for `Depends(get_db)` and authentication (`Depends(get_current_user)`, `Depends(get_current_admin_user)`).
3. **Error Handling:** Use FastAPI's `HTTPException` for API errors (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error).
4. **Logging:** Implement basic logging for API requests, errors, and significant events.
5. **Security:**
    - **Password Hashing:** Ensure `bcrypt` is used for hashing passwords.
    - **JWT:** Correctly implement JWT creation and validation.
    - **Authorization:** Strictly enforce role-based access control using dependencies (Admin vs. Developer).
    - **Input Validation:** Use Pydantic models for request body validation.
6. **Database Interactions:** All database operations should go through SQLAlchemy ORM, preferably via functions in `crud.py`. Avoid raw SQL queries directly in endpoints.
7. **Docstrings and Type Hints:** Use clear docstrings for functions and classes, and Python type hints for better code readability and maintainability.
8. **Testing (Conceptual):** While not implementing tests directly, hint at the need for unit and integration tests for key functions (e.g., `crud` operations, skill gap calculations).
9. **Database Migrations (Future Consideration):** Mention that for production, a tool like Alembic would be used for database migrations.

**After generating the code for each task, please provide instructions on how to continue to the next task or how to run the application (e.g., `uvicorn main:app --reload`).**

Let's begin by following these instructions step by step.
