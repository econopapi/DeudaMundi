import { Sphere } from "@react-three/drei";
import type { ThreeEvent } from "@react-three/fiber";
import type { JSX } from "react";
import countries from "world-countries";

import { useGlobeStore } from "../../store/globeStore";
import type { GlobeDataPoint } from "../../types/api";
import { getDebtColor } from "./globeColors";

type CountryMarkersProps = {
  points: GlobeDataPoint[];
  minDebtPctGdp: number;
  maxDebtPctGdp: number;
  onSelectCountry: (iso3: string) => void;
};

type CountryLatLngMap = Record<string, [number, number]>;
type CountrySeed = {
  cca3?: string;
  latlng?: [number, number] | number[];
};

const countryLatLngMap: CountryLatLngMap = (countries as CountrySeed[]).reduce<CountryLatLngMap>((
  acc,
  country,
) => {
  const iso3 = country.cca3;
  const latlng = country.latlng;

  if (iso3 && Array.isArray(latlng) && latlng.length === 2) {
    acc[iso3] = [latlng[0], latlng[1]];
  }

  return acc;
}, {});

function latLngToCartesian(lat: number, lng: number, radius = 1.01): [number, number, number] {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);

  const x = -radius * Math.sin(phi) * Math.cos(theta);
  const y = radius * Math.cos(phi);
  const z = radius * Math.sin(phi) * Math.sin(theta);

  return [x, y, z];
}

export function CountryMarkers({
  points,
  minDebtPctGdp,
  maxDebtPctGdp,
  onSelectCountry,
}: CountryMarkersProps): JSX.Element {
  const setHoveredCountry = useGlobeStore((state) => state.setHoveredCountry);

  return (
    <group>
      {points.map((point) => {
        const latLng = countryLatLngMap[point.iso3];
        if (!latLng) {
          return null;
        }

        const [lat, lng] = latLng;
        const position = latLngToCartesian(lat, lng);
        const color = getDebtColor(point.debt_pct_gdp ?? 0, minDebtPctGdp, maxDebtPctGdp);

        const markerSize = point.total_external_debt_usd ? 0.012 : 0.009;

        const handlePointerEnter = (event: ThreeEvent<PointerEvent>) => {
          event.stopPropagation();
          setHoveredCountry({
            iso3: point.iso3,
            name: point.name_en,
            debtPctGdp: point.debt_pct_gdp,
            debtTotalUsd: point.total_external_debt_usd,
          });
          document.body.style.cursor = "pointer";
        };

        const handlePointerLeave = () => {
          setHoveredCountry(null);
          document.body.style.cursor = "default";
        };

        return (
          <Sphere
            key={point.iso3}
            args={[markerSize, 10, 10]}
            position={position}
            onPointerEnter={handlePointerEnter}
            onPointerLeave={handlePointerLeave}
            onClick={(event) => {
              event.stopPropagation();
              onSelectCountry(point.iso3);
            }}
          >
            <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.2} />
          </Sphere>
        );
      })}
    </group>
  );
}
