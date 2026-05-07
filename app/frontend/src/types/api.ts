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
  answer: string;
  parsed_payload: RecommendationRequest;
  recommendations: RecommendationItem[];
};

