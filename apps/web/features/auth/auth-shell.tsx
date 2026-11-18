import type { ReactNode } from "react";

import { SiteHeader } from "@/components/site-header";

type AuthShellProps = {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
  footer: ReactNode;
};

export function AuthShell({ eyebrow, title, description, children, footer }: AuthShellProps) {
  return (
    <main className="min-h-screen">
      <SiteHeader compact />
      <section className="mx-auto grid max-w-5xl items-center gap-12 px-6 pb-16 pt-10 lg:grid-cols-[0.85fr_1.15fr] lg:px-8 lg:pt-20">
        <div className="max-w-lg">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-moss">{eyebrow}</p>
          <h1 className="mt-5 text-4xl font-black tracking-[-0.045em] sm:text-5xl">{title}</h1>
          <p className="mt-5 text-lg leading-8 text-ink/65">{description}</p>
        </div>
        <div className="rounded-[2rem] border border-white/75 bg-white/70 p-6 shadow-card backdrop-blur sm:p-9">
          {children}
          <div className="mt-7 border-t border-ink/10 pt-6 text-center text-sm text-ink/65">
            {footer}
          </div>
        </div>
      </section>
    </main>
  );
}
