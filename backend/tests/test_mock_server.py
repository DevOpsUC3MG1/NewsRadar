import pytest
import responses
import requests

@responses.activate
def test_worker_con_servidor_mock(mock_rss_xml):
    """
    Simula un servidor web real que responde con nuestro XML falso
    cuando el worker intenta acceder a una URL específica.
    """
    url_falsa = "https://noticias-tecnologia.com/rss.xml"

    # Configuramos el servidor mock para que cuando reciba un GET a esa URL,
    # devuelva un código 200 y el contenido de nuestro archivo feed_falso.xml
    responses.add(
        responses.GET,
        url_falsa,
        body=mock_rss_xml,
        status=200,
        content_type='application/rss+xml',
    )

    # El "Worker" (aquí simulado con requests) intenta descargar la noticia
    respuesta = requests.get(url_falsa)

    # Validamos que el servidor falso ha respondido correctamente
    assert respuesta.status_code == 200
    assert "NewsRadar Test Times" in respuesta.text
    assert "La IA revoluciona la educación" in respuesta.text