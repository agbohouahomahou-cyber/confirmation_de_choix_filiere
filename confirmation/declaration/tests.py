from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import Candidature, Decision, Ecole, Financement


class TelechargerFicheTests(TestCase):
	def setUp(self):
		self.candidature = Candidature.objects.create(
			npi="1234567890",
			numero_table="BAC2026-123",
			nom="Nom",
			prenoms="Prénom",
			date_naissance=date(2005, 1, 1),
			lieu_naissance="Cotonou",
			telephone="97000000",
			pere_nom="Père",
			pere_prenoms="Prénom père",
			mere_nom="Mère",
			mere_prenoms="Prénom mère",
			decision=Decision.CONFIRMER,
			ecole=Ecole.EGPVS,
			financement=Financement.PAYANT,
			code_verification="ABCDEF123456",
		)
		session = self.client.session
		session["candidature_code"] = self.candidature.code_verification
		session.save()

	def test_downloads_pdf_as_attachment(self):
		response = self.client.get(reverse("declaration:telecharger_fiche"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response["Content-Type"], "application/pdf")
		self.assertIn("attachment;", response["Content-Disposition"])
		self.assertTrue(response.content.startswith(b"%PDF-"))
		self.assertNotIn("candidature_code", self.client.session)

		response = self.client.get(reverse("declaration:ma_fiche"))
		self.assertRedirects(response, reverse("declaration:declarer"))

	def test_fiche_renders_absolute_verification_url_and_root_static_path(self):
		response = self.client.get(reverse("declaration:ma_fiche"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "http://testserver/verifier/ABCDEF123456/")
		self.assertContains(response, 'href="/static/css/tailwind.css"')
		self.assertContains(response, 'rel="icon" type="image/png"')
		self.assertContains(response, 'src="/static/img/logo-una.png"')
		self.assertContains(response, "print:max-w-none")

	def test_redirects_when_candidate_is_not_in_session(self):
		self.client.session.flush()

		response = self.client.get(reverse("declaration:telecharger_fiche"))

		self.assertRedirects(response, reverse("declaration:declarer"))
