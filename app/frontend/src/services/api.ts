import type { ChatResponse, Implement, RecommendationRequest, RecommendationResponse } from "../types/api";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || data.error || "Erro de comunicacao com a API");
  }
  return data as T;
}

export const api = {
  health: () => request<{ status: string }>("/api/health"),
  stats: () =>
    request<{
      implements: Array<{ grupo: string; total: number; potencia_media: number; peso_medio: number }>;
      tractors: { total: number; potencia_min: number; potencia_max: number; potencia_media: number };
      families: Array<{ familia: string; grupo: string; total: number }>;
      model: { mae_hp: number; rmse_hp: number; training_rows: number };
    }>("/api/recommendations/dashboard"),
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
  train: () => request("/api/ml/train", { method: "POST" }),
};

