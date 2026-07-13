"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  WorkspaceBody,
  WorkspaceContainer,
  WorkspaceHeader,
} from "@/components/workspace/workspace-container";
import { getFeedbackStats } from "@/core/influencer/api";
interface Stats {
  total: number;
  avg_rating: number | null;
  distribution: Record<string, number>;
}

function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-muted-foreground text-sm font-normal">
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{value}</div>
        {sub && (
          <p className="text-muted-foreground mt-1 text-xs">{sub}</p>
        )}
      </CardContent>
    </Card>
  );
}

function RatingBar({
  stars,
  count,
  total,
}: {
  stars: number;
  count: number;
  total: number;
}) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div className="flex items-center gap-3">
      <span className="w-12 text-right text-sm">{stars} 星</span>
      <div className="bg-muted h-4 flex-1 overflow-hidden rounded-full">
        <div
          className="bg-yellow-400 h-full rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-muted-foreground w-10 text-right text-sm">
        {count}
      </span>
    </div>
  );
}

export default function AnalyticsPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const abortRef = useRef<AbortController | null>(null);

  const fetchStats = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await getFeedbackStats();
      if (!signal?.aborted) setStats(data);
    } catch (err: unknown) {
      if (signal?.aborted) return;
      toast.error(err instanceof Error ? err.message : "加载统计失败");
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    void fetchStats(controller.signal);
    return () => controller.abort();
  }, [fetchStats]);

  useEffect(() => {
    document.title = "数据分析 - DeerFlow";
  }, []);

  return (
    <WorkspaceContainer>
      <WorkspaceHeader />
      <WorkspaceBody>
        <div className="mx-auto flex w-full max-w-(--container-width-md) flex-col gap-6 p-6">
          <h1 className="text-2xl font-semibold">反馈分析</h1>

          {loading && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-28 rounded-xl" />
              ))}
            </div>
          )}

          {!loading && stats && (
            <>
              {/* Summary cards */}
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <StatCard
                  label="总反馈数"
                  value={String(stats.total)}
                  sub="累计收到的合作评价"
                />
                <StatCard
                  label="平均评分"
                  value={
                    stats.avg_rating != null
                      ? stats.avg_rating.toFixed(1)
                      : "-"
                  }
                  sub="满分 5.0"
                />
                <StatCard
                  label="评分分布"
                  value={
                    stats.total > 0
                      ? `${Object.values(stats.distribution).filter((c) => c > 0).length} 个等级`
                      : "-"
                  }
                  sub={
                    stats.total > 0
                      ? `${Object.entries(stats.distribution)
                          .sort(([, a], [, b]) => b - a)
                          [0]?.[0] ?? "-"} 星最多`
                      : undefined
                  }
                />
              </div>

              {/* Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">评分分布</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[5, 4, 3, 2, 1].map((stars) => (
                    <RatingBar
                      key={stars}
                      stars={stars}
                      count={stats.distribution[String(stars)] ?? 0}
                      total={stats.total}
                    />
                  ))}
                  {stats.total === 0 && (
                    <p className="text-muted-foreground py-8 text-center text-sm">
                      暂无反馈数据。完成达人合作后，品牌方可在此提交反馈。
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* Trend Note */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">评分趋势</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-end gap-2 h-32">
                    {[1, 2, 3, 4, 5].map((star) => {
                      const count = stats.distribution[String(star)] ?? 0;
                      const maxCount = Math.max(
                        ...Object.values(stats.distribution),
                        1,
                      );
                      const height = (count / maxCount) * 100;
                      return (
                        <div
                          key={star}
                          className="flex flex-1 flex-col items-center gap-1"
                        >
                          <span className="text-xs font-medium">
                            {count}
                          </span>
                          <div
                            className="w-full rounded-t bg-yellow-400 transition-all"
                            style={{ height: `${Math.max(height, 4)}%` }}
                          />
                          <span className="text-muted-foreground text-xs">
                            {star}★
                          </span>
                        </div>
                      );
                    })}
                  </div>
                  <p className="text-muted-foreground mt-4 text-xs">
                    趋势数据按时间累计。随着反馈量增加，评分分布将反映达人合作效果的真实趋势。
                  </p>
                </CardContent>
              </Card>

              {/* Weights info */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">评分模型</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-sm">
                    当前权重：匹配度 35% | 传播力 25% | 带货力 25% | 性价比 15%
                  </p>
                  <p className="text-muted-foreground mt-1 text-sm">
                    权重随反馈积累自动优化。每提交一次合作反馈，系统对比预测分与实际评分，微调各维度权重以提升推荐准确度。
                  </p>
                  {stats.total < 3 && (
                    <p className="text-muted-foreground mt-2 text-xs">
                      (需至少 3 条反馈才能触发权重自动调整)
                    </p>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </WorkspaceBody>
    </WorkspaceContainer>
  );
}
