ALTER TABLE public.user_settings
ADD COLUMN IF NOT EXISTS overlay_effect TEXT NOT NULL DEFAULT 'off';
