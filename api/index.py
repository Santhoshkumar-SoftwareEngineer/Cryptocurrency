"""
Vercel Serverless Function entry point for Cryptocurrency Price Tracker.
Exports the WSGI / ASGI web application handler for Vercel Python runtime.
"""
import sys
from pathlib import Path

# Ensure root workspace directory is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import app

# Vercel entry points
handler = app
application = app
