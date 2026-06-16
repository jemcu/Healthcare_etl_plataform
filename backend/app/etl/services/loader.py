import pandas as pd
import logging
from datetime import datetime
from django.apps import apps
from django.db import transaction

logger = logging.getLogger(__name__)


def get_model(app, name):
    return apps.get_model(app, name)


def load_to_database(df: pd.DataFrame, etl_log) -> dict:
    """
    Inserta los registros limpios en la tabla de pacientes.
    Usa bulk_create para eficiencia.
    Retorna { cargados, errores }
    """
    Paciente = get_model('patients', 'Paciente')

    cargados = 0
    errores = []
    pacientes_nuevos = []

    # Limpiar tabla si es carga completa (opcional: comentar para modo incremental)
    Paciente.objects.all().delete()
    logger.info("[LOAD] Tabla pacientes limpiada para carga fresca.")

    for _, row in df.iterrows():
        try:
            p = Paciente(
                id_paciente=int(row.get('id_paciente', 0)) if pd.notna(row.get('id_paciente')) else None,
                nombres=str(row.get('nombres', '')).strip()[:100],
                apellidos=str(row.get('apellidos', '')).strip()[:100],
                edad=int(row['edad']) if pd.notna(row.get('edad')) else 0,
                sexo=str(row.get('sexo', 'Sin datos'))[:20],
                peso=float(row['peso']) if pd.notna(row.get('peso')) else 0.0,
                altura=float(row['altura']) if pd.notna(row.get('altura')) else 0.0,
                imc=float(row['imc']) if pd.notna(row.get('imc')) else 0.0,
                presion_sistolica=int(row['presion_sistolica']) if pd.notna(row.get('presion_sistolica')) else 0,
                presion_diastolica=int(row['presion_diastolica']) if pd.notna(row.get('presion_diastolica')) else 0,
                frecuencia_cardiaca=int(row['frecuencia_cardiaca']) if pd.notna(row.get('frecuencia_cardiaca')) else 0,
                glucosa=float(row['glucosa']) if pd.notna(row.get('glucosa')) else 0.0,
                colesterol=float(row['colesterol']) if pd.notna(row.get('colesterol')) else 0.0,
                saturacion_oxigeno=float(row['saturacion_oxigeno']) if pd.notna(row.get('saturacion_oxigeno')) else 0.0,
                temperatura=float(row['temperatura']) if pd.notna(row.get('temperatura')) else 0.0,
                antecedentes_familiares=bool(row.get('antecedentes_familiares', False)),
                fumador=bool(row.get('fumador', False)),
                consumo_alcohol=bool(row.get('consumo_alcohol', False)),
                actividad_fisica=str(row.get('actividad_fisica', ''))[:50],
                diagnostico_preliminar=str(row.get('diagnostico_preliminar', ''))[:200],
                riesgo_enfermedad=str(row.get('riesgo_enfermedad', 'Bajo'))[:20],
                fecha_consulta=row['fecha_consulta'].date() if pd.notna(row.get('fecha_consulta')) else datetime.now().date(),
            )
            pacientes_nuevos.append(p)

        except Exception as e:
            errores.append({
                'fila': int(row.get('id_paciente', '?')),
                'error': str(e)
            })

    # Inserción masiva en bloques de 500
    BATCH = 500
    with transaction.atomic():
        for i in range(0, len(pacientes_nuevos), BATCH):
            batch = pacientes_nuevos[i:i + BATCH]
            Paciente.objects.bulk_create(batch, ignore_conflicts=True)
            cargados += len(batch)
            logger.info(f"[LOAD] Bloque {i // BATCH + 1}: {len(batch)} registros cargados.")

    logger.info(f"[LOAD] Total cargados: {cargados} | Errores: {len(errores)}")

    # Actualizar el ETL log con resultado
    etl_log.registros_cargados = cargados
    etl_log.detalle_errores = errores[:50]  # Guardar max 50 errores
    etl_log.save(update_fields=['registros_cargados', 'detalle_errores'])

    return {'cargados': cargados, 'errores': errores}