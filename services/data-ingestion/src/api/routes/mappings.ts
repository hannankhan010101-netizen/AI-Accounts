import type { FastifyInstance, FastifyRequest } from "fastify";
import { z } from "zod";
import { prisma } from "../../lib/prisma.js";
import { requireTenantAccess, type TenantParams } from "../middleware/auth.js";
import {
  suggestMappings,
  rulesFromSuggestions,
} from "../../engines/mapping-engine.js";
import { getTargetSchema } from "../../domain/target-schemas.js";
import { EntityModuleSchema } from "../../types/pipeline.js";
import { config } from "../../config.js";

export async function mappingRoutes(app: FastifyInstance) {
  app.addHook("preHandler", requireTenantAccess);

  app.get<{ Params: TenantParams }>("/mapping-profiles", async (request) => {
    const profiles = await prisma.ingMappingProfile.findMany({
      where: { companyId: request.params.companyId },
      include: { rules: { orderBy: { sortOrder: "asc" } } },
    });
    return { result: profiles };
  });

  app.post<{ Params: TenantParams }>("/mapping-profiles", async (request, reply) => {
    const body = z
      .object({
        name: z.string(),
        module: EntityModuleSchema,
        sourceSystem: z.string().default("generic"),
        rules: z.array(
          z.object({
            sourceField: z.string(),
            targetField: z.string(),
            transform: z.string().optional(),
            defaultValue: z.string().optional(),
            isRequired: z.boolean().optional(),
          }),
        ),
      })
      .parse(request.body);

    const profile = await prisma.ingMappingProfile.create({
      data: {
        companyId: request.params.companyId,
        name: body.name,
        module: body.module,
        sourceSystem: body.sourceSystem,
        rules: {
          create: body.rules.map((r, i) => ({ ...r, sortOrder: i })),
        },
      },
      include: { rules: true },
    });

    reply.code(201);
    return { result: profile };
  });

  app.post<{ Params: TenantParams & { profileId: string } }>(
    "/mapping-profiles/:profileId/suggest",
    async (request) => {
      const body = z
        .object({
          sourceFields: z.array(z.string()),
          sourceSystem: z.string().default("generic"),
        })
        .parse(request.body);

      const profile = await prisma.ingMappingProfile.findFirst({
        where: { id: request.params.profileId, companyId: request.params.companyId },
      });
      if (!profile) throw Object.assign(new Error("Not found"), { statusCode: 404 });

      let suggestions = suggestMappings(
        profile.module as z.infer<typeof EntityModuleSchema>,
        body.sourceFields,
        body.sourceSystem,
      );

      if (config.AI_MAPPING_URL && config.AI_MAPPING_API_KEY) {
        suggestions = await enhanceWithAi(suggestions, body.sourceFields, profile.module);
      }

      const required = getTargetSchema(profile.module as z.infer<typeof EntityModuleSchema>)
        .filter((f) => f.required)
        .map((f) => f.field);

      return {
        result: {
          suggestions,
          proposedRules: rulesFromSuggestions(suggestions, required),
        },
      };
    },
  );

  app.get<{ Params: TenantParams & { module: string } }>(
    "/target-schema/:module",
    async (request) => {
      const module = EntityModuleSchema.parse(request.params.module);
      return { result: getTargetSchema(module) };
    },
  );
}

async function enhanceWithAi(
  base: ReturnType<typeof suggestMappings>,
  sourceFields: string[],
  module: string,
): Promise<ReturnType<typeof suggestMappings>> {
  try {
    const res = await fetch(config.AI_MAPPING_URL!, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${config.AI_MAPPING_API_KEY}`,
      },
      body: JSON.stringify({ sourceFields, module, existing: base }),
    });
    if (!res.ok) return base;
    const data = (await res.json()) as { suggestions?: typeof base };
    return data.suggestions ?? base;
  } catch {
    return base;
  }
}
