import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, type RenderOptions } from "@testing-library/react";
import type { ReactElement, ReactNode } from "react";

export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
}

function TestQueryProvider({ children, client }: { children: ReactNode; client: QueryClient }) {

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

export function renderWithQueryClient(
  element: ReactElement,
  options?: Omit<RenderOptions, "wrapper"> & { queryClient?: QueryClient },
) {
  const { queryClient = createTestQueryClient(), ...renderOptions } = options ?? {};
  return render(element, {
    wrapper: ({ children }) => <TestQueryProvider client={queryClient}>{children}</TestQueryProvider>,
    ...renderOptions,
  });
}
