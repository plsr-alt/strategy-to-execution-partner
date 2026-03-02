/**
 * Zustand グローバルステート管理
 */
import { create } from 'zustand';

// ============================================
// ユーザー情報
// ============================================
interface UserProfile {
  id: string;
  nickname: string;
  gender: string;
  seekingGender: string;
  age: number;
  prefecture: string;
  purpose: 'dating' | 'marriage';
  bio: string;
}

interface DiagnosisTag {
  id: string;
  label: string;
  prob: number;
  category: string;
}

// ============================================
// Store
// ============================================
interface AppState {
  // Auth
  isAuthenticated: boolean;
  userId: string | null;
  setAuth: (userId: string) => void;
  clearAuth: () => void;

  // Profile
  profile: UserProfile | null;
  setProfile: (profile: UserProfile) => void;

  // Diagnosis
  diagnosisTags: DiagnosisTag[];
  diagnosisConfidence: number;
  tagVector: number[];
  setDiagnosis: (tags: DiagnosisTag[], confidence: number, vector: number[]) => void;

  // Explore mode
  exploreMode: 'unified' | 'complement';
  setExploreMode: (mode: 'unified' | 'complement') => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Auth
  isAuthenticated: false,
  userId: null,
  setAuth: (userId) => set({ isAuthenticated: true, userId }),
  clearAuth: () => set({ isAuthenticated: false, userId: null, profile: null }),

  // Profile
  profile: null,
  setProfile: (profile) => set({ profile }),

  // Diagnosis
  diagnosisTags: [],
  diagnosisConfidence: 0,
  tagVector: [],
  setDiagnosis: (tags, confidence, vector) =>
    set({ diagnosisTags: tags, diagnosisConfidence: confidence, tagVector: vector }),

  // Explore
  exploreMode: 'unified',
  setExploreMode: (mode) => set({ exploreMode: mode }),
}));
