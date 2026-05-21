"""
Worker de RSS para ingestión de noticias en segundo plano.

Responsabilidades:
1. Ejecutar según cron_expression de cada alerta
2. Fetch de canales RSS asociados a la alerta
3. Detección de noticias que coincidan con descriptores/sinónimos
4. Clasificación IPTC automática
5. Almacenamiento en MongoDB
6. Registro de estadísticas para notificaciones
"""

import logging
import feedparser
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models import Alert as AlertModel, RSSChannel as RSSChannelModel, Category as CategoryModel
from .keyword_service import classify_iptc_level1, expand_keywords

logger = logging.getLogger(__name__)


_CATEGORY_CODE_TO_DB_NAME = {
    "politics": "politica",
    "government": "politica",
    "economy": "economia",
    "technology": "tecnologia",
    "sports": "deportes",
    "culture": "cultura",
    "consumption": "sociedad",
    "society": "sociedad",
    "international": "internacional",
    "health": "salud",
    "education": "educacion",
    "science": "ciencia",
    "travel": "viajes",
    "entertainment": "entretenimiento",
    "national": "nacional",
}


class RSSWorker:
    """Procesa feeds RSS y almacena noticias detectadas."""

    def __init__(self, db: AsyncSession, mongo_db: AsyncIOMotorDatabase):
        self.db = db
        self.mongo_db = mongo_db

    @staticmethod
    def _normalize_category_value(value: Any) -> str:
        if value is None:
            return ""
        text = str(value).strip().lower()
        return (
            text.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("ü", "u")
            .replace("ñ", "n")
            .replace("_", " ")
        )

    @classmethod
    def _category_aliases(cls, raw_category: Any) -> set[str]:
        if not isinstance(raw_category, dict):
            return set()

        aliases: set[str] = set()
        for key in ("code", "label", "name"):
            normalized = cls._normalize_category_value(raw_category.get(key))
            if not normalized:
                continue
            aliases.add(normalized)
            mapped = _CATEGORY_CODE_TO_DB_NAME.get(normalized)
            if mapped:
                aliases.add(mapped)
        return aliases

    async def process_alert(self, alert_id: int) -> Dict[str, Any]:
        """
        Procesa una alerta: fetch RSS, detección y clasificación.

        Args:
            alert_id: ID de la alerta a procesar

        Returns:
            Diccionario con estadísticas de la ejecución
        """
        stats = {
            "alert_id": alert_id,
            "processed_at": datetime.utcnow(),
            "channels_processed": 0,
            "articles_detected": 0,
            "articles_stored": 0,
            "errors": []
        }

        # 1. Obtener la alerta y sus categorías
        result = await self.db.execute(select(AlertModel).where(AlertModel.id == alert_id))
        alert = result.scalar_one_or_none()

        if not alert:
            logger.warning(f"Alerta {alert_id} no encontrada")
            stats["errors"].append(f"Alerta {alert_id} no encontrada")
            return stats

        # 2. Obtener descriptores y sinónimos de la alerta
        descriptors = alert.descriptors or []
        # descriptors son List[str] en el modelo
        base_keywords = descriptors if isinstance(descriptors, list) else [descriptors]

        if not base_keywords:
            logger.info(f"Alerta {alert_id} sin descriptores")
            return stats

        # 2b. Ampliar keywords usando diccionario (MongoDB) + IA (si hace falta)
        try:
            keywords = await expand_keywords(
                self.mongo_db,
                keywords=base_keywords,
                max_synonyms_per_keyword=5,
                max_age_days=30,
            )
        except Exception as e:
            logger.error("Error expandiendo keywords con diccionario: %s", str(e))
            keywords = base_keywords

        # 3. Obtener canales RSS asociados a las categorías de la alerta
        rss_channels = await self._get_alert_channels(alert)
        stats["channels_processed"] = len(rss_channels)

        # 4. Procesar cada canal RSS
        for channel in rss_channels:
            try:
                articles = await self._fetch_and_parse_channel(channel, keywords)
                stats["articles_detected"] += len(articles)

                # 5. Guardar en MongoDB
                for article in articles:
                    try:
                        stored = await self._store_article(article, alert_id)
                        if stored:
                            stats["articles_stored"] += 1
                    except Exception as e:
                        logger.error(f"Error guardando artículo: {str(e)}")
                        stats["errors"].append(str(e))

            except Exception as e:
                logger.error(f"Error procesando canal {channel.id}: {str(e)}")
                stats["errors"].append(f"Canal {channel.id}: {str(e)}")

        return stats

    async def _get_alert_channels(self, alert: AlertModel) -> List[RSSChannelModel]:
        """Obtiene canales RSS asociados a la alerta (por categorías)."""
        channel_ids: List[int] = []
        for raw_id in (alert.rss_channels_ids or []):
            try:
                channel_ids.append(int(raw_id))
            except (TypeError, ValueError):
                continue

        if channel_ids:
            result = await self.db.execute(
                select(RSSChannelModel).where(RSSChannelModel.id.in_(channel_ids))
            )
            return result.scalars().all()

        category_ids = [c.get("id") for c in (alert.categories or []) if isinstance(c, dict) and c.get("id")]
        if category_ids:
            result = await self.db.execute(
                select(RSSChannelModel).where(RSSChannelModel.category_id.in_(category_ids))
            )
            return result.scalars().all()

        category_aliases = set()
        for raw_category in (alert.categories or []):
            category_aliases.update(self._category_aliases(raw_category))

        if not category_aliases:
            return []

        result = await self.db.execute(select(CategoryModel))
        matched_category_ids = [
            category.id
            for category in result.scalars().all()
            if self._normalize_category_value(category.name) in category_aliases
        ]
        if not matched_category_ids:
            return []

        result = await self.db.execute(
            select(RSSChannelModel).where(RSSChannelModel.category_id.in_(matched_category_ids))
        )
        return result.scalars().all()

    async def _fetch_and_parse_channel(self, channel: RSSChannelModel, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch de un canal RSS y detección de artículos relevantes.

        Args:
            channel: Objeto RSSChannelModel con URL del feed
            keywords: Palabras clave para detectar artículos relevantes

        Returns:
            Lista de artículos que coinciden con los keywords
        """
        articles = []

        try:
            # Fetch del feed
            feed = feedparser.parse(str(channel.url))

            if feed.bozo:
                logger.warning(f"Feed malformado en {channel.url}: {feed.bozo_exception}")

            # Parsear cada entrada
            for entry in feed.entries[:20]:  # Limitar a últimas 20 entradas
                if self._matches_keywords(entry, keywords):
                    article = {
                        "title": entry.get("title", ""),
                        "description": entry.get("summary", "") or entry.get("description", ""),
                        "url": entry.get("link", ""),
                        "channel_id": channel.id,
                        "published_date": self._parse_date(entry.get("published", "")),
                        "source_origin": str(channel.information_source_id) if channel.information_source_id else None,
                    }
                    articles.append(article)

            logger.info(f"Canal {channel.id}: {len(articles)} artículos detectados")

        except Exception as e:
            logger.error(f"Error fetching canal {channel.url}: {str(e)}")

        return articles

    def _matches_keywords(self, entry: Dict[str, Any], keywords: List[str]) -> bool:
        """
        Verifica si una entrada RSS contiene alguno de los keywords.

        Args:
            entry: Entrada del feed (feedparser entry)
            keywords: Palabras clave a buscar

        Returns:
            True si al menos un keyword está presente
        """
        text_to_search = " ".join([
            entry.get("title", ""),
            entry.get("summary", ""),
            entry.get("description", ""),
        ]).lower()

        for keyword in keywords:
            if keyword.lower() in text_to_search:
                return True

        return False

    def _parse_date(self, date_str: str) -> datetime:
        """Parsea fecha RFC2822 o ISO 8601 a datetime."""
        if not date_str:
            return datetime.utcnow()

        try:
            # Intentar ISO 8601
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            pass

        try:
            # Intentar formato común de RSS (RFC2822)
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            pass

        # Fallback
        return datetime.utcnow()

    async def _store_article(self, article: Dict[str, Any], alert_id: int) -> bool:
        """
        Guardar artículo en MongoDB con clasificación IPTC.

        Args:
            article: Datos del artículo
            alert_id: ID de la alerta que lo generó

        Returns:
            True si se guardó exitosamente
        """
        try:
            # Clasificación IPTC automática
            text_for_classification = f"{article['title']} {article['description']}"
            iptc_category = classify_iptc_level1(text_for_classification)

            # Verificar si el artículo ya existe
            existing = await self.mongo_db.news.find_one({
                "url": article["url"],
                "alert_id": alert_id
            })

            if existing:
                logger.debug(f"Artículo duplicado: {article['url']}")
                return False

            # Documento final
            doc = {
                **article,
                "iptc_category": iptc_category,
                "alert_id": alert_id,
                "created_at": datetime.utcnow(),
            }

            result = await self.mongo_db.news.insert_one(doc)
            logger.info(f"Artículo guardado: {result.inserted_id}")
            return True

        except Exception as e:
            logger.error(f"Error guardando artículo en MongoDB: {str(e)}")
            return False
