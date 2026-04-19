-- =============================================================================
-- Migration 001 — Holdings & stocks (Fase 1)
--
-- Crea las tablas necesarias para el drill-down ETF → empresa:
--   - etf_holdings:    qué empresas tiene cada ETF, con su peso % y fecha
--   - stock_metadata:  metadatos de cada empresa (sector, industria, país)
--   - stock_daily:     precios históricos de empresas individuales
--
-- Todas las tablas tienen RLS activado: `anon` solo puede SELECT.
-- La escritura la hace el script agents/fetch_holdings.py vía service_role
-- desde GitHub Actions (semanal, lunes 04:00 UTC).
--
-- Para aplicar:
--   · Con MCP Supabase en Cowork/Claude Code: usar apply_migration
--   · Manualmente: copiar este SQL al SQL Editor del dashboard
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. stock_metadata
-- -----------------------------------------------------------------------------
create table if not exists public.stock_metadata (
  symbol         text primary key,
  isin           text,
  name           text,
  sector         text,
  industry       text,
  country        text,
  search_count   integer not null default 0,
  is_trending    boolean not null default false,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

create index if not exists stock_metadata_sector_idx   on public.stock_metadata (sector);
create index if not exists stock_metadata_trending_idx on public.stock_metadata (is_trending) where is_trending;

alter table public.stock_metadata enable row level security;

drop policy if exists "anon can read stock_metadata" on public.stock_metadata;
create policy "anon can read stock_metadata"
  on public.stock_metadata for select
  to anon
  using (true);

-- -----------------------------------------------------------------------------
-- 2. etf_holdings
-- -----------------------------------------------------------------------------
create table if not exists public.etf_holdings (
  etf_symbol    text not null references public.etf_metadata(symbol) on delete cascade,
  stock_symbol  text not null,
  weight        numeric(8,4) not null check (weight >= 0 and weight <= 100),
  as_of_date    date not null,
  created_at    timestamptz not null default now(),
  primary key (etf_symbol, stock_symbol, as_of_date)
);

create index if not exists etf_holdings_stock_idx on public.etf_holdings (stock_symbol);
create index if not exists etf_holdings_asof_idx  on public.etf_holdings (as_of_date desc);

alter table public.etf_holdings enable row level security;

drop policy if exists "anon can read etf_holdings" on public.etf_holdings;
create policy "anon can read etf_holdings"
  on public.etf_holdings for select
  to anon
  using (true);

-- -----------------------------------------------------------------------------
-- 3. stock_daily  (precios históricos de empresas individuales)
-- -----------------------------------------------------------------------------
create table if not exists public.stock_daily (
  symbol       text not null references public.stock_metadata(symbol) on delete cascade,
  date         date not null,
  close        numeric(14,4),
  adj_close    numeric(14,4),
  volume       bigint,
  fetched_at   timestamptz not null default now(),
  primary key (symbol, date)
);

create index if not exists stock_daily_date_idx on public.stock_daily (date desc);

alter table public.stock_daily enable row level security;

drop policy if exists "anon can read stock_daily" on public.stock_daily;
create policy "anon can read stock_daily"
  on public.stock_daily for select
  to anon
  using (true);

-- -----------------------------------------------------------------------------
-- 4. Trigger utilitario: actualizar updated_at en stock_metadata
-- -----------------------------------------------------------------------------
create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists stock_metadata_touch on public.stock_metadata;
create trigger stock_metadata_touch
  before update on public.stock_metadata
  for each row execute function public.touch_updated_at();

-- =============================================================================
-- Verificación (opcional, ejecuta manualmente tras aplicar):
--   select count(*) from public.stock_metadata;
--   select count(*) from public.etf_holdings;
--   select count(*) from public.stock_daily;
-- =============================================================================
