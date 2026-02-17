
import "@/styles/globals.css";
import type { Metadata, Viewport } from "next";
import LocaleProvider from "@/lib/LocaleProvider";
import FeedbackButton from "@/components/layout/FeedbackButton";

export const metadata: Metadata = {
  title: "EduAI — Personal AI Tutor",
  description: "Adaptive Multi-Model AI Tutoring Platform",
  manifest: "/manifest.json",
  icons: {
    apple: "/icons/icon-192.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#0d1117",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <LocaleProvider>{children}</LocaleProvider>
        <FeedbackButton />
      </body>
    </html>
  );
}
