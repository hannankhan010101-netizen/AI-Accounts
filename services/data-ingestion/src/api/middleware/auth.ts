import type { FastifyRequest } from "fastify";

export interface TenantParams {
  companyId: string;
}

export async function requireTenantAccess(
  request: FastifyRequest<{ Params: TenantParams }>,
): Promise<void> {
  const auth = request.headers.authorization;
  if (!auth?.startsWith("Bearer ")) {
    throw Object.assign(new Error("Unauthorized"), { statusCode: 401 });
  }

  const token = auth.slice(7);
  const payload = decodeJwtPayload(token);
  if (!payload?.companyId || payload.companyId !== request.params.companyId) {
    throw Object.assign(new Error("Tenant mismatch"), { statusCode: 403 });
  }

  (request as FastifyRequest & { accessToken: string }).accessToken = token;
}

function decodeJwtPayload(token: string): { companyId?: string; sub?: string } | null {
  try {
    const part = token.split(".")[1];
    if (!part) return null;
    const json = Buffer.from(part, "base64url").toString("utf-8");
    return JSON.parse(json) as { companyId?: string; sub?: string };
  } catch {
    return null;
  }
}

export function getAccessToken(request: FastifyRequest): string | undefined {
  return (request as FastifyRequest & { accessToken?: string }).accessToken;
}
