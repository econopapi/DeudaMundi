import { presentEquivalences } from "./equivalences";

describe("presentEquivalences", () => {
  it("maps known labels to localized titles and icons", () => {
    const result = presentEquivalences(
      [
        {
          label: "hospitales_publicos",
          value: 12.5,
          description: "unused",
        },
      ],
      "es",
    );

    expect(result[0]).toMatchObject({
      icon: "🏥",
      title: "Hospitales públicos potenciales",
      value: 12.5,
    });
  });

  it("falls back gracefully for unknown labels", () => {
    const result = presentEquivalences(
      [
        {
          label: "otro_indicador",
          value: 1,
          description: "Fallback description",
        },
      ],
      "en",
    );

    expect(result[0]).toMatchObject({
      icon: "💡",
      title: "Otro Indicador",
      description: "Fallback description",
    });
  });
});
