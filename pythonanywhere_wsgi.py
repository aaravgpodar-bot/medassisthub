"""
PythonAnywhere WSGI helper for MedAssist Hub.

Use this only for the new MedAssist Hub web app. Replace YOUR_USERNAME with
your PythonAnywhere username before pasting it into that web app's WSGI file.
"""
import sys
from pathlib import Path


project_home = Path("/home/YOUR_USERNAME/medassist-hub")
if str(project_home) not in sys.path:
    sys.path.insert(0, str(project_home))

from app import app as application  # noqa: E402
