"""
Demonio NewsRadar.

Flujo:
  1. Login contra la API.
  2. Carga rss_sources.json y sincroniza alertas vía API.
  3. Programa cada alerta en APScheduler según su cron_expression.
  4. Cada disparo:
        - calcula `since` (última ejecución de esa alerta).
        - descarga los canales RSS de la alerta en paralelo.
        - filtra por descriptor OR categoría.
        - si hay matches: envía email + crea notificación vía API.
  5. Refresca alertas periódicamente (por si se crean/borran/editan).

Uso:
    python -m app.daemon
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from .api_client import NewsRadarAPIClient, NewsRadarAPIError
from .email_sender import send_alert_email
from .rss_processor import gather_news, matches_alert

logger = logging.getLogger("newsradar.daemon")


# ------------------------------------------------------------- configuración
class Config:
    def __init__(self) -> None:
        load_dotenv()
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.daemon_email = os.getenv("DAEMON_EMAIL", "admin@newsradar.com")
        self.daemon_password = os.getenv("DAEMON_PASSWORD", "admin123")

        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.gmail_sender = os.getenv("GMAIL_SENDER", "")
        self.gmail_app_password = os.getenv("GMAIL_APP_PASSWORD", "")

        self.rss_sources_path = Path(
            os.getenv("RSS_SOURCES_PATH", "rss_sources.json")
        )
        # cada cuánto refrescamos la lista de alertas (segundos)
        self.alert_refresh_interval = int(
            os.getenv("ALERT_REFRESH_INTERVAL", "300")
        )
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        # Zona horaria para mostrar fechas en el asunto/cuerpo de los emails
        # y notificaciones. El scheduler internamente sigue en UTC.
        self.display_timezone = os.getenv("DISPLAY_TIMEZONE", "UTC")


# ----------------------------------------------------------- registro de jobs
class AlertRegistry:
    """Mantiene en memoria el mapeo alert_id -> última ejecución."""

    def __init__(self) -> None:
        self._last_run: dict[int, datetime] = {}
        # alertas actualmente programadas (para detectar añadidas/borradas)
        self._scheduled: dict[int, str] = {}  # alert_id -> cron_expression

    def get_last_run(self, alert_id: int) -> datetime | None:
        return self._last_run.get(alert_id)

    def set_last_run(self, alert_id: int, when: datetime) -> None:
        self._last_run[alert_id] = when

    def is_scheduled(self, alert_id: int, cron_expr: str) -> bool:
        return self._scheduled.get(alert_id) == cron_expr

    def mark_scheduled(self, alert_id: int, cron_expr: str) -> None:
        self._scheduled[alert_id] = cron_expr

    def unmark(self, alert_id: int) -> None:
        self._scheduled.pop(alert_id, None)

    def scheduled_ids(self) -> set[int]:
        return set(self._scheduled.keys())


# -------------------------------------------------------- carga rss_sources
def load_rss_sources(path: Path) -> dict[str, Any]:
    """Carga rss_sources.json y construye un índice url -> {source_name, category}."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    url_index: dict[str, dict[str, str]] = {}
    source_index: dict[str, dict[str, Any]] = {}  # name -> source dict
    for src in data["sources"]:
        source_index[src["name"]] = src
        for ch in src["channels"]:
            url_index[ch["url"]] = {
                "source_name": src["name"],
                "category": ch["category"],
                "url": ch["url"],
            }
    return {
        "raw": data,
        "url_index": url_index,
        "source_index": source_index,
    }


