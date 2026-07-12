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
