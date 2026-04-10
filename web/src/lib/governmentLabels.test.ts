import {
  buildLeaderLabel,
  compactLeaderName,
  estimateTextWidth,
  truncateTextToWidth,
} from "./governmentLabels";

describe("governmentLabels", () => {
  it("compacts leader names to first and last token", () => {
    expect(compactLeaderName("Silvio Antonio Berlusconi")).toBe("Silvio Berlusconi");
    expect(compactLeaderName("Giorgia Meloni")).toBe("Giorgia Meloni");
  });

  it("truncates labels with ellipsis when width is constrained", () => {
    const label = truncateTextToWidth("Silvio Berlusconi", 42);
    expect(label.endsWith("…")).toBe(true);
    expect(estimateTextWidth(label)).toBeLessThanOrEqual(42.5);
  });

  it("builds compact readable labels before truncating", () => {
    const label = buildLeaderLabel("Sergio Mattarella", 80);
    expect(label).toBe("Sergio Matta…");

    const compact = buildLeaderLabel("George Herbert Walker Bush", 200);
    expect(compact).toBe("George Bush");
  });

  it("preserves full Spanish names when possible", () => {
    const label = buildLeaderLabel("Enrique Peña Nieto", 200, { locale: "es" });
    expect(label).toBe("Enrique Peña Nieto");
  });

  it("falls back to first name + last two tokens for Spanish names", () => {
    const label = buildLeaderLabel("Andrés Manuel López Obrador", 120, { locale: "es" });
    expect(label).toBe("Andrés López Obrador");

    const labelWithParticle = buildLeaderLabel("Cristina Fernández de Kirchner", 120, { locale: "es" });
    expect(labelWithParticle).toBe("Cristina de Kirchner");
  });

  it("hides unresolved wikidata identifiers used as pseudo labels", () => {
    expect(buildLeaderLabel("Q5771800", 120, { locale: "es" })).toBe("");
    expect(buildLeaderLabel("Q5771800", 120, { locale: "en" })).toBe("");
  });
});
