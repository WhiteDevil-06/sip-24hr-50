import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SoilCast — Soil Moisture Forecasting & Simulation Engine",
  description: "Deep learning-based 24-hour soil moisture forecasting and smart irrigation scenario simulation.",
  icons: {
    icon: "/icon.svg",
    shortcut: "/icon.svg",
    apple: "/icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
      </head>
      <body>{children}</body>
    </html>
  );
}