def resolve_alert_channels(
    alert: dict,
    rss_sources: dict[str, Any],
    api_channels_by_id: dict[str, dict],
    api_sources_by_id: dict[str, dict],
) -> list[dict]:
    """Resuelve la lista de canales RSS que debe consultar una alerta.

    Combina:
      - rss_channels_ids: IDs de canales en la API (PostgreSQL)
      - information_sources_ids: IDs de fuentes; se incluyen TODOS sus canales

    Cada canal de la API tiene un `url`, lo cruzamos con `rss_sources.json`
    para obtener `source_name` y `category` (que es lo que matcheamos).
    """
    selected_urls: set[str] = set()
    alert_id = alert.get("id", "?")

    raw_ch_ids = alert.get("rss_channels_ids", [])
    raw_src_ids = alert.get("information_sources_ids", [])

    # 1) canales explícitos
    for ch_id in raw_ch_ids:
        ch = api_channels_by_id.get(str(ch_id))
        if ch and ch.get("url"):
            selected_urls.add(ch["url"])
        else:
            logger.warning(
                "Alerta %s | canal id=%r no encontrado en api_channels_by_id",
                alert_id, ch_id,
            )

    # 2) fuentes -> todos sus canales
    for src_id in raw_src_ids:
        src = api_sources_by_id.get(str(src_id))
        if not src:
            logger.warning(
                "Alerta %s | fuente id=%r no encontrada en api_sources_by_id",
                alert_id, src_id,
            )
            continue
        for ch in src.get("_channels", []):
            if ch.get("url"):
                selected_urls.add(ch["url"])

    # 3) cruzar con rss_sources.json para obtener source_name + category
    url_index = rss_sources["url_index"]
    channels: list[dict] = []
    for url in selected_urls:
        info = url_index.get(url)
        if info:
            channels.append(info)
        else:
            # canal en API que no está en rss_sources.json: lo incluimos
            # con categoría "Desconocida" para no perder noticias.
            channels.append({
                "source_name": "Desconocida",
                "category": "Desconocida",
                "url": url,
            })
    return channels


