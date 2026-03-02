/**
 * マッチ一覧画面
 */
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function MatchesScreen() {
  // TODO: GET /v1/matches API連携
  return (
    <View style={styles.container}>
      <Text style={styles.title}>マッチ</Text>
      <View style={styles.empty}>
        <Ionicons name="heart-outline" size={64} color="#ddd" />
        <Text style={styles.emptyText}>まだマッチがありません</Text>
        <Text style={styles.emptySubtext}>探索画面でいいねを送ってみましょう</Text>
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
