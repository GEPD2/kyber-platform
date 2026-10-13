// Typed client for the FastAPI backend. Answers never come back from these
// endpoints; the browser only learns right/wrong per gap after a submit.
import type {
  HintResult, Lang, LeaderRow, Me, Mode, ModeContent, Progress, SubmitResult,
} from "./types";

const BASE = "/api";
const TOKEN_KEY = "kyber_token";

let csrf: string | null = null;

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

function readToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function writeToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage blocked: the session lasts for this page only */
  }
}

export function isLoggedIn(): boolean {
  return readToken() !== null;
}

function headers(method: string): HeadersInit {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  const token = readToken();
  if (token) h.Authorization = `Bearer ${token}`;
  if (csrf && method !== "GET") h["X-CSRF-Token"] = csrf;
  return h;
}

async function errorMessage(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) return body.detail.map((d: { msg?: string }) => d.msg).join("; ");
  } catch {
    /* non-JSON error body */
  }
  return `HTTP ${res.status}`;
}

async function refreshAccess(): Promise<boolean> {
  const res = await fetch(`${BASE}/auth/refresh`, { method: "POST", credentials: "include" });
  if (!res.ok) return false;
  const body = await res.json();
  writeToken(body.access_token);
  return true;
}

function sendToLogin(): void {
  writeToken(null);
  csrf = null;
  if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
    window.location.assign("/login/");
  }
}

async function request<T>(path: string, method = "GET", body?: unknown, retried = false): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: headers(method),
    credentials: "include",
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (res.status === 401 && !retried && !path.startsWith("/auth/login")) {
    if (await refreshAccess()) return request<T>(path, method, body, true);
    sendToLogin();
    throw new ApiError(401, "Session expired.");
  }
  if (res.status === 403 && !retried && method !== "GET") {
    const msg = await errorMessage(res);
    if (msg.toLowerCase().includes("csrf")) {
      csrf = null;
      await ensureCsrf();
      return request<T>(path, method, body, true);
    }
    throw new ApiError(403, msg);
  }
  if (!res.ok) throw new ApiError(res.status, await errorMessage(res));
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

async function ensureCsrf(): Promise<void> {
  if (csrf) return;
  const body = await request<{ csrf_token: string }>("/auth/csrf-token");
  csrf = body.csrf_token;
}

async function mutate<T>(path: string, method: string, body?: unknown): Promise<T> {
  await ensureCsrf();
  return request<T>(path, method, body);
}

export const api = {
  async login(username: string, password: string): Promise<void> {
    const body = await request<{ access_token: string }>("/auth/login", "POST", { username, password });
    writeToken(body.access_token);
    csrf = null;
    await ensureCsrf();
  },

  register(username: string, email: string, password: string): Promise<{ message: string }> {
    return request("/auth/register", "POST", { username, email, password });
  },

  async logout(): Promise<void> {
    try {
      await request("/auth/logout", "POST", {});
    } finally {
      writeToken(null);
      csrf = null;
    }
  },

  me: () => request<Me>("/users/me"),
  changePassword: (current_password: string, new_password: string) =>
    mutate<void>("/users/me/password", "PUT", { current_password, new_password }),

  modes: () => request<Record<Mode, number>>("/challenges/modes"),
  content: (mode: Mode, lang: Lang) => request<ModeContent>(`/challenges/${mode}?lang=${lang}`),
  progress: (mode: Mode) => request<Progress>(`/challenges/progress/${mode}`),

  submit: (mode: Mode, question_id: number, answer: string, streak: number, lang: Lang) =>
    mutate<SubmitResult>("/challenges/submit", "POST", { mode, question_id, answer, streak, lang }),

  hint: (mode: Mode, question_id: number, gap: number, lang: Lang) =>
    mutate<HintResult>("/challenges/hint", "POST", { mode, question_id, gap, lang }),

  leaderboard: () => request<LeaderRow[]>("/leaderboard/global"),
};
