from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import DetailView, ListView
from django.http import HttpResponse, Http404, FileResponse
from django.views import View

from .models import Certificate


class MyCertificatesView(LoginRequiredMixin, ListView):
    """Liste des certificats de l'utilisateur courant."""
    template_name = 'certificates/my_certificates.html'
    context_object_name = 'certificates'

    def get_queryset(self):
        return Certificate.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__category').order_by('-issued_at')


class CertificateDetailView(LoginRequiredMixin, DetailView):
    """Détail d'un certificat de l'utilisateur."""
    model = Certificate
    template_name = 'certificates/certificate_detail.html'
    context_object_name = 'certificate'
    slug_field = 'verification_uuid'
    slug_url_kwarg = 'uuid'

    def dispatch(self, request, *args, **kwargs):
        cert = self.get_object()
        if cert.student != request.user:
            messages.error(request, "Ce certificat ne vous appartient pas.")
            return redirect('certificates:my_certificates')
        return super().dispatch(request, *args, **kwargs)


@login_required
def download_certificate(request, uuid):
    """Télécharge le PDF du certificat."""
    certificate = get_object_or_404(Certificate, verification_uuid=uuid, student=request.user)

    # Générer le PDF s'il n'existe pas encore
    if not certificate.pdf_file:
        try:
            certificate.generate_pdf()
        except Exception as e:
            messages.error(request, f"Erreur lors de la génération du certificat : {e}")
            return redirect('certificates:detail', uuid=certificate.verification_uuid)

    response = FileResponse(
        certificate.pdf_file.open('rb'),
        as_attachment=True,
        filename=f"Certificat-Kairos-{certificate.certificate_number}.pdf",
        content_type='application/pdf'
    )
    return response


class VerifyCertificateView(View):
    """
    Page publique de vérification d'un certificat.
    Accessible à tous, sans connexion.
    """
    template_name = 'certificates/verify.html'

    def get(self, request, uuid=None):
        certificate = None
        if uuid:
            try:
                certificate = Certificate.objects.select_related('course', 'student').get(
                    verification_uuid=uuid
                )
            except Certificate.DoesNotExist:
                pass

        return render(request, self.template_name, {
            'certificate': certificate,
            'uuid': uuid,
        })

    def post(self, request):
        """Recherche par numéro de certificat."""
        certificate_number = request.POST.get('certificate_number', '').strip().upper()

        try:
            certificate = Certificate.objects.get(certificate_number=certificate_number)
            return redirect('certificates:verify', uuid=certificate.verification_uuid)
        except Certificate.DoesNotExist:
            return render(request, self.template_name, {
                'certificate': None,
                'error': f"Aucun certificat trouvé avec le numéro « {certificate_number} ».",
                'searched_number': certificate_number,
            })