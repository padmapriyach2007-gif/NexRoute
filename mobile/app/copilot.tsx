import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, FlatList, SafeAreaView, KeyboardAvoidingView, Platform } from 'react-native';
import { copilotApi, ChatMessage } from '../src/services/api/copilotApi';
import { colors } from '../src/theme/colors';
import { tokens } from '../src/theme/tokens';
import { t, getLanguage } from '../src/i18n';

export default function CopilotScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'aura',
      text: t('aura.greeting'),
      timestamp: Date.now(),
      suggestions: [
        'Plan a 1-day city journey',
        'Estimate trip fuel budget',
        'Compare fastest vs eco route',
        'Suggest wheelchair-accessible destinations'
      ]
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (textToSend?: string) => {
    const prompt = (textToSend || inputText).trim();
    if (!prompt || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: 'user',
      text: prompt,
      timestamp: Date.now()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);

    try {
      const auraReply = await copilotApi.sendMessage(prompt, messages, getLanguage());
      setMessages((prev) => [...prev, auraReply]);
    } catch {
      // Ignored
    } finally {
      setIsLoading(false);
    }
  };

  const renderItem = ({ item }: { item: ChatMessage }) => {
    const isUser = item.sender === 'user';
    return (
      <View style={[styles.messageBubble, isUser ? styles.userBubble : styles.auraBubble]}>
        {!isUser && (
          <View style={styles.auraHeader}>
            <Text style={styles.auraEmblem}>✨</Text>
            <Text style={styles.auraLabel}>AURA AI Copilot</Text>
          </View>
        )}
        <Text style={[styles.messageText, isUser ? styles.userText : styles.auraText]}>
          {item.text}
        </Text>

        {item.suggestions && item.suggestions.length > 0 && (
          <View style={styles.suggestionsContainer}>
            {item.suggestions.map((s, idx) => (
              <TouchableOpacity
                key={idx}
                onPress={() => handleSend(s)}
                style={styles.suggestionChip}
              >
                <Text style={styles.suggestionText}>{s}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <FlatList
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
        />

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            placeholder={t('copilot.placeholder')}
            placeholderTextColor={colors.textMuted}
            value={inputText}
            onChangeText={setInputText}
            onSubmitEditing={() => handleSend()}
            returnKeyType="send"
          />
          <TouchableOpacity
            activeOpacity={0.8}
            onPress={() => handleSend()}
            disabled={!inputText.trim() || isLoading}
            style={[
              styles.sendButton,
              (!inputText.trim() || isLoading) && styles.sendButtonDisabled
            ]}
          >
            <Text style={styles.sendButtonText}>➔</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.background
  },
  container: {
    flex: 1
  },
  listContent: {
    padding: tokens.spacing.md,
    gap: 12
  },
  messageBubble: {
    maxWidth: '85%',
    borderRadius: tokens.radii.lg,
    padding: tokens.spacing.md,
    ...tokens.elevation.card
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: 'rgba(2, 132, 199, 0.45)',
    borderWidth: 1.5,
    borderColor: colors.cyan
  },
  auraBubble: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(15, 23, 42, 0.92)',
    borderWidth: 1.5,
    borderColor: colors.violet
  },
  auraHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 6
  },
  auraEmblem: {
    fontSize: 14
  },
  auraLabel: {
    fontSize: 11,
    fontWeight: '800',
    color: colors.violet,
    letterSpacing: 0.5,
    textTransform: 'uppercase'
  },
  messageText: {
    fontSize: 14,
    lineHeight: 20
  },
  userText: {
    color: '#ffffff',
    fontWeight: '600'
  },
  auraText: {
    color: colors.textSecondary,
    fontWeight: '500'
  },
  suggestionsContainer: {
    marginTop: 10,
    gap: 6
  },
  suggestionChip: {
    backgroundColor: 'rgba(168, 85, 247, 0.15)',
    borderWidth: 1,
    borderColor: 'rgba(168, 85, 247, 0.40)',
    borderRadius: tokens.radii.full,
    paddingHorizontal: 12,
    paddingVertical: 6,
    alignSelf: 'flex-start'
  },
  suggestionText: {
    fontSize: 12,
    color: '#e9d5ff',
    fontWeight: '600'
  },
  inputContainer: {
    flexDirection: 'row',
    padding: tokens.spacing.md,
    backgroundColor: 'rgba(8, 18, 36, 0.98)',
    borderTopWidth: 1.5,
    borderTopColor: colors.borderCyan,
    gap: 8,
    alignItems: 'center'
  },
  textInput: {
    flex: 1,
    minHeight: 44,
    backgroundColor: colors.backgroundCard,
    borderWidth: 1.5,
    borderColor: colors.borderCyan,
    borderRadius: tokens.radii.md,
    paddingHorizontal: 12,
    color: '#ffffff',
    fontSize: 14
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.cyanMuted,
    borderWidth: 1.5,
    borderColor: colors.cyan,
    alignItems: 'center',
    justifyContent: 'center'
  },
  sendButtonDisabled: {
    opacity: 0.4
  },
  sendButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '900'
  }
});
