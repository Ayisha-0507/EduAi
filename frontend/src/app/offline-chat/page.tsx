"use client";

/**
 * EduAI — Offline Chat (No Internet Required)
 * Uses a built-in local knowledge engine for basic tutoring
 * when the user has no internet connection. No API calls at all.
 */

import { useState, useRef, useEffect } from "react";
import { FiArrowLeft, FiSend, FiWifiOff } from "react-icons/fi";
import { useRouter } from "next/navigation";
import AppLayout from "@/components/layout/AppLayout";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { playSendSound } from "@/lib/sfx";


interface OfflineMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

// ── Local Knowledge Base ──────────────────────────────────────────────────────

const KNOWLEDGE: Record<string, string> = {
  // Math
  "pythagorean theorem": "The **Pythagorean Theorem** states that in a right triangle, the square of the hypotenuse equals the sum of the squares of the other two sides: **a² + b² = c²**\n\nExample: If a = 3 and b = 4, then c = √(9 + 16) = √25 = **5**",
  "quadratic formula": "The **Quadratic Formula** solves any equation of the form ax² + bx + c = 0:\n\n**x = (-b ± √(b² - 4ac)) / 2a**\n\nThe discriminant (b² - 4ac) determines:\n- Positive → 2 real solutions\n- Zero → 1 real solution\n- Negative → no real solutions",
  "derivative": "A **derivative** measures the rate of change of a function.\n\n**Basic Rules:**\n- Power Rule: d/dx(xⁿ) = nxⁿ⁻¹\n- Sum Rule: d/dx(f + g) = f' + g'\n- Product Rule: d/dx(fg) = f'g + fg'\n- Chain Rule: d/dx(f(g(x))) = f'(g(x)) · g'(x)",
  "integral": "An **integral** calculates the area under a curve.\n\n**Basic Integrals:**\n- ∫xⁿ dx = xⁿ⁺¹/(n+1) + C\n- ∫eˣ dx = eˣ + C\n- ∫sin(x) dx = -cos(x) + C\n- ∫cos(x) dx = sin(x) + C\n- ∫1/x dx = ln|x| + C",
  "trigonometry": "**Key Trig Ratios** (for right triangles):\n- sin(θ) = Opposite / Hypotenuse\n- cos(θ) = Adjacent / Hypotenuse\n- tan(θ) = Opposite / Adjacent\n\n**Important Identities:**\n- sin²θ + cos²θ = 1\n- sin(2θ) = 2sinθ·cosθ\n- cos(2θ) = cos²θ - sin²θ",
  "algebra": "**Core Algebra Concepts:**\n\n1. **Solving equations**: Isolate the variable\n2. **Factoring**: a² - b² = (a+b)(a-b)\n3. **Exponents**: aᵐ · aⁿ = aᵐ⁺ⁿ\n4. **Logarithms**: log(ab) = log(a) + log(b)\n5. **Inequalities**: Flip sign when multiplying/dividing by negative",
  "probability": "**Probability Basics:**\n\nP(event) = Favorable outcomes / Total outcomes\n\n- P(A or B) = P(A) + P(B) - P(A and B)\n- P(A and B) = P(A) × P(B) if independent\n- Complement: P(not A) = 1 - P(A)\n- Conditional: P(A|B) = P(A and B) / P(B)",

  // Science
  "newton": "**Newton's Three Laws of Motion:**\n\n1. **First Law (Inertia)**: An object stays at rest or in motion unless acted on by a force\n2. **Second Law**: F = ma (Force = mass × acceleration)\n3. **Third Law**: Every action has an equal and opposite reaction\n\n**Universal Gravitation**: F = G(m₁m₂)/r²",
  "photosynthesis": "**Photosynthesis** converts sunlight into food for plants.\n\n**Equation**: 6CO₂ + 6H₂O + Light → C₆H₁₂O₆ + 6O₂\n\n**Stages:**\n1. **Light Reactions** (in thylakoids): Water splits, ATP & NADPH produced\n2. **Calvin Cycle** (in stroma): CO₂ fixed into glucose using ATP & NADPH",
  "cell": "**Cell Structure:**\n\n**Both Plant & Animal:**\n- Cell membrane, Nucleus, Mitochondria, Ribosomes, ER, Golgi\n\n**Plant Only:**\n- Cell wall, Chloroplasts, Large vacuole\n\n**Animal Only:**\n- Centrioles, Lysosomes (more common)\n\nThe **nucleus** stores DNA and controls cell activities.",
  "periodic table": "**Periodic Table Organization:**\n\n- **Rows (Periods)**: 7 periods, elements increase in atomic number\n- **Columns (Groups)**: Elements in same group share chemical properties\n- **Group 1**: Alkali metals (Li, Na, K...)\n- **Group 17**: Halogens (F, Cl, Br...)\n- **Group 18**: Noble gases (He, Ne, Ar...)\n\nElectronegativity generally increases → and ↑",
  "dna": "**DNA (Deoxyribonucleic Acid):**\n\n- **Structure**: Double helix with sugar-phosphate backbone\n- **Base pairs**: A-T (Adenine-Thymine), G-C (Guanine-Cytosine)\n- **Replication**: Semi-conservative, uses DNA polymerase\n- **Transcription**: DNA → mRNA (in nucleus)\n- **Translation**: mRNA → Protein (at ribosome)\n\nThe **Central Dogma**: DNA → RNA → Protein",
  "atom": "**Atomic Structure:**\n\n- **Protons** (+): In nucleus, define the element\n- **Neutrons** (0): In nucleus, affect isotope/mass\n- **Electrons** (-): Orbit in shells/orbitals\n\n**Key concepts:**\n- Atomic number = number of protons\n- Mass number = protons + neutrons\n- Isotopes = same element, different neutrons\n- Ions = atom with net charge (gained/lost electrons)",

  // Programming
  "python": "**Python Basics:**\n\n```python\n# Variables\nname = \"EduAI\"\nage = 1\n\n# Lists\nnums = [1, 2, 3]\nnums.append(4)\n\n# Functions\ndef greet(name):\n    return f\"Hello, {name}!\"\n\n# Loops\nfor i in range(5):\n    print(i)\n\n# Conditionals\nif age >= 18:\n    print(\"Adult\")\n```",
  "javascript": "**JavaScript Basics:**\n\n```javascript\n// Variables\nconst name = 'EduAI';\nlet count = 0;\n\n// Functions\nconst greet = (name) => `Hello, ${name}!`;\n\n// Arrays\nconst nums = [1, 2, 3];\nnums.map(n => n * 2); // [2, 4, 6]\n\n// Async/Await\nasync function fetchData() {\n  const res = await fetch(url);\n  const data = await res.json();\n}\n```",
  "html": "**HTML Basics:**\n\n```html\n<!DOCTYPE html>\n<html>\n<head>\n  <title>My Page</title>\n</head>\n<body>\n  <h1>Hello World</h1>\n  <p>This is a paragraph.</p>\n  <a href=\"url\">Link</a>\n  <img src=\"img.jpg\" alt=\"Image\">\n  <ul>\n    <li>Item 1</li>\n  </ul>\n</body>\n</html>\n```\n\nHTML = Structure, CSS = Style, JS = Behavior",
  "css": "**CSS Basics:**\n\n```css\n/* Selectors */\nh1 { color: blue; }\n.class { font-size: 16px; }\n#id { margin: 10px; }\n\n/* Flexbox */\n.container {\n  display: flex;\n  justify-content: center;\n  align-items: center;\n}\n\n/* Grid */\n.grid {\n  display: grid;\n  grid-template-columns: 1fr 1fr;\n  gap: 10px;\n}\n```",
  "data structure": "**Common Data Structures:**\n\n| Structure | Access | Search | Insert | Delete |\n|-----------|--------|--------|--------|--------|\n| Array     | O(1)   | O(n)   | O(n)   | O(n)   |\n| Linked List| O(n)  | O(n)   | O(1)   | O(1)   |\n| Hash Table| O(1)   | O(1)   | O(1)   | O(1)   |\n| BST       | O(log n)| O(log n)| O(log n)| O(log n)|\n\n**Stack**: LIFO (Last In, First Out)\n**Queue**: FIFO (First In, First Out)",
  "algorithm": "**Key Algorithms:**\n\n**Sorting:**\n- Bubble Sort: O(n²) — Simple, compare adjacent\n- Merge Sort: O(n log n) — Divide and conquer\n- Quick Sort: O(n log n) avg — Pivot-based\n\n**Searching:**\n- Linear Search: O(n)\n- Binary Search: O(log n) — requires sorted array\n\n**Recursion**: Function calls itself with a base case\n```\nfactorial(n) = n × factorial(n-1), base: factorial(0) = 1\n```",

  // English / Writing
  "essay": "**Essay Structure:**\n\n1. **Introduction** (1 paragraph)\n   - Hook/attention grabber\n   - Context/background\n   - **Thesis statement** (main argument)\n\n2. **Body** (2-4 paragraphs)\n   - Topic sentence\n   - Evidence/examples\n   - Analysis\n   - Transition to next point\n\n3. **Conclusion** (1 paragraph)\n   - Restate thesis (different words)\n   - Summarize key points\n   - Closing thought",
  "grammar": "**Key Grammar Rules:**\n\n- **Subject-Verb Agreement**: \"The dog runs\" (not \"run\")\n- **Their/There/They're**: Possessive / Place / They are\n- **Its/It's**: Possessive / It is\n- **Your/You're**: Possessive / You are\n- **Affect/Effect**: Verb / Noun (usually)\n- **Comma splice**: Don't join sentences with just a comma\n- **Active voice**: Preferred over passive (\"I wrote\" vs \"was written\")",
};

