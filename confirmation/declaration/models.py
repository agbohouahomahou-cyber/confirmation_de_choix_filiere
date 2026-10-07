from xml.parsers.expat import model

from django.db import models

# Create your models here.

class Ecole(models.TextChoices):
    EGPVS = "EGPVS", "EGPVS – Gestion et production végétale et semencière"
    EHAEB = "EHAEV", "EHAEV – Horticulture et aménagement des espaces verts"
    EFORT = "EForT", "EForT – Foresterie tropicale"
    EGESE = "EGESE", "EGESE – Gestion et exploitation des systèmes d'élevage"
    EAQ = "EAq", "EAq – Aquaculture"
    EGR = "EGR", "EGR – Génie rural"
    ESTCTPA = "ESTCTPA", "ESTCTPA – Conservation et transformation des produits agricoles"
    EAPA = "EAPA", "EAPA – Agrobusiness et politiques agricoles"
    ESRVA = "ESRVA", "ESRVA – Sociologie rurale et vulgarisation agricole"


class Decision(models.TextChoices):
    CONFIRMER = "confirmer", "Je confirme ma place"
    DEMISSION = "demission", "Je démissionne de ma place"

class Financement(models.TextChoices):
    BOURSIER_EXCELLENCE = "boursier_excellence", "Boursier (excellence)"
    BOURSIER_ORDINATEUR = "boursier_ordinateur", "Boursier (ordinateur)"
    PARTIEL = "partiel", "Partiellement payant"
    PAYANT = "payant", "Entièrement payant"

class Handicap(models.TextChoices):
    AUCUN = "Aucun", "Aucun"
    VISUEL = "Visuel", "Visuel"
    AUDITIF = "Auditif", "Auditif"
    MOTEUR = "Moteur", "Moteur"
    AUTRE = "Autre", "Autre"

class Candidature(models.Model):
    #Etape1:identité

    npi = models.CharField("NPI", max_length=10, unique=True)
    numero_table = models.CharField("Numéro de table du BAC", max_length=20)
    nom = models.CharField(max_length=200)
    prenoms = models.CharField("Prénoms", max_length=200)
    date_naissance = models.DateField("Date de naissance")
    lieu_naissance = models.CharField("Lieu de naissance", max_length=150)
    # Étape 2 – Contact
    telephone = models.CharField("Téléphone", max_length=20)
    handicap = models.CharField(max_length=10, choices=Handicap.choices, default=Handicap.AUCUN)
    handicap_precision = models.CharField(max_length=200, blank=True)
    # Étape 3 – Filiation
    pere_nom = models.CharField("Nom du père ou tuteur", max_length=100)
    pere_prenoms = models.CharField("Prénoms du père ou tuteur", max_length=150)
    mere_nom = models.CharField("Nom de la mère ou tutrice", max_length=100)
    mere_prenoms = models.CharField("Prénoms de la mère ou tutrice", max_length=150)
    # Étapes 4 et 5 – École et financement
    decision = models.CharField(max_length=10, choices=Decision.choices)
    ecole = models.CharField(max_length=10, choices=Ecole.choices)
    financement = models.CharField(max_length=20, choices=Financement.choices)
    # Suivi
    code_verification = models.CharField(max_length=12, unique=True, editable=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cree_le"]

    def __str__(self):
        return f"{self.nom} {self.prenoms} ({self.npi})"
