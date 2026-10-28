import * as Speech from 'expo-speech';
import { SupportedLanguage } from '../../i18n';

/**
 * Voice Navigation Service with Deduplication & Multi-Language Support
 */

const LANGUAGE_VOICE_CODES: Record<SupportedLanguage, string> = {
  en: 'en-US',
  te: 'te-IN',
  hi: 'hi-IN',
  ta: 'ta-IN',
  kn: 'kn-IN',
  ml: 'ml-IN',
  bn: 'bn-IN',
  mr: 'mr-IN'
};

export class TtsService {
  private isMuted: boolean = false;
  private currentLanguage: SupportedLanguage = 'en';
  private speechRate: number = 0.95;
  private lastAnnouncedManeuverId: string | null = null;
  private lastAnnouncedTimestamp: number = 0;

  public setMuted(muted: boolean): void {
    this.isMuted = muted;
    if (muted) {
      this.stop();
    }
  }

  public getMuted(): boolean {
    return this.isMuted;
  }

  public setLanguage(lang: SupportedLanguage): void {
    this.currentLanguage = lang;
  }

  public setRate(rate: number): void {
    this.speechRate = Math.max(0.5, Math.min(1.5, rate));
  }

  public async announceManeuver(
    maneuverId: string,
    instructionText: string,
    distanceMeters?: number
  ): Promise<void> {
    if (this.isMuted || !instructionText) return;

    const now = Date.now();
    // Prevent duplicate spam if GPS updates repeatedly within 4 seconds for the same maneuver
    if (this.lastAnnouncedManeuverId === maneuverId && (now - this.lastAnnouncedTimestamp) < 4000) {
      return;
    }

    let speechText = instructionText;
    if (distanceMeters !== undefined && distanceMeters > 50) {
      const rounded = Math.round(distanceMeters / 50) * 50;
      speechText = `In ${rounded} meters, ${instructionText}`;
    }

    this.lastAnnouncedManeuverId = maneuverId;
    this.lastAnnouncedTimestamp = now;

    const voiceCode = LANGUAGE_VOICE_CODES[this.currentLanguage] || 'en-US';

    try {
      await Speech.stop();
      Speech.speak(speechText, {
        language: voiceCode,
        rate: this.speechRate,
        pitch: 1.0
      });
    } catch {
      // Graceful fallback if native TTS is disabled on device
    }
  }

  public async announceArrival(): Promise<void> {
    if (this.isMuted) return;
    const voiceCode = LANGUAGE_VOICE_CODES[this.currentLanguage] || 'en-US';
    try {
      await Speech.stop();
      Speech.speak('You have arrived at your destination.', {
        language: voiceCode,
        rate: this.speechRate
      });
    } catch {
      // Ignore
    }
  }

  public stop(): void {
    try {
      Speech.stop();
    } catch {
      // Ignore
    }
  }
}

export const ttsService = new TtsService();
