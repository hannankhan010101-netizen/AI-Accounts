/**
 * Standalone layout for print views — strips the app shell.
 * Use browser's native Print (Ctrl/Cmd+P) to render PDF; A4 page sizing in CSS.
 */
import "@/app/globals.css";
import { Providers } from "@/app/providers";
import { BRAND } from "@/lib/brand";

export const metadata = {
  title: `${BRAND.name} — Print`,
  icons: { icon: BRAND.logoIcon },
};

export default function PrintLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-neutral-900 print:bg-white print:text-black">
        <style>{`
          @media print {
            @page { size: A4; margin: 16mm; }
            body { background: #fff; }
            .no-print { display: none !important; }
          }
        `}</style>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
