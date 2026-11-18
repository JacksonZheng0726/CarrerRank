import type { z } from "zod";

type RequestOptions<T> = RequestInit & {
  schema: z.ZodType<T>;
};

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function validationMessage(detail: unknown): string | null {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (
          typeof item === "object" &&
          item !== null &&
          "msg" in item &&
          typeof item.msg === "string"
        ) {
          return item.msg;
        }
        return null;
      })
      .filter((item): item is string => item !== null);

    return messages.length > 0 ? messages.join(". ") : null;
  }

  return null;
}

async function errorFromResponse(response: Response): Promise<ApiError> {
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  const detail =
    typeof payload === "object" && payload !== null && "detail" in payload
      ? validationMessage(payload.detail)
      : null;

  return new ApiError(
    response.status,
    detail ?? "The request could not be completed. Please try again.",
  );
}

function requestHeaders(init: RequestInit): Headers {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return headers;
}

export async function requestJson<T>(
  path: string,
  { schema, ...init }: RequestOptions<T>,
): Promise<T> {
  const response = await fetch(path, {
    ...init,
    credentials: "include",
    headers: requestHeaders(init),
    cache: "no-store",
  });

  if (!response.ok) {
    throw await errorFromResponse(response);
  }

  const payload: unknown = await response.json();
  const parsed = schema.safeParse(payload);
  if (!parsed.success) {
    throw new ApiError(502, "The server returned an unexpected response.");
  }
  return parsed.data;
}

export async function requestWithoutBody(
  path: string,
  init: RequestInit,
): Promise<void> {
  const response = await fetch(path, {
    ...init,
    credentials: "include",
    headers: requestHeaders(init),
    cache: "no-store",
  });

  if (!response.ok) {
    throw await errorFromResponse(response);
  }
}
