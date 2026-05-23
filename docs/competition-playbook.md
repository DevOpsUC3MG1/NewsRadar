# Competition Playbook

## Añadir funcionalidad

1. Crear rama desde `main`: `git checkout -b feat/nombre-cambio`
2. Implementar backend (FastAPI + endpoint en `main.py`)
3. Añadir tests en `backend/tests/`
4. Verificar tests localmente:
   ```bash
   DATABASE_URL="postgresql+asyncpg://newsuser:newspassword@localhost:5432/newsradar_db" \
   MONGODB_URL="mongodb://admin:adminpassword@localhost:27017" \
   ENV=testing python -m pytest backend/tests/ -v --cov=backend/newsradar_api --cov-report=term
   ```
5. Verificar lint: `flake8 . --exclude=backend/migrations --max-line-length=120`
6. Commit + push → PR a `main`
7. Merge tras CI verde

## Desactivar funcionalidad (feature flag)

El sistema usa flags por variable de entorno definidas en `.env`:

| Flag | Efecto |
|------|--------|
| `ENV=testing` | Desactiva validaciones externas (email, etc.) |
| `DISABLE_EMAIL_VERIFICATION=true` | Salta envío de correos de verificación |

Para desactivar una funcionalidad sin borrar código:
1. Localizar su flag en `.env` o crear una nueva variable
2. Añadir guard clause en el endpoint:
   ```python
   if os.getenv("FEATURE_X_ENABLED", "true").lower() == "false":
       raise HTTPException(status_code=503, detail="Feature disabled")
   ```
3. Desplegar cambiando la variable en `.env` del servidor

## Rollback a versión previa

```bash
# Ver historial de versiones (git tags o SHA)
git log --oneline -10

# Rollback a un commit específico
git revert --no-commit <SHA>..HEAD
git commit -m "rollback: revert to <SHA>"

# O desplegar versión anterior
git checkout <tag-anterior>
docker compose up -d --build
```

Tags recomendados para releases:
```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```
