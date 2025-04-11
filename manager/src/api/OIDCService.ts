// OidcService.ts

import { OidcProviderInterface, OidcUser } from '@/lib/oidc';
import { UserManager, User } from 'oidc-client-ts';

import { UserManagerSettings } from 'oidc-client-ts';

const oidcConfig: UserManagerSettings = {
  authority: 'https://your-identity-provider.com', // e.g., Auth0, Keycloak, Azure AD
  client_id: 'your-client-id',
  redirect_uri: 'http://localhost:3000/callback',
  post_logout_redirect_uri: 'http://localhost:3000/',
  response_type: 'code',
  scope: 'openid profile email',
};

export class OidcClientService implements OidcProviderInterface {
  private userManager = new UserManager(oidcConfig);

  async login() {
    await this.userManager.signinRedirect();
  }

  async handleCallback(): Promise<OidcUser> {
    const user = await this.userManager.signinRedirectCallback();
    return this.mapUser(user);
  }

  async getUser(): Promise<OidcUser | null> {
    const user = await this.userManager.getUser();
    return user ? this.mapUser(user) : null;
  }

  async isAuthenticated(): Promise<boolean> {
    const user = await this.userManager.getUser();
    return !!user && !user.expired;
  }

  async logout() {
    await this.userManager.signoutRedirect();
  }

  async getAccessToken(): Promise<string | null> {
    const user = await this.userManager.getUser();
    return user?.access_token ?? null;
  }

  private mapUser(user: User): OidcUser {
    return {
      id_token: user.id_token || "token",
      access_token: user.access_token,
      expires_at: user.expires_at || 0,
      profile: user.profile,
      state: user.state,
    };
  }
}

export const userManager = new UserManager(oidcConfig);

export const login = () => userManager.signinRedirect();
export const logout = () => userManager.signoutRedirect();
export const getUser = () => userManager.getUser();
export const signinCallback = () => userManager.signinRedirectCallback();
