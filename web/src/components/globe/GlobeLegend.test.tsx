import { render, screen } from "@testing-library/react";

import { GlobeLegend } from "./GlobeLegend";

describe("GlobeLegend", () => {
  it("renders min and max percentages", () => {
    render(<GlobeLegend minDebtPctGdp={5.2} maxDebtPctGdp={123.9} />);

    expect(screen.getByText("Debt % GDP intensity")).toBeInTheDocument();
    expect(screen.getByText("5.2%")).toBeInTheDocument();
    expect(screen.getByText("123.9%")).toBeInTheDocument();
  });
});
