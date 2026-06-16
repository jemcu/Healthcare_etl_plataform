# TODO — Correcciones del proyecto (backend ML)

- [x] Inspeccionar código de ML (trainer.py) y settings.py
- [x] Corregir `backend/app/ml/services/trainer.py` para que `MODELS_DIR` use `settings.ML_MODELS_DIR` en vez de rutas frágiles con `dirname(dirname(...))`
- [x] Corregir `load_active_model()` para que use `EstadoChoices.LISTO` (en vez de string literal)
- [ ] Validar ejecución global con `python manage.py check`
- [ ] Correr `python manage.py makemigrations --check` (sin aplicar) y `python manage.py migrate --plan` (si aplica)
- [ ] Revisar consistencia del modelo (labels/encoding) entre `preprocessor.py`, `evaluator.py` y `predictor.py`
- [ ] Revisar endpoints ML y nombres de apps/urls para asegurar que no haya rutas rotas

