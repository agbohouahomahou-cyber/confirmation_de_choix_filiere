from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from declaration.models import Candidature, Decision, Ecole, Financement, Handicap


PERMISSION = 'declaration.view_candidature'


def candidatures_filtrees(params):
    """Applique recherche et filtres. Réutilisée plus tard par les exports."""
    candidatures = Candidature.objects.all()
    filtres = {
        'q': params.get('q', '').strip(),
        'ecole': params.get('ecole', ''),
        'decision': params.get('decision', ''),
        'financement': params.get('financement', ''),
    }
    if filtres['q']:
        q = filtres['q']
        candidatures = candidatures.filter(
            Q(nom__icontains=q) | Q(prenoms__icontains=q) | Q(npi__icontains=q)
            | Q(numero_table__icontains=q) | Q(telephone__icontains=q))
    # On n'applique un filtre que si la valeur fait partie des choix valides
    if filtres['ecole'] in Ecole.values:
        candidatures = candidatures.filter(ecole=filtres['ecole'])
    else:
        filtres['ecole'] = ''
    if filtres['decision'] in Decision.values:
        candidatures = candidatures.filter(decision=filtres['decision'])
    else:
        filtres['decision'] = ''
    if filtres['financement'] in Financement.values:
        candidatures = candidatures.filter(financement=filtres['financement'])
    else:
        filtres['financement'] = ''
    return candidatures, filtres


@login_required
@permission_required(PERMISSION, raise_exception=True)
def liste_declarations(request):
    candidatures, filtres = candidatures_filtrees(request.GET)

    page_obj = Paginator(candidatures, 25).get_page(request.GET.get('page'))

    # Garde les filtres dans les liens de pagination
    querystring = urlencode({k: v for k, v in filtres.items() if v})
    if querystring:
        querystring += '&'

    contexte = {
        'page_obj': page_obj,
        'filtres': filtres,
        'filtres_actifs': any(filtres.values()),
        'querystring': querystring,
        'ecoles': Ecole.choices,
        'decisions': Decision.choices,
        'financements': Financement.choices,
    }
    return render(request, 'scolarite/liste_declarations.html', contexte)


@login_required
@permission_required(PERMISSION, raise_exception=True)
def tableau_de_bord(request):
    candidatures = Candidature.objects.all()

    # Chiffres clés : une seule requête pour tout compter
    chiffres = candidatures.aggregate(
        total=Count('id'),
        confirmations=Count('id', filter=Q(decision=Decision.CONFIRMER)),
        demissions=Count('id', filter=Q(decision=Decision.DEMISSION)),
        boursiers=Count('id', filter=Q(financement__in=[
            Financement.BOURSIER_EXCELLENCE, Financement.BOURSIER_ORDINATEUR])),
        handicap=Count('id', filter=~Q(handicap=Handicap.AUCUN)),
        aujourdhui=Count('id', filter=Q(cree_le__date=timezone.localdate())),
    )

    # Répartition par école (les 9 écoles, même celles à zéro)
    par_ecole_brut = {
        ligne['ecole']: ligne
        for ligne in candidatures.values('ecole').annotate(
            total=Count('id'),
            confirmations=Count('id', filter=Q(decision=Decision.CONFIRMER)),
            demissions=Count('id', filter=Q(decision=Decision.DEMISSION)),
        )
    }
    par_ecole = []
    for code, libelle in Ecole.choices:
        ligne = par_ecole_brut.get(code, {})
        par_ecole.append({
            'code': code,
            'nom': libelle.split(' – ', 1)[-1],
            'total': ligne.get('total', 0),
            'confirmations': ligne.get('confirmations', 0),
            'demissions': ligne.get('demissions', 0),
        })
    maximum = max((e['total'] for e in par_ecole), default=0) or 1
    for e in par_ecole:
        e['largeur'] = round(e['total'] * 100 / maximum)

    # Répartition par type de financement
    par_financement_brut = {
        ligne['financement']: ligne['total']
        for ligne in candidatures.values('financement').annotate(total=Count('id'))
    }
    total = chiffres['total'] or 1
    par_financement = []
    for code, libelle in Financement.choices:
        nombre = par_financement_brut.get(code, 0)
        par_financement.append({
            'libelle': libelle,
            'total': nombre,
            'pourcentage': round(nombre * 100 / total),
        })

    contexte = {
        'chiffres': chiffres,
        'par_ecole': par_ecole,
        'par_financement': par_financement,
        'dernieres': candidatures[:8],
    }
    return render(request, 'scolarite/tableau_de_bord.html', contexte)