const STUDY_TIPS = [
  "📌 **Spaced Repetition**: Review material at increasing intervals (1 day, 3 days, 7 days, 14 days)",
  "🧠 **Active Recall**: Test yourself instead of re-reading notes",
  "📝 **Feynman Technique**: Explain concepts in simple terms to identify gaps",
  "⏱️ **Pomodoro Technique**: Study 25 min, break 5 min, repeat. Long break after 4 cycles",
  "🗺️ **Mind Mapping**: Visualize connections between ideas for better retention",
  "🎯 **Teach Someone**: Explaining to others deepens your own understanding",
  "💤 **Sleep & Memory**: Sleep within 24h of studying to consolidate memories",
  "📖 **SQ3R Method**: Survey, Question, Read, Recite, Review",
];

const MOTIVATIONAL = [
  "Every expert was once a beginner. Keep going! 💪",
  "The only way to learn is to practice. You're doing great by being here! 🌟",
  "Mistakes are proof that you're trying. Embrace them! 🎯",
  "Small steps every day lead to big results. Stay consistent! 📈",
  "Curiosity is the engine of achievement. Keep asking questions! 🧠",
  "You don't have to be perfect, just persistent. 🔥",
  "Learning is not a race — it's a journey. Enjoy it! 🚀",
];

// ── Local AI Engine ──────────────────────────────────────────────────────────

