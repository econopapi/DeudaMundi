import { type RefObject, useEffect, useState } from "react";

const MOBILE_MAX_VIEWPORT_WIDTH = 767;

export function isMobileViewport(width: number): boolean {
  return width <= MOBILE_MAX_VIEWPORT_WIDTH;
}

export function getLatestChartScrollLeft(scrollWidth: number, clientWidth: number): number {
  return Math.max(0, scrollWidth - clientWidth);
}

export function useMobileChartScrollToLatest(
  scrollRef: RefObject<HTMLElement>,
  dependencyKey: string,
): boolean {
  const [showHint, setShowHint] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const container = scrollRef.current;
    if (!container) {
      return;
    }

    const mobile = isMobileViewport(window.innerWidth);
    if (!mobile) {
      setShowHint(false);
      return;
    }

    const hasOverflow = container.scrollWidth > container.clientWidth + 4;
    setShowHint(hasOverflow);

    if (!hasOverflow) {
      return;
    }

    const targetScrollLeft = getLatestChartScrollLeft(container.scrollWidth, container.clientWidth);

    let frameId2 = 0;
    const frameId1 = window.requestAnimationFrame(() => {
      frameId2 = window.requestAnimationFrame(() => {
        if (scrollRef.current) {
          scrollRef.current.scrollLeft = targetScrollLeft;
        }
      });
    });

    return () => {
      window.cancelAnimationFrame(frameId1);
      if (frameId2) {
        window.cancelAnimationFrame(frameId2);
      }
    };
  }, [scrollRef, dependencyKey]);

  return showHint;
}
