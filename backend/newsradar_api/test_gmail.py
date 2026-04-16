#!/usr/bin/env python3
"""
Script para probar las credenciales de Gmail
Ejecuta: python test_gmail.py
"""
 
import smtplib
import os
from dotenv import load_dotenv
 
# Cargar variables del .env
load_dotenv()
 
GMAIL_SENDER = ""
GMAIL_APP_PASSWORD = "sbwr hqqo cztf eblw"
 
print("=" * 60)
print("PRUEBA DE CREDENCIALES DE GMAIL")
print("=" * 60)
 
# Verificar que las variables existen
if not GMAIL_SENDER:
    print("❌ ERROR: GMAIL_SENDER no está definido en .env")
    exit(1)
 
if not GMAIL_APP_PASSWORD:
    print("❌ ERROR: GMAIL_APP_PASSWORD no está definido en .env")
    exit(1)
 
print(f"\n📧 Email: {GMAIL_SENDER}")
print(f"🔑 Contraseña: {'*' * len(GMAIL_APP_PASSWORD)}")
print(f"   Caracteres: {len(GMAIL_APP_PASSWORD)} (debería ser 16)")
 
print("\n🔄 Intentando conectar a Gmail SMTP...")
 
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        print("✅ Conexión a smtp.gmail.com establecida")
        
        print("🔐 Intentando autenticar...")
        server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
        print("✅ ¡Autenticación exitosa!")
        
        print("\n" + "=" * 60)
        print("✨ Las credenciales son correctas")
        print("=" * 60)
        
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ ERROR DE AUTENTICACIÓN:")
    print(f"   {e}")
    print("\n⚠️  Posibles soluciones:")
    print("   1. Verifica que estés usando 'Contraseña de aplicación', no tu contraseña de Gmail")
    print("   2. Asegúrate de tener autenticación de 2 factores activada")
    print("   3. Revisa que no haya espacios extras en el .env")
    print("   4. La contraseña debe tener 16 caracteres (con espacios: xxxx xxxx xxxx xxxx)")
    
except smtplib.SMTPException as e:
    print(f"\n❌ ERROR SMTP: {e}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")