/**
 * This file defines TypeScript interfaces for OpenID Connect (OIDC) authentication
 * specifically for integration with Authentik identity management system.
 * Authentik provides OIDC capabilities that we leverage for Single Sign-On (SSO).
 */

// ```
// ┌─────────┐      1. Click Login Button       ┌─────────────┐
// │         │─────────────────────────────────>│             │
// │  User   │                                  │ Frontend UI │
// │         │<─────────────────────────────────│             │
// └─────────┘      12. Display Dashboard       └──────┬──────┘
//      ▲                                             │
//      │                                             │ 2. Redirect to /auth/oidc/login
//      │                                             ▼
//      │                                     ┌──────────────┐
//      │                                     │              │
//      │                                     │ Backend API  │
//      │                                     │              │
//      │                                     └──────┬───────┘
//      │                                            │
//      │                                            │ 3. Generate state, nonce
//      │                                            │    Build authorization URL
//      │                                            │
//      │                                            ▼
//      │                                     ┌──────────────┐
//      │                                     │              │
//      │                                     │ Backend API  │
//      │                                     │              │
//      │                                     └──────┬───────┘
//      │                                            │
//      │                                            │ 4. Redirect to Authentik
//      │                                            │    with client_id, redirect_uri,
//      │                                            │    scope, state, nonce
//      │                                            ▼
// ┌─────────┐                                ┌──────────────┐
// │         │    5. Login credentials        │              │
// │  User   │────────────────────────────────> Authentik    │
// │         │                                │   Server     │
// │         │<───────────────────────────────│              │
// └─────────┘    6. Authentication prompt    └──────┬───────┘
//      ▲                                           │
//      │                                           │ 7. User authenticates
//      │                                           │    (username/password, MFA, etc.)
//      │                                           ▼
//      │                                    ┌──────────────┐
//      │                                    │              │
//      │                                    │  Authentik   │
//      │                                    │   Server     │
//      │                                    └──────┬───────┘
//      │                                           │
//      │                                           │ 8. Redirect to callback URL
//      │                                           │    with authorization code
//      │                                           ▼
//      │                                    ┌──────────────-┐
//      │                                    │               │
//      │                                    │ Backend API   │
//      │                                    │ /oidc/callback│
//      │                                    └──────┬───────-┘
//      │                                           │
//      │                                           │ 9. Exchange code for tokens
//      │                                           │    (access_token, id_token, 
//      │                                           │    refresh_token)
//      │                                           ▼
//      │                                    ┌──────────────┐
//      │                                    │              │
//      │                                    │  Authentik   │
//      │                                    │   Server     │
//      │                                    └──────┬───────┘
//      │                                           │
//      │                                           │ 10. Return tokens
//      │                                           ▼
//      │                                    ┌──────────────┐
//      │                                    │              │
//      │                                    │ Backend API  │
//      │                                    │              │
//      │                                    └──────┬───────┘
//      │                                           │
//      │                                           │ 11. Create session, store tokens,
//      │                                           │     redirect to frontend
//      └───────────────────────────────────────────┘
// ```

// 1. **User clicks login button** on the frontend React application
// 2. **Frontend redirects** to backend endpoint `/auth/oidc/login`
// 3. **Backend generates state and nonce** parameters to secure the flow
// 4. **Backend redirects user to Authentik** with proper OIDC parameters
// 5. **Authentik presents login page** to the user
// 6. **User enters credentials** in the Authentik login form
// 7. **Authentik validates credentials** and completes authentication flow (including any MFA if configured)
// 8. **Authentik redirects back** to application's callback URL with authorization code
// 9. **Backend exchanges code for tokens** by making a secure server-to-server request to Authentik
// 10. **Authentik returns tokens** (access_token, id_token, refresh_token)
// 11. **Backend creates user session** and stores tokens securely, then redirects to frontend
// 12. **Frontend displays dashboard** with authenticated user information

/* eslint-disable @typescript-eslint/no-explicit-any */
// NOTE: While disabling ESLint rules can be convenient for development,
// we should consider defining Authentik-specific types rather than 'any'
// since Authentik's token structure and user attributes are well-defined.

/**
 * Represents an authenticated user via Authentik's OIDC provider.
 * Authentik returns standard OIDC claims plus additional custom attributes
 * that are specific to Authentik's identity management capabilities.
 * 
 * @property {string} id_token - JWT containing Authentik-specific identity claims
 * @property {string} access_token - Token used to access Authentik-protected resources
 * @property {number} expires_at - Timestamp when the Authentik access token expires
 * @property {Object} profile - User profile information from Authentik
 * @property {string} profile.sub - Authentik's unique user identifier
 * @property {string} [profile.name] - User's full name from Authentik directory
 * @property {string} [profile.email] - User's email registered in Authentik
 * @property {string} [profile.preferred_username] - Username from Authentik account
 * @property {any} [state] - Application state passed during authentication flow
 */
export interface OidcUser {
  id_token: string;
  access_token: string;
  expires_at: number;
  profile: {
    sub: string;
    name?: string;
    email?: string;
    preferred_username?: string;
    // Index signature for additional Authentik-specific claims
    // Authentik often includes groups, roles, and custom attributes
    [key: string]: any;
  };
  state?: any;
}

