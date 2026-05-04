"""
Envío de emails de notificación de alertas.

Reutiliza la misma lógica que main.py (Gmail SMTP con contraseña de aplicación)
pero la encapsula para enviar emails de actualización de alertas.
"""
from __future__ import annotations

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rss_processor import NewsItem

logger = logging.getLogger(__name__)


def _format_news_html(items: list["NewsItem"]) -> str:
    """Genera el HTML con la lista de noticias."""
    rows = []
    for it in items:
        published = (
            it.published.strftime("%d/%m/%Y %H:%M")
            if it.published else "Fecha no disponible"
        )
        match_info = []
        if it.matched_descriptors:
            match_info.append(
                "Descriptores: " + ", ".join(
                    f"<em>{d}</em>" for d in it.matched_descriptors
                )
            )
        if it.matched_category:
            match_info.append(f"Categoría: <em>{it.matched_category}</em>")
        match_html = (
            f'<div style="font-size:12px;color:#888;margin-top:6px;">'
            f'{" · ".join(match_info)}</div>'
            if match_info else ""
        )
        rows.append(f"""
        <div style="border-bottom:1px solid #eee;padding:14px 0;">
          <div style="font-size:12px;color:#1a73e8;text-transform:uppercase;
                      letter-spacing:0.5px;margin-bottom:4px;">
            {it.source_name} · {it.channel_category}
          </div>
          <a href="{it.link}"
             style="font-size:16px;font-weight:bold;color:#202124;
                    text-decoration:none;">
            {it.title}
          </a>
          <div style="font-size:13px;color:#5f6368;margin-top:4px;">
            {it.summary[:240]}{"..." if len(it.summary) > 240 else ""}
          </div>
          <div style="font-size:11px;color:#888;margin-top:6px;">
            Publicado: {published}
          </div>
          {match_html}
        </div>
        """)
    return "\n".join(rows)


def _format_news_text(items: list["NewsItem"]) -> str:
    """Versión texto plano."""
    lines = []
    for it in items:
        published = (
            it.published.strftime("%d/%m/%Y %H:%M")
            if it.published else "Fecha no disponible"
        )
        lines.append(f"• [{it.source_name} - {it.channel_category}] {it.title}")
        lines.append(f"  {it.link}")
        lines.append(f"  Publicado: {published}")
        lines.append("")
    return "\n".join(lines)


def send_alert_email(
    *,
    smtp_host: str,
    smtp_port: int,
    sender: str,
    app_password: str,
    to_email: str,
    user_first_name: str,
    alert_name: str,
    fired_at: datetime,
    items: list["NewsItem"],
) -> None:
    """Envía el email de actualización de alerta.

    Título: "Actualización de <alerta> en <día/hora>"
    Cuerpo: lista de noticias que han matcheado.
    """
    fired_str = fired_at.strftime("%d/%m/%Y %H:%M")
    subject = f"Actualización de {alert_name} en {fired_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    text_body = (
        f"Hola {user_first_name},\n\n"
        f"Tu alerta '{alert_name}' tiene {len(items)} noticia(s) nueva(s):\n\n"
        + _format_news_text(items)
        + "\n— NewsRadar"
    )

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; max-width: 680px;
                   margin: 0 auto; color:#202124;">
        <div style="background:#1a73e8;color:white;padding:18px 24px;
                    border-radius:6px 6px 0 0;">
          <h2 style="margin:0;">Actualización de "{alert_name}"</h2>
          <div style="font-size:13px;opacity:0.9;margin-top:4px;">
            {fired_str}
          </div>
        </div>
        <div style="border:1px solid #eee;border-top:0;padding:20px 24px;
                    border-radius:0 0 6px 6px;">
          <p>Hola {user_first_name},</p>
          <p>Tu alerta tiene <strong>{len(items)}</strong> noticia(s) nueva(s)
             desde la última revisión:</p>
          {_format_news_html(items)}
          <p style="margin-top:24px;color:#666;font-size:12px;">
            Recibes este correo porque tienes activa una alerta en NewsRadar.
          </p>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(sender, app_password)
        server.sendmail(sender, to_email, msg.as_string())

    logger.info(
        "Email enviado a %s para alerta '%s' con %d noticias",
        to_email, alert_name, len(items),
    )
