import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { RecommendationItem, ModelInfo, ExtendedRating, SessionResponse } from '../types';

interface AppState {
  sessionId: string | null;
  userId: number | null;
  currentModel: string;
  models: ModelInfo[];
  recommendations: RecommendationItem[];
  ratingHistory: ExtendedRating[];
  setSession: (session: SessionResponse) => void;
  setCurrentModel: (model: string) => void;
  setModels: (models: ModelInfo[]) => void;
  setRecommendations: (recommendations: RecommendationItem[]) => void;
  addRatingToHistory: (rating: ExtendedRating) => void;
  clearSession: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sessionId: null,
      userId: null,
      currentModel: 'pmf',
      models: [
        { model_type: 'pmf', model_name: 'PMF Basic', model_path: '' },
        { model_type: 'autoencoder', model_name: 'Autoencoder Deep', model_path: '' }
      ],
      recommendations: [],
      ratingHistory: [],
      setSession: (session) => set({ sessionId: session.session_id, userId: session.user_id }),
      setCurrentModel: (model) => set({ currentModel: model }),
      setModels: (models) => set({ models }),
      setRecommendations: (recommendations) => set({ recommendations }),
      addRatingToHistory: (rating) => set((state) => ({ ratingHistory: [rating, ...state.ratingHistory] })),
      clearSession: () => set({ sessionId: null, userId: null, recommendations: [], ratingHistory: [] }),
    }),
    {
      name: 'jokerec-storage',
      partialize: (state) => ({ 
        sessionId: state.sessionId, 
        userId: state.userId,
        currentModel: state.currentModel, 
        ratingHistory: state.ratingHistory 
      }),
    }
  )
);