/**
* Interface for Authentik OIDC provider integration.
* Defines methods needed to interact with Authentik's OIDC endpoints for authentication.
*/
export interface OidcProviderInterface {
  /**
   * Initiates a redirect to Authentik's login portal.
   * 
   * RECOMMENDATION: Add support for Authentik-specific parameters:
   * - flow: To specify which Authentik flow to use (authentication, enrollment, recovery)
   * - prompt: To control Authentik's authentication prompt behavior
   * - brand_name: For Authentik enterprise with multiple brands
   * 
   * @returns {Promise<void>} Promise that resolves when redirect to Authentik begins
   */
  login(): Promise<void>;

  /**
   * Processes the callback from Authentik after successful authentication.
   * Handles Authentik's authorization code and exchanges it for tokens.
   * 
   * RECOMMENDATION: Add special handling for Authentik-specific error codes:
   * - pending_activation: User exists but needs to activate account
   * - pending_mfa: Multi-factor authentication required
   * - temporary_lockout: Account temporarily locked due to failed attempts
   * 
   * @returns {Promise<OidcUser>} Promise resolving to authenticated user data from Authentik
   * @throws Will throw errors for Authentik-specific authentication failures
   */
  handleCallback(): Promise<OidcUser>;

  /**
   * Retrieves the currently authenticated Authentik user.
   * 
   * RECOMMENDATION: Add support for Authentik's session validation endpoint
   * to verify the session is still valid on the Authentik server, not just locally.
   * 
   * @returns {Promise<OidcUser | null>} Promise resolving to Authentik user or null
   */
  getUser(): Promise<OidcUser | null>;

  /**
   * Verifies if the user has a valid Authentik session.
   * 
   * RECOMMENDATION: Add verification against Authentik's token introspection
   * endpoint to confirm token validity server-side, not just checking expiration.
   * 
   * @returns {Promise<boolean>} Promise resolving to true if authenticated with Authentik
   */
  isAuthenticated(): Promise<boolean>;

  /**
   * Terminates the user's Authentik session.
   * 
   * RECOMMENDATION: Support Authentik's back-channel logout capability
   * which enhances security by directly notifying applications when 
   * sessions are terminated server-side.
   * 
   * @returns {Promise<void>} Promise that resolves when Authentik logout completes
   */
  logout(): Promise<void>;

  /**
   * Retrieves the current Authentik access token for API requests.
   * 
   * RECOMMENDATION: Add support for Authentik's token exchange feature
   * to obtain specialized tokens for different resource servers when needed.
   * 
   * @returns {Promise<string | null>} Promise resolving to Authentik access token
   */
  getAccessToken(): Promise<string | null>;

  /**
   * Revokes the active tokens with Authentik's revocation endpoint.
   * Authentik supports RFC 7009 token revocation for enhanced security.
   * 
   * RECOMMENDATION: Add options to specify which tokens to revoke
   * (access_token, refresh_token, or both) as Authentik supports
   * granular revocation.
   * 
   * @returns {Promise<void>} Promise resolving when Authentik completes token revocation
   */
  revokeSession?(): Promise<void>;
  
  /**
   * RECOMMENDED ADDITION: Refreshes the access token using Authentik's token endpoint.
   * Authentik supports RFC 6749 refresh token flow.
   * 
   * @returns {Promise<OidcUser>} Promise resolving to refreshed Authentik user data
   * @throws Error if refresh fails or token is invalid with Authentik-specific error codes
   */
  refreshToken?(): Promise<OidcUser>;
  
  /**
   * RECOMMENDED ADDITION: Checks if the current Authentik session is about to expire.
   * Useful for preemptively refreshing before user experiences session timeout.
   * 
   * @param {number} [thresholdSeconds=60] Time threshold in seconds
   * @returns {Promise<boolean>} Promise resolving to true if token will expire soon
   */
  isTokenExpiringSoon?(thresholdSeconds?: number): Promise<boolean>;
  
  /**
   * RECOMMENDED ADDITION: Retrieves user permissions and group memberships from Authentik.
   * Authentik provides rich authorization data via userinfo and introspection endpoints.
   * 
   * @returns {Promise<{groups: string[], permissions: string[]}>} User's authorization context
   */
  getAuthorizationContext?(): Promise<{groups: string[], permissions: string[]}>;
  
  /**
   * RECOMMENDED ADDITION: Checks if a specific Authentik stage (like MFA) is required.
   * Useful for handling pending authentication requirements.
   * 
   * @returns {Promise<{stageName: string, required: boolean}[]>} Required authentication stages
   */
  getPendingStages?(): Promise<{stageName: string, required: boolean}[]>;
  
  /**
   * RECOMMENDED ADDITION: Handle Authentik's account linking capabilities.
   * For scenarios where users need to link social accounts to existing Authentik accounts.
   * 
   * @param {string} provider - External provider identifier
   * @returns {Promise<void>} Promise that resolves when link flow initiates
   */
  initiateAccountLinking?(provider: string): Promise<void>;
}