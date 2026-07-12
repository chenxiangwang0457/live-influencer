"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Skeleton } from "@/components/ui/skeleton";
import { InfluencerDetail } from "@/components/workspace/influencer/influencer-detail";
import {
  WorkspaceBody,
  WorkspaceContainer,
  WorkspaceHeader,
} from "@/components/workspace/workspace-container";
import { getInfluencerDetail } from "@/core/influencer/api";
import type { Influencer } from "@/core/influencer/types";

function DetailSkeleton() {
  return (
    <div className="mx-auto flex w-full max-w-(--container-width-md) flex-col gap-6 px-4 py-6">
      {/* Back link */}
      <Skeleton className="h-5 w-28" />

      {/* Profile card */}
      <div className="rounded-xl border p-6">
        <div className="flex items-start gap-4">
          <Skeleton className="size-20 rounded-full" />
          <div className="flex-1 space-y-3">
            <div className="flex items-center gap-3">
              <Skeleton className="h-7 w-36" />
              <Skeleton className="h-7 w-14 rounded-full" />
            </div>
            <div className="flex gap-2">
              <Skeleton className="h-6 w-14 rounded-full" />
              <Skeleton className="h-6 w-16 rounded-full" />
              <Skeleton className="h-6 w-24 rounded-full" />
            </div>
          </div>
        </div>
      </div>

      {/* Score card */}
      <div className="rounded-xl border p-6">
        <Skeleton className="mb-4 h-5 w-20" />
        <div className="flex items-center gap-4">
          <Skeleton className="size-16 rounded" />
          <Skeleton className="h-4 flex-1 rounded-full" />
        </div>
        <div className="mt-5 space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-2.5 flex-1 rounded-full" />
              <Skeleton className="h-4 w-10" />
            </div>
          ))}
        </div>
      </div>

      {/* Stats card */}
      <div className="rounded-xl border p-6">
        <Skeleton className="mb-4 h-5 w-20" />
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-lg" />
          ))}
        </div>
      </div>

      {/* Demographics card */}
      <div className="rounded-xl border p-6">
        <Skeleton className="mb-4 h-5 w-20" />
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-2.5 flex-1 rounded-full" />
              <Skeleton className="h-4 w-10" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function InfluencerDetailPage() {
  const { id: platformUid } = useParams<{ id: string }>();
  const [influencer, setInfluencer] = useState<Influencer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const fetchDetail = useCallback(async (uid: string) => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);
    setNotFound(false);

    try {
      const data = await getInfluencerDetail(uid);
      if (!controller.signal.aborted) {
        setInfluencer(data);
      }
    } catch (err: unknown) {
      if (controller.signal.aborted) return;
      const message =
        err instanceof Error ? err.message : "加载失败，请重试";
      if (
        message.toLowerCase().includes("not found") ||
        message.includes("404")
      ) {
        setNotFound(true);
      } else {
        setError(message);
        toast.error(message);
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    if (platformUid) {
      void fetchDetail(platformUid);
    }
    return () => {
      if (abortRef.current) {
        abortRef.current.abort();
      }
    };
  }, [platformUid, fetchDetail]);

  useEffect(() => {
    if (influencer) {
      document.title = `${influencer.nickname} - 达人详情 - DeerFlow`;
    } else if (!loading) {
      document.title = "达人详情 - DeerFlow";
    }
  }, [influencer, loading]);

  return (
    <WorkspaceContainer>
      <WorkspaceHeader />
      <WorkspaceBody>
        {/* Loading */}
        {loading && <DetailSkeleton />}

        {/* Not found */}
        {!loading && notFound && (
          <div className="flex flex-col items-center justify-center py-24">
            <p className="text-muted-foreground text-lg">达人不存在</p>
            <p className="text-muted-foreground mt-1 text-sm">
              未找到该达人信息，可能已被移除或链接无效
            </p>
          </div>
        )}

        {/* Error */}
        {!loading && error && !notFound && (
          <div className="flex flex-col items-center justify-center py-24">
            <p className="text-destructive text-lg">加载失败</p>
            <p className="text-muted-foreground mt-1 max-w-md text-center text-sm">
              {error}
            </p>
          </div>
        )}

        {/* Success */}
        {!loading && !error && !notFound && influencer && (
          <InfluencerDetail influencer={influencer} />
        )}
      </WorkspaceBody>
    </WorkspaceContainer>
  );
}
