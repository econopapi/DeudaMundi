import type { JSX } from "react";
import type { GlobeDataPoint } from "../../types/api";

type CountryMarkersProps = {
  points: GlobeDataPoint[];
  minDebtPctGdp: number;
  maxDebtPctGdp: number;
  onSelectCountry: (iso3: string) => void;
};

export function CountryMarkers({
  points: _points,
  minDebtPctGdp: _minDebtPctGdp,
  maxDebtPctGdp: _maxDebtPctGdp,
  onSelectCountry: _onSelectCountry,
}: CountryMarkersProps): JSX.Element {
  return <></>;
}
