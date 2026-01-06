import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Mental Coach - AI Supportive Chat',
  description: 'A supportive mental coach powered by AI to help with stress, motivation, habits, and confidence.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

