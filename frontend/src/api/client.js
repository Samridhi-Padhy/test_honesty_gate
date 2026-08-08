export async function fetchGateResult({ mock = false } = {}) {
  const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const url = mock ? `${baseUrl}/gate?mock=true` : `${baseUrl}/gate`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch gate result");
  }
  return response.json();
}