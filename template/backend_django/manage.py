#!/usr/bin/env python
"""
Django backend.  Run from the PROJECT ROOT folder:

    python backend_django/manage.py migrate
    python backend_django/manage.py runserver 8000
"""
import os
import sys
from pathlib import Path

# Make the project root importable so `from ml import service` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
