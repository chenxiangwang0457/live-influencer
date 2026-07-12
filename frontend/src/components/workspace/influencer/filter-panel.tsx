"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { SearchCriteria } from "@/core/influencer/types";
import { CATEGORIES, SORT_OPTIONS } from "@/core/influencer/types";

interface FilterPanelProps {
  onFilterChange: (criteria: Partial<SearchCriteria>) => void;
}

interface FilterState {
  category: string;
  followerMin: string;
  followerMax: string;
  engagementMin: string;
  engagementMax: string;
  priceMin: string;
  priceMax: string;
  sortBy: string;
  sortOrder: "asc" | "desc";
}

const DEFAULT_FILTER_STATE: FilterState = {
  category: "",
  followerMin: "",
  followerMax: "",
  engagementMin: "",
  engagementMax: "",
  priceMin: "",
  priceMax: "",
  sortBy: "",
  sortOrder: "desc",
};

function buildCriteria(state: FilterState): Partial<SearchCriteria> {
  const criteria: Partial<SearchCriteria> = {};

  if (state.category) criteria.category = state.category;

  const followerMin = parseFloat(state.followerMin);
  if (!Number.isNaN(followerMin)) criteria.follower_min = followerMin;

  const followerMax = parseFloat(state.followerMax);
  if (!Number.isNaN(followerMax)) criteria.follower_max = followerMax;

  const engagementMin = parseFloat(state.engagementMin);
  if (!Number.isNaN(engagementMin)) criteria.engagement_min = engagementMin / 100;

  const engagementMax = parseFloat(state.engagementMax);
  if (!Number.isNaN(engagementMax)) criteria.engagement_max = engagementMax / 100;

  const priceMin = parseFloat(state.priceMin);
  if (!Number.isNaN(priceMin)) criteria.price_min = priceMin;

  const priceMax = parseFloat(state.priceMax);
  if (!Number.isNaN(priceMax)) criteria.price_max = priceMax;

  if (state.sortBy) {
    criteria.sort_by = state.sortBy;
    criteria.sort_order = state.sortOrder;
  }

  return criteria;
}

export function FilterPanel({ onFilterChange }: FilterPanelProps) {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTER_STATE);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const emitChange = useCallback(
    (state: FilterState) => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      debounceRef.current = setTimeout(() => {
        onFilterChange(buildCriteria(state));
      }, 300);
    },
    [onFilterChange],
  );

  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  const updateFilter = useCallback(
    (key: keyof FilterState, value: string) => {
      setFilters((prev) => {
        const next = { ...prev, [key]: value };
        emitChange(next);
        return next;
      });
    },
    [emitChange],
  );

  const handleReset = useCallback(() => {
    setFilters(DEFAULT_FILTER_STATE);
    onFilterChange({});
  }, [onFilterChange]);

  const inputClasses = "h-8 w-24 text-xs";

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border p-3">
      {/* Category */}
      <div className="flex items-center gap-1.5">
        <span className="text-muted-foreground shrink-0 text-xs">品类</span>
        <Select
          value={filters.category}
          onValueChange={(value) => updateFilter("category", value === "all" ? "" : value)}
        >
          <SelectTrigger size="sm" className="h-8 w-28 text-xs">
            <SelectValue placeholder="全部" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部</SelectItem>
            {CATEGORIES.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Follower Range */}
      <div className="flex items-center gap-1.5">
        <span className="text-muted-foreground shrink-0 text-xs">粉丝(万)</span>
        <Input
          className={inputClasses}
          type="number"
          placeholder="最小"
          value={filters.followerMin}
          onChange={(e) => updateFilter("followerMin", e.target.value)}
        />
        <span className="text-muted-foreground text-xs">-</span>
        <Input
          className={inputClasses}
          type="number"
          placeholder="最大"
          value={filters.followerMax}
          onChange={(e) => updateFilter("followerMax", e.target.value)}
        />
      </div>

      {/* Engagement Rate */}
      <div className="flex items-center gap-1.5">
        <span className="text-muted-foreground shrink-0 text-xs">互动率(%)</span>
        <Input
          className={inputClasses}
          type="number"
          placeholder="最小"
          value={filters.engagementMin}
          onChange={(e) => updateFilter("engagementMin", e.target.value)}
        />
        <span className="text-muted-foreground text-xs">-</span>
        <Input
          className={inputClasses}
          type="number"
          placeholder="最大"
          value={filters.engagementMax}
          onChange={(e) => updateFilter("engagementMax", e.target.value)}
        />
      </div>

      {/* Price Range */}
      <div className="flex items-center gap-1.5">
        <span className="text-muted-foreground shrink-0 text-xs">报价(元)</span>
        <Input
          className={inputClasses}
          type="number"
          placeholder="最小"
          value={filters.priceMin}
          onChange={(e) => updateFilter("priceMin", e.target.value)}
        />
        <span className="text-muted-foreground text-xs">-</span>
        <Input
          className={inputClasses}
          type="number"
          placeholder="最大"
          value={filters.priceMax}
          onChange={(e) => updateFilter("priceMax", e.target.value)}
        />
      </div>

      {/* Sort */}
      <div className="flex items-center gap-1.5">
        <span className="text-muted-foreground shrink-0 text-xs">排序</span>
        <Select
          value={filters.sortBy}
          onValueChange={(value) => updateFilter("sortBy", value)}
        >
          <SelectTrigger size="sm" className="h-8 w-28 text-xs">
            <SelectValue placeholder="默认" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">默认</SelectItem>
            {SORT_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {filters.sortBy && (
          <Button
            variant="outline"
            size="sm"
            className="h-8 text-xs"
            onClick={() =>
              updateFilter(
                "sortOrder",
                filters.sortOrder === "desc" ? "asc" : "desc",
              )
            }
          >
            {filters.sortOrder === "desc" ? "↓" : "↑"}
          </Button>
        )}
      </div>

      {/* Reset */}
      <Button
        variant="ghost"
        size="sm"
        className="h-8 text-xs"
        onClick={handleReset}
      >
        重置
      </Button>
    </div>
  );
}
