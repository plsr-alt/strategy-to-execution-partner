/**
 * ログイン画面
 * Apple / Google サインイン
 */
import { View, Text, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import * as AppleAuthentication from 'expo-apple-authentication';
import { supabase } from '../../lib/supabase';

export default function LoginScreen() {
  const handleAppleSignIn = async () => {
    try {
      const credential = await AppleAuthentication.signInAsync({
        requestedScopes: [
          AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
          AppleAuthentication.AppleAuthenticationScope.EMAIL,
        ],
      });

      if (credential.identityToken) {
        const { error } = await supabase.auth.signInWithIdToken({
          provider: 'apple',
          token: credential.identityToken,
        });
        if (error) console.error('Apple sign-in error:', error.message);
      }
    } catch (e: any) {
      if (e.code !== 'ERR_REQUEST_CANCELED') {
        console.error('Apple auth error:', e);
      }
    }
  };

  const handleGoogleSignIn = async () => {
    // Google OAuth は Supabase の signInWithOAuth で実装
    // Expo AuthSession と連携
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
    });
    if (error) console.error('Google sign-in error:', error.message);
  };

  return (
    <View style={styles.container}>
      {/* ロゴ & タイトル */}
      <View style={styles.header}>
        <Text style={styles.title}>VibeMatch</Text>
        <Text style={styles.subtitle}>雰囲気で、出会う。</Text>
      </View>

      {/* オンボーディングメッセージ */}
      <View style={styles.features}>
        <Text style={styles.feature}>✨ 似てる判定はしません</Text>
        <Text style={styles.feature}>🎨 雰囲気タグで相性を診断</Text>
        <Text style={styles.feature}>🔀 統一感 / 補完の2モードで探索</Text>
      </View>

      {/* ログインボタン */}
      <View style={styles.buttons}>
        {Platform.OS === 'ios' && (
          <AppleAuthentication.AppleAuthenticationButton
            buttonType={AppleAuthentication.AppleAuthenticationButtonType.SIGN_IN}
            buttonStyle={AppleAuthentication.AppleAuthenticationButtonStyle.BLACK}
            cornerRadius={12}
            style={styles.appleButton}
            onPress={handleAppleSignIn}
          />
        )}

        <TouchableOpacity style={styles.googleButton} onPress={handleGoogleSignIn}>
          <Text style={styles.googleText}>Googleでサインイン</Text>
        </TouchableOpacity>
      </View>

      {/* フッター */}
      <Text style={styles.terms}>
        サインインすることで、利用規約とプライバシーポリシーに同意します
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  title: {
    fontSize: 42,
    fontWeight: '800',
    color: '#1a1a2e',
    letterSpacing: -1,
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
    marginTop: 8,
  },
  features: {
    marginBottom: 48,
    gap: 12,
  },
  feature: {
    fontSize: 16,
    color: '#444',
    textAlign: 'center',
  },
  buttons: {
    width: '100%',
    gap: 12,
  },
  appleButton: {
    width: '100%',
    height: 52,
  },
  googleButton: {
    width: '100%',
    height: 52,
    backgroundColor: '#f1f1f1',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  googleText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  terms: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    marginTop: 32,
    paddingHorizontal: 16,
  },
});
