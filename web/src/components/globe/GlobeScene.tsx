import { OrbitControls, Sphere, Stars } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";

import type { GlobeDataPoint } from "../../types/api";
import { CountryMarkers } from "./CountryMarkers";

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

  const debtRange = useMemo(() => getDebtRange(points), [points]);

  return (
    <div className="h-[560px] w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950">
      <Canvas camera={{ position: [0, 0, 2.6], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[4, 2, 2]} intensity={1.2} />
        <pointLight position={[-3, -2, -2]} intensity={0.6} />

        <Stars radius={80} depth={40} count={2500} factor={3} saturation={0} fade speed={0.5} />

        <Sphere args={[1, 64, 64]}>
          <meshStandardMaterial color="#0f172a" roughness={0.9} metalness={0.05} />
        </Sphere>

        <CountryMarkers
          points={points}
          minDebtPctGdp={debtRange.min}
          maxDebtPctGdp={debtRange.max}
          onSelectCountry={(iso3) => navigate(`/country/${iso3.toLowerCase()}`)}
        />

        <OrbitControls
          enablePan={false}
          minDistance={1.4}
          maxDistance={4}
          rotateSpeed={0.7}
          autoRotate
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </div>
  );
}
