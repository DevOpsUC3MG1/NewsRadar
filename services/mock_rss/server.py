"""
Servidor RSS mock avanzado para NewsRadar.
Genera combinaciones aleatorias de noticias para probar la clasificación IPTC.
"""
import random
import uuid
from datetime import datetime, timezone
from email.utils import format_datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

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
    },
    "Culture": {
        "subjects": ["El Museo del Prado", "La nueva exposición", "El festival de cine", "La obra de teatro", "El artista urbano"],
        "actions": ["inaugura la temporada de", "bate récords de asistencia con", "presenta una muestra sobre", "reinventa el género de"],
        "objects": ["el arte contemporáneo", "la fotografía digital", "la literatura hispanoamericana", "la música clásica"]
    },
    "Health": {
        "subjects": ["La OMS", "El Ministerio de Sanidad", "Los hospitales", "Una nueva vacuna", "Los investigadores"],
        "actions": ["alerta sobre el aumento de", "aprueba el tratamiento para", "mejora los tiempos de espera en", "descubren un vínculo entre"],
        "objects": ["las enfermedades respiratorias", "la salud mental", "la obesidad infantil", "el envejecimiento celular"]
    },
    "Society": {
        "subjects": ["La comunidad educativa", "Los sindicatos", "Las asociaciones vecinales", "La plataforma ciudadana", "El colectivo ecologista"],
        "actions": ["reclama mejoras en", "organiza una protesta por", "denuncia la falta de", "propone un plan para"],
        "objects": ["la educación pública", "el transporte metropolitano", "la vivienda asequible", "la protección del medio ambiente"]
    },
    "World": {
        "subjects": ["La ONU", "La Unión Europea", "La OTAN", "La cumbre climática", "El G20"],
        "actions": ["negocia un acuerdo para", "condena la situación en", "envía ayuda humanitaria a", "debate sobre el futuro de"],
        "objects": ["el conflicto en Oriente Próximo", "la crisis migratoria", "la desglobalización", "las energías renovables"]
    },
    "Science": {
        "subjects": ["La NASA", "El CERN", "Un equipo de investigadores", "La estación espacial", "El nuevo telescopio"],
        "actions": ["descubre un nuevo planeta en", "publica un estudio sobre", "logra un avance histórico en", "explora los límites de"],
        "objects": ["la física cuántica", "la exploración espacial", "la biología sintética", "el cambio climático"]
    },
    "Lifestyle": {
        "subjects": ["Las nuevas tendencias", "El turismo rural", "La gastronomía local", "El sector del bienestar", "La moda sostenible"],
        "actions": ["transforma la experiencia de", "gana popularidad en", "promueve un estilo de vida basado en", "recupera tradiciones de"],
        "objects": ["los viajes de aventura", "la alimentación consciente", "el turismo experiencial", "la artesanía tradicional"]
    },
    "Entertainment": {
        "subjects": ["Netflix", "El nuevo videojuego", "La serie del momento", "El reality show", "La plataforma de streaming"],
        "actions": ["estrena la temporada más esperada de", "arrasa en audiencia con", "rompe récords de reproducciones en", "anuncia una nueva producción sobre"],
        "objects": ["el fenómeno fan", "las series coreanas", "los documentales musicales", "el concurso internacional"]
    },
    "Education": {
        "subjects": ["El Ministerio de Educación", "Las universidades", "Los centros educativos", "La formación profesional", "Las becas universitarias"],
        "actions": ["implanta un nuevo modelo de", "mejora los resultados en", "digitaliza los procesos de", "amplía la oferta de"],
        "objects": ["la educación infantil", "la formación online", "el bilingüismo escolar", "la investigación académica"]
    },
}

MOCK_ROUTES = {
    "/politica.xml": "Politics",
    "/economia.xml": "Business",
    "/deportes.xml": "Sports",
    "/tecnologia.xml": "Technology",
    "/cultura.xml": "Culture",
    "/salud.xml": "Health",
    "/sociedad.xml": "Society",
    "/internacional.xml": "World",
    "/ciencia.xml": "Science",
    "/viajes.xml": "Lifestyle",
    "/entretenimiento.xml": "Entertainment",
    "/educacion.xml": "Education",
}


def generate_news(category: str, count: int = 5):
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
        if self.path in MOCK_ROUTES:
            category = MOCK_ROUTES[self.path]
            items = generate_news(category)
            body = rss_template(f"Noticias de {category}", items).encode("utf-8")
            self._send_rss(body)
        elif self.path == "/test.xml":
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
