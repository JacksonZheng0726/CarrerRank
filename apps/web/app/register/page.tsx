import type { Metadata } from "next";
import Link from "next/link";

import { AuthShell } from "@/features/auth/auth-shell";
import { RegisterForm } from "@/features/auth/register-form";

export const metadata: Metadata = { title: "Create account" };

export default function RegisterPage() {
  return (
    <AuthShell
      description="Create a secure account first. Career intelligence features arrive incrementally as your workspace grows."
      eyebrow="Your private workspace"
      footer={
        <>
          Already have an account?{" "}
          <Link className="font-bold text-moss underline-offset-4 hover:underline" href="/login">
            Sign in
          </Link>
        </>
      }
      title="Build from a solid foundation."
    >
      <RegisterForm />
    </AuthShell>
  );
}
