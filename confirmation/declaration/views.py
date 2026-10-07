import secrets
from io import BytesIO
from xml.sax.saxutils import escape

from django.contrib.staticfiles import finders
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from formtools.wizard.views import SessionWizardView

from . import forms
from .context_processors import annee_academique
from .models import Candidature, Decision, Ecole, Financement

FORMS = [
    ("identite", forms.Etape1Identite),
    ("contact", forms.Etape2Contact),
    ("filiation", forms.Etape3Filiation),
    ("ecole", forms.Etape4Ecole),
    ("financement", forms.Etape5Financement),
    ("relecture", forms.Etape6Relecture),
]
TITRES = {"identite": "Identité", "contact": "Contact", "filiation": "Filiation",
          "ecole": "École", "financement": "Financement", "relecture": "Relecture"}


def accueil(request):
    return render(request, "confirmation/accueil.html")


def ma_fiche(request):
    """Fiche du candidat de cette session ; sinon on le renvoie déclarer."""
    code = request.session.get("candidature_code")
    c = Candidature.objects.filter(code_verification=code).first() if code else None
    if c is None:
        return redirect("declaration:declarer")
    lien_verification = request.build_absolute_uri(
        reverse("declaration:verifier", args=[c.code_verification])
    )
    return render(
        request,
        "confirmation/fiche.html",
        {"c": c, "lien_verification": lien_verification},
    )


def telecharger_fiche(request):
    code = request.session.get("candidature_code")
    c = Candidature.objects.filter(code_verification=code).first() if code else None
    if c is None:
        return redirect("declaration:declarer")

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    dark = colors.HexColor("#0F3D2E")
    muted = colors.HexColor("#5C685F")
    line = colors.HexColor("#D8DED5")
    pale = colors.HexColor("#F2F5F0")
    institution = ParagraphStyle(
        "fiche_institution", parent=styles["Normal"], fontSize=8, leading=10,
        textColor=muted,
    )
    title = ParagraphStyle(
        "fiche_title", parent=styles["Normal"], fontSize=16, leading=20,
        textColor=dark,
    )
    body = ParagraphStyle("fiche_body", parent=styles["Normal"], fontSize=9, leading=13)
    label = ParagraphStyle("fiche_label", parent=body, fontSize=8, textColor=muted)
    value = ParagraphStyle("fiche_value", parent=body, textColor=dark)
    section = ParagraphStyle(
        "fiche_section", parent=body, fontName="Helvetica-Bold", textColor=dark,
    )
    name = ParagraphStyle(
        "fiche_name", parent=styles["Normal"], fontSize=20, leading=24, textColor=dark,
    )
    verification_code = ParagraphStyle(
        "fiche_verification_code", parent=title, fontSize=16, leading=20,
    )
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm, title="Ma fiche – UNA",
    )
    content_width = A4[0] - 40 * mm

    brand = [
        Paragraph("Université Nationale d'Agriculture", institution),
        Paragraph("Fiche de confirmation de choix", title),
        Paragraph(f"Rentrée {escape(annee_academique(request)['annee_academique'])}", label),
    ]
    logo_path = finders.find("img/logo-una.png")
    if logo_path:
        header = Table([[Image(logo_path, width=20 * mm, height=20 * mm), brand]],
                       colWidths=[25 * mm, content_width - 25 * mm])
        header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LINEBELOW", (0, 0), (-1, -1), 0.6, line),
        ]))
    else:
        header = Table([[brand]], colWidths=[content_width])
        header.setStyle(TableStyle([
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LINEBELOW", (0, 0), (-1, -1), 0.6, line),
        ]))

    story = [header, Spacer(1, 7 * mm)]
    story.extend([
        Paragraph(escape(f"{c.nom} {c.prenoms}"), name),
        Paragraph(f"NPI {escape(c.npi)}", label),
        Spacer(1, 5 * mm),
    ])

    choice_cells = [[
        [Paragraph("Décision", label), Paragraph(escape(c.get_decision_display()), value)],
        [Paragraph("École", label), Paragraph(escape(c.get_ecole_display()), value)],
        [Paragraph("Financement", label), Paragraph(escape(c.get_financement_display()), value)],
    ]]
    choices = Table(choice_cells, colWidths=[content_width / 3] * 3)
    choices.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), pale),
        ("BOX", (0, 0), (-1, -1), 0.6, line),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.extend([choices, Spacer(1, 6 * mm)])

    section_heading = Table([[Paragraph("Le candidat", section)]], colWidths=[content_width])
    section_heading.setStyle(TableStyle([
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.6, line),
    ]))
    handicap = c.get_handicap_display()
    if c.handicap_precision:
        handicap += f" ({c.handicap_precision})"
    rows = [
        ("N° de table du BAC", c.numero_table),
        ("Né(e) le", f"{c.date_naissance.strftime('%d/%m/%Y')} à {c.lieu_naissance}"),
        ("Téléphone", c.telephone),
        ("Handicap", handicap),
        ("Soumise le", timezone.localtime(c.cree_le).strftime("%d/%m/%Y à %H:%M")),
    ]
    details_data = [[Paragraph(escape(label_text), label), Paragraph(escape(str(item)), value)]
                    for label_text, item in rows]
    details = Table(details_data, colWidths=[48 * mm, content_width - 48 * mm], hAlign="LEFT")
    details.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, line),
    ]))
    story.extend([section_heading, details, Spacer(1, 7 * mm)])

    import segno

    lien = request.build_absolute_uri(reverse("declaration:verifier", args=[c.code_verification]))
    qr_buffer = BytesIO()
    segno.make(lien, error="m").save(
        qr_buffer, kind="png", scale=5, border=0, dark="#0F3D2E", light="#FFFFFF",
    )
    qr_buffer.seek(0)
    qr = Image(qr_buffer, width=28 * mm, height=28 * mm)
    verification = Table([[
        qr,
        [Paragraph("Code de vérification", label),
         Paragraph(escape(c.code_verification), verification_code),
         Spacer(1, 2 * mm),
         Paragraph("Scannez le QR code ou ouvrez le lien pour vérifier l'authenticité de cette fiche.", body),
         Paragraph(escape(lien), label)],
    ]], colWidths=[35 * mm, content_width - 35 * mm], hAlign="LEFT")
    verification.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, line),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(verification)

    document.build(story)
    request.session.pop("candidature_code", None)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="ma_fiche_{c.code_verification}.pdf"'
    return response


