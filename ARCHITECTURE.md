# Money Tracker — Documento de Arquitectura

> Este documento es la fuente de verdad del proyecto.
> Cualquier agente (Cowork, Claude Code, o un humano) DEBE leer `CLAUDE.md` primero
> (resumen operativo) y este archivo en segundo lugar (decisiones y roadmap completos).
> Última actualización: 19 abril 2026

---

## 1. VISIÓN DEL PRODUCTO

**Money Tracker es el mejor tracker objetivo del flujo de dinero del mundo.**

El usuario entra y ve al instante: de dónde sale el capital, hacia dónde va, en qué sectores, ETFs y empresas. Solo datos objetivos. Sin opiniones, sin noticias, sin sentiment.

### Qué somos
- Un tracker de flujo de capital basado en datos puros (precios, volumen, pesos de holdings)
- Una herramienta visual para ver dónde se mueve el dinero: sector → ETF → empresa
- Una plataforma que se actualiza sola con mínimo mantenimiento

### Qué NO somos (decisiones firmes, no negociables)
- **NO somos un noticiero.** Cero noticias, cero artículos, cero "por qué sube X"
- **NO damos alertas.** El usuario tiene TradingView para eso
- **NO tenemos gamificación.** Ni rachas, ni badges, ni leaderboards
- **NO damos consejo financiero.** Solo datos objetivos
- **NO hacemos sentiment analysis.** Es subjetivo y contradice la visión

### Nota sobre "flujo de dinero"
Lo que mostramos como "entrada/salida de capital" es un PROXY basado en rendimiento de precio. Los flujos reales de un ETF (aportaciones netas) requieren datos de pago (Bloomberg, FactSet). Para el MVP es una simplificación aceptable pero debemos mostrar un disclaimer al usuario.

---

## 2. NIVELES DE PROFUNDIDAD

### Nivel 1 — Vista de pájaro (nada más entrar)
- Recuadro "Flujo del Dinero" arriba: dos columnas (rojo = salida, verde = entrada)
- Selector de timeframe: 1D, 1S, 1M, 3M, 6M
- Resumen objetivo automático: "Esta semana el capital sale de Tecnología (-1.8%) y entra en Energía (+2.4%)"
- Heatmap de sectores/ETFs
- Tablas por sector con % cambio en todos los timeframes

### Nivel 2 — Drill-down (click en ETF o sector)
- Top 10-15 holdings del ETF (empresa, peso %, rendimiento)
- Empresas más relevantes del sector por movimiento

### Nivel 3 — Empresa individual + Popularidad
- Barra de búsqueda global
- Sistema de popularidad: búsquedas registradas → "trending" automático
- Vista de empresa: rendimiento + en qué ETFs aparece

---

## 3. FEATURES APROBADAS

| # | Feature | Fase | Estado |
|---|---------|------|--------|
| 1 | Dashboard sector → ETF con % cambio | 0 | ✅ HECHO |
| 2 | Deploy público en Vercel | 0 | ✅ HECHO |
| 3 | Sección "Flujo del Dinero" visual (agregado sector) | 0 | ✅ HECHO |
| 3b | Disclaimer visible "proxy precio vs. flujos reales" | 0 | ✅ HECHO |
| 3c | Vercel Analytics activado | 0 | ✅ HECHO |
| 3d | Publicación diaria automática en X (inglés) | 0 | ✅ HECHO |
| 3e | Sparklines 1M por fila de ETF | 0 | ✅ HECHO |
| 3f | Heatmap de ETFs (color por rendimiento, sync TF) | 1 | ✅ HECHO |
| 3g | Gráfico de precio en modal + selector TF | 1 | ✅ HECHO |
| 4 | Drill-down ETF → Holdings (tablas Supabase creadas, datos pendientes) | 1 | 🟡 PARCIAL |
| 5 | Daily Brief objetivo (sin LLM, con datos puros) | 1 | 🔲 PENDIENTE |
| 6 | OAuth Google + tabla profiles | 2 | 🔲 PENDIENTE |
| 7 | Watchlist + "Mi Flujo" | 2 | 🔲 PENDIENTE |
| 8 | Snapshot compartible | 2 | 🔲 PENDIENTE |
| 9 | Trending / "Lo más buscado" | 3 | 🔲 PENDIENTE |
| 10 | Monetización Stripe | 4 | 🔲 PENDIENTE |

