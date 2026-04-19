# CLAUDE.md

> Instrucciones para Claude (Cowork, Claude Code, subagentes) y cualquier humano que abra este repo. Léelo completo antes de tocar nada. Si en algún momento la realidad del código contradice este archivo, **actualiza este archivo en el mismo commit**.

---

## 1. Qué es esto

Tracker objetivo del flujo de dinero entre sectores, ETFs y empresas. Datos puros, sin opiniones. Web pública + backend Supabase + automatizaciones gratuitas.

- Producción: https://money-tracker-new-app.vercel.app
- Repo: https://github.com/danipunic-rgb/Money-tracker
- Backend: Supabase `rieyywfkpprgkenljilm` (eu-west-2)
- Fuente de datos: Yahoo Finance (endpoints públicos)

**Documento de visión detallado:** `ARCHITECTURE.md`. Este archivo (`CLAUDE.md`) es el resumen operativo.

---

## 2. Reglas inviolables

No negociable salvo que Dani las cambie explícitamente:

1. **Cero noticias, cero sentiment, cero alertas, cero gamificación, cero consejo financiero.** Solo datos numéricos.
2. **Cero APIs de pago.** Yahoo Finance (gratis) para datos. Supabase Free. Vercel Free. GitHub Actions Free. X API Free tier. No usar API de Anthropic en producción — la curación se hace con Cowork on-demand.
3. **Web en español. Tweets en inglés.** X traduce automáticamente, maximiza alcance global.
4. **El flujo que mostramos es PROXY basado en rendimiento de precio**, no flujos reales de creations/redemptions. El disclaimer debe ser visible en la UI, no enterrado.
5. **RLS activado en todas las tablas públicas.** `anon` solo lee. Solo `service_role` (nunca en frontend) escribe.
6. **Ningún secret en el repo.** Se configuran como GitHub Secrets o Supabase environment vars.

---

## 3. Cómo se trabaja aquí (modelo de agentes)

**No hay múltiples agentes commiteando por separado.** Esto es un proyecto de 1 persona; la complejidad multi-agente no aporta. El modelo es:

- **Dani (humano):** único autor humano. Decide qué hacer. Revisa y aprueba antes de push cuando toca algo sensible.
- **Cowork / Claude Code (un solo agente por sesión):** lee este archivo, ejecuta tareas, escribe código, puede hacer commit y push por su cuenta cuando Dani le da luz verde.
- **Subagentes (Task tool):** herramientas puntuales dentro de una sesión para investigación o tareas paralelas. No son entidades persistentes.
- **Scripts Python en `agents/`:** NO son agentes LLM. Son scripts deterministas que corren en GitHub Actions. El nombre se mantuvo por legacy.

Cuando Dani abra una sesión de Cowork/Claude Code, el orden canónico es:

1. Leer `CLAUDE.md` (este archivo)
2. Leer `ARCHITECTURE.md` si la tarea toca decisiones de diseño
3. Ejecutar la tarea
4. Si hay cambios estructurales → actualizar estos docs en el mismo commit
5. Commit + push

---

## 4. Estructura del repo

```
Money-tracker/
├── CLAUDE.md                    ← este archivo
├── ARCHITECTURE.md              ← visión completa + roadmap
├── COWORK_QUICKSTART.md         ← atajo para primeras sesiones
├── README.md                    ← cara pública del repo
├── index.html                   ← toda la web (1 archivo, zero-build)
├── vercel.json                  ← config de deploy (mínima)
├── data/
│   ├── sectors.json             ← curación manual: qué sectores rastreamos
│   ├── etfs.json                ← curación manual: qué ETFs por sector
│   └── holdings.json            ← generado automático (lunes semanal)
├── agents/
│   ├── fetch_holdings.py        ← scrapper semanal de holdings
│   └── publish_x_daily.py       ← publicación diaria en X
├── supabase/
│   └── migrations/              ← SQL versionado de cambios de schema
└── .github/
    └── workflows/
        ├── update-holdings.yml  ← lunes 04:00 UTC
        └── publish-x-daily.yml  ← L-V 21:05 UTC
```

