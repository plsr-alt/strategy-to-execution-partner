/**
 * プロフィール & 設定画面
 */
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { supabase } from '../../lib/supabase';
import { useAppStore } from '../../lib/store';

export default function ProfileScreen() {
  const { profile, diagnosisTags, diagnosisConfidence } = useAppStore();

  const handleSignOut = () => {
    Alert.alert('ログアウト', 'ログアウトしますか？', [
      { text: 'キャンセル', style: 'cancel' },
      {
        text: 'ログアウト',
        style: 'destructive',
        onPress: () => supabase.auth.signOut(),
      },
    ]);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>プロフィール</Text>

      {/* 印象タグ表示 */}
      {diagnosisTags.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>あなたの印象タグ</Text>
          <View style={styles.tagRow}>
            {diagnosisTags.map((tag) => (
              <View key={tag.id} style={styles.tagChip}>
                <Text style={styles.tagText}>{tag.label}</Text>
                <Text style={styles.tagProb}>{Math.round(tag.prob * 100)}%</Text>
              </View>
            ))}
          </View>
          {diagnosisConfidence > 0 && (
            <Text style={styles.confidence}>
              診断信頼度: {diagnosisConfidence}%
            </Text>
          )}
        </View>
      )}

      {/* 基本情報 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>基本情報</Text>
        <Text style={styles.info}>{profile?.nickname || '未設定'}</Text>
        <Text style={styles.info}>{profile?.age || '-'}歳 / {profile?.prefecture || '-'}</Text>
        <Text style={styles.info}>
          目的: {profile?.purpose === 'dating' ? '恋活' : profile?.purpose === 'marriage' ? '婚活' : '-'}
        </Text>
      </View>

      {/* メニュー */}
      <View style={styles.menu}>
        <MenuItem icon="camera-outline" label="写真を変更" onPress={() => {/* TODO */}} />
        <MenuItem icon="refresh-outline" label="印象タグを再診断" onPress={() => {/* TODO */}} />
        <MenuItem icon="shield-checkmark-outline" label="通報履歴" onPress={() => {/* TODO */}} />
        <MenuItem icon="trash-outline" label="画像データを削除" onPress={() => {/* TODO */}} />
        <MenuItem icon="log-out-outline" label="ログアウト" onPress={handleSignOut} danger />
      </View>
    </View>
  );
}

function MenuItem({
  icon,
  label,
  onPress,
  danger,
}: {
  icon: string;
  label: string;
  onPress: () => void;
  danger?: boolean;
}) {
  return (
    <TouchableOpacity style={styles.menuItem} onPress={onPress}>
      <Ionicons name={icon as any} size={22} color={danger ? '#FF6B6B' : '#555'} />
      <Text style={[styles.menuText, danger && { color: '#FF6B6B' }]}>{label}</Text>
      <Ionicons name="chevron-forward" size={18} color="#ccc" />
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FAFAFA', paddingTop: 60 },
  title: { fontSize: 28, fontWeight: '800', color: '#1a1a2e', paddingHorizontal: 16, marginBottom: 16 },

  section: { backgroundColor: '#fff', marginHorizontal: 16, borderRadius: 12, padding: 16, marginBottom: 12 },
  sectionTitle: { fontSize: 14, fontWeight: '600', color: '#999', marginBottom: 8 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  tagChip: {
    flexDirection: 'row',
    backgroundColor: '#F0EEFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 4,
  },
  tagText: { fontSize: 13, color: '#6C5CE7', fontWeight: '600' },
  tagProb: { fontSize: 12, color: '#A29BFE' },
  confidence: { fontSize: 12, color: '#999', marginTop: 8 },
  info: { fontSize: 16, color: '#333', marginBottom: 4 },

  menu: { marginHorizontal: 16, backgroundColor: '#fff', borderRadius: 12, overflow: 'hidden' },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 0.5,
    borderBottomColor: '#f0f0f0',
    gap: 12,
  },
  menuText: { fontSize: 16, color: '#333', flex: 1 },
});
