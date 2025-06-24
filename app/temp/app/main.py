from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import employees as employees

app = FastAPI()

# Add CORS middleware to allow requests from http://localhost:4200
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the employees router
app.include_router(employees.router)
