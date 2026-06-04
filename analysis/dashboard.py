#!/usr/bin/env python3
"""
Dashboard interactivo del análisis de escenarios (corpus_v1).

Uso (desde la raíz del repo):
  streamlit run scenarios/analysis/dashboard.py
  python3 -m streamlit run scenarios/analysis/dashboard.py
"""

from dashboard.app import main

if __name__ == "__main__":
    main()