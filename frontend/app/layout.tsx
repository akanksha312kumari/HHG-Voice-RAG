import "./globals.css";

export const metadata = {
  title: "Voice RAG System",
  description: "HH Goa 2026 - Task 2",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">{children}</body>
    </html>
  );
}

