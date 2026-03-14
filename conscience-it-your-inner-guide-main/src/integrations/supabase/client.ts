import { createClient } from '@supabase/supabase-js';
import type { Database } from './types';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_PUBLISHABLE_KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!SUPABASE_URL || !SUPABASE_PUBLISHABLE_KEY) {
  throw new Error('Missing Supabase configuration. Please check your .env file.');
}

export const supabase = createClient<Database>(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
  auth: {
    storage: localStorage,
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
    flowType: 'pkce',
  }
});

// OAuth Providers Configuration
export const oauthProviders = {
  google: {
    name: 'Google',
    icon: 'https://authjs.dev/img/providers/google.svg',
    provider: 'google' as const,
    scopes: 'email profile'
  },
  apple: {
    name: 'Apple',
    icon: 'https://authjs.dev/img/providers/apple.svg',
    provider: 'apple' as const,
    scopes: 'email name'
  },
  github: {
    name: 'GitHub',
    icon: 'https://authjs.dev/img/providers/github.svg',
    provider: 'github' as const,
    scopes: 'user:email'
  },
  x: {
    name: 'X (Twitter)',
    icon: 'https://authjs.dev/img/providers/x.svg',
    provider: 'twitter' as const,
    scopes: 'tweet.read users.read'
  }
};

// Authentication helper functions
export const signInWithProvider = async (provider: keyof typeof oauthProviders) => {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: oauthProviders[provider].provider,
    options: {
      scopes: oauthProviders[provider].scopes,
      redirectTo: `${import.meta.env.VITE_REDIRECT_URL}?provider=${provider}`
    }
  });
  return { data, error };
};

export const getAccessToken = async () => {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || null;
};