"""Offline attendance-analysis pipeline (export -> clean -> metrics).

See analysis/config.py for paths and settings. The maths is shared with the live
API via backend_django/api/stats.py, so notebooks and the dashboard never disagree.
"""
