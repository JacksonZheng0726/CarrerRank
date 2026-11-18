import { z } from "zod";

const passwordSchema = z
  .string()
  .min(12, "Password must be at least 12 characters")
  .max(128, "Password must be at most 128 characters");

export const loginSchema = z
  .object({
    email: z.string().trim().email("Enter a valid email address"),
    password: passwordSchema,
  })
  .strict();

export const registerSchema = z
  .object({
    email: z.string().trim().email("Enter a valid email address"),
    password: passwordSchema,
    confirmPassword: z.string(),
  })
  .strict()
  .refine((value) => value.password === value.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
