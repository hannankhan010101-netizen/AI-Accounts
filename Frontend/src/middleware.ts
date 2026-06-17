import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/** Never allow credentials in URLs (logs, history, Referer). */
const CREDENTIAL_QUERY_KEYS = new Set([
  "email",
  "password",
  "passwd",
  "pwd",
  "pass",
  "token",
  "secret",
  "access_token",
  "refresh_token",
]);

function hasCredentialQuery(searchParams: URLSearchParams): boolean {
  for (const key of searchParams.keys()) {
    if (CREDENTIAL_QUERY_KEYS.has(key.toLowerCase())) return true;
  }
  return false;
}

export function middleware(request: NextRequest) {
  const { pathname, searchParams } = request.nextUrl;
  if (pathname !== "/login" && pathname !== "/signup") {
    return NextResponse.next();
  }

  if (!hasCredentialQuery(searchParams)) {
    return NextResponse.next();
  }

  const url = request.nextUrl.clone();
  url.search = "";
  return NextResponse.redirect(url);
}

export const config = {
  matcher: ["/login", "/signup"],
};
