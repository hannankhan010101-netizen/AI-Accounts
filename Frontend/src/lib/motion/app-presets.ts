import type { Transition, Variants } from "framer-motion";

import { motionDuration, motionSpring } from "@/lib/motion/tokens";
import {
  fadeVariants,
  scaleVariants,
  slideUpVariants,
  staggerContainer,
  staggerItem,
  withReducedMotion,
} from "@/lib/motion/variants";

const pageEnterVariants: Variants = {
  hidden: { opacity: 0, y: 8 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: motionDuration.normal, ease: [0.16, 1, 0.3, 1] },
  },
  exit: { opacity: 0, y: 4, transition: { duration: motionDuration.fast } },
};

const metricEnterVariants: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: motionDuration.normal, ease: [0.16, 1, 0.3, 1] },
  },
};

const modalEnterVariants: Variants = {
  hidden: { opacity: 0, scale: 0.96, y: 8 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: motionDuration.fast, ease: [0.16, 1, 0.3, 1] },
  },
  exit: {
    opacity: 0,
    scale: 0.98,
    y: 4,
    transition: { duration: motionDuration.instant },
  },
};

export const appPresets = {
  pageEnter: {
    variants: withReducedMotion(pageEnterVariants),
    transition: { duration: motionDuration.normal } as Transition,
  },
  staggerList: {
    variants: staggerContainer,
    itemVariants: staggerItem,
  },
  metricEnter: {
    variants: withReducedMotion(metricEnterVariants),
    transition: { duration: motionDuration.normal } as Transition,
  },
  modalEnter: {
    variants: withReducedMotion(modalEnterVariants),
    transition: { duration: motionDuration.fast } as Transition,
  },
  drawerEnter: {
    variants: scaleVariants,
    transition: motionSpring.soft as Transition,
  },
  fade: { variants: fadeVariants },
  slideUp: { variants: slideUpVariants },
  barGrow: {
    transition: { duration: motionDuration.slow, ease: [0.16, 1, 0.3, 1] } as Transition,
  },
} as const;
