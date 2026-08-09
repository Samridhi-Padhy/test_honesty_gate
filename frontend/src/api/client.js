/**
 * Client for the Test Honesty Gate API.
 *
 * The contract shape is locked in docs/CONTRACTS.md and must not be
 * reshaped here. If a field looks wrong, the contract is the source of
 * truth and whoever broke it fixes their own side.
 */

const API_BASE =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// The gate runs 5 real pytest subprocesses, which can take 25-35 seconds on Render.
// 60 seconds is a ceiling, not an expectation, so a slow runner shows an
// error instead of hanging the UI forever.
const REQUEST_TIMEOUT_MS = 60000;

export async function fetchGateResult({ mock = false } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const url = `${API_BASE}/gate${mock ? "?mock=true" : ""}`;
    const response = await fetch(url, { signal: controller.signal });

    if (!response.ok) {
      throw new Error(
        `Gate API returned ${response.status} ${response.statusText}`
      );
    }

    const data = await response.json();

    if (!data || typeof data.verdict !== "string") {
      throw new Error("Gate API returned a response that is not the contract shape");
    }

    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The gate took too long to respond. Is the backend running?", { cause: error });
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
