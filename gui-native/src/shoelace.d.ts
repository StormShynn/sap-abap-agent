// Type declarations cho Shoelace deep imports (side-effect only) và custom elements.

declare module "@shoelace-style/shoelace/dist/themes/light.css";
declare module "@shoelace-style/shoelace/dist/themes/dark.css";
declare module "@shoelace-style/shoelace/dist/components/alert/alert.js";
declare module "@shoelace-style/shoelace/dist/components/badge/badge.js";
declare module "@shoelace-style/shoelace/dist/components/progress-bar/progress-bar.js";
declare module "@shoelace-style/shoelace/dist/utilities/icon-library.js";

declare global {
  // Shoelace ship types rieng (SlAlert/SlBadge/SlProgressBar + global map)
  // trong dist/components/*.d.ts — khong can augment lai o day.
}

export {};
