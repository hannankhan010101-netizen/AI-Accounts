import Fastify from "fastify";
import cors from "@fastify/cors";
import multipart from "@fastify/multipart";
import { config } from "./config.js";
import { logger } from "./lib/logger.js";
import { migrationRoutes } from "./api/routes/migrations.js";
import { mappingRoutes } from "./api/routes/mappings.js";
import { previewRoutes } from "./api/routes/preview.js";
import { webhookRoutes } from "./api/routes/webhooks.js";

export async function buildServer() {
  const app = Fastify({ logger: true });

  await app.register(cors, { origin: true });
  await app.register(multipart, { limits: { fileSize: 500 * 1024 * 1024 } });

  app.get("/health", async () => ({ status: "ok", service: "data-ingestion" }));

  await app.register(migrationRoutes, { prefix: "/api/v1/companies/:companyId/migrations" });
  await app.register(mappingRoutes, { prefix: "/api/v1/companies/:companyId/migrations" });
  await app.register(previewRoutes, { prefix: "/api/v1/companies/:companyId/migrations" });
  await app.register(webhookRoutes, { prefix: "/api/v1/webhooks" });

  return app;
}

async function main() {
  const app = await buildServer();
  await app.listen({ port: config.PORT, host: "0.0.0.0" });
  logger.info({ port: config.PORT }, "Data ingestion API listening");
}

main().catch((err) => {
  logger.error(err, "Failed to start server");
  process.exit(1);
});
