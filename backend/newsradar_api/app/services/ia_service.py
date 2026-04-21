"""
Servicio de IA para generación de sinónimos y procesamiento con OpenAI.

RNF-06: Trazabilidad de prompts IA
- Todos los prompts utilizados están documentados en PROMPTS.md
- Versión del modelo: gpt-3.5-turbo (configurable)
"""

import os
import logging
from typing import List
from openai import OpenAI

logger = logging.getLogger(__name__)

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def generate_synonyms(keywords: List[str], max_synonyms: int = 5) -> List[str]:
    """
    Genera sinónimos y palabras relacionadas para un conjunto de palabras clave.
    
    PROMPT_ID: IA-001-SYNONYMS
    Descripción: Generación de sinónimos para descriptores de alertas
    Modelo: gpt-3.5-turbo
    
    Args:
        keywords: Lista de palabras clave para las cuales generar sinónimos
        max_synonyms: Número máximo de sinónimos a generar (default 5)
        
    Returns:
        Lista de sinónimos o palabras relacionadas (entre 3 y 10 palabras)
    """
    if not client:
        logger.warning("OPENAI_API_KEY no está configurada. Devolviendo palabras vacías.")
        return []
    
    if not keywords:
        return []
    
    keywords_str = ", ".join(keywords)
    
    prompt = f"""
Eres un asistente especializado en generación de palabras clave relacionadas para motores de búsqueda de noticias.

Dadas estas palabras clave: {keywords_str}

Genera entre 3 y 10 sinónimos o palabras relacionadas que podrían mejorar la búsqueda y captura de noticias relevantes.
Las palabras deben ser:
- En español
- Relevantes al tema
- Que amplíen la cobertura sin ser demasiado genéricas
- Separadas por comas

Responde SOLO con las palabras, sin explicación adicional.
Ejemplo de respuesta: "economía digital, transformación digital, negocio electrónico"
"""
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente experto en generación de palabras clave para búsqueda de noticias."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=150,
        )
        
        # Parsear respuesta
        synonyms_text = response.choices[0].message.content.strip()
        synonyms = [s.strip() for s in synonyms_text.split(",")]
        
        logger.info(f"Sinónimos generados para {keywords_str}: {synonyms}")
        return synonyms[:max_synonyms]
        
    except Exception as e:
        logger.error(f"Error generando sinónimos con OpenAI: {str(e)}")
        return []


def classify_iptc_level1(text: str) -> str:
    """
    Clasifica un texto bajo categorías IPTC de nivel 1.
    
    PROMPT_ID: IA-002-IPTC-CLASSIFICATION
    Descripción: Clasificación automática de noticias en categorías IPTC nivel 1
    Modelo: gpt-3.5-turbo
    
    Args:
        text: Texto o descripción de la noticia a clasificar
        
    Returns:
        Categoría IPTC de nivel 1 (ej: "Politics", "Business", "Sports", etc.)
    """
    if not client:
        logger.warning("OPENAI_API_KEY no está configurada. Devolviendo 'General'.")
        return "General"
    
    if not text or len(text.strip()) < 10:
        return "General"
    
    prompt = f"""
Clasifica el siguiente texto en UNA ÚNICA categoría IPTC de nivel 1.

Categorías disponibles:
- Politics
- Business
- Sports
- Entertainment
- Science
- Technology
- Health
- Lifestyle
- World
- General

Texto a clasificar:
{text[:500]}

Responde SOLO con el nombre de la categoría, sin explicación.
"""
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un clasificador experto de noticias en categorías IPTC nivel 1."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=50,
        )
        
        category = response.choices[0].message.content.strip()
        logger.info(f"Categoría IPTC asignada: {category}")
        return category
        
    except Exception as e:
        logger.error(f"Error clasificando con OpenAI: {str(e)}")
        return "General"
