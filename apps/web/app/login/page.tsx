import type { Metadata } from "next";
import Link from "next/link";

import { AuthShell } from "@/features/auth/auth-shell";
import { LoginForm } from "@/features/auth/login-form";

export const metadata: Metadata = { title: "Sign in" };

export default function LoginPage() {
  return (
    <AuthShell
      description="Return to your private workspace and continue building an evidence-led job search."
      eyebrow="Welcome back"
      footer={
        <>
          New to CareerRank?{" "}
          <Link className="font-bold text-moss underline-offset-4 hover:underline" href="/register">
            Create an account
          </Link>
        </>
      }
      title="Pick up where you left off."
    >
      <LoginForm />
    </AuthShell>
  );
}
