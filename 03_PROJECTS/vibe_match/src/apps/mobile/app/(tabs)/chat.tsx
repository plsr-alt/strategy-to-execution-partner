/**
 * チャット一覧画面
 */
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function ChatScreen() {
  // TODO: GET /v1/chats API連携 + Supabase Realtime
  return (
    <View style={styles.container}>
      <Text style={styles.title}>チャット</Text>
      <View style={styles.empty}>
        <Ionicons name="chatbubble-outline" size={64} color="#ddd" />
        <Text style={styles.emptyText}>まだメッセージがありません</Text>
        <Text style={styles.emptySubtext}>マッチした相手と会話を始めましょう</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FAFAFA', paddingTop: 60 },
  title: { fontSize: 28, fontWeight: '800', color: '#1a1a2e', paddingHorizontal: 16, marginBottom: 16 },
  empty: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  emptyText: { fontSize: 16, color: '#999', marginTop: 16 },
  emptySubtext: { fontSize: 14, color: '#bbb', marginTop: 4 },
});
