"""
Générateur de certificat PDF au design Kairos.
Utilise reportlab pour créer un PDF élégant A4 paysage.
"""
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Circle
from reportlab.graphics import renderPDF


# Couleurs Kairos
OBSIDIAN = HexColor('#0A0A0B')
INK = HexColor('#1A1A1C')
SMOKE = HexColor('#6B6B70')
FOG = HexColor('#A8A8AD')
MIST = HexColor('#E8E8EA')
IVORY = HexColor('#FAFAF7')
PAPER = HexColor('#F5F5F0')
AMBER = HexColor('#D97706')
AMBER_LIGHT = HexColor('#FCD34D')
FOREST = HexColor('#166534')


def draw_decorative_corner(c, x, y, size=40, color=AMBER, flip_x=False, flip_y=False):
    """Dessine un coin décoratif en angle."""
    c.setStrokeColor(color)
    c.setLineWidth(1.5)

    # Ligne horizontale
    dx = -1 if flip_x else 1
    dy = -1 if flip_y else 1

    c.line(x, y, x + (size * dx), y)
    c.line(x, y, x, y + (size * dy))


def create_certificate_pdf(certificate):
    """
    Crée le PDF du certificat.
    Retourne les bytes du PDF.
    """
    buffer = BytesIO()

    # Format paysage A4
    page_width, page_height = landscape(A4)

    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    c.setTitle(f"Certificat Kairos - {certificate.certificate_number}")

    # ============================
    # FOND & CADRE
    # ============================
    # Fond ivory
    c.setFillColor(IVORY)
    c.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # Cadre extérieur fin (marge de 1cm)
    c.setStrokeColor(MIST)
    c.setLineWidth(1)
    c.rect(1 * cm, 1 * cm, page_width - 2 * cm, page_height - 2 * cm, fill=0, stroke=1)

    # Cadre intérieur décoratif (2cm de marge)
    c.setStrokeColor(OBSIDIAN)
    c.setLineWidth(2)
    c.rect(1.8 * cm, 1.8 * cm, page_width - 3.6 * cm, page_height - 3.6 * cm, fill=0, stroke=1)

    # Coins décoratifs amber
    corner_size = 25
    margin = 1.8 * cm
    draw_decorative_corner(c, margin, page_height - margin, corner_size, AMBER, flip_y=True)
    draw_decorative_corner(c, page_width - margin, page_height - margin, corner_size, AMBER, flip_x=True, flip_y=True)
    draw_decorative_corner(c, margin, margin, corner_size, AMBER)
    draw_decorative_corner(c, page_width - margin, margin, corner_size, AMBER, flip_x=True)

    # ============================
    # HEADER - Logo Kairos
    # ============================
    # Carré noir avec "K"
    logo_size = 1.3 * cm
    logo_x = page_width / 2 - logo_size / 2
    logo_y = page_height - 3.5 * cm

    c.setFillColor(OBSIDIAN)
    c.roundRect(logo_x, logo_y, logo_size, logo_size, 4, fill=1, stroke=0)
    c.setFillColor(IVORY)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(logo_x + logo_size / 2, logo_y + logo_size / 2 - 5, "K")

    # Point amber en haut à droite du logo
    c.setFillColor(AMBER)
    c.circle(logo_x + logo_size - 2, logo_y + logo_size - 2, 2.5, fill=1, stroke=0)

    # Nom Kairos
    c.setFillColor(OBSIDIAN)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_width / 2, logo_y - 0.6 * cm, "KAIROS")
    c.setFont("Helvetica", 7)
    c.setFillColor(SMOKE)
    c.drawCentredString(page_width / 2, logo_y - 0.95 * cm, "E-LEARNING PLATFORM")

    # ============================
    # TITRE
    # ============================
    title_y = page_height - 6 * cm

    # Petit séparateur
    sep_y = title_y + 0.4 * cm
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.5)
    c.line(page_width / 2 - 25, sep_y, page_width / 2 + 25, sep_y)

    # "CERTIFICAT DE RÉUSSITE"
    c.setFillColor(SMOKE)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(page_width / 2, title_y - 0.3 * cm, "CERTIFICAT DE RÉUSSITE")

    # Grand titre éditorial
    c.setFillColor(OBSIDIAN)
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(page_width / 2, title_y - 1.7 * cm, "Ce certificat est décerné à")

    # ============================
    # NOM DE L'ÉTUDIANT
    # ============================
    name_y = page_height - 10 * cm

    # Nom en très grand (simule Fraunces)
    c.setFillColor(OBSIDIAN)
    c.setFont("Helvetica-Bold", 48)

    # Calculer la largeur pour centrer correctement le nom
    student_name = certificate.student_name
    c.drawCentredString(page_width / 2, name_y, student_name)

    # Ligne de décoration sous le nom
    name_line_width = 7 * cm
    c.setStrokeColor(OBSIDIAN)
    c.setLineWidth(0.5)
    c.line(
        page_width / 2 - name_line_width / 2,
        name_y - 0.5 * cm,
        page_width / 2 + name_line_width / 2,
        name_y - 0.5 * cm
    )

    # ============================
    # DESCRIPTION
    # ============================
    desc_y = page_height - 12 * cm

    c.setFillColor(INK)
    c.setFont("Helvetica", 13)
    c.drawCentredString(
        page_width / 2,
        desc_y,
        "pour avoir complété avec succès le cours"
    )

    # Titre du cours en italique amber
    c.setFillColor(AMBER)
    c.setFont("Helvetica-BoldOblique", 20)

    course_title = certificate.course_title
    # Si trop long, réduire la taille
    if len(course_title) > 50:
        c.setFont("Helvetica-BoldOblique", 16)

    c.drawCentredString(page_width / 2, desc_y - 1 * cm, f'« {course_title} »')

    # Dispensé par...
    c.setFillColor(SMOKE)
    c.setFont("Helvetica", 11)
    c.drawCentredString(
        page_width / 2,
        desc_y - 1.8 * cm,
        f"dispensé par {certificate.instructor_name}"
    )

    # ============================
    # INFOS BAS (2 colonnes : gauche date, centre numéro, droite signature)
    # ============================
    bottom_y = 4 * cm
    col_width = (page_width - 5 * cm) / 3

    # Colonne gauche : Date
    left_x = 2.5 * cm + col_width / 2

    c.setStrokeColor(MIST)
    c.setLineWidth(0.5)
    c.line(left_x - 2 * cm, bottom_y + 0.8 * cm, left_x + 2 * cm, bottom_y + 0.8 * cm)

    c.setFillColor(OBSIDIAN)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(left_x, bottom_y + 0.3 * cm, certificate.issued_at.strftime("%d %B %Y"))

    c.setFillColor(SMOKE)
    c.setFont("Helvetica", 7)
    c.drawCentredString(left_x, bottom_y - 0.1 * cm, "DATE DE DÉLIVRANCE")

    # Colonne centrale : Score ou Certificat
    center_x = page_width / 2

    c.setStrokeColor(MIST)
    c.line(center_x - 2 * cm, bottom_y + 0.8 * cm, center_x + 2 * cm, bottom_y + 0.8 * cm)

    if certificate.quiz_score:
        c.setFillColor(AMBER)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(center_x, bottom_y + 0.3 * cm, f"{certificate.quiz_score:.0f}%")

        c.setFillColor(SMOKE)
        c.setFont("Helvetica", 7)
        c.drawCentredString(center_x, bottom_y - 0.1 * cm, "SCORE AU QUIZ FINAL")
    else:
        c.setFillColor(FOREST)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(center_x, bottom_y + 0.3 * cm, "100% COMPLÉTÉ")

        c.setFillColor(SMOKE)
        c.setFont("Helvetica", 7)
        c.drawCentredString(center_x, bottom_y - 0.1 * cm, "TAUX DE COMPLÉTION")

    # Colonne droite : Numéro certificat
    right_x = page_width - 2.5 * cm - col_width / 2

    c.setStrokeColor(MIST)
    c.line(right_x - 2.2 * cm, bottom_y + 0.8 * cm, right_x + 2.2 * cm, bottom_y + 0.8 * cm)

    c.setFillColor(OBSIDIAN)
    c.setFont("Courier-Bold", 11)
    c.drawCentredString(right_x, bottom_y + 0.3 * cm, certificate.certificate_number)

    c.setFillColor(SMOKE)
    c.setFont("Helvetica", 7)
    c.drawCentredString(right_x, bottom_y - 0.1 * cm, "NUMÉRO DE CERTIFICAT")

    # ============================
    # FOOTER - URL de vérification
    # ============================
    c.setFillColor(FOG)
    c.setFont("Helvetica", 7)
    c.drawCentredString(
        page_width / 2,
        1.3 * cm,
        "Authenticité vérifiable sur kairos.tg/certificats/verifier · Document généré automatiquement"
    )

    # ============================
    # SCEAU DÉCORATIF (coin bas droit)
    # ============================
    seal_x = page_width - 4 * cm
    seal_y = bottom_y + 2.8 * cm
    seal_radius = 1 * cm

    # Cercle externe
    c.setStrokeColor(AMBER)
    c.setLineWidth(2)
    c.circle(seal_x, seal_y, seal_radius, fill=0, stroke=1)

    # Cercle interne
    c.setStrokeColor(AMBER)
    c.setLineWidth(0.5)
    c.circle(seal_x, seal_y, seal_radius - 4, fill=0, stroke=1)

    # Étoile/Symbole au centre
    c.setFillColor(AMBER)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(seal_x, seal_y - 4, "✓")

    # Texte autour (simulé simple)
    c.setFillColor(AMBER)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(seal_x, seal_y + seal_radius + 0.2 * cm, "CERTIFIÉ • VALIDÉ")

    # ============================
    # Générer le PDF
    # ============================
    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes