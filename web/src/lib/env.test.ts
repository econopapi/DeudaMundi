import { getApiBaseUrlForHost } from "./env";

describe("getApiBaseUrlForHost", () => {
  it("uses localhost API when frontend host is localhost", () => {
    expect(getApiBaseUrlForHost("localhost")).toBe("http://localhost:8000");
  });

  it("uses same LAN host for private IPv4", () => {
    expect(getApiBaseUrlForHost("192.168.3.109")).toBe("http://192.168.3.109:8000");
  });

  it("uses same LAN host for mDNS local hostnames", () => {
    expect(getApiBaseUrlForHost("macbook.local")).toBe("http://macbook.local:8000");
  });

  it("keeps production API base for public hosts", () => {
    expect(getApiBaseUrlForHost("deudamundi.econopapi.com")).toBe("https://deudamundi.econopapi.com");
  });
});
