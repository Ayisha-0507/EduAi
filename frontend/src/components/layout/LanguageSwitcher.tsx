import { useRouter } from 'next/navigation';

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी' },
  { code: 'ta', label: 'தமிழ்' },
];

export default function LanguageSwitcher() {
  const router = useRouter();
  const current = typeof window !== 'undefined' ? (localStorage.getItem('locale') || 'en') : 'en';

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const lang = e.target.value;
    localStorage.setItem('locale', lang);
    router.refresh();
  };

  return (
    <select value={current} onChange={handleChange} className="px-2 py-1 rounded border border-border-default">
      {LANGUAGES.map((l) => (
        <option key={l.code} value={l.code}>{l.label}</option>
      ))}
    </select>
  );
}
