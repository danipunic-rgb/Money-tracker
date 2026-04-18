# Money Tracker — Documento de Arquitectura

> Este documento es la fuente de verdad del proyecto. Cualquier agente (Cowork, Claude Code, o un humano) que trabaje en el repo DEBE leer esto primero.
> Última actualización: 18 abril 2026

---

## 1. VISIÓN DEL PRODUCTO

**Money Tracker es el mejor tracker objetivo del flujo de dinero del mundo.**

El usuario entra en la web y ve al instante: de dónde sale el dinero, hacia dónde va, en qué sectores, en qué ETFs, y en qué empresas. Solo datos objetivos. Sin opiniones, sin noticias, sin sentiment.

### Qué somos
- Un tracker de flujo de capital basado en datos puros (precios, volumen, pesos de holdings)
- Una herramienta visual para ver dónde se mueve el dinero: sector → ETF → empresa
- Una plataforma que se actualiza sola y requiere mínimo mantenimiento

### Qué NO somos (decisiones firmes)
- **NO somos un noticiero.** No mostramos noticias, no explicamos "por qué" sube o baja algo. Cero noticias, cero artículos, cero sentiment analysis.
- **NO damos alertas.** El usuario tiene TradingView y otros servicios mucho más reputados para eso. Nosotros mostramos datos.
- **NO tenemos gamificación.** Ni rachas, ni badges, ni leaderboards. Es una herramienta profesional de datos, no Duolingo.
- **NO damos consejo financiero.** Solo datos objetivos, el usuario decide.

### Nota importante: "Flujo de dinero" ≠ precio
Lo que mostramos como "entrada/salida de capital" es un PROXY basado en rendimiento (si el ETF sube, asumimos entrada de capital). Los flujos reales de un ETF (aportaciones/reembolsos netos) requieren datos de pago (Bloomberg, FactSet). Para el MVP es una simplificación aceptable, pero debemos ser transparentes con el usuario añadiendo un disclaimer tipo "basado en rendimiento de precio, no en flujos netos reales".

---

## 2. NIVELES DE PROFUNDIDAD

### Nivel 1 — Vista de pájaro (lo que ve el usuario nada más entrar)
- **Recuadro "Flujo del Dinero"** en la parte superior: dos columnas (rojo = salida, verde = entrada) con los sectores/ETFs que más se mueven
- **Selector de timeframe**: 1D, 1S, 1M, 3M, 6M (arriba a la derecha del recuadro)
- **Resumen objetivo**: frase generada automáticamente tipo "Esta semana el capital sale de Tecnología (-1.8%) y entra en Energía (+2.4%)"
- **Heatmap de sectores/ETFs**: cuadrícula de colores donde cada celda = sector o ETF, color = flujo neto, tamaño proporcional a relevancia
- Debajo: las tablas por sector que ya tenemos (ETFs con % cambio en todos los timeframes)

### Nivel 2 — Drill-down (click en un ETF o sector)
- Modal o sección expandible con:
  - Top 10-15 holdings del ETF (empresa, peso %, rendimiento 1D/1S/1M/3M)
  - Las 2-3 empresas más relevantes del sector (por peso o por movimiento)
  - Flujo detallado del sector

### Nivel 3 — Empresa individual + Popularidad
- Barra de búsqueda global (ETFs y empresas)
- **Sistema de popularidad automática**: cada búsqueda se registra en `search_logs`. Si una empresa supera un umbral de búsquedas → se marca como "trending" y aparece en el Flujo del Dinero y en su sector
- Vista de empresa: rendimiento por timeframes + en qué ETFs aparece + peso

---

## 3. FEATURES APROBADAS (por orden de prioridad)

