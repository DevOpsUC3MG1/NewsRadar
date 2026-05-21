"""
Script de seeding para cargar datos iniciales de RSS desde rss_sources.json
Carga:
- 10 medios (information_sources)
- 100+ canales RSS (rss_channels)
- 12 categorías IPTC (categories)

Uso: python app/seed.py
"""

import json
import asyncio
import logging
import sys
from pathlib import Path
from sqlalchemy import select
from .database import get_async_session_maker
from .models import Category as CategoryModel, InformationSource as InformationSourceModel, RSSChannel as RSSChannelModel

logger = logging.getLogger(__name__)


def _find_data_root() -> Path:
    start = Path(__file__).resolve()
    for parent in start.parents:
        candidate = parent / "data" / "rss_sources.json"
        if candidate.exists():
            return parent
    return start.parents[3]


_PROJECT_ROOT = _find_data_root()
_RSS_SOURCES_PATH = _PROJECT_ROOT / "data" / "rss_sources.json"


def load_rss_sources():
    """Carga el archivo rss_sources.json y devuelve su contenido."""
    with open(_RSS_SOURCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


async def run():
    data = load_rss_sources()
    async with get_async_session_maker()() as db:
        # 1. Crear categorías
        logger.info("Cargando categorías IPTC...")
        for category_name in data.get("categories", []):
            existing = await db.execute(
                select(CategoryModel).where(
                    CategoryModel.name == category_name
                )
            )
            if not existing.scalar_one_or_none():
                category = CategoryModel(name=category_name, source="IPTC")
                db.add(category)
                logger.info(f"  ✓ Categoría creada: {category_name}")

        await db.commit()
        logger.info(f"Categorías: {len(data.get('categories', []))} cargadas")

        # 2. Cargar fuentes (medios) y canales
        logger.info("\nCargando medios y canales RSS...")
        total_channels = 0

        for source_data in data.get("sources", []):
            source_name = source_data["name"]
            source_url = source_data["url"]

            # Obtener o crear fuente
            existing_source = await db.execute(
                select(InformationSourceModel).where(
                    InformationSourceModel.name == source_name
                )
            )
            source = existing_source.scalar_one_or_none()

            if not source:
                source = InformationSourceModel(
                    name=source_name,
                    url=source_url
                )
                db.add(source)
                await db.flush()
                logger.info(f"  ✓ Fuente creada: {source_name}")
            else:
                logger.info(f"  - Fuente existente: {source_name}")

            # Cargar canales
            for channel_data in source_data.get("channels", []):
                channel_url = channel_data["url"]
                category_name = channel_data["category"]

                # Obtener categoría
                category_result = await db.execute(
                    select(CategoryModel).where(
                        CategoryModel.name == category_name
                    )
                )
                category = category_result.scalar_one_or_none()

                if not category:
                    logger.warning(f"    Categoría no encontrada: {category_name}")
                    continue

                # Verificar si canal existe
                existing_channel = await db.execute(
                    select(RSSChannelModel).where(
                        RSSChannelModel.url == channel_url
                    )
                )
                if existing_channel.scalar_one_or_none():
                    logger.debug(f"    Canal existente: {channel_url[:50]}...")
                else:
                    channel = RSSChannelModel(
                        url=channel_url,
                        category_id=category.id,
                        information_source_id=source.id
                    )
                    db.add(channel)
                    total_channels += 1
                    logger.debug(f"    Canal: {channel_url[:50]}...")

            await db.commit()

        logger.info(f"\nCanales: {total_channels} cargados")
        logger.info("Seeding completado exitosamente")


async def main():
    """Punto de entrada del script."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s:%(name)s:%(message)s")
    try:
        await run()
    except Exception as e:
        logger.error(f"Error durante seeding: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
