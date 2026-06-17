import { startPipelineWorker } from "./workers/pipeline-worker.js";
import { logger } from "./lib/logger.js";

startPipelineWorker();
logger.info("Worker process ready");
