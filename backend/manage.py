#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    # Get the absolute path of the current file (manage.py) and then the backend directory.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # The project root is one level up from the backend directory.
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    # Add the project root to the Python path so that the 'ml' folder can be imported.
    sys.path.insert(0, PROJECT_ROOT)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'statement_analysis.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable? "
            "Did you forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()