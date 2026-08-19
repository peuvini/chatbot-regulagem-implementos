import type {
  AuthResponse,
  ChatConversation,
  ChatConversationDetail,
  ChatResponse,
  DashboardData,
  Implement,
  LoginRequest,
  OperationPlanningRequest,
  OperationPlanningResponse,
  RecommendationRequest,
  RecommendationResponse,
  RegisterRequest,
  User,
} from "../types/api";

const apiBaseUrl = import.meta.env.VITE_API_URL?.replace(/\/$/, "") ?? "";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const token = localStorage.getItem("regulagem_implementos_token");
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${apiBaseUrl}${url}`, {
    ...init,
    headers,
  });
  const data = await response.json();
  if (!response.ok) {
    throw parseApiError(response.status, data);
  }
  return data as T;
}

export type ApiFieldError = { field: string; message: string; type: string };

export class ApiError extends Error {
  constructor(
    message: string,
    readonly code = "API_ERROR",
    readonly status = 0,
    readonly fields: ApiFieldError[] = [],
  ) {
    super(message);
    this.name = "ApiError";
  }

  fieldMessage(field: string): string | undefined {
    return this.fields.find((item) => item.field === field)?.message;
  }
}

export function parseApiError(status: number, data: { code?: unknown; message?: unknown; fields?: unknown; detail?: unknown; error?: unknown }): ApiError {
  if (typeof data.message === "string") {
    const fields = Array.isArray(data.fields)
      ? data.fields.filter((item): item is ApiFieldError => Boolean(item && typeof item === "object" && "field" in item && "message" in item && "type" in item))
      : [];
    return new ApiError(data.message, typeof data.code === "string" ? data.code : "API_ERROR", status, fields);
  }
  if (typeof data.detail === "string") return new ApiError(data.detail, "API_ERROR", status);
  if (Array.isArray(data.detail)) {
    const message = data.detail
      .map((item) => {
        if (item && typeof item === "object" && "msg" in item) return String(item.msg).replace(/^Value error,\s*/i, "");
        return String(item);
      })
      .join("; ");
    return new ApiError(message, "VALIDATION_ERROR", status);
  }
  if (typeof data.error === "string") return new ApiError(data.error, "API_ERROR", status);
  return new ApiError("Não foi possível concluir a solicitação. Tente novamente.", "API_ERROR", status);
}

export const api = {
  health: () => request<{ status: string }>("/api/health"),
  register: (payload: RegisterRequest) =>
    request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  login: (payload: LoginRequest) =>
    request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  me: (token: string) =>
    request<User>("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    }),
  stats: () => request<DashboardData>("/api/recommendations/dashboard"),
  implements: (params: URLSearchParams) => request<{ items: Implement[] }>(`/api/implements?${params.toString()}`),
  recommend: (payload: RecommendationRequest) =>
    request<RecommendationResponse>("/api/recommendations", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  chat: (message: string) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  chatInConversation: (message: string, conversationId?: number | null) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId ?? null }),
    }),
  chatConversations: () => request<ChatConversation[]>("/api/chat/conversations"),
  chatConversation: (conversationId: number) => request<ChatConversationDetail>(`/api/chat/conversations/${conversationId}`),
  planOperation: (payload: OperationPlanningRequest) =>
    request<OperationPlanningResponse>("/api/operation-planning/calculate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  train: () => request("/api/ml/train", { method: "POST" }),
};
