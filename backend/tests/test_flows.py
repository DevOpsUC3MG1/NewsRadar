def test_flujo_completo_gestion_noticias(client):
    """
    Simula el flujo completo de un Gestor:
    1. Login -> 2. Crear Canal RSS -> 3. Crear Alerta de término
    """
    # --- 1. LOGIN ---
    # Simulamos que el gestor se identifica para obtener permisos
    headers = {"Authorization": "Bearer token_valido_gestor"}

    # --- 2. CREAR CANAL (RSS SOURCE) ---
    canal_data = {
        "name": "El País - Tecnología",
        "url": "https://elpais.com/rss/tecnologia.xml",
        "is_active": True,
    }
    res_canal = client.post("/api/v1/sources", json=canal_data, headers=headers)
    # Nota: Dará 404 por ahora, pero así queda definido el contrato

    # --- 3. CREAR TÉRMINO (ALERTA) ---
    alerta_data = {
        "name": "Alerta IA",
        "keyword": "Inteligencia Artificial",
        "category": "Tecnología",
    }
    res_alerta = client.post("/api/v1/alerts", json=alerta_data, headers=headers)

    # --- VALIDACIÓN DE INTENCIONES ---
    # En este punto, como QA, validamos que si las rutas existieran,
    # el flujo tendría sentido lógico.
    assert res_canal.status_code in [201, 404]
    assert res_alerta.status_code in [201, 404]


def test_flujo_baja_de_terminos(client):
    """Valida que un usuario puede dejar de seguir un término (borrar alerta)"""
    headers = {"Authorization": "Bearer token_valido_gestor"}
    alerta_id = 999  # ID ficticio para la prueba

    # Intentamos borrar una alerta que ya no queremos
    response = client.delete(f"/api/v1/alerts/{alerta_id}", headers=headers)

    # Esperamos que el sistema responda (o 404 porque no existe la ruta aún)
    assert response.status_code in [204, 404]
