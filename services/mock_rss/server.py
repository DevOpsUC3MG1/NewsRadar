"""
Servidor RSS mock avanzado para NewsRadar.
Genera combinaciones aleatorias de noticias para probar la clasificación IPTC.
"""
import random
import uuid
from datetime import datetime, timezone
from email.utils import format_datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Diccionario de componentes para generar noticias dinámicas
TEMPLATES = {
    "Politics": {
        "subjects": ["El Congreso", "Pedro Sánchez", "La oposición", "El Ministerio", "Bruselas"],
        "actions": ["debate sobre", "aprueba el nuevo plan de", "critica la gestión de", "anuncia medidas para"],
        "objects": ["la ley de vivienda", "los presupuestos", "la reforma laboral", "el estado de alarma"]
    },
    "Business": {
        "subjects": ["El Ibex 35", "El BCE", "Santander", "La inflación", "El sector energético"],
        "actions": ["sube un 2% por", "se desploma tras", "mantiene los tipos ante", "lidera el crecimiento en"],
        "objects": ["la crisis de suministros", "los resultados trimestrales", "la banca europea", "el precio del gas"]
    },
    "Sports": {
        "subjects": ["El Real Madrid", "Carlos Alcaraz", "La selección", "El Barça", "Rafa Nadal"],
        "actions": ["gana con solvencia en", "avanza a la final de", "sufre una derrota en", "ficha a una estrella para"],
        "objects": ["la Champions", "Roland Garros", "el derbi", "el próximo mundial"]
    },
    "Technology": {
        "subjects": ["Apple", "La IA generativa", "Google", "El nuevo chip", "La ciberseguridad"],
        "actions": ["revoluciona el mercado de", "presenta mejoras en", "advierte sobre riesgos en", "lanza su versión de"],
        "objects": ["la computación cuántica", "los smartphones", "la privacidad de datos", "el Metaverso"]
    }
}


def generate_news(category: str, count: int = 5):
    """Genera una lista de noticias aleatorias basadas en plantillas."""
    news = []
    data = TEMPLATES.get(category, TEMPLATES["Politics"])
    for i in range(count):
        title = f"{random.choice(data['subjects'])} {random.choice(data['actions'])} {random.choice(data['objects'])}"
        news.append({
            "title": title,
            "description": f"Detalle importante sobre cómo {title.lower()}. Cobertura especial NewsRadar.",
            "link": f"http://mock_rss/{category.lower()}/{uuid.uuid4().hex[:8]}",
            "guid": str(uuid.uuid4())
        })
    return news


def rss_template(channel_title: str, items: list) -> str:
    now = datetime.now(timezone.utc)
    items_xml = ""
    for it in items:
        items_xml += f"""
    <item>
      <title>{it['title']}</title>
      <description>{it['description']}</description>
      <link>{it['link']}</link>
      <guid isPermaLink="false">{it['guid']}</guid>
      <pubDate>{format_datetime(now)}</pubDate>
    </item>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{channel_title}</title>
    <link>http://mock_rss</link>
    <description>Feed dinámico para NewsRadar</description>
    <lastBuildDate>{format_datetime(now)}</lastBuildDate>
    {items_xml}
  </channel>
</rss>"""


class AdvancedHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Mapeo de rutas a categorías IPTC
        routes = {
            "/politica.xml": "Politics",
            "/economia.xml": "Business",
            "/deportes.xml": "Sports",
            "/tecnologia.xml": "Technology"
        }

        if self.path in routes:
            category = routes[self.path]
            items = generate_news(category)
            body = rss_template(f"Noticias de {category}", items).encode("utf-8")
            self._send_rss(body)
        elif self.path == "/test.xml":
            # Caso especial para matchear todo
            items = [{
                "title": "TEST: Ibex Sánchez Madrid Alcaraz IA",
                "description": "Noticia de prueba con múltiples palabras clave para test de alertas.",
                "link": "http://mock_rss/test/unique",
                "guid": str(uuid.uuid4())
            }]
            body = rss_template("Mock Test Global", items).encode("utf-8")
            self._send_rss(body)
        else:
            self.send_response(404)
            self.end_headers()

    def _send_rss(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "application/rss+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), AdvancedHandler)
    print("Servidor Mock Pro iniciado en puerto 8080...")
    server.serve_forever()
