-- VibeMatch MVP: Initial Schema
-- Run this in Supabase SQL Editor

-- ============================================
-- 1. Users
-- ============================================
CREATE TABLE public.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_id UUID UNIQUE NOT NULL,          -- Supabase Auth UID
  nickname TEXT NOT NULL,
  gender TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other')),
  seeking_gender TEXT NOT NULL CHECK (seeking_gender IN ('male', 'female', 'both')),
  age INT NOT NULL CHECK (age >= 18 AND age <= 100),
  prefecture TEXT NOT NULL,
  purpose TEXT NOT NULL CHECK (purpose IN ('dating', 'marriage')),
  bio TEXT DEFAULT '',
  is_premium BOOLEAN DEFAULT FALSE,
  premium_expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ                 -- 論理削除
);

-- ============================================
-- 2. Photos
-- ============================================
CREATE TABLE public.photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  storage_path TEXT NOT NULL,            -- Supabase Storage path
  status TEXT DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processed', 'rejected', 'deleted')),
  quality_score INT,
  rejection_reason TEXT,
  sort_order INT DEFAULT 0,
  expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_photos_user_id ON public.photos(user_id);

-- ============================================
-- 3. Diagnoses (AI診断結果)
-- ============================================
CREATE TABLE public.diagnoses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  photo_ids UUID[] NOT NULL,
  model_version TEXT NOT NULL DEFAULT 'clip-vit-l-14-v1',
  overall_confidence INT NOT NULL CHECK (overall_confidence >= 0 AND overall_confidence <= 100),
  tags JSONB NOT NULL DEFAULT '[]',
  -- tags format: [{"id": "cool", "label": "クール", "prob": 0.82}, ...]
  explanation JSONB DEFAULT '[]',
  -- explanation format: [{"type": "explain", "text": "..."}, ...]
  tag_vector FLOAT8[] DEFAULT '{}',      -- 8次元ベクトル (各大カテゴリの確率)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_diagnoses_user_id ON public.diagnoses(user_id);

-- ============================================
-- 4. Likes
-- ============================================
CREATE TABLE public.likes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  from_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  to_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  mode TEXT NOT NULL CHECK (mode IN ('unified', 'complement')),
  reason_pick TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(from_user_id, to_user_id)
);

CREATE INDEX idx_likes_to_user ON public.likes(to_user_id);
CREATE INDEX idx_likes_from_user ON public.likes(from_user_id);

-- ============================================
-- 5. Matches
-- ============================================
CREATE TABLE public.matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_a UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  user_b UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  matched_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'unmatched', 'blocked')),
  UNIQUE(user_a, user_b)
);

CREATE INDEX idx_matches_user_a ON public.matches(user_a);
CREATE INDEX idx_matches_user_b ON public.matches(user_b);

-- ============================================
-- 6. Messages
-- ============================================
CREATE TABLE public.messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID NOT NULL REFERENCES public.matches(id) ON DELETE CASCADE,
  sender_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_match_id ON public.messages(match_id, created_at);

-- ============================================
-- 7. Reports (通報)
-- ============================================
CREATE TABLE public.reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id UUID NOT NULL REFERENCES public.users(id),
  target_user_id UUID NOT NULL REFERENCES public.users(id),
  category TEXT NOT NULL CHECK (category IN ('harassment', 'spam', 'fake', 'inappropriate', 'underage', 'other')),
  detail TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'actioned', 'dismissed')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 8. Blocks
-- ============================================
CREATE TABLE public.blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  blocker_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  blocked_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(blocker_id, blocked_id)
);

-- ============================================
-- 9. Skips (スキップ履歴 → 推薦除外用)
-- ============================================
CREATE TABLE public.skips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  from_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  to_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(from_user_id, to_user_id)
);