class ConfirmationWizard(SessionWizardView):
    form_list = FORMS
    template_name = "confirmation/etape.html"

    def dispatch(self, request, *args, **kwargs):
        code = request.session.get("candidature_code")
        if code and Candidature.objects.filter(code_verification=code).exists():
            return redirect("declaration:ma_fiche")   # déjà déclaré : pas de seconde déclaration
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        ctx = super().get_context_data(form=form, **kwargs)
        ctx["titre"] = TITRES[self.steps.current]
        ctx["total"] = len(FORMS) + 1          # +1 : page de la fiche
        ctx["numero"] = self.steps.index + 1
        ctx["pourcentage"] = round(self.steps.index / (len(FORMS)) * 100)
        if self.steps.current == "relecture":
            d = self.get_all_cleaned_data()
            ctx["recap"] = [
                ("Identité", [("NPI", d.get("npi")), ("N° de table", d.get("numero_table")), ("Nom", d.get("nom")),
                              ("Prénoms", d.get("prenoms")), ("Date de naissance", d.get("date_naissance")),
                              ("Lieu de naissance", d.get("lieu_naissance"))]),
                ("Contact", [("Téléphone", d.get("telephone")), ("Handicap", d.get("handicap")),
                             ("Précision", d.get("handicap_precision"))]),
                ("Filiation", [("Père ou tuteur", f'{d.get("pere_nom", "")} {d.get("pere_prenoms", "")}'),
                               ("Mère ou tutrice", f'{d.get("mere_nom", "")} {d.get("mere_prenoms", "")}')]),
                ("École", [("Décision", dict(Decision.choices).get(d.get("decision"))),
                           ("École", dict(Ecole.choices).get(d.get("ecole")))]),
                ("Financement", [("Statut", dict(Financement.choices).get(d.get("financement")))]),
            ]
        return ctx

    def done(self, form_list, **kwargs):
        data = {k: v for f in form_list for k, v in f.cleaned_data.items() if k != "honneur"}
        for _ in range(5):                      # code unique, quelques essais
            try:
                with transaction.atomic():
                    c = Candidature.objects.create(code_verification=secrets.token_hex(6).upper(), **data)
                break
            except IntegrityError:
                if Candidature.objects.filter(npi=data["npi"]).exists():
                    return render(self.request, "confirmation/deja_declare.html", status=409)
        self.request.session["candidature_code"] = c.code_verification
        return redirect("declaration:ma_fiche")


def verifier_fiche(request, code):
    """Page publique de contrôle d'une fiche à partir de son code."""
    c = get_object_or_404(Candidature, code_verification=code.upper())
    return render(request, "confirmation/verification.html", {"c": c})