---

## 5. Backend Supabase — estado actual

Proyecto: `rieyywfkpprgkenljilm.supabase.co` (eu-west-2, plan Free).

Tablas existentes:
- `etf_metadata` — qué ETFs rastreamos (15 filas, RLS SELECT anon)
- `etf_daily` — histórico de precios (~7.5k filas, RLS SELECT anon)

Edge Functions:
- `fetch-etfs` — pull desde Yahoo Finance, upsert en `etf_daily`. Param `?days=N`.

Cron Supabase (pg_cron):
- `fetch-etfs-daily` — `30 22 * * 1-5` (diario L-V, tras cierre US en CET)

Tablas pendientes (Fase 1, ver `supabase/migrations/001_holdings.sql`):
- `etf_holdings`, `stock_metadata`, `stock_daily`

**Para aplicar migraciones** desde Cowork/Claude Code con el MCP de Supabase configurado, usar `apply_migration`. Si no está el MCP, pegar el SQL en el SQL Editor del dashboard.

---

## 6. Automatizaciones (qué corre solo y qué no)

| Tarea | Schedule | Cómo | Requisitos |
|---|---|---|---|
| Precios ETFs | `30 22 * * 1-5` UTC | Supabase pg_cron → `fetch-etfs` | Ya activo |
| Holdings ETFs | `0 4 * * 1` UTC | GitHub Actions → `fetch_holdings.py` | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` |
| Tweet diario | `5 21 * * 1-5` UTC | GitHub Actions → `publish_x_daily.py` | X API secrets (ver §7) |
| Curación sectores/ETFs | Manual, semanal o cuando Dani quiera | Cowork edita JSONs → push | — |

**Por qué este horario para X:** 21:05 UTC = cierre de NYSE + 5min (en invierno), captura prime time de finance Twitter en US, tarde en Europa, amanecer en Asia.

---

## 7. X / Twitter API — configuración

Crear app en https://developer.x.com, plan Free (500 posts/mes). Obtener 4 credenciales y guardarlas como GitHub Secrets en el repo:

- `X_API_KEY` (OAuth 1.0a consumer key)
- `X_API_SECRET` (OAuth 1.0a consumer secret)
- `X_ACCESS_TOKEN` (OAuth 1.0a user access token)
- `X_ACCESS_TOKEN_SECRET` (OAuth 1.0a user access token secret)

El script `publish_x_daily.py` usa `tweepy` (wrapper oficial), falla con log claro si falta alguno, y nunca expone credenciales.

**Nota:** la API v2 requiere OAuth 1.0a User Context para `POST /2/tweets`. OAuth 2.0 Bearer Token solo permite lectura. No confundirse.

---

## 8. Comandos comunes

```bash
# Ver estado
git status && git log --oneline -10

# Ejecutar scraper de holdings local (sin escribir en Supabase)
python agents/fetch_holdings.py

# Ejecutar scraper escribiendo en Supabase (requiere env vars)
SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... \
  python agents/fetch_holdings.py --write-supabase

# Probar el tweet publisher en modo dry-run (no publica)
python agents/publish_x_daily.py --dry-run

# Forzar fetch de precios desde la web (botón "Forzar fetch")
# o vía curl:
curl "https://rieyywfkpprgkenljilm.supabase.co/functions/v1/fetch-etfs?days=7" \
  -H "Authorization: Bearer <ANON_KEY>"

# Aplicar migración manualmente (copia el SQL al dashboard)
cat supabase/migrations/001_holdings.sql
```

---

## 9. Cómo añadir un sector nuevo (ejemplo: Defensa)

1. Editar `data/sectors.json`: añadir entry con `id`, `name`, `color`, `description`.
2. Editar `data/etfs.json`: añadir los ETFs (ej. ITA, XAR) con `sector_id` coincidente.
3. Insertar las filas correspondientes en `etf_metadata` de Supabase (vía SQL Editor o Cowork con MCP).
4. Forzar el fetch para poblar `etf_daily` con el histórico: `GET /functions/v1/fetch-etfs?days=500`.
5. Commit + push. Vercel redeploya.

---

## 10. Protocolo git — cómo NO destruir trabajo

Lecciones aprendidas a golpes. Léelas antes de tocar `git` cuando algo falle.

### 10.1 Si aparece `fatal: Unable to create '.git/index.lock': Permission denied`

Es casi siempre un `index.lock` huérfano (otro proceso de git murió sin limpiar). **NO ejecutar `git reset --hard`** como "arreglo", porque destruye los cambios no commiteados en ficheros trackeados.

Protocolo correcto:

```bash
# 1) Asegúrate de que no hay otro git corriendo
ps aux | grep git

