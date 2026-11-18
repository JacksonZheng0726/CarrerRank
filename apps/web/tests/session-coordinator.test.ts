import { describe, expect, it, vi } from "vitest";

import {
  publishSessionChanged,
  subscribeToSessionChanged,
} from "@/lib/auth/session-coordinator";

class FakeBroadcastChannel {
  static readonly channels = new Set<FakeBroadcastChannel>();

  readonly name: string;
  private readonly listeners = new Set<(event: MessageEvent<unknown>) => void>();

  constructor(name: string) {
    this.name = name;
    FakeBroadcastChannel.channels.add(this);
  }

  addEventListener(
    _: "message",
    listener: (event: MessageEvent<unknown>) => void,
  ): void {
    this.listeners.add(listener);
  }

  removeEventListener(
    _: "message",
    listener: (event: MessageEvent<unknown>) => void,
  ): void {
    this.listeners.delete(listener);
  }

  postMessage(data: unknown): void {
    for (const channel of FakeBroadcastChannel.channels) {
      if (channel !== this && channel.name === this.name) {
        for (const listener of channel.listeners) {
          listener(new MessageEvent("message", { data }));
        }
      }
    }
  }

  close(): void {
    FakeBroadcastChannel.channels.delete(this);
  }
}

describe("session change coordination", () => {
  it("broadcasts when browser storage is unavailable", () => {
    vi.stubGlobal("BroadcastChannel", FakeBroadcastChannel);
    const storage = vi
      .spyOn(Storage.prototype, "setItem")
      .mockImplementation(() => {
        throw new Error("storage unavailable");
      });
    const listener = vi.fn();
    const unsubscribe = subscribeToSessionChanged(listener);

    try {
      publishSessionChanged();
      expect(listener).toHaveBeenCalledTimes(1);
    } finally {
      unsubscribe();
      storage.mockRestore();
      vi.unstubAllGlobals();
      FakeBroadcastChannel.channels.clear();
    }
  });
});
