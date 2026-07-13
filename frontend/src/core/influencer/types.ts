export interface InfluencerDemographics {
  age_18_24: number;
  age_25_34: number;
  age_35_plus: number;
  gender_male: number;
  top_cities: string[];
}

export interface BrandHistory {
  brand: string;
  year: number;
}

export interface Influencer {
  platform: string;
  platform_uid: string;
  nickname: string;
  avatar_url: string;
  category: string;
  sub_categories: string[];
  followers_count: number;
  avg_likes: number;
  avg_comments: number;
  avg_shares: number;
  engagement_rate: number;
  avg_gmv: number;
  avg_sales: number;
  price_range_min: number;
  price_range_max: number;
  demographics: InfluencerDemographics;
  content_style: string[];
  brand_history: BrandHistory[];
  data_source: string;
  total_score?: number;
}

export interface SearchCriteria {
  keyword?: string;
  platform?: string;
  category?: string;
  follower_min?: number;
  follower_max?: number;
  engagement_min?: number;
  engagement_max?: number;
  price_min?: number;
  price_max?: number;
  gmv_min?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
}

export const CATEGORIES = [
  "美妆", "食品", "服饰", "母婴", "3C数码", "家居", "运动", "图书",
] as const;

export const SORT_OPTIONS = [
  { value: "followers_count", label: "粉丝数" },
  { value: "engagement_rate", label: "互动率" },
  { value: "avg_gmv", label: "场均GMV" },
  { value: "avg_sales", label: "场均销量" },
  { value: "price_range_min", label: "报价" },
] as const;

export function formatFollowers(n: number): string {
  if (n >= 10000_0000) return `${(n / 10000_0000).toFixed(1)}亿`;
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`;
  return n.toString();
}

export function formatPrice(n: number): string {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`;
  return `¥${n.toLocaleString()}`;
}

export function getInitials(nickname: string): string {
  return nickname.slice(0, 2) || "?";
}

export interface DimensionScores {
  match: number;
  reach: number;
  sales: number;
  value: number;
}

/** Derive approximate dimension scores (0-100) from available metrics (MVP). */
export function computeDimensionScores(inf: Influencer): DimensionScores {
  const toPercent = (v: number, max: number) =>
    Math.min(100, Math.round((v / max) * 100));

  const reachScore = Math.max(
    toPercent(inf.followers_count, 10_000_000),
    Math.min(100, Math.round(inf.engagement_rate * 1000)),
  );

  const salesScore = toPercent(inf.avg_sales, 100_000);

  const valueScore =
    inf.price_range_min > 0
      ? toPercent(inf.avg_gmv / inf.price_range_min, 50)
      : 50;

  return {
    match: inf.total_score ?? Math.round((reachScore + salesScore + valueScore) / 3),
    reach: reachScore,
    sales: salesScore,
    value: valueScore,
  };
}

export const DIMENSION_LABELS: Record<string, string> = {
  match: "匹配度",
  reach: "传播力",
  sales: "带货力",
  value: "性价比",
};

export function stripBasicMarkdown(md: string): string {
  return md
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/\*(.+?)\*/g, "$1")
    .replace(/`(.+?)`/g, "$1")
    .replace(/\[(.+?)\]\(.+?\)/g, "$1")
    .replace(/^[-*+]\s+/gm, "• ")
    .replace(/^\d+\.\s+/gm, "")
    .replace(/^>\s?/gm, "")
    .replace(/---+/g, "─".repeat(40));
}

// ── Selection types ──

export interface Selection {
  id: string;
  title: string;
  goal?: string;
  criteria?: Record<string, unknown>;
  status: string;
  created_at?: string;
}

export interface Candidate {
  id: string;
  influencer_id: string;
  match_score: number;
  match_reason?: string;
  status: string;
  added_by: string;
  notes?: string;
}

export interface SelectionDetail extends Selection {
  candidates: Candidate[];
}

export const CANDIDATE_STATUSES = [
  { value: "shortlisted", label: "待联系" },
  { value: "contacted", label: "已联系" },
  { value: "selected", label: "已选定" },
  { value: "rejected", label: "已拒绝" },
] as const;

export const SELECTION_STATUS_LABELS: Record<string, string> = {
  draft: "草稿",
  in_progress: "进行中",
  completed: "已完成",
  archived: "已归档",
};
