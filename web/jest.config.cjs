module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  moduleNameMapper: {
    "\\.(css|less|sass|scss)$": "identity-obj-proxy",
    "\\.svg$": "<rootDir>/src/test/fileMock.ts",
  },
  testMatch: ["**/*.test.ts", "**/*.test.tsx"],
};
