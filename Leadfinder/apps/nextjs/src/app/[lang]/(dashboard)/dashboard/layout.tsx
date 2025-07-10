import { notFound } from "next/navigation";

import { MainNav } from "~/components/main-nav";
import { DashboardNav } from "~/components/nav";
import { SiteFooter } from "~/components/site-footer";
import { i18n, type Locale } from "~/config/i18n-config";
import { getDashboardConfig } from "~/config/ui/dashboard";
import { getDictionary } from "~/lib/get-dictionary";

interface DashboardLayoutProps {
  children?: React.ReactNode;
  params: {
    lang: Locale;
  };
}

export function generateStaticParams() {
  return i18n.locales.map((locale) => ({ lang: locale }));
}

export default function DashboardLayout({ children, params: { lang } }: DashboardLayoutProps) {
  // const dict = await getDictionary(lang); // (if needed for footer)
  // const dashboardConfig = await getDashboardConfig({ params: { lang } });
  return (
    <div className="flex min-h-screen flex-col space-y-6">
      <header className="sticky top-0 z-40 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <MainNav items={[]} params={{ lang: `${lang}` }} />
          <div className="flex items-center space-x-3">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">User</span>
            </div>
          </div>
        </div>
      </header>
      <div className="container grid flex-1 gap-12 md:grid-cols-[200px_1fr]">
        <aside className="hidden w-[200px] flex-col md:flex">
          {/* Sidebar nav can be added here later */}
        </aside>
        <main className="flex w-full flex-1 flex-col overflow-hidden">
          {children}
        </main>
      </div>
      {/* <SiteFooter ... /> can be added back if needed */}
    </div>
  );
}
