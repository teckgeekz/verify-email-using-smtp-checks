import { NextRequest, NextResponse } from 'next/server';
import { match as matchLocale } from "@formatjs/intl-localematcher";
import Negotiator from "negotiator";
import { i18n } from "~/config/i18n-config";

const noNeedProcessRoute = [".*\\.png", ".*\\.jpg", ".*\\.opengraph-image.png"];
const noRedirectRoute = ["/api(.*)", "/trpc(.*)", "/admin"];
const publicRoutes = [
  new RegExp("/(\\w{2}/)?signin(.*)"),
  new RegExp("/(\\w{2}/)?terms(.*)"),
  new RegExp("/(\\w{2}/)?privacy(.*)"),
  new RegExp("/(\\w{2}/)?docs(.*)"),
  new RegExp("/(\\w{2}/)?blog(.*)"),
  new RegExp("/(\\w{2}/)?pricing(.*)"),
  new RegExp("^/\\w{2}$"), // root with locale
];

export function getLocale(request: NextRequest): string | undefined {
  const negotiatorHeaders: Record<string, string> = {};
  request.headers.forEach((value, key) => (negotiatorHeaders[key] = value));
  const locales = Array.from(i18n.locales);
  const languages = new Negotiator({ headers: negotiatorHeaders }).languages(locales);
  return matchLocale(languages, locales, i18n.defaultLocale);
}

export function isNoRedirect(request: NextRequest): boolean {
  const pathname = request.nextUrl.pathname;
  return noRedirectRoute.some((route) => new RegExp(route).test(pathname));
}

export function isNoNeedProcess(request: NextRequest): boolean {
  const pathname = request.nextUrl.pathname;
  return noNeedProcessRoute.some((route) => new RegExp(route).test(pathname));
}

export function isPublicRoute(request: NextRequest): boolean {
  const pathname = request.nextUrl.pathname;
  return publicRoutes.some((route) => route.test(pathname));
}

export default async function middleware(request: NextRequest) {
  if (isNoNeedProcess(request)) {
    return null;
  }

  // Allow /api/user-sync through without auth
  if (request.nextUrl.pathname.startsWith("/api/user-sync")) {
    return NextResponse.next();
  }

  // Allow webhooks through
  const isWebhooksRoute = request.nextUrl.pathname.startsWith("/api/webhooks/");
  if (isWebhooksRoute) {
    return NextResponse.next();
  }

  const pathname = request.nextUrl.pathname;
  
  // Check if there is any supported locale in the pathname
  const pathnameIsMissingLocale = i18n.locales.every(
    (locale) =>
      !pathname.startsWith(`/${locale}/`) && pathname !== `/${locale}`,
  );
  
  // Redirect if there is no locale
  if (!isNoRedirect(request) && pathnameIsMissingLocale) {
    const locale = getLocale(request);
    return NextResponse.redirect(
      new URL(
        `/${locale}${pathname.startsWith("/") ? "" : "/"}${pathname}`,
        request.url,
      ),
    );
  }

  // Allow public routes
  if (isPublicRoute(request)) {
    return null;
  }

  // For now, allow all routes through (Firebase auth will be handled client-side)
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!.*\\..*|_next).*)",
    "/",
    "/(api|trpc)(.*)",
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)"
  ],
};
