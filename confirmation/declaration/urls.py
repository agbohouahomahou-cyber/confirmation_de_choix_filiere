from django.urls import path

from . import views

app_name = "declaration"
urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("declarer/", views.ConfirmationWizard.as_view(), name="declarer"),   # on déclare d'abord
    path("ma-fiche/", views.ma_fiche, name="ma_fiche"),                        # puis on consulte sa fiche
    path("ma-fiche/telecharger/", views.telecharger_fiche, name="telecharger_fiche"),
    path("verifier/<str:code>/", views.verifier_fiche, name="verifier"),
]