### Features RECHAZADAS (no implementar)

| Feature | Motivo |
|---------|--------|
| Noticias / News tracker | No somos noticiero, riesgo de info mala |
| Sentiment analysis | Subjetivo, contradice visión |
| Alertas push/email | El usuario tiene herramientas mejores |
| Gamificación | No encaja con tono profesional |
| Consejo financiero | Riesgo legal |

---

## 4. STACK TÉCNICO

```
Frontend:   HTML/JS estático → Vercel (auto-deploy desde GitHub)
Backend:    Supabase (PostgreSQL + Edge Functions + Auth + RLS)
Repo:       github.com/danipunic-rgb/Money-tracker
Automación: GitHub Actions (cron, scripts Python puros, SIN API de LLM)
Datos:      Yahoo Finance (gratis, server-side via Edge Functions)
Curación:   Cowork / Claude Code (sesiones manuales del fundador)
```

### URLs activas
- **Web producción**: https://money-tracker-new-app.vercel.app
- **Supabase**: https://rieyywfkpprgkenljilm.supabase.co
- **Repo**: https://github.com/danipunic-rgb/Money-tracker

---

## 5. SUPABASE — Estado actual

### Proyecto
- **ID**: `rieyywfkpprgkenljilm`
- **Región**: eu-west-2
- **Plan**: Free
- **Organización**: Dani (ybahlmdwofhddgkqbcdk)

> IMPORTANTE: proyecto SEPARADO del dashboard personal (fhufubhakkxwxhusejou)

### Anon key (pública, segura por RLS)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpZXl5d2ZrcHByZ2tlbmxqaWxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYzNzQ5NDgsImV4cCI6MjA5MTk1MDk0OH0.d4H4QW_BeBc6axpgmevLKNdMb0gJ-U6hQ15Rk9Bn-20
```

### Tablas existentes

**etf_metadata** — Qué ETFs rastreamos
```sql
symbol (PK), name, sector, sector_color, sector_desc, display_order, enabled, created_at
-- 25 ETFs en 9 sectores: Tecnología, Energía, Financieros, Salud, Defensa,
--   Inmobiliario, Consumo, Crypto, Referencias (incl. ACWI/URTH/IEMG como proxies de índice)
```

**etf_daily** — Precios históricos
```sql
symbol (FK), date, close, adj_close, volume, fetched_at
-- PK: (symbol, date). ~11k filas. Rango: abr-2024 → hoy
```

**etf_holdings** — Holdings de ETFs (Fase 1, creada 19-abr-2026, pendiente de poblar)
```sql
etf_symbol (FK→etf_metadata), stock_symbol, weight, as_of_date | PK: (etf_symbol, stock_symbol, as_of_date)
```

**stock_metadata** — Metadatos de empresas (Fase 1, creada 19-abr-2026)
```sql
symbol (PK), isin, name, sector, industry, country, search_count, is_trending, created_at, updated_at
```

**stock_daily** — Precios de empresas individuales (Fase 1, creada 19-abr-2026)
```sql
symbol (FK→stock_metadata), date, close, adj_close, volume | PK: (symbol, date)
```

### RLS: anon = SELECT. Solo service_role puede escribir.

### Edge Functions
- **fetch-etfs** v2: Yahoo Finance → upsert en etf_daily. Params: `?days=N` y `?symbols=ITA,XAR` (opcional, filtra símbolos)

### Cron activo
- **fetch-etfs-daily**: `30 22 * * 1-5` (22:30 UTC L-V = 00:30 CEST)

### Tablas PENDIENTES

```sql
-- Fase 2
profiles (id uuid → auth.users, tier, created_at)
user_watchlist (user_id, symbol, symbol_type, added_at)

