import { User, UserManager, WebStorageStateStore } from "oidc-client-ts";

const authority = import.meta.env.VITE_COGNITO_AUTHORITY;
const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN;
const useMocks = import.meta.env.VITE_USE_MOCKS === "true" || !import.meta.env.VITE_API_BASE_URL;

export const apiConfigured = !useMocks && Boolean(import.meta.env.VITE_API_BASE_URL);
export const authConfigured = Boolean(authority && clientId && cognitoDomain);
export const authExpiredEvent = "tariffguard:auth-expired";

const userManager = authConfigured
  ? new UserManager({
      authority: authority!,
      client_id: clientId!,
      redirect_uri: window.location.origin,
      post_logout_redirect_uri: window.location.origin,
      response_type: "code",
      scope: "openid email profile",
      automaticSilentRenew: true,
      monitorSession: false,
      userStore: new WebStorageStateStore({ store: window.localStorage }),
    })
  : null;

export async function initializeAuth(): Promise<User | null> {
  if (!userManager) return null;
  const params = new URLSearchParams(window.location.search);
  if (params.has("code") && params.has("state")) {
    const user = await userManager.signinRedirectCallback();
    window.history.replaceState({}, document.title, window.location.pathname);
    return user;
  }
  const user = await userManager.getUser();
  return user && !user.expired ? user : null;
}

export async function signIn(): Promise<void> {
  if (!userManager) throw new Error("Cognito authentication is not configured");
  await userManager.signinRedirect();
}

export async function signOut(): Promise<void> {
  if (!userManager || !clientId || !cognitoDomain) return;
  await userManager.removeUser();
  const query = new URLSearchParams({
    client_id: clientId,
    logout_uri: window.location.origin,
  });
  window.location.assign(`${cognitoDomain}/logout?${query.toString()}`);
}

export async function getAccessToken(): Promise<string | null> {
  if (!userManager) return null;
  const user = await userManager.getUser();
  if (!user || user.expired) return null;
  return user.access_token;
}