# ----------------------------------------------------------- procesar alerta
async def process_alert(
    alert_id: int,
    user_id: int,
    cfg: Config,
    api: NewsRadarAPIClient,
    rss_sources: dict[str, Any],
    registry: AlertRegistry,
) -> None:
    """Ejecuta una alerta: descarga RSS, filtra, manda email, crea notificación.

    Carga la alerta y los canales/fuentes frescos en cada ejecución, así si
    el usuario edita la alerta no hay que reprogramar nada (salvo el cron).
    """
    fired_at = datetime.now(timezone.utc)

    # Convertimos a la zona horaria de display para el asunto del email
    # y el título de la notificación. El scheduler/timestamps internos
    # siguen siendo UTC.
    try:
        local_tz = ZoneInfo(cfg.display_timezone)
    except Exception:
        logger.warning(
            "DISPLAY_TIMEZONE=%r no válida; usando UTC", cfg.display_timezone,
        )
        local_tz = timezone.utc
    fired_local = fired_at.astimezone(local_tz)

    # 1. cargar alerta fresca desde la API
    try:
        alerts = await api.list_user_alerts(user_id)
    except NewsRadarAPIError as e:
        logger.error("No se pudo cargar alerta %s: %s", alert_id, e)
        return

    alert = next((a for a in alerts if a["id"] == alert_id), None)
    if not alert:
        logger.warning("Alerta %s ya no existe para user %s", alert_id, user_id)
        return

    alert_name = alert["name"]
    logger.info(
        "Procesando alerta id=%s name='%s' user=%s",
        alert_id, alert_name, user_id,
    )

    # 2. cargar fuentes y canales frescos
    try:
        sources = await api.list_information_sources()
        api_sources_by_id: dict[str, dict] = {}
        api_channels_by_id: dict[str, dict] = {}
        for src in sources:
            src_id = str(src["id"])
            channels_of_src = await api.list_source_channels(src["id"])
            src["_channels"] = channels_of_src
            api_sources_by_id[src_id] = src
            for ch in channels_of_src:
                api_channels_by_id[str(ch["id"])] = ch
    except NewsRadarAPIError as e:
        logger.error("No se pudieron cargar fuentes/canales: %s", e)
        return

    # 3. resolver canales de la alerta
    channels = resolve_alert_channels(
        alert, rss_sources, api_channels_by_id, api_sources_by_id,
    )
    if not channels:
        logger.warning("Alerta %s no tiene canales RSS asociados", alert_id)
        registry.set_last_run(alert_id, fired_at)
        return

    # 4. fecha desde la que buscar noticias
    since = registry.get_last_run(alert_id)
    if since is None:
        # primera ejecución: usamos "ahora" como baseline para no notificar
        # noticias antiguas al arrancar.
        since = fired_at
        logger.info(
            "Primera ejecución de alerta %s; baseline = %s",
            alert_id, since.isoformat(),
        )

    # 5. descargar y parsear feeds
    items = await gather_news(channels, since=since)
    logger.info(
        "Alerta %s: %d items obtenidos de %d canales (since=%s)",
        alert_id, len(items), len(channels), since.isoformat(),
    )

    # 6. filtrar por descriptor OR categoría
    descriptors = alert.get("descriptors") or []
    categories = alert.get("categories") or []
    category_codes = [c.get("code", "") for c in categories if c.get("code")]

    matched = [it for it in items if matches_alert(it, descriptors, category_codes)]
    logger.info("Alerta %s: %d/%d noticias matchean", alert_id, len(matched), len(items))

    # actualizamos el last_run aunque no haya matches: ya hemos revisado hasta aquí
    registry.set_last_run(alert_id, fired_at)

    if not matched:
        return

    # 7. obtener email del usuario
    try:
        user = await api.get_user(user_id)
        user_email = user["email"]
        user_first_name = user.get("first_name", "")
    except NewsRadarAPIError as e:
        logger.error("No se pudo obtener email de user %s: %s", user_id, e)
        return

    # 8. enviar email (usando hora local en el asunto y cuerpo)
    if cfg.gmail_sender and cfg.gmail_app_password:
        try:
            # smtplib es bloqueante; lo movemos a un thread para no bloquear el loop
            await asyncio.to_thread(
                send_alert_email,
                smtp_host=cfg.smtp_host,
                smtp_port=cfg.smtp_port,
                sender=cfg.gmail_sender,
                app_password=cfg.gmail_app_password,
                to_email=user_email,
                user_first_name=user_first_name,
                alert_name=alert_name,
                fired_at=fired_local,
                items=matched,
            )
        except Exception as e:
            logger.exception("Error enviando email para alerta %s: %s", alert_id, e)
    else:
        logger.warning(
            "GMAIL_SENDER/APP_PASSWORD no configurados; omito email para alerta %s",
            alert_id,
        )

    # 9. crear notificación vía API (buzón en la app)
    sources_count = len({it.source_name for it in matched})
    metrics = [
        {"name": "news_count", "value": float(len(matched))},
        {"name": "sources_count", "value": float(sources_count)},
        {"name": "matched_by_descriptor", "value": float(
            sum(1 for it in matched if it.matched_descriptors)
        )},
        {"name": "matched_by_category", "value": float(
            sum(1 for it in matched if it.matched_category)
        )},
    ]

    # Título: "Actualización de <alerta> en <día/hora>" en hora local
    fired_str = fired_local.strftime("%d/%m/%Y %H:%M")
    title = f"Actualización de {alert_name} en {fired_str}"

    # Contenido: resumen + lista de noticias en bullets.
    content_lines = [
        f"Tu alerta '{alert_name}' tiene {len(matched)} noticia(s) nueva(s):",
        "",
    ]
    for it in matched:
        if it.published:
            published_str = it.published.astimezone(local_tz).strftime("%d/%m/%Y %H:%M")
        else:
            published_str = "fecha n/d"
        content_lines.append(
            f"• [{it.source_name} · {it.channel_category}] {it.title}"
        )
        content_lines.append(f"  {it.link}")
        content_lines.append(f"  Publicado: {published_str}")
        content_lines.append("")
    content = "\n".join(content_lines).strip()

    # Lista estructurada de las noticias para que el frontend las renderice.
    news_payload = [
        {
            "title": it.title[:500],
            "link": it.link[:2000],
            "source_name": it.source_name[:200],
            "category": it.channel_category[:100],
            "published": it.published.isoformat() if it.published else None,
        }
        for it in matched
    ]

    try:
        await api.create_notification(
            user_id=user_id,
            alert_id=alert_id,
            timestamp=fired_at,
            metrics=metrics,
            title=title,
            content=content,
            news=news_payload,
        )
        logger.info(
            "Notificación creada en API para alerta %s con título '%s'",
            alert_id, title,
        )
    except NewsRadarAPIError as e:
        logger.error("Error creando notificación en API: %s", e)