-- Fase 3
search_logs (id, user_id, symbol, searched_at)
```

---

## 6. SISTEMA DE AUTOMATIZACIÓN (sin API de pago)

### Principio clave
La automatización se divide en dos tipos:

**TIPO A — Ejecución repetitiva (100% automática, 100% gratis)**
Scripts Python puros que descargan datos de APIs gratuitas y los escriben en Supabase.
No necesitan LLM. Corren solos vía GitHub Actions o Supabase cron.

**TIPO B — Investigación y curación (manual, con Cowork)**
Decidir qué sectores rastrear, qué ETFs añadir, cómo estructurar los datos.
Esto lo hace el fundador en sesiones de Cowork/Claude Code cuando quiera.
Ocurre 1-2 veces al mes, no diariamente.

### Lo que corre SOLO (Tipo A)

| Qué | Cómo | Frecuencia | Coste |
|-----|------|------------|-------|
| Precios de ETFs | Supabase pg_cron → Edge Function → Yahoo Finance | Diario 22:30 UTC L-V | $0 |
| Holdings de ETFs | GitHub Actions → Python → Yahoo Finance → Supabase | Semanal (lunes 06:00 CEST) | $0 |
| Precios de acciones | GitHub Actions → Python → Yahoo Finance → Supabase | Diario (cuando Fase 1 esté lista) | $0 |

### Lo que haces TÚ con Cowork (Tipo B)

| Qué | Cuándo | Cómo |
|-----|--------|------|
| Añadir/quitar sectores | Cuando quieras | Abres Cowork → "añade sector Defensa con ETFs ITA y XAR" → push |
| Añadir/quitar ETFs | Cuando quieras | Abres Cowork → "añade ARKK al sector Tecnología" → push |
| Diseñar nuevas features | Cuando quieras | Abres Cowork → "implementa el heatmap" → push |
| Generar ARCHITECTURE.md actualizado | Tras cambios grandes | Abres Cowork → "actualiza ARCHITECTURE.md con los cambios" |

### Flujo completo

```
TÚ (con Cowork, cuando quieras):
  1. Decides qué sectores/ETFs rastrear
  2. Editas data/sectors.json y data/etfs.json
  3. git push → Vercel redeploya la web

GITHUB ACTIONS (solo, cada lunes):
  1. Lee data/etfs.json
  2. Para cada ETF, descarga holdings de Yahoo Finance
  3. Escribe holdings en Supabase
  4. Commitea data/holdings.json actualizado

SUPABASE CRON (solo, cada día laborable):
  1. pg_cron dispara Edge Function fetch-etfs
  2. Edge Function pide precios a Yahoo
  3. Upsert en etf_daily
```

### ¿Por qué esto es más profesional que agentes con LLM?
En sistemas reales de datos financieros (Bloomberg, FactSet, Morningstar), la curación de datos SIEMPRE tiene supervisión humana. Un LLM decidiendo solo qué ETFs añadir a un tracker financiero es un riesgo: puede añadir ETFs delisted, confundir tickers, o incluir productos que no existen. La investigación con Cowork + ejecución automática es exactamente cómo lo haría un equipo profesional de 2-3 personas, pero con una sola persona.

---

## 7. PIPELINE DE GITHUB ACTIONS

### Workflow: update-holdings (semanal)
```
Cada lunes 06:00 CEST:
  1. Checkout repo
  2. Lee data/etfs.json (curado por el fundador)
  3. Para cada ETF:
     - Llama a Yahoo Finance API (server-side, sin CORS)
     - Descarga top 15 holdings
     - Parsea: empresa, peso %, ISIN si disponible
  4. Genera data/holdings.json actualizado
  5. Si hay tablas en Supabase: upsert en etf_holdings + stock_metadata
  6. Commit + push del JSON actualizado
