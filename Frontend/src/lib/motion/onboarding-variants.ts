import type { Variants, Transition } from "framer-motion";

import { motionSpring } from "@/lib/motion/tokens";

export const onboardingSpring: Transition = motionSpring.soft;

export const stepCardVariants: Variants = {
  hidden: { opacity: 0, y: 10, scale: 0.98 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: onboardingSpring,
  },
  exit: {
    opacity: 0,
    y: -6,
    scale: 0.99,
    transition: { duration: 0.15 },
  },
};

export const hubPanelVariants: Variants = {
  hidden: { opacity: 0, y: 8, scale: 0.97 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: motionSpring.snappy,
  },
  exit: { opacity: 0, y: 4, scale: 0.98, transition: { duration: 0.12 } },
};

export const celebrationVariants: Variants = {
  hidden: { opacity: 0, y: 16, scale: 0.94 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: motionSpring.gentle,
  },
  exit: { opacity: 0, y: 8, transition: { duration: 0.18 } },
};

export const fabGlowVariants: Variants = {
  idle: { opacity: 0.35, scale: 1 },
  hover: { opacity: 0.55, scale: 1.08, transition: { duration: 0.35 } },
};
