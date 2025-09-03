-- db/sql/001_roles.sql
-- UUID ovunque. Supabase in genere ha già pgcrypto attivo; per sicurezza:
create extension if not exists "pgcrypto";

create table if not exists public.roles (
  id uuid primary key default gen_random_uuid(),
  name varchar(64) unique not null,
  description varchar(255)
);

create table if not exists public.user_roles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  role_id uuid not null references public.roles(id) on delete cascade,
  constraint uq_user_role unique(user_id, role_id)
);

create index if not exists idx_user_roles_user on public.user_roles(user_id);
create index if not exists idx_roles_name on public.roles(name);