```

### Workflow: publish-x-daily (diario L-V)
```
Cada día laborable 21:05 UTC (tras cierre NYSE):
  1. Checkout repo
  2. Instala httpx + tweepy
  3. Llama a Edge Function fetch-etfs?days=2 (precios frescos)
  4. Lee metadata + últimos precios de Supabase vía REST anon
  5. Calcula promedio % cambio por sector (excluye Referencias)
  6. Renderiza tweet en inglés con emojis + url de la web
  7. Publica vía X API v2 (OAuth 1.0a User Context, tweepy)
  8. Guarda artifact con el texto publicado (retention 14d)
```

Trigger manual: `workflow_dispatch` con inputs `dry_run`, `timeframe`, `intro`, `force_fetch`.

### Secrets de GitHub necesarios
- `SUPABASE_URL` ✅
- `SUPABASE_SERVICE_ROLE_KEY` ✅ (solo para update-holdings)
- `SUPABASE_ANON_KEY` (opcional, tiene fallback embebido en el script)
- `X_API_KEY` ✅
- `X_API_SECRET` ✅
- `X_ACCESS_TOKEN` ✅
- `X_ACCESS_TOKEN_SECRET` ✅
- `ANTHROPIC_API_KEY` ❌ (no necesario, y no lo vamos a usar)

---

## 8. DISEÑO VISUAL

### Principios
- Fondo `#f9f7f4` con radial gradients sutiles
- Fraunces (serif, títulos) + Plus Jakarta Sans (cuerpo) + JetBrains Mono (datos)
- Estilo editorial/periódico
- Verde #15803d subidas, rojo #b91c1c bajadas
- Celdas con tinte proporcional al cambio

### Colores de sectores
| Sector | Color |
|--------|-------|
| Tecnología | #7c3aed |
| Energía | #c2410c |
| Financieros | #0369a1 |
| Salud | #15803d |
| Referencias | #78716c |

---

## 9. MARKET VISION — Navegador jerárquico

### Concepto
Árbol interactivo Índice→Sector→ETF→Empresa en la pestaña "Mercado". El usuario navega colapsando/expandiendo nodos. Cada nodo muestra el % cambio del ETF proxy en el timeframe seleccionado.

### Estructura de datos: `data/hierarchy.json`
```json
{
  "indices": [
    { "id": "msci_acwi", "proxy_etf": "ACWI", "children": ["msci_world", "msci_em"] },
    { "id": "msci_world", "proxy_etf": "URTH", "parent": "msci_acwi",
      "key_indices": ["sp500","nasdaq100","russell2000"],
      "sectors_applicable": ["technology","energy","financials","healthcare","defense","real_estate","consumer","crypto"] },
    { "id": "msci_em",     "proxy_etf": "IEMG", "parent": "msci_acwi" },
    { "id": "sp500",       "proxy_etf": "SPY",  "parent": "msci_world" },
    { "id": "nasdaq100",   "proxy_etf": "QQQ",  "parent": "msci_world" },
    { "id": "russell2000", "proxy_etf": "IWM",  "parent": "msci_world" }
  ],
  "subsectors": [
    {"id":"semiconductors","parent_sector":"technology"},
    {"id":"biotech","parent_sector":"healthcare"},
    {"id":"renewables","parent_sector":"energy"},
    {"id":"uranium","parent_sector":"energy"},
    {"id":"banks_regional","parent_sector":"financials"},
    {"id":"banks_big","parent_sector":"financials"}
  ],
  "etf_to_subsector": { "SMH":"semiconductors","KRE":"banks_regional",... }
}
```

### Implementación
- `renderMarketVision(tf)` — renderiza el árbol en `#mvContainer` como HTML estático con collapse/expand por class `mv-open`
- Event delegation único en `#mvContainer` (click en `.mv-row` → toggle; `[data-open-etf]` → modal ETF; `.mv-chip` → modal empresa)
- `data/hierarchy.json` se carga una vez por sesión y se cachea en `mvHierarchy`
- Validación automática en CI: `python scripts/validate_hierarchy.py` en `update-holdings.yml`

