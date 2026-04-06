import type { FeatureCollection, Geometry } from "geojson";
import Globe from "react-globe.gl";
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import countries110m from "world-atlas/countries-110m.json";
import countries from "world-countries";

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

function getDebtRange(points: GlobeDataPoint[]): { min: number; max: number } {
  const values = points
    .map((point) => point.debt_pct_gdp)
    .filter((value): value is number => value !== null && Number.isFinite(value));

  if (values.length === 0) {
    return { min: 0, max: 1 };
  }

  return {
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

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
  const pointsByIso3 = useMemo(() => {
    return new Map(points.map((point) => [point.iso3, point]));
  }, [points]);

  const countryNameByIso3 = useMemo(() => {
    return countries.reduce<Map<string, string>>((acc, country) => {
      if (country.cca3 && country.name?.common) {
        acc.set(country.cca3, country.name.common);
      }

      return acc;
    }, new Map());
  }, []);

  const iso3ByNumericCode = useMemo(() => {
    return countries.reduce<Map<number, string>>((acc, country) => {
      const ccn3 = Number(country.ccn3);
      if (Number.isFinite(ccn3) && country.cca3) {
        acc.set(ccn3, country.cca3);
      }

      return acc;
    }, new Map());
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadGeoFeatures() {
      const topology = countries110m as TopologyInput;
      const topojson = await import("topojson-client");
      const featureCollection = topojson.feature(
        topology as unknown as Parameters<typeof topojson.feature>[0],
        topology.objects.countries as Parameters<typeof topojson.feature>[1],
      ) as FeatureCollection;

      if (cancelled) {
        return;
      }

      const mappedFeatures = (featureCollection.features ?? [])
        .map((feature) => {
          const numericId = Number(feature.id);
          const iso3 = iso3ByNumericCode.get(numericId);

          return {
            ...(feature as CountryFeature),
            properties: {
              ...(feature.properties as CountryFeatureProperties),
              iso3,
              name: iso3 ? countryNameByIso3.get(iso3) : undefined,
            },
          };
        })
        .filter((feature) => Boolean(feature.properties.iso3)) as CountryFeature[];

      setGeoFeatures(mappedFeatures);
    }

    void loadGeoFeatures();

    return () => {
      cancelled = true;
    };
  }, [countryNameByIso3, iso3ByNumericCode]);

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
    setHoveredCountry({
      iso3,
      name: point?.name_en ?? feature.properties.name ?? iso3,
      debtPctGdp: point?.debt_pct_gdp ?? null,
      debtTotalUsd: point?.total_external_debt_usd ?? null,
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
    if (!point || point.debt_pct_gdp === null || !Number.isFinite(point.debt_pct_gdp)) {
      return "rgba(51, 65, 85, 0.55)";
    }

    return getDebtColor(point.debt_pct_gdp, debtRange.min, debtRange.max);
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
