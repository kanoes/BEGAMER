PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  google_sub TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  avatar_url TEXT,
  created_at TEXT NOT NULL,
  last_login_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS steam_accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL REFERENCES users(google_sub) ON DELETE CASCADE,
  steam_id TEXT NOT NULL,
  display_name TEXT NOT NULL,
  profile_url TEXT,
  avatar_url TEXT,
  is_demo INTEGER NOT NULL DEFAULT 0,
  is_active INTEGER NOT NULL DEFAULT 0,
  last_synced_at TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(user_id, steam_id)
);

CREATE INDEX IF NOT EXISTS ix_steam_accounts_user_active
  ON steam_accounts(user_id, is_active);

CREATE TABLE IF NOT EXISTS library_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL REFERENCES steam_accounts(id) ON DELETE CASCADE,
  app_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  icon_url TEXT,
  cover_url TEXT NOT NULL,
  hero_url TEXT NOT NULL,
  playtime_forever INTEGER NOT NULL DEFAULT 0,
  playtime_2weeks INTEGER NOT NULL DEFAULT 0,
  last_played_at TEXT,
  achievements_unlocked INTEGER,
  achievements_total INTEGER,
  tags TEXT NOT NULL DEFAULT '[]',
  moods TEXT NOT NULL DEFAULT '[]',
  favorite INTEGER NOT NULL DEFAULT 0,
  custom_status TEXT,
  note TEXT,
  first_seen_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(account_id, app_id)
);

CREATE INDEX IF NOT EXISTS ix_library_entries_account
  ON library_entries(account_id);

CREATE INDEX IF NOT EXISTS ix_library_entries_account_name
  ON library_entries(account_id, name);
