import type { Influencer, PaginatedResponse, SearchCriteria } from "./types";

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
