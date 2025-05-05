# app/main.py

from fastapi import FastAPI
from app.routes.auth import auth
from app.routes.content import content

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(debug=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the auth routes (registration, login, token generation)
app.include_router(auth.router)
app.include_router(content.content_router)