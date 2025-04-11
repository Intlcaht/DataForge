// CallbackPage.tsx
import { signinCallback } from '@/api/OIDCService';
import { createFileRoute } from '@tanstack/react-router';
import { useEffect } from 'react';

// ┌─────────┐                                    ┌─────────────  ┐
// │         │ 1. Redirect with authorization     │               │
// │Authentik│──────────────code─────────────────>│ Frontend UI   │
// │         │                                    │ /auth/callback│
// └─────────┘                                    └──────┬──────  ┘
//                                                      │
//                                                      │ 2. Extract code from URL,
//                                                      │    call backend API
//                                                      ▼
//                                               ┌──────────────  ┐
//                                               │                │
//                                               │ Backend API    │
//                                               │ /oidc/callback │
//                                               └──────┬───────  ┘
//                                                      │
//                                                      │ 3. Verify state parameter
//                                                      │    Exchange code for tokens
//                                                      ▼
//                                               ┌──────────────┐
//                                               │              │
//                                               │  Authentik   │
//                                               │   Server     │
//                                               └──────┬───────┘
//                                                      │
//                                                      │ 4. Return tokens
//                                                      │    (access_token, id_token,
//                                                      │    refresh_token)
//                                                      ▼
//                                               ┌──────────────┐
//                                               │              │
//                                               │ Backend API  │
//                                               │              │
//                                               └──────┬───────┘
//                                                      │
//                                                      │ 5. Create session
//                                                      │    Store tokens securely
//                                                      │    Return success response
//                                                      ▼
//                                               ┌──────────────┐
//                                               │              │
//                                               │ Frontend UI  │
//                                               │              │
//                                               └──────┬───────┘
//                                                      │
//                                                      │ 6. Navigate to dashboard
//                                                      │    after successful auth
//                                                      ▼
//                                               ┌──────────────┐
//                                               │              │
//                                               │  Dashboard   │
//                                               │              │
//                                               └──────────────┘
// 1. **Authentik redirects to frontend callback URL** with authorization code after successful authentication
// 2. **Frontend extracts code** from URL and calls backend callback endpoint
// 3. **Backend verifies state parameter** to prevent CSRF attacks and exchanges code for tokens
// 4. **Authentik returns tokens** after successful code exchange
// 5. **Backend creates user session** and returns success response to frontend
// 6. **Frontend navigates to dashboard** after receiving confirmation of successful authentication

const CallbackPage = () => {
  useEffect(() => {
    signinCallback().then(() => {
      window.location.href = '/'; // redirect to homepage or dashboard
    });
  }, []);

  return <div>Signing in...</div>;
};


export const Route = createFileRoute('/auth/callback')({
  component: CallbackPage,
})


