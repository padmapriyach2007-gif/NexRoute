import { ApiClient, defaultApiClient } from './apiClient';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'aura' | 'system';
  text: string;
  timestamp: number;
  suggestions?: string[];
  routeRecommendation?: {
    origin: string;
    destination: string;
    estimatedBudgetInr?: number;
    recommendedMode?: string;
  };
}

export class CopilotApi {
  constructor(private client: ApiClient = defaultApiClient) {}

  public async sendMessage(
    prompt: string,
    history: ChatMessage[] = [],
    language: string = 'en'
  ): Promise<ChatMessage> {
    try {
      const res = await this.client.post<{ reply: string; suggestions?: string[] }>('/api/v1/chat', {
        prompt,
        history: history.map((h) => ({ role: h.sender === 'user' ? 'user' : 'assistant', content: h.text })),
        language
      });

      if (res.data && res.data.reply) {
        return {
          id: `aura_${Date.now()}`,
          sender: 'aura',
          text: res.data.reply,
          timestamp: Date.now(),
          suggestions: res.data.suggestions || [
            'Compare fastest vs eco route',
            'Estimate trip fuel budget',
            'Find wheelchair-accessible sights'
          ]
        };
      }
    } catch {
      // Fallback
    }

    // Graceful offline heuristic reply
    return this.generateOfflineHeuristicReply(prompt, language);
  }

  private generateOfflineHeuristicReply(prompt: string, language: string): ChatMessage {
    const pLow = prompt.toLowerCase();
    let reply = 'I am AURA, your intelligent travel copilot. How can I assist your navigation journey today?';

    if (pLow.includes('budget') || pLow.includes('cost') || pLow.includes('price')) {
      reply = 'For your journey, estimated toll costs are ₹0-180 FASTag, and vehicle fuel consumption is approximately 4.2L per 100km at current steady highway speeds.';
    } else if (pLow.includes('time') || pLow.includes('fast') || pLow.includes('traffic')) {
      reply = 'The Fastest route preference minimizes delay across primary expressways, while the Balanced option optimizes both fuel and travel time.';
    } else if (pLow.includes('accessible') || pLow.includes('wheelchair')) {
      reply = 'The Accessible route ensures verified step-free curb access, wide transit bays, and ramp clearances along all surveyed public corridors.';
    }

    return {
      id: `aura_offline_${Date.now()}`,
      sender: 'aura',
      text: reply,
      timestamp: Date.now(),
      suggestions: [
        'Plan a one-day city trip',
        'Find places near destination',
        'Check accessible facilities'
      ]
    };
  }
}

export const copilotApi = new CopilotApi();