-- ============================================
-- 10. Audit Logs (監査ログ)
-- ============================================
CREATE TABLE public.audit_logs (
  id BIGSERIAL PRIMARY KEY,
  actor_id UUID,
  action TEXT NOT NULL,
  target_type TEXT,
  target_id UUID,
  detail JSONB,
  ip TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_actor ON public.audit_logs(actor_id, created_at);

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================

-- Users: 自分のデータのみ読み書き
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_select_own" ON public.users
  FOR SELECT USING (auth.uid() = auth_id);
CREATE POLICY "users_update_own" ON public.users
  FOR UPDATE USING (auth.uid() = auth_id);
CREATE POLICY "users_insert_own" ON public.users
  FOR INSERT WITH CHECK (auth.uid() = auth_id);
-- 他ユーザーのプロフィールは推薦で見えるようにする
CREATE POLICY "users_select_for_recommendations" ON public.users
  FOR SELECT USING (deleted_at IS NULL);

-- Photos: 自分の写真のみ管理
ALTER TABLE public.photos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "photos_own" ON public.photos
  FOR ALL USING (user_id IN (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- Diagnoses: 自分の診断のみ
ALTER TABLE public.diagnoses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "diagnoses_own" ON public.diagnoses
  FOR ALL USING (user_id IN (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- Likes: 自分が送ったもの
ALTER TABLE public.likes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "likes_insert_own" ON public.likes
  FOR INSERT WITH CHECK (from_user_id IN (SELECT id FROM public.users WHERE auth_id = auth.uid()));
CREATE POLICY "likes_select_own" ON public.likes
  FOR SELECT USING (
    from_user_id IN (SELECT id FROM public.users WHERE auth_id = auth.uid())
    OR to_user_id IN (SELECT id FROM public.users WHERE auth_id = auth.uid())
  );

-- Matches: 自分が含まれるマッチ
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "matches_own" ON public.matches
  FOR SELECT USING (
    user_a IN (SELECT id FROM public.users WHERE auth_id = auth.uid())
    OR user_b IN (SELECT id FROM public.users WHERE auth_id = auth.uid())
  );

-- Messages: マッチ内のメッセージ
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "messages_in_own_match" ON public.messages
  FOR ALL USING (
    match_id IN (
      SELECT id FROM public.matches
      WHERE user_a IN (SELECT id FROM public.users WHERE auth_id = auth.uid())
         OR user_b IN (SELECT id FROM public.users WHERE auth_id = auth.uid())
    )
  );

-- Reports: 自分が報告したもの
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "reports_insert_own" ON public.reports
  FOR INSERT WITH CHECK (reporter_id IN (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- Blocks: 自分が設定したもの
ALTER TABLE public.blocks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "blocks_own" ON public.blocks
  FOR ALL USING (blocker_id IN (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- Skips: 自分のスキップ
ALTER TABLE public.skips ENABLE ROW LEVEL SECURITY;

CREATE POLICY "skips_own" ON public.skips
  FOR ALL USING (from_user_id IN (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- ============================================
-- Helper Functions
-- ============================================

-- マッチ判定: 相互いいね検出 & 自動マッチ作成
CREATE OR REPLACE FUNCTION public.check_and_create_match()
RETURNS TRIGGER AS $$
DECLARE
  mutual_exists BOOLEAN;
  new_match_id UUID;
BEGIN
  -- 相手から自分へのいいねがあるか
  SELECT EXISTS(
    SELECT 1 FROM public.likes
    WHERE from_user_id = NEW.to_user_id
      AND to_user_id = NEW.from_user_id
  ) INTO mutual_exists;

  IF mutual_exists THEN
    -- user_a < user_b で正規化（重複防止）
    INSERT INTO public.matches (user_a, user_b)
    VALUES (
      LEAST(NEW.from_user_id, NEW.to_user_id),
      GREATEST(NEW.from_user_id, NEW.to_user_id)
    )
    ON CONFLICT (user_a, user_b) DO NOTHING;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trigger_check_match
  AFTER INSERT ON public.likes
  FOR EACH ROW
  EXECUTE FUNCTION public.check_and_create_match();

-- updated_at 自動更新
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at();
