"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { FilterPanel } from "@/components/workspace/influencer/filter-panel";
import { InfluencerCard } from "@/components/workspace/influencer/influencer-card";
import { SearchBar } from "@/components/workspace/influencer/search-bar";
import {
  WorkspaceBody,
  WorkspaceContainer,
  WorkspaceHeader,
} from "@/components/workspace/workspace-container";
import { searchInfluencers } from "@/core/influencer/api";
import type {
  Influencer,
  PaginatedResponse,
  SearchCriteria,
} from "@/core/influencer/types";

const PAGE_SIZE = 12;

function InfluencerCardSkeleton() {
  return (
    <div className="rounded-xl border p-4">
      <div className="flex items-start gap-3">
        <Skeleton className="size-12 rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2">
        <Skeleton className="h-10 rounded-md" />
        <Skeleton className="h-10 rounded-md" />
        <Skeleton className="h-10 rounded-md" />
      </div>
    </div>
  );
}

export default function InfluencerSquarePage() {
  const [keyword, setKeyword] = useState("");
  const [filterCriteria, setFilterCriteria] = useState<Partial<SearchCriteria>>({});
  const [currentFilterCriteria, setCurrentFilterCriteria] =
    useState<Partial<SearchCriteria>>({});
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PaginatedResponse<Influencer> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const fetchData = useCallback(
    async (criteria: Partial<SearchCriteria>, pageNum: number, signal?: AbortSignal) => {
      setLoading(true);
      setError(null);
      try {
        const data = await searchInfluencers({
          ...criteria,
          page: pageNum,
          page_size: PAGE_SIZE,
        });
        if (!signal?.aborted) {
          setResult(data);
        }
      } catch (err: unknown) {
        if (signal?.aborted) return;
        const message =
          err instanceof Error ? err.message : "搜索失败，请重试";
        setError(message);
        toast.error(message);
      } finally {
        if (!signal?.aborted) {
          setLoading(false);
        }
      }
    },
    [],
  );

  // Fetch on mount and when criteria/page change
  useEffect(() => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
    const controller = new AbortController();
    abortRef.current = controller;
    void fetchData(currentFilterCriteria, page, controller.signal);
    return () => {
      controller.abort();
    };
  }, [currentFilterCriteria, page, fetchData]);

  // Search bar debounce
  const searchDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const handleKeywordChange = useCallback(
    (value: string) => {
      setKeyword(value);
      if (searchDebounceRef.current) {
        clearTimeout(searchDebounceRef.current);
      }
      searchDebounceRef.current = setTimeout(() => {
        const newCriteria = { ...filterCriteria, keyword: value || undefined };
        setCurrentFilterCriteria(newCriteria);
        setPage(1);
      }, 300);
    },
    [filterCriteria],
  );

  useEffect(() => {
    return () => {
      if (searchDebounceRef.current) {
        clearTimeout(searchDebounceRef.current);
      }
    };
  }, []);

  // Filter panel callback
  const handleFilterChange = useCallback(
    (criteria: Partial<SearchCriteria>) => {
      setFilterCriteria(criteria);
      const newCriteria = { ...criteria, keyword: keyword || undefined };
      setCurrentFilterCriteria(newCriteria);
      setPage(1);
    },
    [keyword],
  );

  const totalPages = result ? Math.max(1, Math.ceil(result.total / PAGE_SIZE)) : 1;
  const hasPrev = page > 1;
  const hasNext = page < totalPages;

  useEffect(() => {
    document.title = "达人广场 - DeerFlow";
  }, []);

  return (
    <WorkspaceContainer>
      <WorkspaceHeader />
      <WorkspaceBody>
        <div className="mx-auto flex w-full max-w-(--container-width-md) flex-col gap-4 p-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold">达人广场</h1>
            <Button asChild>
              <Link href="/workspace/influencer/selections">选人任务</Link>
            </Button>
          </div>

          {/* Search Bar */}
          <SearchBar
            keyword={keyword}
            onKeywordChange={handleKeywordChange}
            onSearch={() => {
              const newCriteria = {
                ...filterCriteria,
                keyword: keyword || undefined,
              };
              setCurrentFilterCriteria(newCriteria);
              setPage(1);
            }}
          />

          {/* Filter Panel */}
          <FilterPanel onFilterChange={handleFilterChange} />

          {/* Results */}
          {error && !loading && (
            <div className="text-destructive text-sm">加载失败: {error}</div>
          )}

          {loading && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: PAGE_SIZE }).map((_, i) => (
                <InfluencerCardSkeleton key={`skeleton-${i}`} />
              ))}
            </div>
          )}

          {!loading && !error && result?.data.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <p className="text-lg">未找到匹配的达人</p>
              <p className="mt-1 text-sm">尝试调整搜索条件或筛选条件</p>
            </div>
          )}

          {!loading && result && result.data.length > 0 && (
            <>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {result.data.map((inf) => (
                  <InfluencerCard key={inf.platform_uid} influencer={inf} />
                ))}
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-center gap-4 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!hasPrev}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  上一页
                </Button>
                <span className="text-muted-foreground text-sm">
                  第 {page} / {totalPages} 页 (共 {result.total} 位达人)
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!hasNext}
                  onClick={() => setPage((p) => p + 1)}
                >
                  下一页
                </Button>
              </div>
            </>
          )}
        </div>
      </WorkspaceBody>
    </WorkspaceContainer>
  );
}
