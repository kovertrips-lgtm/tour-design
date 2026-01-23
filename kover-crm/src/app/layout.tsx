import type { Metadata } from "next";
import { Inter } from "next/font/google"; // 
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Kover CRM | AmoClone",
  description: "Internal CRM",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div style={{ display: "flex", minHeight: "100vh" }}>
          <Sidebar />
          <main
            style={{
              flex: 1,
              background: "var(--bg-body)",
              overflow: "hidden"
            }}
          >
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
