# Money Tracker

El mejor tracker objetivo del flujo de dinero del mundo.

Entra → ve al instante de dónde sale el capital y hacia dónde va → sectores → ETFs → empresas.

Solo datos puros. Sin noticias. Sin opiniones. Sin sentiment.

## Stack

- **Frontend**: HTML/JS estático en Vercel
- **Backend**: Supabase (PostgreSQL + Edge Functions)
- **Agentes**: GitHub Actions + API de Anthropic (cron semanal)
- **Datos**: Yahoo Finance (precios diarios automáticos)

## Desarrollo

```bash
# Clonar el repo
git clone https://github.com/danipunic-rgb/Money-tracker.git
cd Money-tracker

# Editar archivos (o usar Cowork/Claude Code)
# Luego push para deploy automático en Vercel
git add . && git commit -m "cambios" && git push
```

## Documentación

Lee [`ARCHITECTURE.md`](./ARCHITECTURE.md) antes de hacer cualquier cambio.
