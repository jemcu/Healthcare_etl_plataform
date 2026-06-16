import io
from datetime import datetime
import xlsxwriter


def _add_header(ws, workbook, title: str):
    """Escribe el encabezado estándar del reporte."""
    header_fmt = workbook.add_format({
        'bold': True, 'font_size': 14,
        'font_color': '#1a6fa8', 'border': 0,
    })
    sub_fmt = workbook.add_format({'font_size': 10, 'font_color': '#555555'})
    ws.write('A1', 'HealthAnalytics IPS', header_fmt)
    ws.write('A2', title, sub_fmt)
    ws.write('A3', f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', sub_fmt)


def _col_header_fmt(workbook):
    return workbook.add_format({
        'bold': True, 'bg_color': '#1a6fa8',
        'font_color': 'white', 'border': 1,
        'align': 'center', 'valign': 'vcenter',
        'font_size': 9,
    })


def _riesgo_fmt(workbook, riesgo: str):
    COLOR_MAP = {
        'Crítico': '#dc2626', 'Alto': '#f97316',
        'Medio':   '#eab308', 'Bajo': '#16a34a',
    }
    bg = COLOR_MAP.get(riesgo, '#ffffff')
    return workbook.add_format({
        'bg_color': bg, 'font_color': 'white',
        'bold': True, 'align': 'center', 'border': 1,
    })


def _cell_fmt(workbook, row_idx: int):
    bg = '#e8f4fd' if row_idx % 2 == 0 else '#ffffff'
    return workbook.add_format({'bg_color': bg, 'border': 1, 'font_size': 8})


# ── Generadores públicos ──────────────────────────────────────────────────────

def generar_excel_pacientes(pacientes_qs, filtros: dict = None) -> bytes:
    """Excel con listado completo de pacientes."""
    buffer = io.BytesIO()
    wb = xlsxwriter.Workbook(buffer, {'in_memory': True})
    ws = wb.add_worksheet('Pacientes')

    _add_header(ws, wb, 'Reporte de Pacientes')

    headers = [
        'ID', 'Nombres', 'Apellidos', 'Edad', 'Sexo',
        'Peso', 'Altura', 'IMC', 'Clasif. IMC',
        'P. Sistólica', 'P. Diastólica', 'FC',
        'Glucosa', 'Colesterol', 'Sat. O₂', 'Temperatura',
        'Antecedentes', 'Fumador', 'Alcohol', 'Actividad Física',
        'Diagnóstico', 'Riesgo', 'Fecha Consulta',
    ]
    col_w = [6, 14, 14, 6, 12, 7, 7, 8, 13, 12, 12, 7,
             9, 10, 8, 11, 12, 9, 9, 14, 20, 10, 14]

    hfmt = _col_header_fmt(wb)
    START_ROW = 5

    for col, (h, w) in enumerate(zip(headers, col_w)):
        ws.write(START_ROW, col, h, hfmt)
        ws.set_column(col, col, w)

    for row_idx, p in enumerate(pacientes_qs):
        r = START_ROW + 1 + row_idx
        cfmt = _cell_fmt(wb, row_idx)
        rfmt = _riesgo_fmt(wb, p.riesgo_enfermedad)

        ws.write(r,  0, p.id_paciente, cfmt)
        ws.write(r,  1, p.nombres, cfmt)
        ws.write(r,  2, p.apellidos, cfmt)
        ws.write(r,  3, p.edad, cfmt)
        ws.write(r,  4, p.sexo, cfmt)
        ws.write(r,  5, p.peso, cfmt)
        ws.write(r,  6, p.altura, cfmt)
        ws.write(r,  7, round(p.imc, 2), cfmt)
        ws.write(r,  8, p.clasificacion_imc, cfmt)
        ws.write(r,  9, p.presion_sistolica, cfmt)
        ws.write(r, 10, p.presion_diastolica, cfmt)
        ws.write(r, 11, p.frecuencia_cardiaca, cfmt)
        ws.write(r, 12, p.glucosa, cfmt)
        ws.write(r, 13, p.colesterol, cfmt)
        ws.write(r, 14, p.saturacion_oxigeno, cfmt)
        ws.write(r, 15, p.temperatura, cfmt)
        ws.write(r, 16, 'Sí' if p.antecedentes_familiares else 'No', cfmt)
        ws.write(r, 17, 'Sí' if p.fumador else 'No', cfmt)
        ws.write(r, 18, 'Sí' if p.consumo_alcohol else 'No', cfmt)
        ws.write(r, 19, p.actividad_fisica, cfmt)
        ws.write(r, 20, p.diagnostico_preliminar, cfmt)
        ws.write(r, 21, p.riesgo_enfermedad, rfmt)
        ws.write(r, 22, str(p.fecha_consulta) if p.fecha_consulta else '', cfmt)

    total = pacientes_qs.count()
    ws.write(START_ROW + 1 + total + 1, 0,
             f'Total: {total}',
             wb.add_format({'bold': True, 'font_size': 10}))

    wb.close()
    return buffer.getvalue()


def generar_excel_analitica(kpis: dict, segmentos: dict = None) -> bytes:
    """Excel con KPIs y segmentaciones."""
    buffer = io.BytesIO()
    wb = xlsxwriter.Workbook(buffer, {'in_memory': True})

    # ── Hoja KPIs ──────────────────────────────────────────────────────────
    ws_kpi = wb.add_worksheet('KPIs')
    _add_header(ws_kpi, wb, 'Analítica Clínica — KPIs')
    hfmt = _col_header_fmt(wb)

    ws_kpi.set_column(0, 0, 30)
    ws_kpi.set_column(1, 1, 20)
    ws_kpi.write(5, 0, 'Indicador', hfmt)
    ws_kpi.write(5, 1, 'Valor', hfmt)

    kpi_rows = [
        ('Total Pacientes',         kpis.get('total_pacientes', 0)),
        ('Pacientes Críticos',       kpis.get('pacientes_criticos', 0)),
        ('Hipertensos',              kpis.get('pacientes_hipertensos', 0)),
        ('% Hipertensos',            f"{kpis.get('porcentaje_hipertensos', 0)}%"),
        ('Diabéticos',               kpis.get('pacientes_diabeticos', 0)),
        ('% Diabéticos',             f"{kpis.get('porcentaje_diabeticos', 0)}%"),
        ('Fumadores',                kpis.get('pacientes_fumadores', 0)),
        ('% Fumadores',              f"{kpis.get('porcentaje_fumadores', 0)}%"),
    ]
    for i, (label, val) in enumerate(kpi_rows):
        cfmt = _cell_fmt(wb, i)
        ws_kpi.write(6 + i, 0, label, cfmt)
        ws_kpi.write(6 + i, 1, val, cfmt)

    # Distribución por riesgo
    dist = kpis.get('distribucion_riesgo', {})
    offset = 6 + len(kpi_rows) + 2
    ws_kpi.write(offset, 0, 'Distribución por Riesgo', hfmt)
    ws_kpi.write(offset, 1, 'Cantidad', hfmt)
    for i, (nivel, cant) in enumerate(dist.items()):
        rfmt = _riesgo_fmt(wb, nivel)
        ws_kpi.write(offset + 1 + i, 0, nivel, rfmt)
        ws_kpi.write(offset + 1 + i, 1, cant, _cell_fmt(wb, i))

    # ── Hoja promedios ─────────────────────────────────────────────────────
    ws_avg = wb.add_worksheet('Promedios')
    _add_header(ws_avg, wb, 'Promedios Clínicos')
    ws_avg.set_column(0, 0, 28)
    ws_avg.set_column(1, 1, 18)
    ws_avg.write(5, 0, 'Variable', hfmt)
    ws_avg.write(5, 1, 'Promedio', hfmt)
    promedios = kpis.get('promedios', {})
    for i, (k, v) in enumerate(promedios.items()):
        cfmt = _cell_fmt(wb, i)
        ws_avg.write(6 + i, 0, k.replace('_', ' ').title(), cfmt)
        ws_avg.write(6 + i, 1, v, cfmt)

    wb.close()
    return buffer.getvalue()


def generar_excel_ml(modelo_data: dict, metricas: dict) -> bytes:
    """Excel con métricas del modelo ML."""
    buffer = io.BytesIO()
    wb = xlsxwriter.Workbook(buffer, {'in_memory': True})
    ws = wb.add_worksheet('Modelo ML')
    _add_header(ws, wb, 'Reporte Machine Learning')
    hfmt = _col_header_fmt(wb)
    ws.set_column(0, 1, 25)

    ws.write(5, 0, 'Parámetro', hfmt)
    ws.write(5, 1, 'Valor', hfmt)

    rows = [
        ('Nombre',      modelo_data.get('nombre', '')),
        ('Algoritmo',   modelo_data.get('algoritmo_display', '')),
        ('Versión',     modelo_data.get('version', '')),
        ('Registros',   modelo_data.get('registros_entrenamiento', '')),
        ('Accuracy',    metricas.get('accuracy', 0)),
        ('Precision',   metricas.get('precision', 0)),
        ('Recall',      metricas.get('recall', 0)),
        ('F1-Score',    metricas.get('f1_score', 0)),
        ('ROC AUC',     metricas.get('roc_auc', 'N/A')),
    ]
    for i, (k, v) in enumerate(rows):
        cfmt = _cell_fmt(wb, i)
        ws.write(6 + i, 0, k, cfmt)
        ws.write(6 + i, 1, v, cfmt)

    wb.close()
    return buffer.getvalue()