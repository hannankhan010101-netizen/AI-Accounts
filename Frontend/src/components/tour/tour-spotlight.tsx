"use client";

import { SpotlightOverlay } from "@/components/overlays/spotlight-overlay";
import type { TargetRect } from "@/lib/tour/target-resolver";

export function TourSpotlight({ rect }: { rect: TargetRect }) {
  return <SpotlightOverlay rect={rect} />;
}
