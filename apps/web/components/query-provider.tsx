"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";

import { authQueryKeys } from "@/lib/auth/query-keys";
import { subscribeToSessionChanged } from "@/lib/auth/session-coordinator";

type QueryProviderProps = {
  children: ReactNode;
};

export function QueryProvider({ children }: QueryProviderProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: false,
            refetchOnWindowFocus: false,
            staleTime: 30_000,
          },
          mutations: { retry: false },
        },
      }),
  );

  useEffect(
    () => {
      const unsubscribe = subscribeToSessionChanged(() => {
        // resetQueries notifies active observers immediately, so account data
        // disappears from an already-rendered dashboard in another tab.
        void queryClient.resetQueries({ queryKey: authQueryKeys.me, exact: true });
        queryClient.getMutationCache().clear();
      });
      const revalidateVisibleSession = (): void => {
        if (document.visibilityState === "visible") {
          void queryClient.invalidateQueries({ queryKey: authQueryKeys.me, exact: true });
        }
      };
      document.addEventListener("visibilitychange", revalidateVisibleSession);
      return () => {
        unsubscribe();
        document.removeEventListener("visibilitychange", revalidateVisibleSession);
      };
    },
    [queryClient],
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
