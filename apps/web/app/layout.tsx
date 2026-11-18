import type { Metadata } from "next";
import type { ReactNode } from "react";

import { QueryProvider } from "@/components/query-provider";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: {
    default: "CareerRank",
    template: "%s | CareerRank",
  },
  description: "Outcome-driven job search intelligence.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
