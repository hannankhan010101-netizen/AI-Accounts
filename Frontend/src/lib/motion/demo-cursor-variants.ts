import type { Variants } from "framer-motion";

export const demoCursorVariants: Variants = {
  hidden: { opacity: 0, scale: 0.6 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { type: "spring", stiffness: 380, damping: 26 },
  },
  exit: { opacity: 0, scale: 0.5, transition: { duration: 0.12 } },
};

export const clickRippleVariants: Variants = {
  hidden: { opacity: 0, scale: 0.4 },
  pulse: {
    opacity: [0.7, 0],
    scale: [0.4, 1.8],
    transition: { duration: 0.55, ease: "easeOut" },
  },
};
