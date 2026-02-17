import { NextIntlProvider } from 'next-intl';
import { useRouter } from 'next/navigation';

export default function LocaleProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  // Default to English if not set
  const locale = typeof window !== 'undefined' ? (localStorage.getItem('locale') || 'en') : 'en';
  let messages = {};
  try {
    messages = require(`../locales/${locale}.json`);
  } catch {
    messages = require('../locales/en.json');
  }
  return <NextIntlProvider locale={locale} messages={messages}>{children}</NextIntlProvider>;
}