function generateOfflineResponse(input: string): string {
  const lower = input.toLowerCase().trim();

  // Greetings
  if (/^(hi|hello|hey|yo|sup|hola|namaste)\b/.test(lower)) {
    return "Hello! 👋 I'm EduAI Offline Mode. I can help with **math, science, programming, writing**, and **study tips**. I have limited knowledge offline, but I'll do my best!\n\nTry asking about:\n- Pythagorean theorem\n- Photosynthesis\n- Python basics\n- Essay structure\n- Study tips";
  }

  // Help
  if (/\b(help|what can you|how to use|commands)\b/.test(lower)) {
    return "**Offline Mode Topics:**\n\n📐 **Math**: algebra, trigonometry, calculus, probability, quadratic formula\n🔬 **Science**: Newton's laws, photosynthesis, cell structure, DNA, atoms, periodic table\n💻 **Programming**: Python, JavaScript, HTML, CSS, data structures, algorithms\n✍️ **Writing**: essay structure, grammar rules\n📌 **Study Tips**: Ask for study tips or motivation!\n\nJust type a topic name and I'll explain it!";
  }

  // Study tips
  if (/\b(study tips?|how to study|learning tips?|revision)\b/.test(lower)) {
    const tip = STUDY_TIPS[Math.floor(Math.random() * STUDY_TIPS.length)];
    return `Here's a study tip for you:\n\n${tip}\n\nAsk for more tips anytime!`;
  }

  // Motivation
  if (/\b(motivat|inspire|encourage|sad|tired|bored|give up|hard)\b/.test(lower)) {
    const msg = MOTIVATIONAL[Math.floor(Math.random() * MOTIVATIONAL.length)];
    return msg;
  }

  // Math shortcuts
  if (/\b(\d+)\s*[\+\-\*\/\^]\s*(\d+)\b/.test(lower)) {
    try {
      const expr = lower.replace(/[^0-9\+\-\*\/\.\(\)\s\^]/g, "").replace(/\^/g, "**");
      const result = Function(`"use strict"; return (${expr})`)();
      if (typeof result === "number" && isFinite(result)) {
        return `**Result**: ${input.match(/[\d\+\-\*\/\^\.\s\(\)]+/)?.[0]?.trim()} = **${result}**`;
      }
    } catch {}
  }

  // Search knowledge base
  for (const [key, value] of Object.entries(KNOWLEDGE)) {
    if (lower.includes(key)) {
      return value;
    }
  }

  // Partial matches
  const words = lower.split(/\s+/);
  for (const word of words) {
    if (word.length < 3) continue;
    for (const [key, value] of Object.entries(KNOWLEDGE)) {
      const keyWords = key.split(/\s+/);
      if (keyWords.some((kw) => kw.startsWith(word) || word.startsWith(kw))) {
        return value;
      }
    }
  }

  // Fallback
  return "I don't have offline information about that topic yet. 🤔\n\nIn offline mode, I can help with:\n- **Math**: algebra, trigonometry, calculus, probability\n- **Science**: physics, biology, chemistry\n- **Programming**: Python, JavaScript, HTML/CSS\n- **Writing**: essays, grammar\n- **Study tips** and **motivation**\n\nTry asking about one of these topics, or connect to the internet for full AI-powered tutoring!";
}

