import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/react";

import { GlobeLegend } from "./GlobeLegend";

describe("GlobeLegend", () => {
  it("renders min and max percentages", () => {
    render(<GlobeLegend minDebtPctGdp={5.2} maxDebtPctGdp={123.9} />);

    expect(screen.getByText("Intensidad de deuda externa (% PIB)")).toBeInTheDocument();
    expect(screen.getByText("5.2%")).toBeInTheDocument();
    expect(screen.getByText("123.9%")).toBeInTheDocument();
  });

  it("allows selecting a debt band", async () => {
    const user = userEvent.setup();
    const onBandChange = jest.fn();

    render(
      <GlobeLegend minDebtPctGdp={5.2} maxDebtPctGdp={123.9} selectedBand="all" onBandChange={onBandChange} />,
    );

    await user.click(screen.getByRole("button", { name: "Alta" }));

    expect(onBandChange).toHaveBeenCalledWith("high");
  });

  it("renders fallback mode and coverage metadata", () => {
    render(
      <GlobeLegend
        minDebtPctGdp={7}
        maxDebtPctGdp={12}
        mode="total_external_debt_usd_log"
        availableCountries={120}
        totalCountries={217}
      />,
    );

    expect(screen.getByText("Intensidad de deuda externa (fallback: deuda externa absoluta)")).toBeInTheDocument();
    expect(screen.getByText("Cobertura de datos: 120/217")).toBeInTheDocument();
  });
});
