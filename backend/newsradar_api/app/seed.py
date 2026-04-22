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
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal
from .models import Category as CategoryModel
from .models import InformationSource as InformationSourceModel
from .models import RSSChannel as RSSChannelModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_rss_sources():
    """Carga RSS sources desde JSON y los inserta en la BD."""
    
    # Leer JSON
    json_path = Path(__file__).parent.parent.parent / "data" / "rss_sources.json"
    
    if not json_path.exists():
        logger.error(f"Archivo {json_path} no encontrado")
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    async with AsyncSessionLocal() as db:
        # 1. Crear categorías
        logger.info("Cargando categorías IPTC...")
        for category_name in data.get("categories", []):
            existing = await db.execute(
                __import__("sqlalchemy").select(CategoryModel).where(
                    CategoryModel.name == category_name
                )
            )
            if not existing.scalar_one_or_none():
                category = CategoryModel(name=category_name, source="IPTC")
                db.add(category)
                logger.info(f"  ✓ Categoría creada: {category_name}")
        
        await db.commit()
        logger.info(f"✅ {len(data.get('categories', []))} categorías cargadas")
        
        # 2. Cargar fuentes (medios) y canales
        logger.info("\nCargando medios y canales RSS...")
        total_channels = 0
        
        for source_data in data.get("sources", []):
            source_name = source_data["name"]
            source_url = source_data["url"]
            
            # Obtener o crear fuente
            existing_source = await db.execute(
                __import__("sqlalchemy").select(InformationSourceModel).where(
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
                logger.info(f"  → Fuente existente: {source_name}")
            
            # Cargar canales
            for channel_data in source_data.get("channels", []):
                channel_url = channel_data["url"]
                category_name = channel_data["category"]
                
                # Obtener categoría
                category_result = await db.execute(
                    __import__("sqlalchemy").select(CategoryModel).where(
                        CategoryModel.name == category_name
                    )
                )
                category = category_result.scalar_one_or_none()
                
                if not category:
                    logger.warning(f"    ⚠ Categoría no encontrada: {category_name}")
                    continue
                
                # Verificar si canal existe
                existing_channel = await db.execute(
                    __import__("sqlalchemy").select(RSSChannelModel).where(
                        RSSChannelModel.url == channel_url
                    )
                )
                if existing_channel.scalar_one_or_none():
                    logger.debug(f"    → Canal existente: {channel_url[:50]}...")
                else:
                    channel = RSSChannelModel(
                        url=channel_url,
                        category_id=category.id,
                        information_source_id=source.id
                    )
                    db.add(channel)
                    total_channels += 1
                    logger.debug(f"    ✓ Canal añadido: {channel_url[:50]}...")
            
            await db.commit()
        
        logger.info(f"\n✅ {total_channels} canales cargados")
        logger.info("🎉 Seeding completado exitosamente")


async def main():
    """Punto de entrada del script."""
    try:
        await load_rss_sources()
    except Exception as e:
        logger.error(f"❌ Error durante el seeding: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