// ── Component ────────────────────────────────────────────────────────────────

export default function OfflineChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<OfflineMessage[]>([
    {
      role: "assistant",
      content:
        "🔌 **Offline Mode Active**\n\nNo internet? No problem! I have a built-in knowledge base covering math, science, programming, writing, and study tips.\n\nType any topic and I'll explain it. I can also do basic math calculations!\n\n*Note: For full AI-powered tutoring, use the main Chat with internet.*",
      timestamp: Date.now(),
    },
  ]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    playSendSound();
    const userMsg: OfflineMessage = {
      role: "user",
      content: input.trim(),
      timestamp: Date.now(),
    };
    const response = generateOfflineResponse(input.trim());
    const aiMsg: OfflineMessage = {
      role: "assistant",
      content: response,
      timestamp: Date.now() + 1,
    };
    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setInput("");
  };

  return (
    <AppLayout>
      <div className="flex-1 flex flex-col h-screen">
        {/* Header */}
        <div className="px-3 md:px-6 py-4 border-b border-border-default bg-bg-secondary/50 flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-lg bg-bg-tertiary hover:bg-border-default text-text-secondary hover:text-text-primary transition border border-border-default"
          >
            <FiArrowLeft size={18} />
          </button>
          <div className="flex-1">
            <h1 className="text-lg font-bold text-text-primary flex items-center gap-2">
              <FiWifiOff className="text-amber-400" /> Offline Chat
            </h1>
            <p className="text-xs text-text-secondary">No internet needed — local knowledge engine</p>
          </div>
          <div className="px-2 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-xs text-amber-400 font-medium">
            Offline
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-3 md:px-6 py-4 space-y-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[95%] sm:max-w-[80%] rounded-xl px-3 md:px-4 py-3 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-accent-green/15 border border-accent-green/25 text-text-primary"
                    : "bg-bg-tertiary/80 border border-border-default text-text-primary"
                }`}
              >
                {msg.role === "assistant" ? (
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  <p>{msg.content}</p>
                )}
                <p className="text-[10px] text-text-secondary/50 mt-1 text-right">
                  {new Date(msg.timestamp).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="px-3 md:px-6 py-3 border-t border-border-default bg-bg-secondary/50">
          <div className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="Ask about math, science, coding..."
              className="flex-1 bg-bg-primary border border-border-default rounded-lg px-4 py-3 text-text-primary placeholder-text-secondary/50 focus:border-amber-500 focus:ring-1 focus:ring-amber-500/30 outline-none transition"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="px-4 py-3 bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FiSend size={18} />
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
