/**
 * VibeMatch ルートレイアウト
 * 認証状態に応じて (auth) or (tabs) にルーティング
 */
import { Stack } from 'expo-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { useAppStore } from '../lib/store';

const queryClient = new QueryClient();

export default function RootLayout() {
  const { isAuthenticated, setAuth, clearAuth } = useAppStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // セッション復元
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setAuth(session.user.id);
      }
      setLoading(false);
    });

    // Auth状態変化リスナー
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (session?.user) {
          setAuth(session.user.id);
        } else {
          clearAuth();
        }
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  if (loading) return null;

  return (
    <QueryClientProvider client={queryClient}>
      <Stack screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="(tabs)" />
        ) : (
          <Stack.Screen name="(auth)" />
        )}
      </Stack>
    </QueryClientProvider>
  );
}
