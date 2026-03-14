import React from 'react'
import { oauthProviders, signInWithProvider } from '@/integrations/supabase/client'

interface AuthButtonsProps {
  enabledProviders?: Array<keyof typeof oauthProviders>
  className?: string
}

export const AuthButtons: React.FC<AuthButtonsProps> = ({ 
  enabledProviders = Object.keys(oauthProviders) as Array<keyof typeof oauthProviders>,
  className = ''
}) => {
  const handleOAuthSignIn = async (provider: keyof typeof oauthProviders) => {
    try {
      await signInWithProvider(provider)
    } catch (error) {
      console.error(`${provider} sign in failed:`, error)
    }
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {enabledProviders.map((provider) => {
        const config = oauthProviders[provider]
        return (
          <button
            key={String(provider)}
            onClick={() => handleOAuthSignIn(provider)}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg bg-card border border-border/50 text-foreground hover:bg-muted/50 transition-colors"
          >
            <img 
              src={config.icon} 
              alt={config.name}
              className="w-5 h-5"
            />
            <span className="text-sm font-medium">
              Continue with {config.name}
            </span>
          </button>
        )
      })}
    </div>
  )
}

export default AuthButtons
