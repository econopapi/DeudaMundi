import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/react";

import { GlobeLegend } from "./GlobeLegend";

describe("GlobeLegend", () => {
  it("renders min and max percentages", () => {
    render(<GlobeLegend minDebtPctGdp={5.2} maxDebtPctGdp={123.9} />);

    expect(screen.getByText("Debt % GDP intensity")).toBeInTheDocument();
    expect(screen.getByText("5.2%")).toBeInTheDocument();
    expect(screen.getByText("123.9%")).toBeInTheDocument();
  });

  it("allows selecting a debt band", async () => {
    const user = userEvent.setup();
    const onBandChange = jest.fn();

    render(
      <GlobeLegend minDebtPctGdp={5.2} maxDebtPctGdp={123.9} selectedBand="all" onBandChange={onBandChange} />,
    );

    await user.click(screen.getByRole("button", { name: "High" }));

    expect(onBandChange).toHaveBeenCalledWith("high");
  });
});
