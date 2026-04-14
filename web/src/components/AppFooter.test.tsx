import { render, screen } from "@testing-library/react";

import { AppFooter } from "./AppFooter";

describe("AppFooter", () => {
  it("renders project name, local provenance, and compact author credits", () => {
    render(<AppFooter />);

    expect(screen.getByText("DeudaMundi · Atlas de Deuda Externa")).toBeInTheDocument();
    expect(screen.getByText("Hecho con ❤️ en México")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Daniel Limon" })).toHaveAttribute("href", "https://econopapi.com");
    expect(screen.getByRole("link", { name: "dani@dlimon.net" })).toHaveAttribute("href", "mailto:dani@dlimon.net");
  });
});