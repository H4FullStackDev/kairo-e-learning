from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('mes-certificats/', views.MyCertificatesView.as_view(), name='my_certificates'),
    path('verifier/', views.VerifyCertificateView.as_view(), name='verify_search'),
    path('verifier/<uuid:uuid>/', views.VerifyCertificateView.as_view(), name='verify'),
    path('telecharger/<uuid:uuid>/', views.download_certificate, name='download'),
    path('<uuid:uuid>/', views.CertificateDetailView.as_view(), name='detail'),
]