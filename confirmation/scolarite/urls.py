from django.contrib.auth import views as auth_views
from django.urls import path
from . import exports, views

app_name = 'scolarite'

urlpatterns = [
    path('', views.tableau_de_bord, name='tableau_de_bord'),
    path('declarations/', views.liste_declarations, name='liste'),
    path('exports/', exports.page_exports, name='exports'),
    path('exports/excel/', exports.export_excel, name='export_excel'),
    path('exports/csv/', exports.export_csv, name='export_csv'),
    path('exports/pdf/', exports.export_pdf, name='export_pdf'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='scolarite/connexion.html',
        redirect_authenticated_user=True), name='connexion'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='deconnexion'),
]
