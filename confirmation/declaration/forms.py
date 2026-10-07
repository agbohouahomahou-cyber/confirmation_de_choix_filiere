from datetime import date

from django import forms
from django.core.validators import RegexValidator

from .models import *
from .validators import NumeroTableField

npi_validator = RegexValidator(r"^\d{10}$", "Le NPI comporte 10 chiffres.")
tel_validator = RegexValidator(r"^[\d\s+]{8,15}$", "Numéro de téléphone invalide.")


class Etape1Identite(forms.Form):
    npi = forms.CharField(
        label="Numéro personnel d'identification (NPI)",
        help_text="10 chiffres, tels qu'ils figurent sur votre carte NPI.",
        validators=[npi_validator],
        widget=forms.TextInput(attrs={
            "inputmode": "numeric", "autocomplete": "off", "maxlength": "10", "placeholder": "Ex. 1234567890"}))
    numero_table = NumeroTableField(
        label="Numéro de table du BAC",
        help_text="Format : 215-AA00-0000, tel qu'il figure sur votre relevé du BAC.",
        max_length=14,
        widget=forms.TextInput(attrs={
            "placeholder": "Ex. 215-AA00-0000", "maxlength": "14", "autocomplete": "off",
            "autocapitalize": "characters", "spellcheck": "false", "data-masque": "numero-table"}))
    nom = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "family-name", "autocapitalize": "characters"}))
    prenoms = forms.CharField(
        label="Prénoms", max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "given-name", "autocapitalize": "words"}))
    # format ISO obligatoire : sans lui, la date saisie disparaît quand on clique sur « Retour »
    date_naissance = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "autocomplete": "bday"}))
    lieu_naissance = forms.CharField(
        label="Lieu de naissance", max_length=120,
        widget=forms.TextInput(attrs={"autocomplete": "off", "autocapitalize": "words"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # calculé à chaque affichage (et non à l'import) pour rester juste après minuit
        self.fields["date_naissance"].widget.attrs["max"] = date.today().isoformat()

    def clean_npi(self):
        npi = self.cleaned_data["npi"]
        if Candidature.objects.filter(npi=npi).exists():
            raise forms.ValidationError("Une déclaration existe déjà pour ce NPI.")
        return npi

    def clean(self):
        data = super().clean()
        for k in ("nom", "prenoms"):
            if data.get(k):
                data[k] = data[k].strip().upper() if k == "nom" else data[k].strip()
        return data


class Etape2Contact(forms.Form):
    telephone = forms.CharField(
        label="Téléphone (WhatsApp de préférence)",
        help_text="Un numéro joignable, avec l'indicatif si possible.",
        validators=[tel_validator],
        widget=forms.TextInput(attrs={
            "type": "tel", "inputmode": "tel", "autocomplete": "tel", "placeholder": "Ex. +229 01 97 00 00 00"}))
    handicap = forms.ChoiceField(label="Situation de handicap", choices=Handicap.choices)
    handicap_precision = forms.CharField(
        label="Précision (facultatif)", required=False, max_length=200,
        widget=forms.TextInput(attrs={"autocomplete": "off"}))


class Etape3Filiation(forms.Form):
    pere_nom = forms.CharField(label="Nom du père ou tuteur", max_length=100,
                               widget=forms.TextInput(attrs={"autocomplete": "off", "autocapitalize": "characters"}))
    pere_prenoms = forms.CharField(label="Prénoms du père ou tuteur", max_length=150,
                                   widget=forms.TextInput(attrs={"autocomplete": "off", "autocapitalize": "words"}))
    mere_nom = forms.CharField(label="Nom de la mère ou tutrice", max_length=100,
                               widget=forms.TextInput(attrs={"autocomplete": "off", "autocapitalize": "characters"}))
    mere_prenoms = forms.CharField(label="Prénoms de la mère ou tutrice", max_length=150,
                                   widget=forms.TextInput(attrs={"autocomplete": "off", "autocapitalize": "words"}))


class Etape4Ecole(forms.Form):
    decision = forms.ChoiceField(label="Votre décision", choices=Decision.choices, widget=forms.RadioSelect)
    ecole = forms.ChoiceField(label="École", choices=Ecole.choices, widget=forms.RadioSelect)


class Etape5Financement(forms.Form):
    financement = forms.ChoiceField(label="Statut de financement", choices=Financement.choices,
                                    widget=forms.RadioSelect)


class Etape6Relecture(forms.Form):
    honneur = forms.BooleanField(
        label="Je certifie sur l'honneur que ces informations sont exactes et correspondent à mes documents officiels.",
        error_messages={"required": "Cochez cette case pour confirmer."})
