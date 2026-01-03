"""Vercel serverless function handler for FastAPI app."""
from app.main import app

# Vercel Python runtime automatically detects FastAPI apps
# The app variable will be used as the handler

