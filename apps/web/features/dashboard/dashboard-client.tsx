"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { SiteHeader } from "@/components/site-header";
import { getMe, logout } from "@/lib/api/auth";
import { authQueryKeys } from "@/lib/auth/query-keys";

function DashboardLoading() {
  return (
    <main className="min-h-screen" aria-busy="true" aria-label="Loading your account">
      <SiteHeader compact />
      <div className="mx-auto max-w-6xl animate-pulse px-6 py-14 lg:px-8">
        <div className="h-4 w-28 rounded-full bg-ink/10" />
        <div className="mt-5 h-12 max-w-lg rounded-2xl bg-ink/10" />
        <div className="mt-12 grid gap-5 md:grid-cols-2">
          <div className="h-52 rounded-[2rem] bg-white/65" />
          <div className="h-52 rounded-[2rem] bg-white/65" />
        </div>
      </div>
    </main>
  );
}

type DashboardErrorProps = {
  message: string;
  onRetry: () => void;
};

function DashboardError({ message, onRetry }: DashboardErrorProps) {
  return (
    <main className="min-h-screen">
      <SiteHeader compact />
      <section className="mx-auto max-w-xl px-6 py-20 text-center">
        <div className="rounded-[2rem] border border-red-200 bg-white/75 p-8 shadow-card" role="alert">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-red-700">Account unavailable</p>
          <h1 className="mt-4 text-3xl font-black tracking-tight">We could not load your workspace.</h1>
          <p className="mt-4 leading-7 text-ink/65">{message}</p>
          <div className="mt-7 flex flex-wrap justify-center gap-3">
            <button
              className="rounded-full bg-ink px-5 py-3 text-sm font-bold text-cream"
              onClick={onRetry}
              type="button"
            >
              Try again
            </button>
            <Link
              className="rounded-full border border-ink/15 bg-white px-5 py-3 text-sm font-bold"
              href="/login"
            >
              Return to sign in
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}

function valueOrFallback(value: string | null): string {
  return value === null || value.trim() === "" ? "Not added yet" : value;
}

export function DashboardClient() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const meQuery = useQuery({
    queryKey: authQueryKeys.me,
    queryFn: ({ signal }) => getMe(signal),
  });
  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () => {
      void queryClient.resetQueries({ queryKey: authQueryKeys.me, exact: true });
      queryClient.getMutationCache().clear();
      router.replace("/login");
      router.refresh();
    },
  });

  if (meQuery.isPending) {
    return <DashboardLoading />;
  }

  if (meQuery.isError) {
    return (
      <DashboardError
        message={
          meQuery.error instanceof Error
            ? meQuery.error.message
            : "Please check your connection and try again."
        }
        onRetry={() => {
          void meQuery.refetch();
        }}
      />
    );
  }

  const { user, candidate_profile: profile } = meQuery.data;
  const roles = profile.preferred_roles.length > 0 ? profile.preferred_roles.join(", ") : "Not added yet";
  const locations =
    profile.preferred_locations.length > 0
      ? profile.preferred_locations.join(", ")
      : "Not added yet";

  return (
    <main className="min-h-screen">
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6 lg:px-8">
        <Link className="inline-flex items-center gap-3" href="/" aria-label="CareerRank home">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-ink text-sm font-black text-cream shadow-card">
            CR
          </span>
          <span className="text-lg font-bold tracking-tight">CareerRank</span>
        </Link>
        <button
          className="rounded-full border border-ink/15 bg-white/65 px-5 py-2.5 text-sm font-bold transition-colors hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
          disabled={logoutMutation.isPending}
          onClick={() => logoutMutation.mutate()}
          type="button"
        >
          {logoutMutation.isPending ? "Signing out…" : "Sign out"}
        </button>
      </header>

      <section className="mx-auto max-w-6xl px-6 pb-20 pt-12 lg:px-8 lg:pt-20">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-moss">Your workspace</p>
        <h1 className="mt-4 max-w-3xl text-balance text-4xl font-black tracking-[-0.045em] sm:text-6xl">
          Welcome, {user.email}.
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-ink/65">
          Your account and candidate profile are connected. This Phase 0 workspace is ready for
          the next CareerRank capability.
        </p>

        {logoutMutation.isError && (
          <div className="mt-8 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
            {logoutMutation.error instanceof Error
              ? logoutMutation.error.message
              : "Sign out failed. Please try again."}
          </div>
        )}

        <div className="mt-12 grid gap-5 md:grid-cols-2">
          <article className="rounded-[2rem] border border-white/75 bg-white/70 p-7 shadow-card">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-moss">Account</p>
            <dl className="mt-6 space-y-5">
              <div>
                <dt className="text-sm text-ink/50">Email</dt>
                <dd className="mt-1 break-all font-bold">{user.email}</dd>
              </div>
              <div>
                <dt className="text-sm text-ink/50">Member since</dt>
                <dd className="mt-1 font-bold">
                  {new Intl.DateTimeFormat(undefined, { dateStyle: "long" }).format(
                    new Date(user.created_at),
                  )}
                </dd>
              </div>
            </dl>
          </article>

          <article className="rounded-[2rem] border border-white/75 bg-white/70 p-7 shadow-card">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-moss">Candidate profile</p>
            <dl className="mt-6 grid gap-5 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <dt className="text-sm text-ink/50">Headline</dt>
                <dd className="mt-1 font-bold">{valueOrFallback(profile.headline)}</dd>
              </div>
              <div>
                <dt className="text-sm text-ink/50">Preferred roles</dt>
                <dd className="mt-1 font-bold">{roles}</dd>
              </div>
              <div>
                <dt className="text-sm text-ink/50">Preferred locations</dt>
                <dd className="mt-1 font-bold">{locations}</dd>
              </div>
              <div>
                <dt className="text-sm text-ink/50">Remote preference</dt>
                <dd className="mt-1 font-bold">{valueOrFallback(profile.remote_preference)}</dd>
              </div>
              <div>
                <dt className="text-sm text-ink/50">Years of experience</dt>
                <dd className="mt-1 font-bold">
                  {profile.years_experience === null ? "Not added yet" : profile.years_experience}
                </dd>
              </div>
            </dl>
          </article>
        </div>
      </section>
    </main>
  );
}
