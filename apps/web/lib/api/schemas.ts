import { z } from "zod";

const dateTimeSchema = z.string().datetime({ offset: true });

export const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  created_at: dateTimeSchema,
});

export const candidateProfileSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  headline: z.string().nullable(),
  years_experience: z.number().nonnegative().nullable(),
  preferred_roles: z.array(z.string()),
  preferred_locations: z.array(z.string()),
  work_authorization: z.record(z.string(), z.unknown()),
  remote_preference: z.string().nullable(),
  created_at: dateTimeSchema,
  updated_at: dateTimeSchema,
});

export const authResponseSchema = z.object({
  user: userSchema,
});

export const meResponseSchema = authResponseSchema.extend({
  candidate_profile: candidateProfileSchema,
});

export type User = z.infer<typeof userSchema>;
export type CandidateProfile = z.infer<typeof candidateProfileSchema>;
export type AuthResponse = z.infer<typeof authResponseSchema>;
export type MeResponse = z.infer<typeof meResponseSchema>;
