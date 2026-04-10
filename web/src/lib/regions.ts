export const HOME_REGION_OPTIONS = [
  "East Asia & Pacific",
  "Europe & Central Asia",
  "Latin America & Caribbean",
  "Middle East & North Africa",
  "North America",
  "South Asia",
  "Sub-Saharan Africa",
] as const;

export const RANKINGS_REGION_OPTIONS = [
  "East Asia & Pacific",
  "Europe & Central Asia",
  "Latin America & Caribbean",
  "Middle East & North Africa",
  "Middle East, North Africa, Afghanistan & Pakistan",
  "North America",
  "South Asia",
  "Sub-Saharan Africa",
] as const;

type RegionOptions = readonly string[];

function isRegionInOptions<T extends RegionOptions>(region: string, options: T): region is T[number] {
  return options.includes(region);
}

export function isHomeRegion(region: string): region is (typeof HOME_REGION_OPTIONS)[number] {
  return isRegionInOptions(region, HOME_REGION_OPTIONS);
}

export function isRankingsRegion(region: string): region is (typeof RANKINGS_REGION_OPTIONS)[number] {
  return isRegionInOptions(region, RANKINGS_REGION_OPTIONS);
}
