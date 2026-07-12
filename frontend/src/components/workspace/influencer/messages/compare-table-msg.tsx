"use client";

import { useMemo } from "react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import type { Influencer } from "@/core/influencer/types";
import { formatFollowers, formatPrice } from "@/core/influencer/types";
import { cn } from "@/lib/utils";

interface CompareTableMsgProps {
  influencers: Influencer[];
}

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

function getInitials(nickname: string): string {
  return nickname.slice(0, 2) || "?";
}

export function CompareTableMsg({ influencers }: CompareTableMsgProps) {
  const metricExtremes = useMemo(() => {
    const extremes: Record<
      string,
      | { best: number; worst: number; bestIdx: number; worstIdx: number }
      | null
    > = {};
    for (const metric of METRICS) {
      if (influencers.length === 0) {
        extremes[metric.key] = null;
        continue;
      }
      let bestVal = metric.accessor(influencers[0]!);
      let worstVal = bestVal;
      let bestIdx = 0;
      let worstIdx = 0;
      for (let i = 1; i < influencers.length; i++) {
        const val = metric.accessor(influencers[i]!);
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
      extremes[metric.key] = {
        best: bestVal,
        worst: worstVal,
        bestIdx,
        worstIdx,
      };
    }
    return extremes;
  }, [influencers]);

  const getCellClass = (metricKey: string, colIdx: number): string => {
    const extreme = metricExtremes[metricKey];
    if (!extreme) return "";
    if (colIdx === extreme.bestIdx) {
      return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
    }
    if (
      colIdx === extreme.worstIdx &&
      influencers.length > 1
    ) {
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
    }
    return "";
  };

  if (influencers.length === 0) {
    return (
      <div className="text-muted-foreground rounded-lg border px-4 py-6 text-center text-sm">
        暂无可对比的达人数据
      </div>
    );
  }

  return (
    <div className="my-3 space-y-3">
      <p className="text-sm font-medium">
        达人对比 (共 {influencers.length} 位)
      </p>

      <div className="border-border overflow-x-auto rounded-lg border">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b">
              <th className="bg-background text-muted-foreground sticky left-0 z-10 px-3 py-2 text-left text-xs font-medium">
                指标
              </th>
              {influencers.map((inf, idx) => (
                <th
                  key={inf.platform_uid}
                  className={cn(
                    "bg-background px-3 py-2 text-center font-medium",
                    {
                      "border-r-0": idx === influencers.length - 1,
                    },
                  )}
                >
                  <div className="flex flex-col items-center gap-1">
                    <Avatar className="size-7">
                      <AvatarImage
                        src={inf.avatar_url}
                        alt={inf.nickname}
                      />
                      <AvatarFallback className="text-[10px]">
                        {getInitials(inf.nickname)}
                      </AvatarFallback>
                    </Avatar>
                    <span className="max-w-[60px] truncate text-[11px]">
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
                <td className="bg-background text-muted-foreground sticky left-0 z-10 whitespace-nowrap px-3 py-2 text-left text-xs font-medium">
                  {metric.label}
                </td>
                {influencers.map((inf, idx) => (
                  <td
                    key={`${inf.platform_uid}-${metric.key}`}
                    className={cn(
                      "whitespace-nowrap px-3 py-2 text-center text-xs",
                      getCellClass(metric.key, idx),
                    )}
                  >
                    {metric.format(metric.accessor(inf))}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
