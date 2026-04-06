import { create } from "zustand";

type HoveredCountry = {
  iso3: string;
  name: string;
  debtPctGdp: number | null;
  debtTotalUsd: number | null;
};

type GlobeState = {
  hoveredCountry: HoveredCountry | null;
  setHoveredCountry: (country: HoveredCountry | null) => void;
};

export const useGlobeStore = create<GlobeState>((set) => ({
  hoveredCountry: null,
  setHoveredCountry: (country) => set({ hoveredCountry: country }),
}));
