import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { DashboardClient } from "@/features/dashboard/dashboard-client";
import { QueryProvider } from "@/components/query-provider";
import { renderWithQueryClient } from "@/tests/test-utils";

const router = vi.hoisted(() => ({
  replace: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => router,
}));

const user = {
  id: "a562f5df-ded8-4ac5-b4fb-0ff34add00a2",
  email: "candidate@example.com",
  created_at: "2026-08-13T12:00:00Z",
};

const meResponse = {
  additive_backend_field: "ignored for forward compatibility",
  user,
  candidate_profile: {
    id: "f2049f87-daac-41f4-94e7-493967324548",
    user_id: user.id,
    headline: null,
    years_experience: null,
    preferred_roles: [],
    preferred_locations: [],
    work_authorization: {},
    remote_preference: null,
    created_at: "2026-08-13T12:00:00Z",
    updated_at: "2026-08-13T12:00:00Z",
    additive_profile_field: "ignored for forward compatibility",
  },
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("dashboard session behavior", () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    fetchMock.mockReset();
    router.replace.mockReset();
    router.refresh.mockReset();
    vi.stubGlobal("fetch", fetchMock);
    document.cookie = "careerrank_csrf=csrf-test-token; Path=/";
  });

  it("refreshes an expired access session once and retries me", async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ detail: "Not authenticated" }, 401))
      .mockResolvedValueOnce(jsonResponse({ detail: "Not authenticated" }, 401))
      .mockResolvedValueOnce(jsonResponse({ user }))
      .mockResolvedValueOnce(jsonResponse(meResponse));

    renderWithQueryClient(<DashboardClient />);

    expect(await screen.findByRole("heading", { name: "Welcome, candidate@example.com." })).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(4);
    expect(fetchMock.mock.calls.map(([path]) => path)).toEqual([
      "/api/v1/auth/me",
      "/api/v1/auth/me",
      "/api/v1/auth/refresh",
      "/api/v1/auth/me",
    ]);
    const refreshHeaders = new Headers(fetchMock.mock.calls[2]?.[1]?.headers);
    expect(refreshHeaders.get("X-CSRF-Token")).toBe("csrf-test-token");
  });

  it("sends the CSRF token when signing out", async () => {
    document.cookie = "__Host-careerrank_csrf=production-csrf-token; Secure; Path=/";
    fetchMock
      .mockResolvedValueOnce(jsonResponse(meResponse))
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    const browser = userEvent.setup();
    renderWithQueryClient(<DashboardClient />);

    await screen.findByText("candidate@example.com", { selector: "dd" });
    await browser.click(screen.getByRole("button", { name: "Sign out" }));

    await waitFor(() => expect(router.replace).toHaveBeenCalledWith("/login"));
    expect(fetchMock.mock.calls[1]?.[0]).toBe("/api/v1/auth/logout");
    const logoutHeaders = new Headers(fetchMock.mock.calls[1]?.[1]?.headers);
    expect(logoutHeaders.get("X-CSRF-Token")).toBe("production-csrf-token");
  });

  it("removes rendered account data when another tab signs out", async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse(meResponse))
      .mockImplementation(() => new Promise<Response>(() => undefined));
    render(
      <QueryProvider>
        <DashboardClient />
      </QueryProvider>,
    );

    await screen.findByText("candidate@example.com", { selector: "dd" });
    window.dispatchEvent(
      new StorageEvent("storage", {
        key: "careerrank:session-event",
        newValue: JSON.stringify({ id: "another-tab", type: "session-changed" }),
      }),
    );

    expect(await screen.findByLabelText("Loading your account")).toBeInTheDocument();
    expect(screen.queryByText("candidate@example.com", { selector: "dd" })).not.toBeInTheDocument();
  });

  it("renders an actionable error state when session recovery fails", async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ detail: "Not authenticated" }, 401))
      .mockResolvedValueOnce(jsonResponse({ detail: "Not authenticated" }, 401))
      .mockResolvedValueOnce(jsonResponse({ detail: "Refresh token is invalid" }, 401));

    renderWithQueryClient(<DashboardClient />);

    expect(await screen.findByText("Refresh token is invalid")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Return to sign in" })).toHaveAttribute("href", "/login");
    expect(JSON.parse(window.localStorage.getItem("careerrank:session-event") ?? "{}"))
      .toMatchObject({ type: "session-changed" });
  });
});
