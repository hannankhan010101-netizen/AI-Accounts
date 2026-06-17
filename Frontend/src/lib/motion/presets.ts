import type { Transition, Variants } from "framer-motion";

import { motionDuration, motionSpring } from "@/lib/motion/tokens";
import { fadeVariants, scaleVariants, slideUpVariants } from "@/lib/motion/variants";
import type { MotionPresetId } from "@/lib/tour/types";

export const motionPresets: Record<
  MotionPresetId,
  { variants: Variants; transition?: Transition }
> = {
  fade: { variants: fadeVariants },
  slideUp: { variants: slideUpVariants },
  scale: { variants: scaleVariants },
  spotlight: {
    variants: {
      hidden: { opacity: 0 },
      visible: { opacity: 1 },
      exit: { opacity: 0 },
    },
    transition: { duration: motionDuration.normal },
  },
  tooltip: {
    variants: slideUpVariants,
    transition: { duration: motionDuration.fast },
  },
  fab: {
    variants: scaleVariants,
    transition: motionSpring.snappy,
  },
  drawer: {
    variants: {
      hidden: { x: "100%" },
      visible: { x: 0 },
      exit: { x: "100%" },
    },
    transition: { type: "spring", stiffness: 320, damping: 34 },
  },
  navDrawer: {
    variants: {
      hidden: { x: "-100%" },
      visible: { x: 0 },
      exit: { x: "-100%" },
    },
    transition: { type: "spring", stiffness: 320, damping: 34 },
  },
  bottomSheet: {
    variants: {
      hidden: { y: "100%" },
      visible: { y: 0 },
      exit: { y: "100%" },
    },
    transition: { type: "spring", stiffness: 320, damping: 34 },
  },
};
