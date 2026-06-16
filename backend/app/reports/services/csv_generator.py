import csv
import io


def generar_csv_pacientes(pacientes_qs) -> bytes:
    """CSV con todos los campos del paciente."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        'id_paciente', 'nombres', 'apellidos', 'edad', 'sexo',
        'peso', 'altura', 'imc', 'clasificacion_imc',
        'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca',
        'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura',
        'antecedentes_familiares', 'fumador', 'consumo_alcohol',
        'actividad_fisica', 'diagnostico_preliminar',
        'riesgo_enfermedad', 'fecha_consulta',
    ])

    for p in pacientes_qs:
        writer.writerow([
            p.id_paciente, p.nombres, p.apellidos, p.edad, p.sexo,
            p.peso, p.altura, round(p.imc, 2), p.clasificacion_imc,
            p.presion_sistolica, p.presion_diastolica, p.frecuencia_cardiaca,
            p.glucosa, p.colesterol, p.saturacion_oxigeno, p.temperatura,
            p.antecedentes_familiares, p.fumador, p.consumo_alcohol,
            p.actividad_fisica, p.diagnostico_preliminar,
            p.riesgo_enfermedad, p.fecha_consulta,
        ])

    return buffer.getvalue().encode('utf-8-sig')  # BOM para Excel en español


def generar_csv_etl(etl_logs_qs) -> bytes:
    """CSV con historial de ejecuciones ETL."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        'id', 'fecha_inicio', 'archivo_origen', 'tipo_origen',
        'registros_extraidos', 'registros_limpios', 'registros_cargados',
        'duplicados_removidos', 'nulos_tratados',
        'outliers_corregidos', 'tiempo_ejecucion', 'estado', 'mensaje',
    ])

    for log in etl_logs_qs:
        writer.writerow([
            log.id,
            log.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S'),
            log.archivo_origen,
            log.tipo_origen,
            log.registros_extraidos,
            log.registros_limpios,
            log.registros_cargados,
            log.duplicados_removidos,
            log.nulos_tratados,
            log.outliers_corregidos,
            round(log.tiempo_ejecucion, 2),
            log.estado,
            log.mensaje,
        ])

    return buffer.getvalue().encode('utf-8-sig')