---

## 10. SECTORES Y ETFs ACTUALES  <!-- was §9 before Market Vision section -->

| Sector | ETFs | Justificación |
|--------|------|---------------|
| Tecnología | XLK, SMH, QQQ | Software + semis + Nasdaq amplio |
| Energía | XLE, ICLN, URA | Fósiles + renovables + nuclear |
| Financieros | XLF, KRE, KBE | Grandes bancos + regionales + bancario puro |
| Salud | XLV, IBB, XBI | Farma + biotech grande + biotech especulativo |
| Defensa | ITA, XAR | Aerospace & defense — tendencia macro relevante en 2026 |
| Inmobiliario | VNQ | REITs diversificados — sensible a tipos de interés |
| Consumo | XLY, XLP | Discrecional + básico — spread indica apetito de riesgo |
| Crypto | IBIT, BITO | Bitcoin spot + futures — proxy de risk-on extremo |
| Referencias | SPY, IWM, GLD, ACWI, URTH, IEMG | Mercado amplio + small caps + oro + proxies MSCI (Market Vision) |

### Sectores candidatos (para investigar con Cowork)
- Mercados emergentes (EEM, VWO)
- China (KWEB, FXI)
- Commodities (DBC, GSG)
- Bonos (TLT, BND, TIP)
- Europa (VGK, EZU)

---

## 10. FLUJO DE TRABAJO CON COWORK

### Primer uso
```
1. Abre Cowork apuntando a la carpeta Money-tracker/
2. Di: "Lee ARCHITECTURE.md completo antes de hacer nada"
3. Luego pide lo que necesites:
   - "Implementa la sección Flujo del Dinero en index.html"
   - "Añade el sector Defensa con los ETFs ITA y XAR"
   - "Crea las tablas de holdings en Supabase"
```

### Para cambios de código
```
Cowork edita → tú revisas → git push → Vercel deploya en 30s
```

### Para investigación de sectores/ETFs
```
Tú le preguntas a Cowork → Claude investiga → sugiere cambios a los JSON → tú apruebas → push
```

### Para features nuevas
```
Tú describes la feature → Cowork implementa → tú revisas → push
```

---

## 11. MONETIZACIÓN (preparar, no activar)

### Modelo futuro: Freemium
| Tier | Precio | Acceso |
|------|--------|--------|
| Free | 0€ | Dashboard público, top 3 flujo, top 5 holdings |
| Pro | ~6.99€/mes | Todo ilimitado + heatmap + Daily Brief + snapshots |

### Preparar en Fase 2
- Supabase Auth (Google OAuth)
- Tabla profiles con tier
- Feature flags en frontend

### Fuentes de ingreso adicionales (futuro)
- Afiliados de brokers (eToro, IBKR, Degiro) en cada ETF/empresa
- Google AdSense (solo con volumen significativo)

---

## 12. MÉTRICAS

### Desde día 1 (Vercel Analytics, gratis)
- Pageviews, usuarios únicos, países, dispositivos

### Desde Fase 2 (con Auth)
- Usuarios registrados, tasa de registro, búsquedas

---

## 13. ROADMAP POR FASES

### FASE 0 — MVP público (ACTUAL)
- [x] Supabase con 15 ETFs × 501 días de histórico
- [x] Edge Function fetch-etfs + cron diario
- [x] HTML funcional leyendo de Supabase
- [x] Deploy en Vercel (money-tracker-new-app.vercel.app)
- [x] Repo en GitHub con estructura de agentes
- [x] `CLAUDE.md` como fuente operativa (19-abr)
- [x] Sección "Flujo del Dinero" visual + selector de timeframe (19-abr)
- [x] Modal drill-down ETF → holdings (con fallback si no hay datos) (19-abr)
- [x] Disclaimer visible "proxy precio vs. flujos reales" (19-abr)
- [x] Vercel Analytics activado (19-abr)
- [x] Pipeline de publicación diaria en X (21:05 UTC L-V, inglés) (19-abr)
- [ ] Comprar dominio propio

