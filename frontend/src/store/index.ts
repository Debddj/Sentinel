// Global state management with Zustand
import { create } from 'zustand';

interface AppState {
  isAuthenticated: boolean;
  alerts: [];
  models: [];
}

export const useStore = create<AppState>((set) => ({
  isAuthenticated: false,
  alerts: [],
  models: [],
}));
