import { forwardRef, type ComponentPropsWithoutRef } from "react";

type FormFieldProps = ComponentPropsWithoutRef<"input"> & {
  label: string;
  error?: string;
};

export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(function FormField(
  { id, label, error, ...inputProps },
  ref,
) {
  const errorId = error === undefined ? undefined : `${id}-error`;

  return (
    <div>
      <label className="mb-2 block text-sm font-bold" htmlFor={id}>
        {label}
      </label>
      <input
        {...inputProps}
        aria-describedby={errorId}
        aria-invalid={error !== undefined}
        className="w-full rounded-xl border border-ink/15 bg-cream/45 px-4 py-3 text-base text-ink shadow-sm transition-colors placeholder:text-ink/35 hover:border-moss/45 focus:border-moss focus:bg-white focus:outline-none"
        id={id}
        ref={ref}
      />
      {error !== undefined && (
        <p className="mt-2 text-sm font-medium text-red-700" id={errorId} role="alert">
          {error}
        </p>
      )}
    </div>
  );
});
