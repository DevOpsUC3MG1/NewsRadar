"""
Script de seeding para cargar datos iniciales de RSS desde rss_sources.json.

Carga:
- 10+ medios (information_sources)
- 100+ canales RSS (rss_channels)
- catálogo oficial IPTC (categories)
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

from sqlalchemy import select

from .database import get_async_session_maker
from .models import Category as CategoryModel
from .models import InformationSource as InformationSourceModel
from .models import RSSChannel as RSSChannelModel

logger = logging.getLogger(__name__)


RSS_TO_IPTC_CATEGORY = {
    "Politica": "Política",
    "Economia": "Economía, negocios y finanzas",
    "Tecnologia": "Ciencia y tecnología",
    "Deportes": "Deporte",
    "Cultura": "Artes, cultura, entretenimiento y medios",
    "Sociedad": "Sociedad",
    "Internacional": "Conflicto, guerra y paz",
    "Salud": "Salud",
    "Educacion": "Educación",
    "Ciencia": "Ciencia y tecnología",
    "Viajes": "Estilo de vida y tiempo libre",
    "Entretenimiento": "Artes, cultura, entretenimiento y medios",
}


def _find_data_root() -> Path:
    start = Path(__file__).resolve()
    for parent in start.parents:
        candidate = parent / "data" / "rss_sources.json"
        if candidate.exists():
            return parent
    return start.parents[3]


_PROJECT_ROOT = _find_data_root()
_RSS_SOURCES_PATH = _PROJECT_ROOT / "data" / "rss_sources.json"
_IPTC_CATALOG_PATH = _PROJECT_ROOT / "data" / "iptc_catalog.json"


def load_rss_sources():
    with open(_RSS_SOURCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_iptc_catalog():
    with open(_IPTC_CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


async def run():
    data = load_rss_sources()
    iptc_catalog = load_iptc_catalog()

    async with get_async_session_maker()() as db:
        logger.info("Cargando categorías IPTC...")
        for item in iptc_catalog:
            category_id = int(item["code"])
            category_name = item["name"]
            existing = await db.execute(select(CategoryModel).where(CategoryModel.id == category_id))
            category = existing.scalar_one_or_none()

            if category:
                category.name = category_name
                category.source = "IPTC"
            else:
                db.add(CategoryModel(id=category_id, name=category_name, source="IPTC"))
                logger.info("  Categoria creada: %s", category_name)

        await db.commit()
        logger.info("Categorías: %s cargadas", len(iptc_catalog))

        logger.info("Cargando medios y canales RSS...")
        total_channels = 0

        for source_data in data.get("sources", []):
            source_name = source_data["name"]
            source_url = source_data["url"]

            existing_source = await db.execute(
                select(InformationSourceModel).where(InformationSourceModel.name == source_name)
            )
            source = existing_source.scalar_one_or_none()

            if not source:
                source = InformationSourceModel(name=source_name, url=source_url)
                db.add(source)
                await db.flush()
                logger.info("  Fuente creada: %s", source_name)
            else:
                logger.info("  Fuente existente: %s", source_name)

            for channel_data in source_data.get("channels", []):
                channel_url = channel_data["url"]
                source_category_name = channel_data["category"]
                category_name = RSS_TO_IPTC_CATEGORY.get(source_category_name, source_category_name)

                category_result = await db.execute(
                    select(CategoryModel).where(CategoryModel.name == category_name)
                )
                category = category_result.scalar_one_or_none()

                if not category:
                    logger.warning("    Categoría no encontrada: %s", category_name)
                    continue

                existing_channel = await db.execute(
                    select(RSSChannelModel).where(RSSChannelModel.url == channel_url)
                )
                if existing_channel.scalar_one_or_none():
                    logger.debug("    Canal existente: %s...", channel_url[:50])
                else:
                    db.add(
                        RSSChannelModel(
                            url=channel_url,
                            category_id=category.id,
                            information_source_id=source.id,
                        )
                    )
                    total_channels += 1
                    logger.debug("    Canal: %s...", channel_url[:50])

            await db.commit()

        first_source = await db.execute(select(InformationSourceModel))
        source = first_source.scalars().first()
        if source:
            for item in iptc_catalog:
                category_id = int(item["code"])
                existing_channel = await db.execute(
                    select(RSSChannelModel).where(RSSChannelModel.category_id == category_id)
                )
                if existing_channel.scalars().first():
                    continue

                db.add(
                    RSSChannelModel(
                        url=f"https://newsradar.local/rss/{item['code']}.xml",
                        category_id=category_id,
                        information_source_id=source.id,
                    )
                )
                total_channels += 1

            await db.commit()

        logger.info("Canales: %s cargados", total_channels)
        logger.info("Seeding completado exitosamente")


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s:%(name)s:%(message)s")
    try:
        await run()
    except Exception as e:
        logger.error("Error durante seeding: %s", str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())
