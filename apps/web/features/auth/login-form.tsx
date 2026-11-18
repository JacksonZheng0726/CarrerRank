"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import { FormField } from "@/features/auth/form-field";
import { login } from "@/lib/api/auth";
import { loginSchema, type LoginInput } from "@/lib/auth/schemas";
import { authQueryKeys } from "@/lib/auth/query-keys";

export function LoginForm() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });
  const mutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: authQueryKeys.me, exact: true });
      router.replace("/dashboard");
      router.refresh();
    },
  });

  return (
    <form className="space-y-5" noValidate onSubmit={handleSubmit((input) => mutation.mutate(input))}>
      <FormField
        autoComplete="email"
        error={errors.email?.message}
        id="email"
        inputMode="email"
        label="Email address"
        placeholder="you@example.com"
        type="email"
        {...register("email")}
      />
      <FormField
        autoComplete="current-password"
        error={errors.password?.message}
        id="password"
        label="Password"
        type="password"
        {...register("password")}
      />
      {mutation.error !== null && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
          {mutation.error instanceof Error
            ? mutation.error.message
            : "Sign in failed. Please try again."}
        </div>
      )}
      <button
        className="w-full rounded-xl bg-ink px-5 py-3.5 font-bold text-cream shadow-card transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={mutation.isPending}
        type="submit"
      >
        {mutation.isPending ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