| # | Feature | Fase | Descripción |
|---|---------|------|-------------|
| 1 | Dashboard sector → ETF con % cambio | 0 (HECHO) | Ya funciona con 15 ETFs y 2 años de histórico |
| 2 | Sección "Flujo del Dinero" visual | 0 | Entrada/salida por sector con selector de timeframe |
| 3 | Deploy público en Vercel | 0 | URL pública accesible desde cualquier dispositivo |
| 4 | Drill-down ETF → Holdings | 1 | Click en ETF → top empresas con rendimiento |
| 5 | Daily Brief objetivo | 1 | Resumen matutino generado con datos puros (sin noticias) |
| 6 | OAuth Google + tabla profiles | 2 | Usuarios identificados, preparación para monetización |
| 7 | Watchlist + "Mi Flujo" | 2 | Usuarios logueados guardan ETFs/empresas favoritas |
| 8 | Snapshot compartible | 2 | Botón que genera URL/imagen del estado actual del flujo |
| 9 | Heatmap sectores/empresas | 2 | Cuadrícula visual con color = flujo neto |
| 10 | Trending / "Lo más buscado" | 3 | Basado en búsquedas reales de usuarios |
| 11 | Monetización Stripe (Free/Pro/Ultra) | 4 | Solo cuando haya >1.000 usuarios recurrentes |

### Features RECHAZADAS (no implementar nunca)

| Feature | Motivo del rechazo |
|---------|-------------------|
| Noticias / News tracker | No somos un noticiero. Complica la web y riesgo de información mala |
| Sentiment analysis | Subjetivo, contradice la visión de "solo datos objetivos" |
| Alertas (push/email/WhatsApp) | El usuario tiene herramientas mejores (TradingView). No competimos ahí |
| Gamificación (rachas, badges) | No encaja con el tono profesional de la herramienta |
| Consejo financiero / recomendaciones | Riesgo legal, fuera de scope |

---

## 4. STACK TÉCNICO

```
Frontend:  HTML/JS estático (single file por ahora) → servido por Vercel
Backend:   Supabase (PostgreSQL + Edge Functions + Auth + RLS)
Hosting:   Vercel (auto-deploy desde GitHub, analytics gratuito)
Repo:      GitHub (danipunic-rgb/Money-tracker)
Agentes:   GitHub Actions (cron semanal) + API de Anthropic
Datos:     Yahoo Finance (gratis, via Edge Functions server-side)
Dominio:   moneytracker.vercel.app (temporal) → dominio propio cuando esté listo
```

### ¿Por qué esta stack?
- **Todo serverless**: no hay servidor que mantener, pagas $0 hasta que crezcas mucho
- **Supabase ya existe y funciona**: proyecto `money-tracker` (ID: `rieyywfkpprgkenljilm`) en eu-west-2
- **Vercel**: deploy en 1 click, preview branches, analytics gratis, CDN global
- **GitHub Actions para agentes**: corren en la nube sin tu ordenador, 2.000 min/mes gratis
- **HTML puro por ahora**: cuando necesitemos routing (URLs por sector, por ETF), migramos a Next.js. No antes.

---

## 5. SUPABASE — Estado actual

