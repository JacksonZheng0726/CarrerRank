import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { LoginForm } from "@/features/auth/login-form";
import { RegisterForm } from "@/features/auth/register-form";
import { authQueryKeys } from "@/lib/auth/query-keys";
import { createTestQueryClient, renderWithQueryClient } from "@/tests/test-utils";

const router = vi.hoisted(() => ({
  replace: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => router,
}));

const userResponse = {
  user: {
    id: "a562f5df-ded8-4ac5-b4fb-0ff34add00a2",
    email: "candidate@example.com",
    created_at: "2026-08-13T12:00:00Z",
  },
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("authentication forms", () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    fetchMock.mockReset();
    router.replace.mockReset();
    router.refresh.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  it("validates the login form before making a request", async () => {
    const user = userEvent.setup();
    renderWithQueryClient(<LoginForm />);

    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Enter a valid email address")).toBeInTheDocument();
    expect(screen.getByText("Password must be at least 12 characters")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("submits valid login credentials and opens the dashboard", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(userResponse));
    const user = userEvent.setup();
    renderWithQueryClient(<LoginForm />);

    await user.type(screen.getByLabelText("Email address"), "candidate@example.com");
    await user.type(screen.getByLabelText("Password"), "a-secure-password");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => expect(router.replace).toHaveBeenCalledWith("/dashboard"));
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [path, init] = fetchMock.mock.calls[0] ?? [];
    expect(path).toBe("/api/v1/auth/login");
    expect(init?.credentials).toBe("include");
    expect(JSON.parse(String(init?.body))).toEqual({
      email: "candidate@example.com",
      password: "a-secure-password",
    });
  });

  it("removes a previous user's cached profile after login", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(userResponse));
    const queryClient = createTestQueryClient();
    queryClient.setQueryData(authQueryKeys.me, {
      user: { ...userResponse.user, email: "previous@example.com" },
      candidate_profile: { id: "cached-profile" },
    });
    const browser = userEvent.setup();
    renderWithQueryClient(<LoginForm />, { queryClient });

    await browser.type(screen.getByLabelText("Email address"), "candidate@example.com");
    await browser.type(screen.getByLabelText("Password"), "a-secure-password");
    await browser.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => expect(router.replace).toHaveBeenCalledWith("/dashboard"));
    expect(queryClient.getQueryData(authQueryKeys.me)).toBeUndefined();
  });

  it("shows a FastAPI error without navigating", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ detail: "Invalid email or password" }, 401));
    const user = userEvent.setup();
    renderWithQueryClient(<LoginForm />);

    await user.type(screen.getByLabelText("Email address"), "candidate@example.com");
    await user.type(screen.getByLabelText("Password"), "a-secure-password");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Invalid email or password")).toBeInTheDocument();
    expect(router.replace).not.toHaveBeenCalled();
  });

  it("requires matching registration passwords", async () => {
    const user = userEvent.setup();
    renderWithQueryClient(<RegisterForm />);

    await user.type(screen.getByLabelText("Email address"), "candidate@example.com");
    await user.type(screen.getByLabelText("Password"), "a-secure-password");
    await user.type(screen.getByLabelText("Confirm password"), "a-different-password");
    await user.click(screen.getByRole("button", { name: "Create account" }));

    expect(await screen.findByText("Passwords do not match")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("does not send password confirmation to the API", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(userResponse, 201));
    const user = userEvent.setup();
    renderWithQueryClient(<RegisterForm />);

    await user.type(screen.getByLabelText("Email address"), "candidate@example.com");
    await user.type(screen.getByLabelText("Password"), "a-secure-password");
    await user.type(screen.getByLabelText("Confirm password"), "a-secure-password");
    await user.click(screen.getByRole("button", { name: "Create account" }));

    await waitFor(() => expect(router.replace).toHaveBeenCalledWith("/dashboard"));
    const [path, init] = fetchMock.mock.calls[0] ?? [];
    expect(path).toBe("/api/v1/auth/register");
    expect(JSON.parse(String(init?.body))).toEqual({
      email: "candidate@example.com",
      password: "a-secure-password",
    });
  });
});
