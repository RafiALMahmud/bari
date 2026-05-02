const BASE = "http://localhost:8001/api";

export async function fetchProperties(params = {}) {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== "" && v !== null && v !== undefined)
  ).toString();
  const res = await fetch(`${BASE}/properties${qs ? `?${qs}` : ""}`);
  if (!res.ok) throw new Error("Failed to fetch properties");
  return res.json();
}

export async function fetchProperty(id) {
  const res = await fetch(`${BASE}/properties/${id}`);
  if (!res.ok) throw new Error("Property not found");
  return res.json();
}

export async function createProperty(data) {
  const res = await fetch(`${BASE}/properties/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(JSON.stringify(err.detail));
  }
  return res.json();
}

export async function uploadPhoto(propertyId, file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/properties/${propertyId}/photos`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function uploadDocument(propertyId, file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/properties/${propertyId}/documents`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}
