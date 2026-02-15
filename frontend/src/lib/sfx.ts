// Lightweight send sound effect (very low volume, professional soft click)
const SEND_DATA_URL =
  "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAIlYAAESsAAACABAAZGF0YYQAAAAA/////wAAAP//AAD/AAAA////AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA";

let cachedAudio: HTMLAudioElement | null = null;

export function playSendSound() {
  try {
    if (!cachedAudio) {
      cachedAudio = new Audio(SEND_DATA_URL);
      cachedAudio.volume = 0.08; // very soft
    }
    const audio = cachedAudio.cloneNode(true) as HTMLAudioElement;
    audio.volume = 0.08;
    audio.play().catch(() => {});
  } catch {
    // Fail silently on unsupported environments
  }
}