### Proyecto
- **Nombre**: money-tracker
- **ID**: `rieyywfkpprgkenljilm`
- **Región**: eu-west-2 (London)
- **URL**: `https://rieyywfkpprgkenljilm.supabase.co`
- **Organización**: Dani (ybahlmdwofhddgkqbcdk), plan Free
- **Anon key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpZXl5d2ZrcHByZ2tlbmxqaWxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYzNzQ5NDgsImV4cCI6MjA5MTk1MDk0OH0.d4H4QW_BeBc6axpgmevLKNdMb0gJ-U6hQ15Rk9Bn-20`

> NOTA: Este proyecto es SEPARADO del dashboard personal (fhufubhakkxwxhusejou). No tocar el otro proyecto.

### Tablas existentes

**etf_metadata** — Qué ETFs rastreamos
```
symbol (PK), name, sector, sector_color, sector_desc, display_order, enabled, created_at
```
15 ETFs cargados: XLK, SMH, QQQ, XLE, ICLN, URA, XLF, KRE, KBE, XLV, IBB, XBI, SPY, IWM, GLD

**etf_daily** — Precios históricos
```
symbol (FK), date, close, adj_close, volume, fetched_at
PK: (symbol, date)
```
~7.515 filas. Rango: 17-abr-2024 → 16-abr-2026 (2 años)

### RLS activo
- `anon` puede SELECT en ambas tablas
- Solo `service_role` puede INSERT/UPDATE/DELETE

### Edge Functions desplegadas
- **fetch-etfs**: trae precios de Yahoo Finance (con fallback a Stooq), upsert en etf_daily
  - Parámetro: `?days=N` (por defecto 7)
  - Acepta llamadas sin JWT (verify_jwt=false) para poder ser invocada por pg_cron

### Cron jobs activos
- **fetch-etfs-daily**: `30 22 * * 1-5` (22:30 UTC lunes-viernes, = 00:30 CEST)
  - Llama a la Edge Function con `?days=7`
  - Ya funcionó correctamente en el backfill inicial

### Tablas PENDIENTES (crear en fases posteriores)

```sql
-- Fase 1: Holdings
etf_holdings (etf_symbol, stock_symbol, stock_isin, weight, shares, as_of_date)
stock_metadata (symbol, isin, name, sector, industry, country)
stock_daily (symbol, date, close, adj_close, volume)

-- Fase 2: Auth + Watchlist
profiles (id uuid → auth.users, tier, created_at)
user_watchlist (user_id, symbol, symbol_type, added_at)

