import Link from "next/link";

type SiteHeaderProps = {
  compact?: boolean;
};

export function SiteHeader({ compact = false }: SiteHeaderProps) {
  return (
    <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6 lg:px-8">
      <Link className="group inline-flex items-center gap-3" href="/" aria-label="CareerRank home">
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-ink text-sm font-black text-cream shadow-card transition-transform group-hover:-rotate-3">
          CR
        </span>
        <span className="text-lg font-bold tracking-tight">CareerRank</span>
      </Link>
      {!compact && (
        <nav className="flex items-center gap-3" aria-label="Account">
          <Link
            className="rounded-full px-4 py-2 text-sm font-semibold text-ink transition-colors hover:bg-white/60"
            href="/login"
          >
            Sign in
          </Link>
          <Link
            className="rounded-full bg-ink px-5 py-2.5 text-sm font-semibold text-cream shadow-card transition-transform hover:-translate-y-0.5"
            href="/register"
          >
            Create account
          </Link>
        </nav>
      )}
    </header>
  );
}
