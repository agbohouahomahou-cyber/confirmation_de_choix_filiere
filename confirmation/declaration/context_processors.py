from .models import Candidature
from datetime import date

from django.conf import settings


def declaration(request):
    """Rend `a_declare` disponible dans tous les templates (en-tête, accueil...)."""
    code = request.session.get("candidature_code")
    return {"a_declare": bool(code) and Candidature.objects.filter(code_verification=code).exists()}


def annee_academique(request):
    """Rend {{ annee_academique }} disponible dans tous les templates.

    - Si settings.ANNEE_ACADEMIQUE existe, il est utilisé tel quel (prioritaire).
    - Sinon, calcul automatique : l'année académique démarre en juillet.
      Ex. octobre 2026 -> « 2026 – 2027 » ; mars 2027 -> « 2026 – 2027 ».
    """
    valeur = getattr(settings, "ANNEE_ACADEMIQUE", None)
    if not valeur:
        aujourdhui = date.today()
        debut = aujourdhui.year if aujourdhui.month >= 7 else aujourdhui.year - 1
        valeur = f"{debut} – {debut + 1}"
    return {"annee_academique": valeur}
