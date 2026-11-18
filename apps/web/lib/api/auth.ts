import type { LoginInput, RegisterInput } from "@/lib/auth/schemas";
import {
  coordinateAuthState,
  publishSessionChanged,
} from "@/lib/auth/session-coordinator";
import { ApiError, requestJson, requestWithoutBody } from "@/lib/api/client";
import {
  authResponseSchema,
  meResponseSchema,
  type AuthResponse,
  type MeResponse,
} from "@/lib/api/schemas";

const AUTH_BASE = "/api/v1/auth";
const CSRF_COOKIES = ["__Host-careerrank_csrf", "careerrank_csrf"] as const;

function csrfToken(): string {
  if (typeof document === "undefined") {
    throw new ApiError(403, "A security token is unavailable. Please sign in again.");
  }

  const cookies = document.cookie.split(";").map((part) => part.trim());
  const cookie = CSRF_COOKIES.map((name) => `${name}=`)
    .map((prefix) => cookies.find((part) => part.startsWith(prefix)))
    .find((part) => part !== undefined);

  if (cookie === undefined) {
    throw new ApiError(403, "A security token is unavailable. Please sign in again.");
  }

  return decodeURIComponent(cookie.slice(cookie.indexOf("=") + 1));
}

function csrfHeaders(): HeadersInit {
  return { "X-CSRF-Token": csrfToken() };
}

export function register(input: RegisterInput): Promise<AuthResponse> {
  return coordinateAuthState(async () => {
    const response = await requestJson(`${AUTH_BASE}/register`, {
      method: "POST",
      body: JSON.stringify({ email: input.email, password: input.password }),
      schema: authResponseSchema,
    });
    publishSessionChanged();
    return response;
  });
}

export function login(input: LoginInput): Promise<AuthResponse> {
  return coordinateAuthState(async () => {
    const response = await requestJson(`${AUTH_BASE}/login`, {
      method: "POST",
      body: JSON.stringify(input),
      schema: authResponseSchema,
    });
    publishSessionChanged();
    return response;
  });
}

async function refreshSession(): Promise<AuthResponse> {
  try {
    return await requestJson(`${AUTH_BASE}/refresh`, {
      method: "POST",
      headers: csrfHeaders(),
      schema: authResponseSchema,
    });
  } catch (error: unknown) {
    // A refresh 401 also clears the shared cookie jar on the backend. Notify
    // other tabs so none can continue rendering cached account data.
    if (error instanceof ApiError && error.status === 401) {
      publishSessionChanged();
    }
    throw error;
  }
}

function requestMe(signal?: AbortSignal): Promise<MeResponse> {
  return requestJson(`${AUTH_BASE}/me`, {
    method: "GET",
    schema: meResponseSchema,
    signal,
  });
}

export async function getMe(signal?: AbortSignal): Promise<MeResponse> {
  try {
    return await requestMe(signal);
  } catch (error: unknown) {
    if (!(error instanceof ApiError) || error.status !== 401) {
      throw error;
    }
  }

  return coordinateAuthState(async () => {
    // A different browser tab may have refreshed while this caller waited for
    // the cross-tab lock. Rechecking avoids replaying its rotated token.
    try {
      return await requestMe(signal);
    } catch (error: unknown) {
      if (!(error instanceof ApiError) || error.status !== 401) {
        throw error;
      }
    }

    // Rotation is a server-side state transition. Once started it must finish
    // even if the component that initiated recovery unmounts.
    await refreshSession();
    return requestMe(signal);
  }, signal);
}

export function logout(): Promise<void> {
  return coordinateAuthState(async () => {
    await requestWithoutBody(`${AUTH_BASE}/logout`, {
      method: "POST",
      headers: csrfHeaders(),
    });
    publishSessionChanged();
  });
}
