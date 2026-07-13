"use client";

import { useMemo } from "react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import type { Influencer } from "@/core/influencer/types";
import {
  computeDimensionScores,
  DIMENSION_LABELS,
  formatFollowers,
  formatPrice,
  getInitials,
} from "@/core/influencer/types";
import { cn } from "@/lib/utils";

import { MultiRadarChart } from "./radar-chart";

interface CompareDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  influencers: Influencer[];
}

const MAX_COMPARE = 6;

interface MetricDef {
  key: string;
  label: string;
  accessor: (inf: Influencer) => number;
  format: (val: number) => string;
  higherIsBetter: boolean;
}

const METRICS: MetricDef[] = [
  {
    key: "followers",
    label: "粉丝数",
    accessor: (inf) => inf.followers_count,
    format: (v) => formatFollowers(v),
    higherIsBetter: true,
  },
  {
    key: "engagement",
    label: "互动率",
    accessor: (inf) => inf.engagement_rate,
    format: (v) => `${(v * 100).toFixed(1)}%`,
    higherIsBetter: true,
  },
  {
    key: "avg_gmv",
    label: "场均GMV",
    accessor: (inf) => inf.avg_gmv,
    format: (v) => formatPrice(v),
    higherIsBetter: true,
  },
  {
    key: "avg_sales",
    label: "场均销量",
    accessor: (inf) => inf.avg_sales,
    format: (v) => v.toLocaleString(),
    higherIsBetter: true,
  },
  {
    key: "price_min",
    label: "最低报价",
    accessor: (inf) => inf.price_range_min,
    format: (v) => formatPrice(v),
    higherIsBetter: false,
  },
  {
    key: "price_max",
    label: "最高报价",
    accessor: (inf) => inf.price_range_max,
    format: (v) => formatPrice(v),
    higherIsBetter: false,
  },
];

export function CompareDrawer({
  open,
  onOpenChange,
  influencers,
}: CompareDrawerProps) {
  const displayList = useMemo(
    () => influencers.slice(0, MAX_COMPARE),
    [influencers],
  );

  const radarSeries = useMemo(
    () =>
      displayList.map((inf) => {
        const scores = computeDimensionScores(inf);
        return {
          name: inf.nickname,
          data: [scores.match, scores.reach, scores.sales, scores.value],
        };
      }),
    [displayList],
  );

  const radarLabels = [
    DIMENSION_LABELS.match ?? "匹配度",
    DIMENSION_LABELS.reach ?? "传播力",
    DIMENSION_LABELS.sales ?? "带货力",
    DIMENSION_LABELS.value ?? "性价比",
  ];

  const metricExtremes = useMemo(() => {
    const extremes: Record<
      string,
      { best: number; worst: number; bestIdx: number; worstIdx: number } | null
    > = {};
    for (const metric of METRICS) {
      if (displayList.length === 0) {
        extremes[metric.key] = null;
        continue;
      }
      let bestVal = metric.accessor(displayList[0]!);
      let worstVal = bestVal;
      let bestIdx = 0;
      let worstIdx = 0;
      for (let i = 1; i < displayList.length; i++) {
        const val = metric.accessor(displayList[i]!);
        if (metric.higherIsBetter) {
          if (val > bestVal) {
            bestVal = val;
            bestIdx = i;
          }
          if (val < worstVal) {
            worstVal = val;
            worstIdx = i;
          }
        } else {
          if (val < bestVal) {
            bestVal = val;
            bestIdx = i;
          }
          if (val > worstVal) {
            worstVal = val;
            worstIdx = i;
          }
        }
      }
      extremes[metric.key] = { best: bestVal, worst: worstVal, bestIdx, worstIdx };
    }
    return extremes;
  }, [displayList]);

  const getCellClass = (metricKey: string, colIdx: number): string => {
    const extreme = metricExtremes[metricKey];
    if (!extreme) return "";
    if (colIdx === extreme.bestIdx) {
      return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
    }
    if (colIdx === extreme.worstIdx && displayList.length > 1) {
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
    }
    return "";
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-full overflow-auto sm:max-w-2xl"
      >
        <SheetHeader>
          <SheetTitle>达人对比</SheetTitle>
          <SheetDescription>
            最多对比 {MAX_COMPARE} 位达人
          </SheetDescription>
        </SheetHeader>

        {displayList.length === 0 ? (
          <div className="text-muted-foreground py-12 text-center text-sm">
            请先选择需要对比的达人
          </div>
        ) : (
          <div className="mt-4 overflow-x-auto">
            {/* Multi-dimensional radar chart */}
            <MultiRadarChart
              series={radarSeries}
              labels={radarLabels}
              size={300}
              className="mb-6"
            />

            <table className="w-full border-collapse text-sm">
              <thead>
                <tr>
                  <th className="text-muted-foreground sticky left-0 bg-background px-3 py-2 text-left font-medium">
                    指标
                  </th>
                  {displayList.map((inf, idx) => (
                    <th
                      key={inf.platform_uid}
                      className={cn("px-3 py-2 text-center font-medium", {
                        "border-r-0": idx === displayList.length - 1,
                      })}
                    >
                      <div className="flex flex-col items-center gap-1">
                        <Avatar className="size-8">
                          <AvatarImage
                            src={inf.avatar_url}
                            alt={inf.nickname}
                          />
                          <AvatarFallback className="text-xs">
                            {getInitials(inf.nickname)}
                          </AvatarFallback>
                        </Avatar>
                        <span className="max-w-[80px] truncate text-xs">
                          {inf.nickname}
                        </span>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {METRICS.map((metric) => (
                  <tr key={metric.key} className="border-t">
                    <td className="text-muted-foreground sticky left-0 bg-background px-3 py-2.5 text-left font-medium">
                      {metric.label}
                    </td>
                    {displayList.map((inf, idx) => (
                      <td
                        key={`${inf.platform_uid}-${metric.key}`}
                        className={cn(
                          "px-3 py-2.5 text-center",
                          getCellClass(metric.key, idx),
                        )}
                      >
                        {metric.format(metric.accessor(inf))}
                      </td>
                    ))}
                  </tr>
                ))}

                {/* Content style row */}
                <tr className="border-t">
                  <td className="text-muted-foreground sticky left-0 bg-background px-3 py-2.5 text-left font-medium">
                    内容风格
                  </td>
                  {displayList.map((inf) => (
                    <td
                      key={`${inf.platform_uid}-style`}
                      className="px-3 py-2.5 text-center"
                    >
                      <div className="flex flex-wrap justify-center gap-1">
                        {inf.content_style.length > 0
                          ? inf.content_style.slice(0, 3).map((tag) => (
                              <Badge
                                key={tag}
                                variant="secondary"
                                className="text-[10px]"
                              >
                                {tag}
                              </Badge>
                            ))
                          : "-"}
                        {inf.content_style.length > 3 && (
                          <span className="text-muted-foreground text-[10px]">
                            +{inf.content_style.length - 3}
                          </span>
                        )}
                      </div>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
