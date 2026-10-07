import re

from django import forms
from django.core.exceptions import ValidationError

# Format officiel du numéro de table au BAC (Bénin) : 215-AA00-0000
MOTIF = re.compile(r"^\d{3}-[A-Z]{2}\d{2}-\d{4}$")
MESSAGE = "Numéro de table invalide. Il doit ressembler à 215-AA00-0000."


def normaliser_numero_table(valeur):
    """Met en majuscules et ajoute les tirets si le candidat les a oubliés.
    '215aa000000', '215 AA00 0000' ou '215-aa00-0000' donnent '215-AA00-0000'."""
    valeur = (valeur or "").strip()
    brut = re.sub(r"[\s\-–—_./]", "", valeur).upper()
    if re.fullmatch(r"\d{3}[A-Z]{2}\d{6}", brut):
        return f"{brut[:3]}-{brut[3:7]}-{brut[7:]}"
    return valeur.upper()


def valider_numero_table(valeur):
    if not MOTIF.fullmatch(valeur or ""):
        raise ValidationError(MESSAGE, code="numero_table_invalide")


class NumeroTableField(forms.CharField):
    """Champ de formulaire : corrige d'abord le format, puis le valide."""
    default_validators = [valider_numero_table]

    def to_python(self, value):
        return normaliser_numero_table(super().to_python(value))
