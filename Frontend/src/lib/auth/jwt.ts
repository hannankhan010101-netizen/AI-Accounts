/** Decode JWT payload (no signature verify — client hint only). */

type AccessPayload = {
  companyId?: unknown;
  sub?: unknown;
  userId?: unknown;
};

function decodeAccessPayload(accessToken: string): AccessPayload | null {
  try {
    const segment = accessToken.split(".")[1];
    if (!segment) return null;
    const base64 = segment.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64)) as AccessPayload;
  } catch {
    return null;
  }
}

export function getCompanyIdFromAccessToken(accessToken: string): string | null {
  const json = decodeAccessPayload(accessToken);
  return typeof json?.companyId === "string" ? json.companyId : null;
}

/** Stable key for per-user local preferences (client hint only). */
export function getUserKeyFromAccessToken(accessToken: string): string {
  const json = decodeAccessPayload(accessToken);
  if (typeof json?.sub === "string") return json.sub;
  if (typeof json?.userId === "string") return json.userId;
  return "anonymous";
}