-- Fase 3: Popularidad
search_logs (id, user_id, symbol, searched_at)
-- + trigger: incrementar search_count en stock_metadata, marcar trending si > umbral
```

---

## 6. DISEÑO VISUAL

### Principios
- Fondo claro `#f9f7f4` con radial gradients sutiles
- Tipografía: Fraunces (serif, títulos) + Plus Jakarta Sans (cuerpo) + JetBrains Mono (datos/números)
- Estilo editorial/periódico: dateline, bordes finos, minimalismo controlado
- Verde fuerte (#15803d) para subidas, rojo fuerte (#b91c1c) para bajadas
- Celdas con tinte de color proporcional al cambio (cuanto más fuerte, más saturado)

### Colores de sectores
| Sector | Color |
|--------|-------|
| Tecnología | #7c3aed |
| Energía | #c2410c |
| Financieros | #0369a1 |
| Salud | #15803d |
| Referencias | #78716c |

---

## 7. PIPELINE DE AGENTES

### Concepto
Tres agentes en cadena que se ejecutan semanalmente vía GitHub Actions. Cada agente genera un archivo JSON que alimenta al siguiente. El último agente escribe directamente en Supabase.

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Agent 1: Sectors   │────▶│  Agent 2: ETFs      │────▶│  Agent 3: Holdings  │
│                     │     │                     │     │                     │
│  Input: conocimiento│     │  Input: sectors.json│     │  Input: etfs.json   │
│  Output: sectors.json│    │  Output: etfs.json  │     │  Output: → Supabase │
│  Frecuencia: 1x/sem │     │  Frecuencia: 1x/sem │     │  Frecuencia: 1x/sem │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### Agent 1 — Sector Analyst
- **Qué hace**: Investiga los sectores clave de la economía global (EEUU + resto del mundo), define el alcance exacto de cada sector (qué incluye y qué no), detecta sectores emergentes
- **Output**: `data/sectors.json` con la clasificación actualizada
- **Usa**: API de Anthropic (Claude) con web search para investigar consenso actual

### Agent 2 — ETF Curator
- **Qué hace**: Lee `sectors.json`, investiga los mejores ETFs dentro de cada sector (por AUM, liquidez, tracking error), obtiene ISINs, confirma solapamientos
- **Output**: `data/etfs.json` con el detalle completo de ETFs por sector
- **Usa**: API de Anthropic + Yahoo Finance para verificar que los ETFs existen y están activos

### Agent 3 — Holdings Tracker
- **Qué hace**: Lee `etfs.json`, descarga holdings reales de cada ETF (top 10-15 posiciones), identifica empresas, su peso, sector, país
- **Output**: Upsert directo en Supabase (tablas etf_holdings, stock_metadata)
- **Usa**: Yahoo Finance / FMP API para holdings reales

### Actualización de precios (separado de los agentes)
- Los precios de ETFs se actualizan diariamente vía pg_cron + Edge Function (ya funciona)
- Los precios de acciones individuales (stock_daily) se añadirán cuando tengamos la tabla de holdings

### Dónde corren los agentes
- **GitHub Actions** (gratis, 2.000 min/mes)
- Cron: `0 4 * * 1` = cada lunes a las 04:00 UTC (06:00 CEST)
- Necesita: secret `ANTHROPIC_API_KEY` en el repo de GitHub
- Necesita: secret `SUPABASE_SERVICE_ROLE_KEY` en el repo de GitHub

### Dónde NO corren los agentes
- NO en Cowork (Cowork es para desarrollar, no para crons)
- NO en Edge Functions (timeout de 400s, insuficiente para investigación profunda)
- NO en el navegador del usuario

---

## 8. FLUJO DE TRABAJO PARA DESARROLLO

### Desarrollo con Cowork / Claude Code
1. Abrir Cowork en la carpeta del repo clonado
2. Decirle: "Lee ARCHITECTURE.md antes de hacer nada"
3. Pedir los cambios que quieras
4. Cowork edita los archivos localmente
5. Tú revisas y haces `git add . && git commit -m "descripción" && git push`
6. Vercel auto-deploya en ~30 segundos
7. Verificas en la URL pública

### Añadir un nuevo ETF o sector
1. Si es manual: INSERT directo en Supabase (etf_metadata) + disparar Edge Function
2. Si es automático: los agentes lo detectan y lo añaden solos

### Probar cambios antes de publicar
- Vercel crea "preview deployments" para cada branch que no sea `main`
- Flujo: crear branch → hacer cambios → push → Vercel te da URL temporal → verificar → merge a main → producción

---

## 9. MONETIZACIÓN (preparar, no activar)

### Modelo futuro: Freemium
| Tier | Precio | Acceso |
|------|--------|--------|
| Free | 0€ | Dashboard público, top 3 en flujo, top 5 holdings |
| Pro | ~6.99€/mes | Todo ilimitado + heatmap + Daily Brief completo + snapshots |
| Ultra | ~19€/mes | + API access + datos exportables |

### Qué preparar AHORA (Fase 2)
- Supabase Auth (Google OAuth)
- Tabla `profiles` con columna `tier` (default: 'free')
- Feature flags en el frontend: `if (tier === 'pro') { ... }`
- Botones "Mejora a Pro" discretos en los drill-downs profundos

### Qué preparar DESPUÉS (Fase 4+, solo cuando haya tráfico)
- Stripe integration + webhook que actualiza tier en profiles
- Links de afiliados de brokers (eToro, IBKR, Degiro) en cada ETF/empresa
- Google AdSense (solo si hay volumen significativo)

### Lo que dijo Grok que era correcto
- Dominio propio (moneytracker.com o .es) lo antes posible para confianza
- OAuth desde ya es barato y prepara todo
- Vercel es perfecto para monetizar, la gente paga en .vercel.app si el producto es bueno

---

## 10. VERCEL — Configuración

- **Repo conectado**: github.com/danipunic-rgb/Money-tracker
- **URL temporal**: money-tracker-app-rust-eta.vercel.app
- **Framework**: Other (static HTML)
- **Build**: no build step (archivos estáticos directos)
- **Analytics**: activar Vercel Analytics (gratis, da pageviews, países, dispositivos)
- **Dominio propio**: pendiente de comprar y configurar

---

## 11. SECTORES Y ETFs ACTUALES

### Sectores configurados (v1)
| Sector | ETFs | Color | Justificación |
|--------|------|-------|---------------|
| Tecnología | XLK, SMH, QQQ | #7c3aed | Epicentro del capital en era IA. Cubre software (XLK), semiconductores (SMH) y Nasdaq amplio (QQQ) |
| Energía | XLE, ICLN, URA | #c2410c | Cubre fósiles (XLE), renovables (ICLN) y nuclear/uranio (URA) |
| Financieros | XLF, KRE, KBE | #0369a1 | Termómetro macro. Cubre grandes bancos (XLF), regionales (KRE) y bancario puro (KBE) |
| Salud | XLV, IBB, XBI | #15803d | Cubre farma+dispositivos (XLV), biotech grande (IBB) y biotech especulativo (XBI) |
| Referencias | SPY, IWM, GLD | #78716c | Benchmarks: mercado amplio (SPY), small caps (IWM), oro/refugio (GLD) |

### Sectores a considerar en el futuro (Agent 1 investigará)
- Defensa / Aerospace (ITA, XAR)
- Inmobiliario / REITs (VNQ, XLRE)
- Consumo discrecional vs staples (XLY, XLP)
- Mercados emergentes (EEM, VWO)
- China específico (KWEB, FXI)
- Commodities amplio (DBC, GSG)
- Bonos / Renta fija (TLT, BND) — para contexto macro
- Crypto (BITO, IBIT) — si hay demanda

---

## 12. MÉTRICAS A TRACKEAR

### Desde el día 1 (Vercel Analytics gratuito)
- Pageviews diarios / semanales
- Usuarios únicos
- Países de origen
- Dispositivos (móvil vs desktop)
- Páginas más visitadas (cuando tengamos routing)

### Desde Fase 2 (con Auth)
- Usuarios registrados vs anónimos
- Tasa de registro
- Búsquedas realizadas (tabla search_logs)
- ETFs/empresas más vistos

### Desde Fase 4 (con monetización)
- Tasa de conversión Free → Pro
- Revenue mensual
- Churn rate

---

## 13. CREDENCIALES Y SECRETS

### En el código (público, seguro)
- Supabase URL: `https://rieyywfkpprgkenljilm.supabase.co`
- Supabase anon key: en el HTML (es pública por diseño, RLS la protege)

### En GitHub Secrets (privado, NUNCA en el código)
- `ANTHROPIC_API_KEY`: para los agentes de GitHub Actions
- `SUPABASE_SERVICE_ROLE_KEY`: para que los agentes escriban en la BBDD
- `SUPABASE_URL`: redundante pero mejor tenerlo como secret

### Cómo añadir secrets en GitHub
1. Ir al repo → Settings → Secrets and variables → Actions
2. "New repository secret"
3. Añadir cada una con su nombre exacto

---

## 14. HISTORIAL DE DECISIONES

| Fecha | Decisión | Contexto |
|-------|----------|----------|
| 18-abr-2026 | Crear proyecto Supabase separado | Para no arriesgar el dashboard personal existente |
| 18-abr-2026 | Yahoo Finance como fuente de datos | Gratis, suficiente para MVP. Edge Function server-side evita CORS |
| 18-abr-2026 | No usar Stooq/proxies CORS | Probamos y fallaron. El problema era CORS del navegador, no la fuente |
| 18-abr-2026 | Descartar noticias/sentiment | Decisión firme del fundador. Solo datos objetivos |
| 18-abr-2026 | Descartar alertas | El usuario tiene TradingView para eso |
| 18-abr-2026 | Descartar gamificación | No encaja con el tono profesional |
| 18-abr-2026 | GitHub Actions para agentes | Cowork/Claude Code no corren 24/7. GitHub Actions sí, gratis |
| 18-abr-2026 | Vercel para hosting | Auto-deploy, analytics gratis, CDN, preview deploys |
| 18-abr-2026 | HTML puro por ahora, Next.js después | No migrar hasta que necesitemos routing real |
| 18-abr-2026 | Snapshot compartible SÍ | Viralidad brutal, solo datos objetivos |
| 18-abr-2026 | Daily Brief SÍ | Pero 100% objetivo, generado con datos, sin IA opinando |
