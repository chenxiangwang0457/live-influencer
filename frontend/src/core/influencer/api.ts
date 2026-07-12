import type {
  Influencer,
  PaginatedResponse,
  SearchCriteria,
  Selection,
  SelectionDetail,
} from "./types";

const BASE = "/api/influencer";

export async function searchInfluencers(
  criteria: SearchCriteria,
): Promise<PaginatedResponse<Influencer>> {
  const params = new URLSearchParams();
  if (criteria.keyword) params.set("keyword", criteria.keyword);
  if (criteria.category) params.set("category", criteria.category);
  if (criteria.follower_min) params.set("follower_min", String(criteria.follower_min));
  if (criteria.follower_max) params.set("follower_max", String(criteria.follower_max));
  if (criteria.engagement_min) params.set("engagement_min", String(criteria.engagement_min));
  if (criteria.engagement_max) params.set("engagement_max", String(criteria.engagement_max));
  if (criteria.price_min) params.set("price_min", String(criteria.price_min));
  if (criteria.price_max) params.set("price_max", String(criteria.price_max));
  if (criteria.gmv_min) params.set("gmv_min", String(criteria.gmv_min));
  if (criteria.sort_by) params.set("sort_by", criteria.sort_by);
  if (criteria.sort_order) params.set("sort_order", criteria.sort_order);
  if (criteria.page) params.set("page", String(criteria.page));
  if (criteria.page_size) params.set("page_size", String(criteria.page_size));

  const res = await fetch(`${BASE}/search?${params}`);
  if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);
  return res.json();
}

export async function getInfluencerDetail(platformUid: string): Promise<Influencer> {
  const res = await fetch(`${BASE}/${platformUid}`);
  if (!res.ok) throw new Error(`Detail failed: ${res.statusText}`);
  return res.json();
}

export async function getInfluencerHistory(
  platformUid: string,
): Promise<{ platform_uid: string; brand_history: Influencer["brand_history"] }> {
  const res = await fetch(`${BASE}/${platformUid}/history`);
  if (!res.ok) throw new Error(`History failed: ${res.statusText}`);
  return res.json();
}

// ── Selection APIs ──

export async function listSelections(params?: {
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<PaginatedResponse<Selection>> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set("status", params.status);
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size) searchParams.set("page_size", String(params.page_size));

  const res = await fetch(`${BASE}/selections?${searchParams}`);
  if (!res.ok) throw new Error(`List selections failed: ${res.statusText}`);
  return res.json();
}

export async function createSelection(body: {
  title: string;
  goal?: string;
  criteria?: Record<string, unknown>;
}): Promise<Selection> {
  const res = await fetch(`${BASE}/selections`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Create selection failed: ${res.statusText}`);
  return res.json();
}

export async function getSelection(id: string): Promise<SelectionDetail> {
  const res = await fetch(`${BASE}/selections/${id}`);
  if (!res.ok) throw new Error(`Get selection failed: ${res.statusText}`);
  return res.json();
}

export async function updateSelection(
  id: string,
  body: { title?: string; status?: string },
): Promise<void> {
  const res = await fetch(`${BASE}/selections/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Update selection failed: ${res.statusText}`);
}

export async function addCandidate(
  selectionId: string,
  body: { influencer_id: string; added_by?: string },
): Promise<{ id: string }> {
  const res = await fetch(`${BASE}/selections/${selectionId}/candidates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Add candidate failed: ${res.statusText}`);
  return res.json();
}

export async function removeCandidate(
  selectionId: string,
  candidateId: string,
): Promise<void> {
  const res = await fetch(
    `${BASE}/selections/${selectionId}/candidates/${candidateId}`,
    { method: "DELETE" },
  );
  if (!res.ok) throw new Error(`Remove candidate failed: ${res.statusText}`);
}

export async function updateCandidate(
  selectionId: string,
  candidateId: string,
  body: { status?: string; notes?: string },
): Promise<void> {
  const res = await fetch(
    `${BASE}/selections/${selectionId}/candidates/${candidateId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
  if (!res.ok) throw new Error(`Update candidate failed: ${res.statusText}`);
}
