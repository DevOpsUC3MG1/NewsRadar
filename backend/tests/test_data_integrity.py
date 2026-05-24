async def test_integridad_datos_noticia(client, gestor_headers):
    """
    Simula el flujo de una noticia desde la base de datos hasta el cliente
    verificando que no se pierdan campos obligatorios.
    """
    response = await client.get("/api/v1/news/latest", headers=gestor_headers)

    campos_obligatorios = ["title", "link", "author", "published_at", "content", "source_name"]

    if response.status_code == 200:
        data = response.json()[0]
        for campo in campos_obligatorios:
            assert campo in data, f"Error de integridad: falta el campo {campo}"
    else:
        assert response.status_code == 404
