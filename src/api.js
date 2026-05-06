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

// Safety
export async function getSafety(propertyId) {
  const res = await fetch(`${BASE}/safety/${propertyId}`);
  if (!res.ok) throw new Error("Failed to fetch safety data");
  return res.json();
}

export async function submitSafetyVote(propertyId, data) {
  const res = await fetch(`${BASE}/safety/${propertyId}/vote`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Vote failed");
  return res.json();
}

// Forum
export async function fetchForumPosts(params = {}) {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== "" && v !== null && v !== undefined)
  ).toString();
  const res = await fetch(`${BASE}/forum/${qs ? `?${qs}` : ""}`);
  if (!res.ok) throw new Error("Failed to fetch posts");
  return res.json();
}

export async function createForumPost(data) {
  const res = await fetch(`${BASE}/forum/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "Failed"); }
  return res.json();
}

export async function getForumPost(postId) {
  const res = await fetch(`${BASE}/forum/${postId}`);
  if (!res.ok) throw new Error("Post not found");
  return res.json();
}

export async function upvotePost(postId) {
  const res = await fetch(`${BASE}/forum/${postId}/upvote`, { method: "POST" });
  if (!res.ok) throw new Error("Upvote failed");
  return res.json();
}

export async function getComments(postId) {
  const res = await fetch(`${BASE}/forum/${postId}/comments`);
  if (!res.ok) throw new Error("Failed to fetch comments");
  return res.json();
}

export async function addComment(postId, data) {
  const res = await fetch(`${BASE}/forum/${postId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Comment failed");
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
