import type { Variants } from "framer-motion";

import { motionDuration } from "@/lib/motion/tokens";
import { easeOut } from "@/lib/motion/easing";

const reduced = { duration: 0.01 };

export const fadeVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: motionDuration.fast, ease: easeOut },
  },
  exit: {
    opacity: 0,
    transition: { duration: motionDuration.instant, ease: easeOut },
  },
};

export const slideUpVariants: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: motionDuration.normal, ease: easeOut },
  },
  exit: {
    opacity: 0,
    y: 8,
    transition: { duration: motionDuration.fast, ease: easeOut },
  },
};

export const slideRightVariants: Variants = {
  hidden: { opacity: 0, x: 24 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: motionDuration.normal, ease: easeOut },
  },
  exit: {
    opacity: 0,
    x: 16,
    transition: { duration: motionDuration.fast, ease: easeOut },
  },
};

export const scaleVariants: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: motionDuration.fast, ease: easeOut },
  },
  exit: {
    opacity: 0,
    scale: 0.98,
    transition: { duration: motionDuration.instant, ease: easeOut },
  },
};

export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.06, delayChildren: 0.04 },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 6 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: motionDuration.fast, ease: easeOut },
  },
};

/** Apply when user prefers reduced motion. */
export function withReducedMotion<T extends Variants>(variants: T): T {
  return {
    ...variants,
    visible: { ...variants.visible, transition: reduced },
    exit: { ...variants.exit, transition: reduced },
  } as T;
}
