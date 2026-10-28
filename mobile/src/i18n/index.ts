import en from './en.json';
import te from './te.json';
import hi from './hi.json';
import ta from './ta.json';
import kn from './kn.json';
import ml from './ml.json';
import bn from './bn.json';
import mr from './mr.json';

export type SupportedLanguage = 'en' | 'te' | 'hi' | 'ta' | 'kn' | 'ml' | 'bn' | 'mr';

export interface LanguageMeta {
  code: SupportedLanguage;
  name: string;
  native: string;
  flag: string;
}

export const SUPPORTED_LANGUAGES: Record<SupportedLanguage, LanguageMeta> = {
  en: { code: 'en', name: 'English', native: 'English', flag: '🌐' },
  te: { code: 'te', name: 'Telugu', native: 'తెలుగు', flag: '🇮🇳' },
  hi: { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
  ta: { code: 'ta', name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳' },
  kn: { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳' },
  ml: { code: 'ml', name: 'Malayalam', native: 'മലയാളം', flag: '🇮🇳' },
  bn: { code: 'bn', name: 'Bengali', native: 'বাংলা', flag: '🇮🇳' },
  mr: { code: 'mr', name: 'Marathi', native: 'मराठी', flag: '🇮🇳' }
};

const translations: Record<SupportedLanguage, Record<string, string>> = {
  en,
  te,
  hi,
  ta,
  kn,
  ml,
  bn,
  mr
};

let currentLanguage: SupportedLanguage = 'en';

export const setLanguage = (lang: SupportedLanguage) => {
  if (translations[lang]) {
    currentLanguage = lang;
  }
};

export const getLanguage = (): SupportedLanguage => currentLanguage;

export const translate = (key: string, defaultText?: string): string => {
  const dict = translations[currentLanguage] || translations.en;
  if (dict && key in dict) {
    return dict[key];
  }
  const fallbackDict = translations.en;
  if (fallbackDict && key in fallbackDict) {
    return fallbackDict[key];
  }
  return defaultText || key;
};

export const t = translate;
