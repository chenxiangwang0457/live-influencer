"use client";

import { ArrowLeft, Plus, Sparkles } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CandidateTable } from "@/components/workspace/influencer/candidate-table";
import { CompareDrawer } from "@/components/workspace/influencer/compare-drawer";
import {
  WorkspaceBody,
  WorkspaceContainer,
  WorkspaceHeader,
} from "@/components/workspace/workspace-container";
import {
  getInfluencerDetail,
  getSelection,
  removeCandidate,
  updateCandidate,
} from "@/core/influencer/api";
import {
  SELECTION_STATUS_LABELS,
  type Influencer,
  type SelectionDetail,
} from "@/core/influencer/types";
import { cn } from "@/lib/utils";

function getStatusClassName(status: string): string {
  switch (status) {
    case "in_progress":
      return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400";
    case "completed":
      return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
    case "draft":
    case "archived":
      return "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";
    default:
      return "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";
  }
}

function DetailSkeleton() {
  return (
    <div className="mx-auto flex w-full max-w-(--container-width-md) flex-col gap-6 px-4 py-6">
      <Skeleton className="h-5 w-28" />
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-6 w-16 rounded-full" />
        </div>
        <Skeleton className="h-5 w-96" />
      </div>
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full rounded-lg" />
        ))}
      </div>
    </div>
  );
}

export default function SelectionDetailPage() {
  const { id: selectionId } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<SelectionDetail | null>(null);
  const [influencerMap, setInfluencerMap] = useState<Record<string, Influencer>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [compareOpen, setCompareOpen] = useState(false);
  const [compareList, setCompareList] = useState<Influencer[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const fetchDetail = useCallback(async (selId: string, signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getSelection(selId);
      if (signal?.aborted) return;
      setDetail(data);

      // Fetch influencer details for each candidate
      const uniqueIds = [...new Set(data.candidates.map((c) => c.influencer_id))];
      const map: Record<string, Influencer> = {};
      for (const uid of uniqueIds) {
        if (signal?.aborted) return;
        try {
          const inf = await getInfluencerDetail(uid);
          map[uid] = inf;
        } catch {
          // Skip influencers that fail to load
        }
      }
      if (!signal?.aborted) {
        setInfluencerMap((prev) => ({ ...prev, ...map }));
      }
    } catch (err: unknown) {
      if (signal?.aborted) return;
      const message =
        err instanceof Error ? err.message : "加载选人任务失败";
      setError(message);
      toast.error(message);
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
    const controller = new AbortController();
    abortRef.current = controller;
    if (selectionId) {
      void fetchDetail(selectionId, controller.signal);
    }
    return () => {
      controller.abort();
    };
  }, [selectionId, fetchDetail]);

  useEffect(() => {
    if (detail) {
      document.title = `${detail.title} - 选人任务 - DeerFlow`;
    } else if (!loading) {
      document.title = "选人任务 - DeerFlow";
    }
  }, [detail, loading]);

  const handleUpdateStatus = useCallback(
    async (candidateId: string, status: string) => {
      if (!selectionId) return;
      try {
        await updateCandidate(selectionId, candidateId, { status });
        toast.success("状态已更新");
        setDetail((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            candidates: prev.candidates.map((c) =>
              c.id === candidateId ? { ...c, status } : c,
            ),
          };
        });
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "更新失败";
        toast.error(message);
      }
    },
    [selectionId],
  );

  const handleRemove = useCallback(
    async (candidateId: string) => {
      if (!selectionId) return;
      try {
        await removeCandidate(selectionId, candidateId);
        toast.success("已移除");
        setDetail((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            candidates: prev.candidates.filter((c) => c.id !== candidateId),
          };
        });
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "移除失败";
        toast.error(message);
      }
    },
    [selectionId],
  );

  const handleCompare = useCallback((influencers: Influencer[]) => {
    setCompareList(influencers);
    setCompareOpen(true);
  }, []);

  const handleAiRecommend = useCallback(() => {
    toast.info("AI分析功能即将上线", {
      description: "AI驱动的达人匹配推荐功能正在开发中，敬请期待。",
    });
  }, []);

  const candidateCount = detail?.candidates.length ?? 0;

  return (
    <WorkspaceContainer>
      <WorkspaceHeader />
      <WorkspaceBody>
        {loading && <DetailSkeleton />}

        {!loading && error && (
          <div className="flex flex-col items-center justify-center py-24">
            <p className="text-destructive text-lg">加载失败</p>
            <p className="text-muted-foreground mt-1 max-w-md text-center text-sm">
              {error}
            </p>
          </div>
        )}

        {!loading && !error && !detail && (
          <div className="flex flex-col items-center justify-center py-24">
            <p className="text-muted-foreground text-lg">任务不存在</p>
            <p className="text-muted-foreground mt-1 text-sm">
              未找到该选人任务，可能已被删除
            </p>
          </div>
        )}

        {!loading && !error && detail && (
          <div className="mx-auto flex w-full max-w-(--container-width-md) flex-col gap-6 px-4 py-6">
            {/* Back link */}
            <Link
              href="/workspace/influencer/selections"
              className="text-muted-foreground hover:text-foreground flex w-fit items-center gap-1 text-sm transition-colors"
            >
              <ArrowLeft className="size-4" />
              返回选人任务
            </Link>

            {/* Header */}
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-3">
                  <h1 className="text-xl font-semibold">{detail.title}</h1>
                  <Badge
                    variant="outline"
                    className={cn("text-xs", getStatusClassName(detail.status))}
                  >
                    {SELECTION_STATUS_LABELS[detail.status] ?? detail.status}
                  </Badge>
                </div>
                {detail.goal && (
                  <p className="text-muted-foreground mt-2 text-sm">
                    {detail.goal}
                  </p>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAiRecommend}
                >
                  <Sparkles className="mr-1 size-4" />
                  AI推荐
                </Button>
                <Button size="sm">
                  <Plus className="mr-1 size-4" />
                  手动添加达人
                </Button>
              </div>
            </div>

            {/* Candidate count */}
            <div className="text-muted-foreground text-sm">
              共 {candidateCount} 位候选达人
            </div>

            {/* Candidate Table */}
            <div className="rounded-xl border">
              <CandidateTable
                candidates={detail.candidates}
                influencers={influencerMap}
                onUpdateStatus={handleUpdateStatus}
                onRemove={handleRemove}
                onCompare={handleCompare}
              />
            </div>

            {/* Compare Drawer */}
            <CompareDrawer
              open={compareOpen}
              onOpenChange={setCompareOpen}
              influencers={compareList}
            />
          </div>
        )}
      </WorkspaceBody>
    </WorkspaceContainer>
  );
}
