import { render, screen } from "@testing-library/react";

import { AppHeader } from "./AppHeader";

describe("AppHeader", () => {
  it("renders title, subtitle, and author credits", () => {
    render(<AppHeader title="Global Debt Atlas" subtitle="Visualizando deuda soberana" />);

    expect(screen.getByText("Global Debt Atlas")).toBeInTheDocument();
    expect(screen.getByText("Visualizando deuda soberana")).toBeInTheDocument();
    expect(screen.getByText("Info del autor")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Daniel Limon" })).toHaveAttribute("href", "https://econopapi.com");
    expect(screen.getByRole("img", { name: "Logo de Daniel Limon" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Perfil de Daniel Limon en econopapi.com" })).toHaveAttribute("href", "https://econopapi.com");
    expect(screen.getByRole("link", { name: "dani@dlimon.net" })).toHaveAttribute("href", "mailto:dani@dlimon.net");
  });

  it("renders optional header actions when provided", () => {
    render(
      <AppHeader
        title="Global Debt Atlas"
        subtitle="Visualizando deuda soberana"
        actions={<a href="https://example.com/docs">Project documentation</a>}
      />,
    );

    expect(screen.getByRole("link", { name: "Project documentation" })).toHaveAttribute("href", "https://example.com/docs");
  });
});
