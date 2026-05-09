export interface Joke {
  joke_id: number;
  joke_text: string;
  category?: string;
}

export interface SessionResponse {
  session_id: string;
  user_id: number;
  created_at: string;
  last_active_at: string;
  is_active: boolean;
}

export interface RatingCreateRequest {
  session_id: string;
  user_id: number;
  joke_id: number;
  rating: number;
}

export interface RatingResponse {
  user_id: number;
  joke_id: number;
  rating: number;
  created_at: string;
  updated_at: string;
}

export interface UserRatingsResponse {
  user_id: number;
  ratings: RatingResponse[];
}

export interface RecommendationItem {
  joke_id: number;
  predicted_rating: number;
  rank: number;
  joke_text: string;
}

export interface RecommendationResponse {
  user_id: number;
  model: string;
  top_k: int;
  recommendations: RecommendationItem[];
  generated_at: string;
}

export interface ModelInfo {
  model_type: string;
  model_name: string;
  model_path: string;
  created_at?: string | null;
  metrics?: Record<string, unknown> | null;
}

export interface ModelsListResponse {
  models: ModelInfo[];
  default_model: string;
}

// Global App State Type Additions
export interface ExtendedRating extends RatingResponse {
  joke?: Joke;
}