# --------------------------------------------------------- sincronizar jobs
async def sync_alerts_to_scheduler(
    scheduler: AsyncIOScheduler,
    cfg: Config,
    api: NewsRadarAPIClient,
    rss_sources: dict[str, Any],
    registry: AlertRegistry,
) -> None:
    """Lee las alertas actuales y reconcilia los jobs de APScheduler.

    - Añade jobs nuevos.
    - Reemplaza jobs cuya cron_expression haya cambiado.
    - Elimina jobs cuya alerta ya no exista.
    """
    try:
        alerts = await api.list_all_alerts()
    except NewsRadarAPIError as e:
        logger.error("No se pudieron cargar alertas: %s", e)
        return

    current_ids = {a["id"] for a in alerts}
    previous_ids = registry.scheduled_ids()

    # eliminar jobs que ya no aplican
    for old_id in previous_ids - current_ids:
        job_id = f"alert_{old_id}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info("Job eliminado: %s", job_id)
        registry.unmark(old_id)

    # añadir / actualizar jobs
    for alert in alerts:
        alert_id = alert["id"]
        user_id = alert["user_id"]
        cron_expr = alert.get("cron_expression", "").strip()
        if not cron_expr:
            logger.warning("Alerta %s sin cron_expression; se ignora", alert_id)
            continue

        if registry.is_scheduled(alert_id, cron_expr):
            continue  # ya programada con el mismo cron

        job_id = f"alert_{alert_id}"
        # si existía con otro cron, lo borramos antes de re-añadir
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

        try:
            trigger = CronTrigger.from_crontab(cron_expr, timezone=scheduler.timezone)
        except ValueError as e:
            logger.error(
                "cron_expression inválido en alerta %s ('%s'): %s",
                alert_id, cron_expr, e,
            )
            continue

        scheduler.add_job(
            process_alert,
            trigger=trigger,
            args=[alert_id, user_id, cfg, api, rss_sources, registry],
            id=job_id,
            replace_existing=True,
            misfire_grace_time=60,
            coalesce=True,
        )
        registry.mark_scheduled(alert_id, cron_expr)
        logger.info(
            "Job programado: alerta=%s cron='%s' name='%s'",
            alert_id, cron_expr, alert["name"],
        )


# ------------------------------------------------------------------- main
async def main() -> None:
    cfg = Config()
    logging.basicConfig(
        level=cfg.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if not cfg.rss_sources_path.exists():
        logger.error(
            "No existe el fichero RSS sources: %s. "
            "Define RSS_SOURCES_PATH en .env o ponlo en el cwd.",
            cfg.rss_sources_path,
        )
        sys.exit(1)

    rss_sources = load_rss_sources(cfg.rss_sources_path)
    logger.info(
        "Cargadas %d fuentes con %d canales totales",
        len(rss_sources["source_index"]),
        len(rss_sources["url_index"]),
    )

    api = NewsRadarAPIClient(
        base_url=cfg.api_base_url,
        email=cfg.daemon_email,
        password=cfg.daemon_password,
    )
    await api.login()

    registry = AlertRegistry()
    try:
        scheduler_tz = ZoneInfo(cfg.display_timezone)
    except Exception:
        logger.warning(
            "DISPLAY_TIMEZONE=%r no válida para el scheduler; usando UTC",
            cfg.display_timezone,
        )
        scheduler_tz = timezone.utc
    scheduler = AsyncIOScheduler(timezone=scheduler_tz)
    scheduler.start()

    # primera sincronización
    await sync_alerts_to_scheduler(scheduler, cfg, api, rss_sources, registry)

    # job interno para refrescar alertas periódicamente
    scheduler.add_job(
        sync_alerts_to_scheduler,
        trigger="interval",
        seconds=cfg.alert_refresh_interval,
        args=[scheduler, cfg, api, rss_sources, registry],
        id="_internal_refresh_alerts",
        replace_existing=True,
    )

    # control de apagado limpio
    stop_event = asyncio.Event()

    def _shutdown(*_: Any) -> None:
        logger.info("Señal recibida; apagando…")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown)
        except NotImplementedError:
            # Windows: no soporta add_signal_handler
            signal.signal(sig, _shutdown)

    logger.info("Demonio NewsRadar arrancado. Esperando triggers cron…")
    await stop_event.wait()

    scheduler.shutdown(wait=False)
    await api.close()
    logger.info("Demonio detenido.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass