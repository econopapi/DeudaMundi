import type { FeatureCollection, Geometry } from "geojson";
import Globe from "react-globe.gl";
import { feature } from "topojson-client";
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import countries110m from "world-atlas/countries-110m.json";

import { useGlobeStore } from "../../store/globeStore";
import type { GlobeDataPoint } from "../../types/api";
import { getDebtColor } from "./globeColors";

type CountryFeatureProperties = {
  iso3?: string;
  name?: string;
};

type CountryFeature = {
  type: "Feature";
  id?: string | number;
  properties: CountryFeatureProperties;
  geometry: Geometry;
};

type TopologyInput = {
  type: "Topology";
  objects: {
    countries: unknown;
  };
};

type GlobeSceneProps = {
  points: GlobeDataPoint[];
};

type IntensityMode = "debt_pct_gdp" | "total_external_debt_usd_log";

const TOPO_NAME_TO_POINT_NAME_ALIASES: Record<string, string> = {
  "united states of america": "united states",
  "dominican rep": "dominican republic",
  "dem rep congo": "congo democratic republic",
  "central african rep": "central african republic",
  "eq guinea": "equatorial guinea",
  "bosnia and herzegovina": "bosnia and herzegovina",
  "czech rep": "czech republic",
  "solomon is": "solomon islands",
  "trinidad and tobago": "trinidad and tobago",
  "s sudan": "south sudan",
  "w sahara": "western sahara",
  "falkland is": "falkland islands",
  "timor leste": "timor leste",
};

function normalizeCountryName(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9 ]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function getIntensityValue(point: GlobeDataPoint, mode: IntensityMode): number | null {
  if (mode === "debt_pct_gdp") {
    const ratio = point.debt_pct_gdp;
    return ratio !== null && Number.isFinite(ratio) ? ratio : null;
  }

  const totalDebt = point.total_external_debt_usd;
  if (totalDebt === null || !Number.isFinite(totalDebt) || totalDebt <= 0) {
    return null;
  }

  return Math.log10(totalDebt);
}

function getDebtRange(points: GlobeDataPoint[]): { min: number; max: number } {
  const ratioValues = points
    .map((point) => point.debt_pct_gdp)
    .filter((value): value is number => value !== null && Number.isFinite(value));

  if (ratioValues.length > 0) {
    return {
      min: Math.min(...ratioValues),
      max: Math.max(...ratioValues),
    };
  }

  const debtValues = points
    .map((point) => point.total_external_debt_usd)
    .filter((value): value is number => value !== null && Number.isFinite(value) && value > 0)
    .map((value) => Math.log10(value));

  if (debtValues.length > 0) {
    return {
      min: Math.min(...debtValues),
      max: Math.max(...debtValues),
    };
  }

  return { min: 0, max: 1 };
}

function getIntensityMode(points: GlobeDataPoint[]): IntensityMode {
  const hasRatio = points.some((point) => point.debt_pct_gdp !== null && Number.isFinite(point.debt_pct_gdp));
  return hasRatio ? "debt_pct_gdp" : "total_external_debt_usd_log";
}

const topology = countries110m as TopologyInput;
const countryFeatures = feature(
  topology as unknown as Parameters<typeof feature>[0],
  topology.objects.countries as Parameters<typeof feature>[1],
) as FeatureCollection;

export function GlobeScene({ points }: GlobeSceneProps) {
  const navigate = useNavigate();
  const setHoveredCountry = useGlobeStore((state) => state.setHoveredCountry);
  const globeRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [geoFeatures, setGeoFeatures] = useState<CountryFeature[]>([]);

  useEffect(() => {
    const controls = globeRef.current?.controls?.();
    if (!controls) {
      return;
    }

    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.5;
    controls.enablePan = false;
    controls.minDistance = 120;
    controls.maxDistance = 380;
    controls.rotateSpeed = 0.5;
  }, [dimensions.height, dimensions.width]);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry) {
        return;
      }

      setDimensions({
        width: Math.floor(entry.contentRect.width),
        height: Math.floor(entry.contentRect.height),
      });
    });

    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
    };
  }, []);

  const debtRange = useMemo(() => getDebtRange(points), [points]);
  const intensityMode = useMemo(() => getIntensityMode(points), [points]);
  const pointsByIso3 = useMemo(() => {
    return new Map(points.map((point) => [point.iso3, point]));
  }, [points]);

  const iso3ByNormalizedName = useMemo(() => {
    return points.reduce<Map<string, string>>((acc, point) => {
      acc.set(normalizeCountryName(point.name_en), point.iso3);
      return acc;
    }, new Map());
  }, [points]);

  useEffect(() => {
    const mappedFeatures = (countryFeatures.features ?? [])
      .map((feature) => {
        const rawName = String((feature.properties as CountryFeatureProperties | undefined)?.name ?? "");
        const normalizedTopoName = normalizeCountryName(rawName);
        const aliasedName = TOPO_NAME_TO_POINT_NAME_ALIASES[normalizedTopoName] ?? normalizedTopoName;
        const iso3 = iso3ByNormalizedName.get(aliasedName);

        return {
          ...(feature as CountryFeature),
          properties: {
            ...(feature.properties as CountryFeatureProperties),
            iso3,
            name: rawName || iso3,
          },
        };
      })
      .filter((feature) => Boolean(feature.properties.iso3)) as CountryFeature[];

    setGeoFeatures(mappedFeatures);
  }, [iso3ByNormalizedName]);

  const handlePolygonHover = (feature: CountryFeature | null) => {
    if (!feature) {
      setHoveredCountry(null);
      return;
    }

    const iso3 = feature.properties.iso3;
    if (!iso3) {
      setHoveredCountry(null);
      return;
    }

    const point = pointsByIso3.get(iso3);
    const debtRatio = point?.debt_pct_gdp ?? null;
    const fallbackDebt = point?.total_external_debt_usd ?? null;

    setHoveredCountry({
      iso3,
      name: point?.name_en ?? feature.properties.name ?? iso3,
      debtPctGdp: debtRatio,
      debtTotalUsd: fallbackDebt,
    });
  };

  const handlePolygonClick = (feature: CountryFeature) => {
    const iso3 = feature.properties.iso3;
    if (!iso3) {
      return;
    }

    navigate(`/country/${iso3.toLowerCase()}`);
  };

  const getPolygonColor = (feature: CountryFeature) => {
    const iso3 = feature.properties.iso3;
    if (!iso3) {
      return "rgba(51, 65, 85, 0.55)";
    }

    const point = pointsByIso3.get(iso3);
    if (!point) {
      return "rgba(51, 65, 85, 0.55)";
    }

    const intensityValue = getIntensityValue(point, intensityMode);
    if (intensityValue === null) {
      return "rgba(51, 65, 85, 0.55)";
    }

    return getDebtColor(intensityValue, debtRange.min, debtRange.max);
  };

  return (
    <div ref={containerRef} className="h-[560px] w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950">
      {dimensions.width > 0 && dimensions.height > 0 && (
        <Globe
          ref={globeRef}
          width={dimensions.width}
          height={dimensions.height}
          backgroundColor="#020617"
          showAtmosphere
          atmosphereColor="#60a5fa"
          atmosphereAltitude={0.18}
          polygonsData={geoFeatures}
          polygonAltitude={0.012}
          polygonCapColor={(feature) => getPolygonColor(feature as CountryFeature)}
          polygonSideColor={() => "rgba(15, 23, 42, 0.4)"}
          polygonStrokeColor={() => "rgba(186, 230, 253, 0.55)"}
          polygonsTransitionDuration={250}
          onPolygonHover={(feature) => handlePolygonHover((feature as CountryFeature | null) ?? null)}
          onPolygonClick={(feature) => handlePolygonClick(feature as CountryFeature)}
        />
      )}
    </div>
  );
}
