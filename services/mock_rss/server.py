"""
Servidor RSS mock para pruebas del demonio NewsRadar.

Cada petición genera un feed RSS con noticias cuyo pubDate es "ahora",
así el demonio siempre las considera nuevas.

Endpoints:
  GET /politica.xml   → 3 noticias categoría Politica (con "Ibex", "Sánchez", "Congreso")
  GET /economia.xml   → 3 noticias categoría Economia
  GET /deportes.xml   → 3 noticias categoría Deportes
  GET /test.xml       → 1 noticia genérica de test que matchea cualquier descriptor
                       (siempre incluye "TEST" y "noticia" en el título)
"""
from datetime import datetime, timezone
from email.utils import format_datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import uuid


def rss(channel_title: str, items: list[dict]) -> str:
    now = datetime.now(timezone.utc)
    items_xml = "\n".join(
        f"""    <item>
      <title>{it['title']}</title>
      <description>{it['description']}</description>
      <link>{it['link']}</link>
      <guid isPermaLink="false">{it['guid']}</guid>
      <pubDate>{format_datetime(now)}</pubDate>
    </item>"""
        for it in items
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{channel_title}</title>
    <link>http://mock_rss</link>
    <description>Feed mock para pruebas</description>
    <lastBuildDate>{format_datetime(now)}</lastBuildDate>
{items_xml}
  </channel>
</rss>
"""


FEEDS = {
    "/politica.xml": (
        "Mock Política",
        [
            {"title": "El Ibex 35 cierra con subidas tras la sesión del Congreso",
             "description": "Sánchez comparece ante los medios para explicar los nuevos presupuestos.",
             "link": "http://mock_rss/politica/1"},
            {"title": "Pedro Sánchez se reúne con líderes europeos en Bruselas",
             "description": "Cumbre de jefes de estado para debatir el futuro de la UE.",
             "link": "http://mock_rss/politica/2"},
            {"title": "Debate en el Congreso sobre los presupuestos generales",
             "description": "La oposición critica las cifras presentadas por el gobierno.",
             "link": "http://mock_rss/politica/3"},
        ],
    ),
    "/economia.xml": (
        "Mock Economía",
        [
            {"title": "El Ibex 35 sube un 2% impulsado por la banca",
             "description": "Las acciones de Santander y BBVA lideran las subidas en la bolsa española.",
             "link": "http://mock_rss/economia/1"},
            {"title": "El BCE mantiene los tipos de interés en su última reunión",
             "description": "Christine Lagarde anuncia que vigilan de cerca la inflación.",
             "link": "http://mock_rss/economia/2"},
            {"title": "La inflación se modera al 2.5% en abril",
             "description": "Datos del INE confirman la tendencia bajista del IPC.",
             "link": "http://mock_rss/economia/3"},
        ],
    ),
    "/deportes.xml": (
        "Mock Deportes",
        [
            {"title": "Real Madrid gana la Liga tras vencer al Barcelona",
             "description": "Vinicius marca el gol decisivo en el Bernabéu.",
             "link": "http://mock_rss/deportes/1"},
            {"title": "Carlos Alcaraz avanza a la final de Roland Garros",
             "description": "El murciano supera a Djokovic en cinco sets.",
             "link": "http://mock_rss/deportes/2"},
            {"title": "El Atlético de Madrid ficha a una nueva estrella",
             "description": "El club rojiblanco refuerza su plantilla para la próxima temporada.",
             "link": "http://mock_rss/deportes/3"},
        ],
    ),
    "/test.xml": (
        "Mock Test",
        [
            {"title": "TEST: Esta es una noticia de prueba para NewsRadar",
             "description": "Esta noticia siempre matchea cualquier alerta con descriptor 'TEST' o 'prueba'. Ibex Sánchez Madrid Real BCE inflación.",
             "link": "http://mock_rss/test/1"},
        ],
    ),
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            paths = "\n".join(FEEDS.keys())
            self.wfile.write(f"Mock RSS server. Endpoints:\n{paths}\n".encode())
            return

        if self.path not in FEEDS:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        title, items_template = FEEDS[self.path]
        # GUID único en cada petición → el demonio las trata como nuevas
        items = [{**it, "guid": str(uuid.uuid4())} for it in items_template]
        body = rss(title, items).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/rss+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # logs más limpios
        print(f"[mock_rss] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("Mock RSS server escuchando en :8080")
    print("Endpoints:", ", ".join(FEEDS.keys()))
    server.serve_forever()