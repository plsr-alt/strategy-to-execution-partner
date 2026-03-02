/**
 * 探索画面（メイン）
 * 推薦カード + 統一感/補完モード切替 + いいね/スキップ
 */
import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Dimensions,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../../lib/store';

const { width } = Dimensions.get('window');
const CARD_WIDTH = width - 32;

// TODO: API連携後に実データに置き換え
const MOCK_CARDS = [
  {
    user_id: 'u_001',
    nickname: 'みお',
    age: 24,
    prefecture: '東京',
    photo_url: 'https://via.placeholder.com/400x500',
    compat_score: 85,
    reasons: [
      '落ち着いた雰囲気同士で統一感が出やすい',
      '清潔感寄りの印象タグが近い',
      '活動時間帯が近く会話が続きやすい傾向',
    ],
    tags_preview: ['フレッシュ', 'ナチュラル'],
  },
  {
    user_id: 'u_002',
    nickname: 'ゆうた',
    age: 27,
    prefecture: '大阪',
    photo_url: 'https://via.placeholder.com/400x500',
    compat_score: 78,
    reasons: [
      'クール × ウォームの補完で映える組み合わせ',
      '対比が新鮮な印象を与える',
      '趣味の傾向が近い',
    ],
    tags_preview: ['クール', '知的クール'],
  },
];

export default function ExploreScreen() {
  const { exploreMode, setExploreMode } = useAppStore();
  const [currentIndex, setCurrentIndex] = useState(0);

  const currentCard = MOCK_CARDS[currentIndex];

  const handleLike = () => {
    // TODO: POST /v1/likes API
    if (currentIndex < MOCK_CARDS.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handleSkip = () => {
    // TODO: POST /v1/skips API
    if (currentIndex < MOCK_CARDS.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  if (!currentCard) {
    return (
      <View style={styles.emptyContainer}>
        <Ionicons name="search-outline" size={64} color="#ccc" />
        <Text style={styles.emptyText}>新しい推薦を準備中...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* モード切替 */}
      <View style={styles.modeToggle}>
        <TouchableOpacity
          style={[styles.modeButton, exploreMode === 'unified' && styles.modeActive]}
          onPress={() => setExploreMode('unified')}
        >
          <Text style={[styles.modeText, exploreMode === 'unified' && styles.modeTextActive]}>
            統一感
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.modeButton, exploreMode === 'complement' && styles.modeActive]}
          onPress={() => setExploreMode('complement')}
        >
          <Text style={[styles.modeText, exploreMode === 'complement' && styles.modeTextActive]}>
            補完
          </Text>
        </TouchableOpacity>
      </View>

      {/* 推薦カード */}
      <ScrollView style={styles.cardScroll} showsVerticalScrollIndicator={false}>
        <View style={styles.card}>
          {/* 写真 */}
          <Image source={{ uri: currentCard.photo_url }} style={styles.cardImage} />

          {/* 基本情報 */}
          <View style={styles.cardInfo}>
            <Text style={styles.cardName}>
              {currentCard.nickname}, {currentCard.age}
            </Text>
            <Text style={styles.cardLocation}>
              <Ionicons name="location-outline" size={14} color="#999" />{' '}
              {currentCard.prefecture}
            </Text>
          </View>

          {/* タグ */}
          <View style={styles.tagRow}>
            {currentCard.tags_preview.map((tag, i) => (
              <View key={i} style={styles.tagChip}>
                <Text style={styles.tagText}>{tag}</Text>
              </View>
            ))}
            <View style={styles.compatChip}>
              <Text style={styles.compatText}>{currentCard.compat_score}%</Text>
            </View>
          </View>

          {/* 相性理由 */}
          <View style={styles.reasons}>
            {currentCard.reasons.map((reason, i) => (
              <View key={i} style={styles.reasonRow}>
                <Ionicons name="checkmark-circle" size={16} color="#6C5CE7" />
                <Text style={styles.reasonText}>{reason}</Text>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* アクションボタン */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.skipButton} onPress={handleSkip}>
          <Ionicons name="close" size={32} color="#FF6B6B" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.likeButton} onPress={handleLike}>
          <Ionicons name="heart" size={32} color="#fff" />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FAFAFA' },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  emptyText: { fontSize: 16, color: '#999', marginTop: 16 },

  // Mode toggle
  modeToggle: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingTop: 60,
    paddingBottom: 12,
    gap: 8,
  },
  modeButton: {
    paddingHorizontal: 24,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
  },
  modeActive: { backgroundColor: '#6C5CE7' },
  modeText: { fontSize: 14, fontWeight: '600', color: '#666' },
  modeTextActive: { color: '#fff' },

  // Card
  cardScroll: { flex: 1, paddingHorizontal: 16 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    marginBottom: 16,
  },
  cardImage: { width: CARD_WIDTH, height: CARD_WIDTH * 1.2, backgroundColor: '#eee' },
  cardInfo: { padding: 16, paddingBottom: 8 },
  cardName: { fontSize: 22, fontWeight: '700', color: '#1a1a2e' },
  cardLocation: { fontSize: 14, color: '#999', marginTop: 4 },

  // Tags
  tagRow: { flexDirection: 'row', paddingHorizontal: 16, gap: 8, flexWrap: 'wrap' },
  tagChip: {
    backgroundColor: '#F0EEFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  tagText: { fontSize: 13, color: '#6C5CE7', fontWeight: '600' },
  compatChip: {
    backgroundColor: '#6C5CE7',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  compatText: { fontSize: 13, color: '#fff', fontWeight: '700' },

  // Reasons
  reasons: { padding: 16, gap: 8 },
  reasonRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 8 },
  reasonText: { fontSize: 14, color: '#555', flex: 1, lineHeight: 20 },

  // Actions
  actions: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingBottom: 32,
    gap: 32,
  },
  skipButton: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  likeButton: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#6C5CE7',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#6C5CE7',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
});
