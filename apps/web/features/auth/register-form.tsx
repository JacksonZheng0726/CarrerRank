"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import { FormField } from "@/features/auth/form-field";
import { register as registerAccount } from "@/lib/api/auth";
import { authQueryKeys } from "@/lib/auth/query-keys";
import { registerSchema, type RegisterInput } from "@/lib/auth/schemas";

export function RegisterForm() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", password: "", confirmPassword: "" },
  });
  const mutation = useMutation({
    mutationFn: registerAccount,
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
        id="register-email"
        inputMode="email"
        label="Email address"
        placeholder="you@example.com"
        type="email"
        {...register("email")}
      />
      <FormField
        autoComplete="new-password"
        error={errors.password?.message}
        id="register-password"
        label="Password"
        type="password"
        {...register("password")}
      />
      <p className="-mt-3 text-xs leading-5 text-ink/50">Use 12–128 characters.</p>
      <FormField
        autoComplete="new-password"
        error={errors.confirmPassword?.message}
        id="confirm-password"
        label="Confirm password"
        type="password"
        {...register("confirmPassword")}
      />
      {mutation.error !== null && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
          {mutation.error instanceof Error
            ? mutation.error.message
            : "Account creation failed. Please try again."}
        </div>
      )}
      <button
        className="w-full rounded-xl bg-ink px-5 py-3.5 font-bold text-cream shadow-card transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={mutation.isPending}
        type="submit"
      >
        {mutation.isPending ? "Creating account…" : "Create account"}
      </button>
    </form>
  );
}
