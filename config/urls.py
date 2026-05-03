from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cours/', include('apps.courses.urls', namespace='courses')),
    path('apprentissage/', include('apps.enrollments.urls', namespace='enrollments')),
    path('quiz/', include('apps.quizzes.urls', namespace='quizzes')),
    path('certificats/', include('apps.certificates.urls', namespace='certificates')),
    path('interactions/', include('apps.interactions.urls', namespace='interactions')),
    path('formateur/', include('apps.instructor.urls', namespace='instructor')), 
    path('', include('apps.accounts.urls', namespace='accounts')),
]

# Browser reload en développement
if settings.DEBUG:
    urlpatterns += [
        path('__reload__/', include('django_browser_reload.urls')),
    ]
    # Servir les fichiers médias
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)