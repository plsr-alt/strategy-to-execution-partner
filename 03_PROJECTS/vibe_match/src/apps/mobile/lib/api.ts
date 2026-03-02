/**
 * VibeMatch API クライアント
 */

const AI_API_URL = process.env.EXPO_PUBLIC_AI_API_URL || 'http://localhost:8000';

// ============================================
// AI診断 API
// ============================================
export interface DiagnosisResult {
  diagnosis_id: string;
  overall_confidence: number;
  tags: Array<{
    id: string;
    label: string;
    prob: number;
    category: string;
  }>;
  explanation: Array<{
    type: string;
    text: string;
  }>;
  tag_vector: number[];
  quality_score: number;
  quality_issues: string[];
  quality_suggestions: string[];
  guardrails: Record<string, string>;
  processing_time_ms: number;
}

export async function diagnosePhoto(photoUri: string): Promise<DiagnosisResult> {
  const formData = new FormData();

  // React Native の FormData に画像を追加
  formData.append('photo', {
    uri: photoUri,
    type: 'image/jpeg',
    name: 'photo.jpg',
  } as any);

  const response = await fetch(`${AI_API_URL}/v1/face/diagnose`, {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Diagnosis failed');
  }

  return response.json();
}

// ============================================
// 推薦 API (Supabase Edge Function or App Server)
// ============================================
export interface RecommendationCard {
  user_id: string;
  nickname: string;
  age: number;
  prefecture: string;
  photo_url: string;
  compat_score: number;
  reasons: string[];
  tags_preview: string[];
}

export interface RecommendationsResponse {
  mode: 'unified' | 'complement';
  cards: RecommendationCard[];
  next_cursor: string | null;
}
