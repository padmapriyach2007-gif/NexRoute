import { SUPPORTED_LANGUAGES, SupportedLanguage, setLanguage, getLanguage, translate } from '../src/i18n';

describe('Multilingual Localization Completeness (8 Languages)', () => {
  const targetLanguages: SupportedLanguage[] = ['en', 'te', 'hi', 'ta', 'kn', 'ml', 'bn', 'mr'];

  test('contains all 8 required Indian and global languages', () => {
    targetLanguages.forEach((lang) => {
      expect(SUPPORTED_LANGUAGES[lang]).toBeDefined();
      expect(SUPPORTED_LANGUAGES[lang].name.length).toBeGreaterThan(0);
      expect(SUPPORTED_LANGUAGES[lang].native.length).toBeGreaterThan(0);
    });
  });

  test('translates core navigation keys across languages', () => {
    targetLanguages.forEach((lang) => {
      setLanguage(lang);
      expect(getLanguage()).toBe(lang);

      const navStart = translate('nav.start');
      expect(navStart).toBeDefined();
      expect(navStart.length).toBeGreaterThan(0);

      const objFastest = translate('obj.fastest');
      expect(objFastest).toBeDefined();
      expect(objFastest.length).toBeGreaterThan(0);
    });
  });

  test('falls back gracefully to English when key is missing in custom language', () => {
    setLanguage('te');
    const fallbackText = translate('non.existent.key', 'Default Fallback');
    expect(fallbackText).toBe('Default Fallback');
  });
});
