import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => {
  cleanup();
  document.cookie = "careerrank_csrf=; Max-Age=0; Path=/";
  document.cookie = "__Host-careerrank_csrf=; Max-Age=0; Secure; Path=/";
  window.localStorage.clear();
});
