import { act, render, screen } from "@testing-library/react";

import { MetricCounter } from "./MetricCounter";

describe("MetricCounter", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("animates numeric values to the final formatted output", () => {
    render(
      <MetricCounter
        label="Total debt"
        value={120}
        durationMs={300}
        formatter={(value) => (value === null ? "N/A" : `${Math.round(value)}`)}
      />,
    );

    expect(screen.getByText("Total debt")).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(320);
    });

    expect(screen.getByText("120")).toBeInTheDocument();
  });

  it("renders N/A when value is null", () => {
    render(<MetricCounter label="Debt / GDP" value={null} formatter={() => "N/A"} />);

    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});
