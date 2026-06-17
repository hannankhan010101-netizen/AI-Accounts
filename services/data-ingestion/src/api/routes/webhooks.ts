import { createHmac, timingSafeEqual } from "node:crypto";
import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { prisma } from "../../lib/prisma.js";
import { extractToStaging, enqueuePipelineForRun } from "../../pipeline/orchestrator.js";
import { EntityModuleSchema } from "../../types/pipeline.js";

export async function webhookRoutes(app: FastifyInstance) {
  app.post<{ Params: { provider: string } }>(
    "/:provider/:companyId",
    async (request, reply) => {
      const { provider, companyId } = request.params as {
        provider: string;
        companyId: string;
      };

      const signature = request.headers["x-signature"] as string | undefined;
      const rawBody = JSON.stringify(request.body);

      const sub = await prisma.ingWebhookSubscription.findFirst({
        where: { companyId, provider, isActive: true },
      });

      if (!sub || !verifyHmac(rawBody, signature, sub.secretHash)) {
        reply.code(401);
        return { error: "Invalid signature" };
      }

      const payload = z
        .object({
          records: z.array(z.record(z.unknown())),
          externalRunId: z.string().optional(),
        })
        .parse(request.body);

      const run = await prisma.ingMigrationRun.create({
        data: {
          companyId,
          name: `Webhook ${provider} ${new Date().toISOString()}`,
          module: sub.module,
          mode: "webhook",
          sourceType: "webhook",
          sourceSystem: provider,
          mappingProfileId: sub.mappingProfileId,
          totalRows: payload.records.length,
        },
      });

      const rows = payload.records.map((data, i) => ({
        rowIndex: i + 1,
        data,
      }));

      await extractToStaging(run.id, rows);
      await enqueuePipelineForRun(run.id);

      reply.code(202);
      return { result: { runId: run.id, accepted: rows.length } };
    },
  );
}

function verifyHmac(
  body: string,
  signature: string | undefined,
  secret: string,
): boolean {
  if (!signature) return false;
  const expected = signBody(body, secret);
  try {
    return timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
  } catch {
    return false;
  }
}

function signBody(body: string, secret: string): string {
  return createHmac("sha256", secret).update(body).digest("hex");
}
