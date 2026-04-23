from django.contrib import admin
from django.utils.html import format_html
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'student_name', 'course_title', 'issued_at', 'pdf_link')
    list_filter = ('issued_at', 'course')
    search_fields = ('certificate_number', 'student_name', 'course_title', 'student__email')
    readonly_fields = ('certificate_number', 'verification_uuid', 'issued_at', 'pdf_file')

    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">📄 Voir PDF</a>', obj.pdf_file.url)
        return '—'
    pdf_link.short_description = 'PDF'