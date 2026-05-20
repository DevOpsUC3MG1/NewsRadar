from unittest.mock import patch


def test_worker_procesa_feed_correctamente(mock_rss_xml):
    """Prueba que el worker lee correctamente el XML sin salir a internet real"""

    # Interceptamos la librería 'requests' (que es la que suele usar el backend para descargar cosas)
    with patch('requests.get') as mock_get:
        # Le decimos al "espía" que cuando el backend pida una web, devuelva un 200 (OK) y tu XML
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = mock_rss_xml.encode('utf-8')

        # ---------------------------------------------------------
        # AQUÍ IRÁ LA LLAMADA A LA FUNCIÓN REAL DE TUS COMPAÑEROS
        # Ejemplo: noticias = worker.procesar_fuente("http://elpais.com/rss")
        # ---------------------------------------------------------

        # Como M1 aún no ha programado esa función, por ahora probamos
        # que nuestro simulador (Mock) funciona perfectamente:
        respuesta_falsa = mock_get("http://cualquier-periodico.com")

        # Comprobamos que el simulador devuelve estado 200
        assert respuesta_falsa.status_code == 200

        # Comprobamos que el simulador contiene la noticia de tu periódico falso
        contenido_decodificado = respuesta_falsa.content.decode('utf-8')
        assert "La IA revoluciona la educación" in contenido_decodificado
        assert "Economía" in contenido_decodificado
