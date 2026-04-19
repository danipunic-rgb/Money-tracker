# Guía rápida para Cowork

> Lee esto si eres Claude abriendo este proyecto por primera vez en Cowork.

## Paso 1: Lee ARCHITECTURE.md
Contiene TODA la visión, decisiones, estado actual, y lo que NO hacer.

## Paso 2: Estado actual del proyecto
- Web en producción: https://money-tracker-new-app.vercel.app
- Backend: Supabase proyecto `rieyywfkpprgkenljilm` (eu-west-2)
- 15 ETFs × 501 días de histórico en la BBDD
- Cron diario de precios ACTIVO (22:30 UTC L-V)
- GitHub Actions workflow para holdings (semanal, lunes 06:00 CEST)

## Paso 3: Cómo hacer cambios
1. Editar archivos en esta carpeta
2. El fundador hace `git push` tras revisar
3. Vercel auto-deploya en 30 segundos

## Paso 4: Siguiente tarea pendiente
Mira la sección 13 (ROADMAP) de ARCHITECTURE.md para ver qué falta.
La próxima tarea más prioritaria de Fase 0 es: **Sección "Flujo del Dinero" visual en index.html**

## Reglas importantes
- NO añadir noticias, sentiment, alertas ni gamificación (ver sección 3 de ARCHITECTURE.md)
- NO usar APIs de pago (sin Anthropic API, sin Bloomberg)
- SIEMPRE mantener el disclaimer de "proxy basado en precio, no flujos reales"
- SIEMPRE actualizar ARCHITECTURE.md si haces cambios estructurales