# 2) Borra SOLO el lock (no toques nada más)
rm -f .git/index.lock

# 3) Si el índice está corrupto (raro), regenéralo sin perder el working tree:
rm -f .git/index
git reset            # ← SIN --hard. Recoloca el índice desde HEAD, conserva tus cambios
git status           # verifica que tus modificaciones siguen ahí

# 4) Añade y commitea normal
git add <ficheros>
git commit -m "..."
```

### 10.2 Nunca ejecutar `git reset --hard` salvo que Dani lo pida por nombre

`git reset --hard` borra los cambios no commiteados del working tree. En esta sesión ya perdimos `index.html` y `ARCHITECTURE.md` una vez por esto. Si algo parece requerirlo, casi siempre hay alternativa:

- ¿Quieres descartar un fichero concreto? → `git checkout -- <file>` (también destructivo, pero acotado).
- ¿Quieres volver a `origin/main` pero conservar tu trabajo? → `git stash && git reset --hard origin/main && git stash pop`.
- ¿Solo quieres limpiar el índice bloqueado? → ver §10.1.

### 10.3 Antes de `git commit` en una sesión nueva

Siempre verificar qué vamos a commitear:

```bash
git status
git diff --stat
```

Si aparecen ficheros que no recuerdas haber tocado, **parar** y entender qué pasó antes de commitear. El caso típico: otra sesión dejó cambios a medias y ahora se mezclan con los tuyos.

### 10.4 Cowork sandbox → push

Cowork no tiene credenciales de GitHub en el sandbox. El flujo que ha funcionado es:

1. Cowork hace cambios en `/sessions/.../mnt/Money-tracker/` (esto es el working directory del usuario).
2. Cowork clona el repo a `/tmp/mt-clone`, copia ahí los cambios, commitea y genera parches con `git format-patch` en `_cowork-patches/`.
3. Dani (o Claude Code local) aplica esos parches con `git am` y hace `git push`.

`_cowork-patches/` está en `.gitignore`. Borrarlo tras cada push.

---

## 11. Cuándo actualizar este archivo

**Siempre** que cambie alguno de estos:

- Se añade/elimina una automatización
- Cambia la lista de tablas o el schema de Supabase
- Se introduce una nueva dependencia o API externa
- Se cambia la regla de "qué NO hacemos"
- Se cambian los horarios de cron
- Cambia el modelo de despliegue (hoy: push a main → Vercel auto)

**Nunca** dejar este archivo desactualizado. Un `CLAUDE.md` mentiroso es peor que no tenerlo.

---

## 12. Historial rápido (lo importante)

- 2026-04-18 — Proyecto Supabase separado creado, Edge Function + cron diario activos.
- 2026-04-19 — Repo público en GitHub, deploy en Vercel, ARCHITECTURE.md como fuente de verdad.
- 2026-04-19 — Decisión: scripts Python puros (sin LLM) + Cowork para curación.
- 2026-04-19 — Introducido este `CLAUDE.md`, sección "Flujo del Dinero" visual en la web, pipeline de publicación diaria en X (inglés), disclaimer visible, migración SQL de Fase 1.
- 2026-04-19 — Fix: `publish_x_daily.py` usaba `os.environ.get(k, default)` que no captura el caso "var existe pero vacía" típico de GitHub Actions con secret no configurado. Cambiado a `os.environ.get(k) or default` + validación explícita en `sb_get`. Añadido protocolo git §10 tras perder `index.html`/`ARCHITECTURE.md` por un `git reset --hard` de Claude Code.
