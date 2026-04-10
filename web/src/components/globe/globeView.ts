export type GlobeView = {
  lat: number;
  lng: number;
  altitude: number;
};

export const DEFAULT_GLOBE_VIEW: GlobeView = { lat: +1, lng: -85, altitude: 1.5 };

const REGION_GLOBE_VIEWS: Record<string, GlobeView> = {
  "East Asia & Pacific": { lat: 21, lng: 126, altitude: 1.52 },
  "Europe & Central Asia": { lat: 49, lng: 56, altitude: 1.58 },
  "Latin America & Caribbean": DEFAULT_GLOBE_VIEW,
  "Middle East & North Africa": { lat: 27, lng: 34, altitude: 1.56 },
  "Middle East, North Africa, Afghanistan & Pakistan": { lat: 27, lng: 34, altitude: 1.56 },
  "North America": { lat: 46, lng: -102, altitude: 1.5 },
  "South Asia": { lat: 22, lng: 79, altitude: 1.56 },
  "Sub-Saharan Africa": { lat: 1, lng: 21, altitude: 1.58 },
};

export function getGlobeViewForRegion(region?: string | null): GlobeView {
  if (!region) {
    return DEFAULT_GLOBE_VIEW;
  }

  return REGION_GLOBE_VIEWS[region] ?? DEFAULT_GLOBE_VIEW;
}
