"use client";

import { ArrowLeft, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { useMemo } from "react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { Influencer } from "@/core/influencer/types";
import { formatFollowers, formatPrice, getInitials } from "@/core/influencer/types";
import { cn } from "@/lib/utils";

interface InfluencerDetailProps {
  influencer: Influencer;
}

/** Color helpers matching the existing InfluencerCard pattern. */
function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-600 dark:text-green-400";
  if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
  return "text-gray-500 dark:text-gray-400";
}

function getScoreBg(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-yellow-500";
  return "bg-gray-400";
}

/** Derive approximate dimension scores from available metrics (MVP). */
function computeDimensionScores(inf: Influencer) {
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

const DIMENSION_LABELS: Record<string, string> = {
  match: "综合匹配",
  reach: "传播力",
  sales: "带货力",
  value: "性价比",
};

const DIMENSION_COLORS: Record<string, string> = {
  match: "bg-chart-1",
  reach: "bg-chart-2",
  sales: "bg-chart-3",
  value: "bg-chart-4",
};

export function InfluencerDetail({ influencer }: InfluencerDetailProps) {
  const dimensionScores = useMemo(
    () => computeDimensionScores(influencer),
    [influencer],
  );

  const overallScore =
    influencer.total_score ??
    Math.round(
      (dimensionScores.match +
        dimensionScores.reach +
        dimensionScores.sales +
        dimensionScores.value) /
        4,
    );

  const hasContentStyle = influencer.content_style.length > 0;
  const hasBrandHistory = influencer.brand_history.length > 0;
  const sortedBrandHistory = useMemo(
    () => [...influencer.brand_history].sort((a, b) => b.year - a.year),
    [influencer.brand_history],
  );

  return (
    <div className="mx-auto flex w-full max-w-(--container-width-md) flex-col gap-6 px-4 py-6">
      {/* Back link */}
      <Link
        href="/workspace/influencer"
        className="text-muted-foreground hover:text-foreground flex w-fit items-center gap-1 text-sm transition-colors"
      >
        <ArrowLeft className="size-4" />
        返回达人广场
      </Link>

      {/* ── Profile Header ── */}
      <Card>
        <CardContent className="flex items-start gap-4 pt-6">
          <div className="relative shrink-0">
            <Avatar className="size-20">
              <AvatarImage
                src={influencer.avatar_url}
                alt={influencer.nickname}
              />
              <AvatarFallback className="text-lg">
                {getInitials(influencer.nickname)}
              </AvatarFallback>
            </Avatar>
            <span
              className={cn(
                "absolute -bottom-1 -right-1 rounded-full px-2 py-0.5 text-xs font-medium",
                "bg-[#ff4d4f] text-white",
              )}
            >
              {influencer.platform === "douyin" ? "抖音" : influencer.platform}
            </span>
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-3">
              <h2 className="text-xl font-semibold">{influencer.nickname}</h2>
              {overallScore > 0 && (
                <span
                  className={cn(
                    "shrink-0 rounded-full px-2.5 py-0.5 text-sm font-bold",
                    getScoreColor(overallScore),
                    overallScore >= 80
                      ? "bg-green-100 dark:bg-green-900/30"
                      : overallScore >= 60
                        ? "bg-yellow-100 dark:bg-yellow-900/30"
                        : "bg-gray-100 dark:bg-gray-800",
                  )}
                >
                  {overallScore}分
                </span>
              )}
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <Badge variant="secondary">{influencer.category}</Badge>
              {influencer.sub_categories.map((sub) => (
                <Badge key={sub} variant="outline" className="text-xs">
                  {sub}
                </Badge>
              ))}
              <Badge
                variant="outline"
                className="text-muted-foreground text-xs"
              >
                数据源: {influencer.data_source}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ── Score Section ── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">能力评分</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Overall */}
          <div className="flex items-center gap-4">
            <div className="shrink-0 text-center">
              <div
                className={cn("text-3xl font-bold", getScoreColor(overallScore))}
              >
                {overallScore}
              </div>
              <div className="text-muted-foreground text-xs">综合评分</div>
            </div>
            <div className="bg-muted h-4 flex-1 overflow-hidden rounded-full">
              <div
                className={cn(
                  "h-full rounded-full transition-all duration-500",
                  getScoreBg(overallScore),
                )}
                style={{ width: `${overallScore}%` }}
              />
            </div>
          </div>

          <Separator />

          {/* Dimension breakdown */}
          <div className="space-y-3">
            {Object.entries(dimensionScores).map(([key, score]) => (
              <div key={key} className="flex items-center gap-3">
                <span className="text-muted-foreground w-16 shrink-0 text-sm">
                  {DIMENSION_LABELS[key] ?? key}
                </span>
                <div className="bg-muted h-2.5 flex-1 overflow-hidden rounded-full">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all duration-500",
                      DIMENSION_COLORS[key] ?? "bg-primary",
                    )}
                    style={{ width: `${score}%` }}
                  />
                </div>
                <span
                  className={cn(
                    "w-10 text-right text-sm font-medium",
                    getScoreColor(score),
                  )}
                >
                  {score}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ── Key Stats ── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">关键数据</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {(
              [
                {
                  label: "粉丝数",
                  value: formatFollowers(influencer.followers_count),
                },
                {
                  label: "互动率",
                  value: `${(influencer.engagement_rate * 100).toFixed(1)}%`,
                },
                {
                  label: "场均GMV",
                  value: formatPrice(influencer.avg_gmv),
                },
                {
                  label: "场均销量",
                  value: influencer.avg_sales.toLocaleString(),
                },
                {
                  label: "报价区间",
                  value: `${formatPrice(influencer.price_range_min)} - ${formatPrice(influencer.price_range_max)}`,
                },
              ] as const
            ).map((stat) => (
              <div
                key={stat.label}
                className="bg-muted/50 rounded-lg p-3 text-center"
              >
                <div className="truncate text-lg font-semibold">
                  {stat.value}
                </div>
                <div className="text-muted-foreground text-xs">{stat.label}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ── Fan Demographics ── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">粉丝画像</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Age distribution */}
          <div>
            <p className="text-muted-foreground mb-3 text-sm font-medium">
              年龄分布
            </p>
            <div className="space-y-2.5">
              {(
                [
                  {
                    key: "age_18_24",
                    label: "18-24岁",
                    value: influencer.demographics.age_18_24,
                  },
                  {
                    key: "age_25_34",
                    label: "25-34岁",
                    value: influencer.demographics.age_25_34,
                  },
                  {
                    key: "age_35_plus",
                    label: "35岁以上",
                    value: influencer.demographics.age_35_plus,
                  },
                ] as const
              ).map((item) => {
                const pct = Math.round(item.value * 100);
                return (
                  <div key={item.key} className="flex items-center gap-3">
                    <span className="text-muted-foreground w-20 shrink-0 text-sm">
                      {item.label}
                    </span>
                    <div className="bg-muted h-2.5 flex-1 overflow-hidden rounded-full">
                      <div
                        className="bg-chart-3 h-full rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="w-10 text-right text-sm font-medium">
                      {pct}%
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <Separator />

          {/* Gender ratio */}
          <div>
            <p className="text-muted-foreground mb-3 text-sm font-medium">
              性别比例
            </p>
            <div className="space-y-2.5">
              <div className="flex items-center gap-3">
                <span className="text-muted-foreground w-20 shrink-0 text-sm">
                  男性
                </span>
                <div className="bg-muted h-4 flex-1 overflow-hidden rounded-full">
                  <div
                    className="bg-blue-500 h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.round(influencer.demographics.gender_male * 100)}%`,
                    }}
                  />
                </div>
                <span className="w-12 text-right text-sm font-medium">
                  {Math.round(influencer.demographics.gender_male * 100)}%
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-muted-foreground w-20 shrink-0 text-sm">
                  女性
                </span>
                <div className="bg-muted h-4 flex-1 overflow-hidden rounded-full">
                  <div
                    className="bg-pink-500 h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.round((1 - influencer.demographics.gender_male) * 100)}%`,
                    }}
                  />
                </div>
                <span className="w-12 text-right text-sm font-medium">
                  {Math.round(
                    (1 - influencer.demographics.gender_male) * 100,
                  )}
                  %
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ── Content Style ── */}
      {hasContentStyle && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">内容风格</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {influencer.content_style.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-sm">
                  {tag}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Brand History ── */}
      {hasBrandHistory && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">品牌合作历史</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative space-y-5">
              {/* Timeline line */}
              <div className="bg-border absolute top-1 bottom-1 left-[7px] w-px" />
              {sortedBrandHistory.map((item, idx) => (
                <div key={idx} className="flex items-start gap-4">
                  <div className="bg-primary relative z-10 mt-1 size-3.5 shrink-0 rounded-full" />
                  <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                    <span className="text-muted-foreground text-sm tabular-nums">
                      {item.year}
                    </span>
                    <span className="font-medium">{item.brand}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Risk Notice ── */}
      <Card>
        <CardContent className="flex items-center gap-3 pt-6">
          <div className="bg-muted flex size-10 shrink-0 items-center justify-center rounded-full">
            <ShieldAlert className="text-muted-foreground size-5" />
          </div>
          <div>
            <p className="text-muted-foreground text-sm">
              风险评估功能即将上线，敬请期待
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
