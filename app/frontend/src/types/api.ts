export type Implement = {
  id: number;
  grupo: string;
  familia?: string | null;
  descricao?: string | null;
  modelo?: string | null;
  n_discos?: number | null;
  largura_mm?: number | null;
  peso_medio_kg?: number | null;
  potencia_min_hp?: number | null;
  potencia_max_hp?: number | null;
  potencia_media_hp?: number | null;
  fonte_imagem?: string | null;
};

export type RecommendationRequest = {
  implement_type?: string;
  family?: string;
  tractor_power_hp?: number;
  soil_texture?: string;
  moisture?: string;
  crop?: string;
  slope?: string;
  limit?: number;
};

export type RecommendationItem = {
  score: number;
  reasons: string[];
  ml_predicted_power_hp: number;
  technical_note: string;
  implement: Implement;
};

export type RecommendationResponse = {
  model_metrics: {
    mae_hp: number;
    rmse_hp: number;
    training_rows: number;
  };
  count: number;
  recommendations: RecommendationItem[];
};

export type ChatResponse = {
  conversation_id: number;
  answer: string;
  response_type: "guidance" | "clarification" | "recommendation" | "no_match";
  parsed_payload: RecommendationRequest;
  recommendations: RecommendationItem[];
};

export type ChatConversation = {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  metadata_json?: Record<string, unknown> | null;
};

export type ChatConversationDetail = ChatConversation & {
  messages: ChatMessage[];
};

export type User = {
  id: number;
  name: string;
  email: string;
  cpf: string;
  role: "admin" | "user";
  is_active: boolean;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  user: User;
};

export type RegisterRequest = {
  name: string;
  email: string;
  cpf: string;
  password: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type DashboardData = {
  implements: Array<{ grupo: string; total: number; potencia_media: number; peso_medio: number }>;
  tractors: { total: number; potencia_min: number; potencia_max: number; potencia_media: number };
  families: Array<{ familia: string; grupo: string; total: number }>;
  model: { mae_hp: number; rmse_hp: number; training_rows: number };
  scientific: {
    data_quality: {
      total_implements: number;
      complete_rows: number;
      complete_rows_percent: number;
      completeness: Array<{ field: string; label: string; filled: number; missing: number; percent: number }>;
    };
    power_ranges: Array<{ label: string; count: number; percent: number }>;
    tractor_power_ranges: Array<{ label: string; count: number; percent: number }>;
    ml_readiness: {
      training_coverage_percent: number;
      relative_mae_percent: number;
      feature_count: number;
      target: string;
    };
    recommendation_usage: {
      total_recommendations: number;
      avg_top_score: number;
      avg_returned_items: number;
      top_requested_soils: Array<{ label: string; count: number; percent: number }>;
      top_requested_implements: Array<{ label: string; count: number; percent: number }>;
      top_recommended_groups: Array<{ label: string; count: number; percent: number }>;
    };
    validation_checklist: Array<{ label: string; status: boolean; detail: string }>;
  };
};

export type OperationPlanningRequest = {
  area_ha: number;
  start_date: string;
  end_date: string;
  hours_per_day?: number;
};

export type TimeDistribution = {
  days: number;
  hours_per_day: number;
  total_available_hours: number;
  plow_hours: number;
  harrow_total_hours: number;
  harrow_breaking_hours: number;
  harrow_leveling_hours: number;
};

export type OperationSizing = {
  key: string;
  name: string;
  area_factor: number;
  area_considered_ha: number;
  available_hours: number;
  speed_kmh: number;
  field_efficiency: number;
  operational_rhythm_ha_h: number;
  required_width_m: number;
  selected_width_m?: number | null;
  required_power_hp?: number | null;
  equipment_count: number;
  implement?: Implement | null;
  tractor?: {
    id: number;
    nome?: string | null;
    potencia_hp?: number | null;
    peso_kg?: number | null;
    tracao?: string | null;
    tdp?: string | null;
    tipo_transmissao?: string | null;
  } | null;
  formula: string;
  notes: string[];
};

export type OperationPlanningResponse = {
  input: OperationPlanningRequest;
  time_distribution: TimeDistribution;
  operations: OperationSizing[];
  final_report: string[];
  formulas: string[];
};