### FASE 1 — Holdings + Drill-down
- [x] Tablas etf_holdings + stock_metadata + stock_daily en Supabase (migración 001 aplicada)
- [x] GitHub Actions workflow update-holdings con --write-supabase
- [x] UI: heatmap ETF por sector con color por rendimiento (sincronizado con TF del flow)
- [x] UI: modal con gráfico de precio SVG + selector de TF
- [x] UI: Daily Brief — sección editorial con mejores/peores ETF del día/semana/mes/trimestre
- [x] UI: búsqueda global de ETFs en tiempo real
- [x] UI: highlights 4 columnas (1D/1S/1M/3M), filas clicables abren modal
- [x] Edge Function v2: soporte ?symbols=X,Y para fetch selectivo
- [x] Nuevos sectores: Defensa (ITA, XAR), Inmobiliario (VNQ), Consumo (XLY, XLP), Crypto (IBIT, BITO)
- [x] Market Vision: árbol Índice→Sector→ETF→Empresa (pestaña "Mercado", hierarchy.json, validate_hierarchy.py, CI step)
- [ ] Poblar holdings reales (ejecutar update-holdings workflow manualmente la 1ª vez — requiere SUPABASE_SERVICE_ROLE_KEY en GitHub Secrets)

### FASE 2 — Auth + Watchlist + Snapshot
- [ ] Supabase Auth (Google OAuth)
- [ ] Tabla profiles + tier
- [ ] Watchlist: "Mi Flujo" filtrado
- [ ] Snapshot compartible (URL/imagen)
- [ ] Heatmap visual

### FASE 3 — Trending + Popularidad
- [ ] search_logs + triggers de trending
- [ ] "Lo más buscado hoy"

### FASE 4 — Monetización
- [ ] Stripe + webhook
- [ ] Feature flags Free/Pro
- [ ] Links de afiliados

---

## 14. HISTORIAL DE DECISIONES

| Fecha | Decisión | Motivo |
|-------|----------|--------|
| 18-abr-2026 | Supabase separado del dashboard personal | Cero riesgo al proyecto existente |
| 18-abr-2026 | Yahoo Finance como fuente de datos | Gratis, Edge Function evita CORS |
| 18-abr-2026 | Descartar noticias/sentiment/alertas/gamificación | Decisión firme del fundador |
| 19-abr-2026 | NO usar API de Anthropic para agentes | Coste innecesario. Scripts Python puros para datos, Cowork para curación |
| 19-abr-2026 | Vercel URL: money-tracker-new-app.vercel.app | Reconfigurado tras problema con deploy anterior |
| 19-abr-2026 | Investigación con Cowork, ejecución con GitHub Actions | Más profesional que LLM sin supervisión en datos financieros |
| 19-abr-2026 | `CLAUDE.md` al estilo Karpathy, un único agente por sesión | Multi-agente genera overhead y merge conflicts sin valor en un proyecto de 1 persona |
| 19-abr-2026 | Pipeline X: cron 21:05 UTC L-V | Capta cierre NYSE + prime time Twitter US + Europa tarde + Asia amanece |
| 19-abr-2026 | Agregación del flujo: promedio simple por sector, excluye Referencias | Sin pesos arbitrarios = más objetivo. Benchmarks fuera del flujo por definición |
| 19-abr-2026 | X API v2 via tweepy (OAuth 1.0a User Context) | Obligado por la API para `POST /2/tweets`. Free tier 500 posts/mes sobra |
| 20-abr-2026 | Market Vision: reemplazar pestaña "ETFs & Sectores" (no añadir nueva) | Mantiene UX simple, un único punto de entrada jerárquico |
| 20-abr-2026 | hierarchy.json como fuente única de verdad de la jerarquía + validate_hierarchy.py en CI | Evita que los datos queden desincronizados al añadir sectores/ETFs |
