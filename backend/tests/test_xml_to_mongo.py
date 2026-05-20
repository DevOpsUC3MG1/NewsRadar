from datetime import datetime


def test_transformacion_xml_a_mongodb():
    """
    Simula la entrada de un XML y valida que el diccionario resultante
    tenga el formato exacto requerido por MongoDB.
    """
    # 1. Simulación de dato crudo del XML (Entrada)
    xml_item = {
        "title": "Noticia Espacial",
        "link": "https://nasa.gov/news1",
        "description": "Agua encontrada en Marte",
        "pubDate": "Tue, 05 May 2026 10:00:00 +0000",
    }

    # 2. Lógica de transformación (Lo que debería hacer tu Worker)
    # Aquí simulamos la 'traducción' de nombres de campos
    documento_mongo = {
        "title": xml_item["title"],
        "url": xml_item["link"],  # Cambio de 'link' a 'url'
        "content": xml_item["description"],  # Cambio de 'description' a 'content'
        "published_at": xml_item["pubDate"],  # Mantenemos fecha
        "captured_at": datetime.utcnow().isoformat(),  # Añadimos metadato de sistema
        "status": "unread",  # Estado inicial en DB
    }

    # 3. VALIDACIONES DE INTEGRIDAD
    assert "url" in documento_mongo
    assert "content" in documento_mongo
    assert documento_mongo["title"] == "Noticia Espacial"
    assert isinstance(documento_mongo["captured_at"], str)

    # Comprobamos que no se han colado etiquetas XML raras
    assert "<item>" not in documento_mongo["title"]
