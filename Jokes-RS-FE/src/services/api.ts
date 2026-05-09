import axios from 'axios';
import { 
  SessionResponse, 
  RecommendationResponse, 
  RatingCreateRequest, 
  RatingResponse, 
  ModelsListResponse,
  UserRatingsResponse
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createSession = async (): Promise<SessionResponse> => {
  const response = await api.post<SessionResponse>('/sessions', {});
  return response.data;
};

export const getRecommendations = async (userId: number, model: string = 'pmf', topK: number = 10): Promise<RecommendationResponse> => {
  const response = await api.get<RecommendationResponse>(`/recommendations/${userId}?model=${model}&top_k=${topK}`);
  return response.data;
};

export const submitRating = async (request: RatingCreateRequest): Promise<RatingResponse> => {
  const response = await api.post<RatingResponse>('/ratings', request);
  return response.data;
};

export const getModels = async (): Promise<ModelsListResponse> => {
  const response = await api.get<ModelsListResponse>('/models');
  return response.data;
};

export const getRating = async (userId: number, jokeId: number): Promise<RatingResponse | null> => {
  try {
    const response = await api.get<RatingResponse>(`/ratings/${userId}/${jokeId}`);
    return response.data;
  } catch {
    return null;
  }
};

export const getUserRatings = async (userId: number): Promise<UserRatingsResponse> => {
  const response = await api.get<UserRatingsResponse>(`/ratings/${userId}`);
  return response.data;
};

export default api;
