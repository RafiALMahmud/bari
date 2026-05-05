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

export async function getAvailability(propertyId) {
  const res = await fetch(`${BASE}/bookings/property/${propertyId}/availability`);
  if (!res.ok) throw new Error("Failed to fetch availability");
  return res.json();
}

export async function createBooking(data) {
  const res = await fetch(`${BASE}/bookings/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Booking failed");
  }
  return res.json();
}

export async function getChatMessages(propertyId, sessionToken) {
  const res = await fetch(`${BASE}/chat/${propertyId}/${sessionToken}`);
  if (!res.ok) throw new Error("Failed to load messages");
  return res.json();
}

export async function sendChatMessage(data) {
  const res = await fetch(`${BASE}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to send message");
  return res.json();
}

export async function aiChat(messages, filters = {}) {
  const res = await fetch(`${BASE}/ai/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, ...filters }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "AI unavailable");
  }
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
