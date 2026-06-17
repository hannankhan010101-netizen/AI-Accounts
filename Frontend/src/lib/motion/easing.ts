/** Shared easing curves — matches Linear/Stripe-style polish. */

export const easeOut = [0.16, 1, 0.3, 1] as const;
export const easeInOut = [0.45, 0, 0.15, 1] as const;
export const easeSpringOut = [0.34, 1.56, 0.64, 1] as const;

export const transitionEase = {
  out: easeOut,
  inOut: easeInOut,
  springOut: easeSpringOut,
} as const;
