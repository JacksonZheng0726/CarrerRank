import Link from "next/link";

import { SiteHeader } from "@/components/site-header";

const principles = [
  ["Explainable", "Understand the evidence behind every recommendation."],
  ["Outcome-led", "Turn application history into a clearer search strategy."],
  ["Private by design", "Your career data stays scoped to your account."],
] as const;

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden">
      <SiteHeader />
      <section className="mx-auto grid max-w-6xl gap-14 px-6 pb-20 pt-14 lg:grid-cols-[1.16fr_0.84fr] lg:px-8 lg:pb-28 lg:pt-24">
        <div className="max-w-3xl">
          <p className="mb-6 inline-flex rounded-full border border-moss/20 bg-white/55 px-4 py-2 text-xs font-bold uppercase tracking-[0.2em] text-moss">
            Job search intelligence, grounded in outcomes
          </p>
          <h1 className="text-balance text-5xl font-black leading-[0.98] tracking-[-0.055em] sm:text-7xl">
            Apply with a reason,
            <span className="block text-moss">not a hunch.</span>
          </h1>
          <p className="mt-7 max-w-2xl text-lg leading-8 text-ink/70 sm:text-xl">
            CareerRank helps you build a measurable job-search strategy around fit,
            evidence, and the outcomes you actually receive.
          </p>
          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              className="rounded-full bg-ink px-6 py-3.5 text-sm font-bold text-cream shadow-card transition-transform hover:-translate-y-0.5"
              href="/register"
            >
              Start your profile
            </Link>
            <Link
              className="rounded-full border border-ink/15 bg-white/65 px-6 py-3.5 text-sm font-bold transition-colors hover:bg-white"
              href="/login"
            >
              I already have an account
            </Link>
          </div>
        </div>

        <aside className="relative self-end rounded-[2rem] border border-white/70 bg-white/55 p-5 shadow-card backdrop-blur sm:p-7">
          <div aria-hidden="true" className="absolute -right-16 -top-16 -z-10 h-40 w-40 rounded-full bg-amber/25 blur-3xl" />
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-moss">The foundation</p>
          <div className="mt-5 space-y-3">
            {principles.map(([title, description], index) => (
              <div className="rounded-2xl border border-ink/10 bg-cream/65 p-5" key={title}>
                <div className="flex gap-4">
                  <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-moss text-xs font-black text-white">
                    {index + 1}
                  </span>
                  <div>
                    <h2 className="font-bold">{title}</h2>
                    <p className="mt-1 text-sm leading-6 text-ink/65">{description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </aside>
      </section>
    </main>
  );
}
