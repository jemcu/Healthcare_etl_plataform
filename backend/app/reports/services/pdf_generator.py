import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable,
)


# ── Paleta de colores ─────────────────────────────────────────────────────────
COLOR_PRIMARY   = colors.HexColor('#1a6fa8')
COLOR_SECONDARY = colors.HexColor('#e8f4fd')
COLOR_CRITICO   = colors.HexColor('#dc2626')
COLOR_ALTO      = colors.HexColor('#f97316')
COLOR_MEDIO     = colors.HexColor('#eab308')
COLOR_BAJO      = colors.HexColor('#16a34a')
COLOR_HEADER    = colors.HexColor('#1e3a5f')

RIESGO_COLOR = {
    'Crítico': COLOR_CRITICO,
    'Alto':    COLOR_ALTO,
    'Medio':   COLOR_MEDIO,
    'Bajo':    COLOR_BAJO,
}


def _header_style():
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=18,
        textColor=COLOR_PRIMARY,
        fontName='Helvetica-Bold',
        spaceAfter=4,
    )


def _subheader_style():
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#555555'),
        spaceAfter=12,
    )


def _normal_style():
    return getSampleStyleSheet()['Normal']


def _build_table_style(n_rows: int, header_bg=COLOR_PRIMARY) -> TableStyle:
    style = [
        ('BACKGROUND',   (0, 0), (-1, 0),  header_bg),
        ('TEXTCOLOR',    (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',     (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0),  9),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_SECONDARY]),
        ('FONTSIZE',     (0, 1), (-1, -1), 8),
        ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('LEFTPADDING',  (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]
    return TableStyle(style)


# ── Generadores públicos ──────────────────────────────────────────────────────

def generar_pdf_pacientes(pacientes_qs, filtros: dict = None) -> bytes:
    """
    Genera PDF con listado de pacientes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.5 * cm, leftMargin=1.5 * cm,
        topMargin=1.5 * cm,   bottomMargin=1.5 * cm,
    )

    elements = []
    styles   = getSampleStyleSheet()

    # Encabezado
    elements.append(Paragraph('HealthAnalytics IPS', _header_style()))
    elements.append(Paragraph(
        f'Reporte de Pacientes — Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
        _subheader_style()
    ))
    if filtros:
        elements.append(Paragraph(f'Filtros aplicados: {filtros}', styles['Normal']))
    elements.append(HRFlowable(width='100%', color=COLOR_PRIMARY, thickness=1.5))
    elements.append(Spacer(1, 0.4 * cm))

    # Tabla
    headers = [
        'ID', 'Nombre', 'Edad', 'Sexo', 'IMC', 'Clasif. IMC',
        'P. Sistólica', 'Glucosa', 'Sat. O₂', 'Riesgo', 'Diagnóstico',
    ]
    data = [headers]

    for p in pacientes_qs:
        data.append([
            str(p.id_paciente),
            f"{p.nombres} {p.apellidos}"[:25],
            str(p.edad),
            p.sexo,
            f"{p.imc:.1f}",
            p.clasificacion_imc,
            str(p.presion_sistolica),
            f"{p.glucosa:.0f}",
            f"{p.saturacion_oxigeno:.0f}%",
            p.riesgo_enfermedad,
            p.diagnostico_preliminar[:20],
        ])

    col_widths = [1.2*cm, 4.5*cm, 1.2*cm, 2.5*cm, 1.5*cm, 2.8*cm,
                  2.2*cm, 2*cm, 2*cm, 2*cm, 5*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(_build_table_style(len(data)))
    elements.append(table)
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph(
        f'Total registros: {len(data) - 1}',
        styles['Normal']
    ))

    doc.build(elements)
    return buffer.getvalue()


def generar_pdf_analitica(kpis: dict) -> bytes:
    """
    Genera PDF con KPIs y métricas clínicas del dashboard.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm,   bottomMargin=2*cm)
    elements = []
    styles   = getSampleStyleSheet()

    elements.append(Paragraph('HealthAnalytics IPS', _header_style()))
    elements.append(Paragraph(
        f'Reporte Analítica Clínica — {datetime.now().strftime("%d/%m/%Y %H:%M")}',
        _subheader_style()
    ))
    elements.append(HRFlowable(width='100%', color=COLOR_PRIMARY, thickness=1.5))
    elements.append(Spacer(1, 0.5 * cm))

    # KPIs principales
    elements.append(Paragraph('KPIs Principales', styles['Heading2']))
    kpi_data = [
        ['Indicador', 'Valor'],
        ['Total Pacientes',         str(kpis.get('total_pacientes', 0))],
        ['Pacientes Críticos',      str(kpis.get('pacientes_criticos', 0))],
        ['Pacientes Hipertensos',   f"{kpis.get('pacientes_hipertensos', 0)} ({kpis.get('porcentaje_hipertensos', 0)}%)"],
        ['Pacientes Diabéticos',    f"{kpis.get('pacientes_diabeticos', 0)} ({kpis.get('porcentaje_diabeticos', 0)}%)"],
        ['Pacientes Fumadores',     f"{kpis.get('pacientes_fumadores', 0)} ({kpis.get('porcentaje_fumadores', 0)}%)"],
    ]
    t = Table(kpi_data, colWidths=[10*cm, 7*cm])
    t.setStyle(_build_table_style(len(kpi_data)))
    elements.append(t)
    elements.append(Spacer(1, 0.5 * cm))

    # Distribución por riesgo
    dist = kpis.get('distribucion_riesgo', {})
    if dist:
        elements.append(Paragraph('Distribución por Riesgo', styles['Heading2']))
        riesgo_data = [['Nivel', 'Cantidad']] + [[k, str(v)] for k, v in dist.items()]
        t2 = Table(riesgo_data, colWidths=[10*cm, 7*cm])
        t2.setStyle(_build_table_style(len(riesgo_data)))
        elements.append(t2)

    doc.build(elements)
    return buffer.getvalue()


def generar_pdf_ml(modelo_data: dict, metricas: dict) -> bytes:
    """
    Genera PDF con métricas del modelo ML activo.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm,   bottomMargin=2*cm)
    elements = []
    styles   = getSampleStyleSheet()

    elements.append(Paragraph('HealthAnalytics IPS', _header_style()))
    elements.append(Paragraph(
        f'Reporte Machine Learning — {datetime.now().strftime("%d/%m/%Y %H:%M")}',
        _subheader_style()
    ))
    elements.append(HRFlowable(width='100%', color=COLOR_PRIMARY, thickness=1.5))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph('Información del Modelo', styles['Heading2']))
    model_data_table = [
        ['Parámetro', 'Valor'],
        ['Nombre',    modelo_data.get('nombre', '')],
        ['Algoritmo', modelo_data.get('algoritmo_display', '')],
        ['Versión',   str(modelo_data.get('version', ''))],
        ['Registros entrenamiento', str(modelo_data.get('registros_entrenamiento', ''))],
    ]
    t = Table(model_data_table, colWidths=[9*cm, 8*cm])
    t.setStyle(_build_table_style(len(model_data_table)))
    elements.append(t)
    elements.append(Spacer(1, 0.4 * cm))

    elements.append(Paragraph('Métricas de Evaluación', styles['Heading2']))
    met_data = [
        ['Métrica', 'Valor'],
        ['Accuracy',  f"{metricas.get('accuracy', 0):.4f}"],
        ['Precision', f"{metricas.get('precision', 0):.4f}"],
        ['Recall',    f"{metricas.get('recall', 0):.4f}"],
        ['F1-Score',  f"{metricas.get('f1_score', 0):.4f}"],
        ['ROC AUC',   f"{metricas.get('roc_auc', 'N/A')}"],
    ]
    t2 = Table(met_data, colWidths=[9*cm, 8*cm])
    t2.setStyle(_build_table_style(len(met_data)))
    elements.append(t2)

    doc.build(elements)
    return buffer.getvalue()