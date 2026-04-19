-- =============================================================================
-- Migration 002 — Nuevos sectores: Defensa, Inmobiliario, Consumo, Crypto
--
-- Aplicada via MCP Supabase el 2026-04-19.
-- Estos INSERT se aplicaron directamente con execute_sql (datos, no DDL).
-- =============================================================================

-- Sector Defensa
insert into public.etf_metadata (symbol, name, sector, sector_color, sector_desc, display_order, enabled) values
  ('ITA', 'iShares U.S. Aerospace & Defense', 'Defensa', '#854d0e', 'Aeroespacial, defensa, industria militar', 50, true),
  ('XAR', 'SPDR S&P Aerospace & Defense',     'Defensa', '#854d0e', 'Aeroespacial, defensa, industria militar', 51, true)
on conflict (symbol) do update set
  name=excluded.name, sector=excluded.sector, sector_color=excluded.sector_color,
  sector_desc=excluded.sector_desc, display_order=excluded.display_order, enabled=excluded.enabled;

-- Sector Inmobiliario
insert into public.etf_metadata (symbol, name, sector, sector_color, sector_desc, display_order, enabled) values
  ('VNQ', 'Vanguard Real Estate ETF', 'Inmobiliario', '#0f766e', 'REITs, inmobiliario diversificado', 60, true)
on conflict (symbol) do update set
  name=excluded.name, sector=excluded.sector, sector_color=excluded.sector_color,
  sector_desc=excluded.sector_desc, display_order=excluded.display_order, enabled=excluded.enabled;

-- Sector Consumo
insert into public.etf_metadata (symbol, name, sector, sector_color, sector_desc, display_order, enabled) values
  ('XLY', 'Consumer Discretionary SPDR',  'Consumo', '#a16207', 'Consumo discrecional y básico', 70, true),
  ('XLP', 'Consumer Staples SPDR',        'Consumo', '#a16207', 'Consumo discrecional y básico', 71, true)
on conflict (symbol) do update set
  name=excluded.name, sector=excluded.sector, sector_color=excluded.sector_color,
  sector_desc=excluded.sector_desc, display_order=excluded.display_order, enabled=excluded.enabled;

-- Sector Crypto
insert into public.etf_metadata (symbol, name, sector, sector_color, sector_desc, display_order, enabled) values
  ('IBIT', 'iShares Bitcoin Trust ETF',      'Crypto', '#6d28d9', 'ETFs de Bitcoin y exposición cripto', 80, true),
  ('BITO', 'ProShares Bitcoin Strategy ETF', 'Crypto', '#6d28d9', 'ETFs de Bitcoin y exposición cripto', 81, true)
on conflict (symbol) do update set
  name=excluded.name, sector=excluded.sector, sector_color=excluded.sector_color,
  sector_desc=excluded.sector_desc, display_order=excluded.display_order, enabled=excluded.enabled;

-- Reordenar display_order para agrupar por sector
update public.etf_metadata set display_order = case symbol
  when 'XLK'  then 10 when 'SMH'  then 11 when 'QQQ'  then 12
  when 'XLE'  then 20 when 'ICLN' then 21 when 'URA'  then 22
  when 'XLF'  then 30 when 'KRE'  then 31 when 'KBE'  then 32
  when 'XLV'  then 40 when 'IBB'  then 41 when 'XBI'  then 42
  when 'ITA'  then 50 when 'XAR'  then 51
  when 'VNQ'  then 60
  when 'XLY'  then 70 when 'XLP'  then 71
  when 'IBIT' then 80 when 'BITO' then 81
  when 'SPY'  then 90 when 'IWM'  then 91 when 'GLD'  then 92
  else display_order end;
