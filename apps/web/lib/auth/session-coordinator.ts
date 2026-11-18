const AUTH_STATE_LOCK_NAME = "careerrank-auth-state";
const SESSION_EVENT_KEY = "careerrank:session-event";
const SESSION_CHANNEL_NAME = "careerrank-auth-events";
const SESSION_CHANGED_EVENT = "session-changed";

let localTransitionTail: Promise<void> = Promise.resolve();

type SessionEvent = {
  id: string;
  type: typeof SESSION_CHANGED_EVENT;
};

function asSessionEvent(value: unknown): SessionEvent | null {
  if (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof value.id === "string" &&
    "type" in value &&
    value.type === SESSION_CHANGED_EVENT
  ) {
    return { id: value.id, type: value.type };
  }
  return null;
}

function makeEventId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random()}`;
}

export function publishSessionChanged(): void {
  if (typeof window === "undefined") {
    return;
  }

  const event: SessionEvent = { id: makeEventId(), type: SESSION_CHANGED_EVENT };
  if (typeof BroadcastChannel !== "undefined") {
    try {
      const channel = new BroadcastChannel(SESSION_CHANNEL_NAME);
      channel.postMessage(event);
      channel.close();
    } catch {
      // The storage event below remains available when channels are blocked.
    }
  }
  try {
    window.localStorage.setItem(SESSION_EVENT_KEY, JSON.stringify(event));
  } catch {
    // Storage can be unavailable in restricted browser contexts. The current
    // tab still clears its QueryClient directly after logout.
  }
}

export function subscribeToSessionChanged(listener: () => void): () => void {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  let lastEventId: string | null = null;
  const notifyOnce = (sessionEvent: SessionEvent | null): void => {
    if (sessionEvent === null || sessionEvent.id === lastEventId) {
      return;
    }
    lastEventId = sessionEvent.id;
    listener();
  };
  const handleStorage = (event: StorageEvent): void => {
    if (event.key !== SESSION_EVENT_KEY || event.newValue === null) {
      return;
    }

    try {
      notifyOnce(asSessionEvent(JSON.parse(event.newValue) as unknown));
    } catch {
      // Ignore malformed values written by unrelated scripts or extensions.
    }
  };

  let channel: BroadcastChannel | null = null;
  const handleChannel = (event: MessageEvent<unknown>): void => {
    notifyOnce(asSessionEvent(event.data));
  };
  if (typeof BroadcastChannel !== "undefined") {
    try {
      channel = new BroadcastChannel(SESSION_CHANNEL_NAME);
      channel.addEventListener("message", handleChannel);
    } catch {
      channel = null;
    }
  }
  window.addEventListener("storage", handleStorage);
  return () => {
    window.removeEventListener("storage", handleStorage);
    channel?.removeEventListener("message", handleChannel);
    channel?.close();
  };
}

export function coordinateAuthState<T>(
  transition: () => Promise<T>,
  signal?: AbortSignal,
): Promise<T> {
  if (typeof navigator !== "undefined" && navigator.locks !== undefined) {
    const options: LockOptions = signal === undefined ? {} : { signal };
    const lockedTransition = navigator.locks.request<Promise<T>>(
      AUTH_STATE_LOCK_NAME,
      options,
      transition,
    );
    // The Web Locks algorithm awaits callback promises. TypeScript's DOM
    // declaration models the outer and callback promises separately, so this
    // `then` expresses the runtime flattening without an unsafe cast.
    return lockedTransition.then((response) => response);
  }

  const queued = localTransitionTail.then(transition, transition);
  localTransitionTail = queued.then(
    () => undefined,
    () => undefined,
  );
  return queued;
}
