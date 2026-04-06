import { render, screen } from "@testing-library/react";

import { AppHeader } from "./AppHeader";

describe("AppHeader", () => {
  it("renders title and subtitle", () => {
    render(<AppHeader title="Global Debt Atlas" subtitle="Visualizando deuda soberana" />);

    expect(screen.getByText("Global Debt Atlas")).toBeInTheDocument();
    expect(screen.getByText("Visualizando deuda soberana")).toBeInTheDocument();
  });
});
