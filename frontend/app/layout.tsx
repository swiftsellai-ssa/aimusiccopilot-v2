import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ErrorBoundary from "../components/ErrorBoundary";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "amc - AI Music Co-pilot",
  description: "AI-powered music generation platform for producers",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ErrorBoundary>
          {children}
        </ErrorBoundary>

        {/* Global Footer */}
        <footer className="w-full py-4 text-center text-gray-500 text-sm bg-gray-900/50 backdrop-blur-sm fixed bottom-0 z-10">
          <p>
            &copy; {new Date().getFullYear()} amc - AI Music Co-pilot.
            <a href="/legal" className="text-xs text-gray-500 hover:text-gray-300 ml-2">Legal & Terms</a>
          </p>
        </footer>
      </body>
    </html>
  );
}
