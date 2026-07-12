"use client";

import Link from "next/link";
import { useMemo } from "react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Influencer } from "@/core/influencer/types";
import { formatFollowers, formatPrice, getInitials } from "@/core/influencer/types";
import { cn } from "@/lib/utils";

interface SearchResultMsgProps {
  influencers: Influencer[];
  total: number;
}

function getScoreColor(score: number): string {
  if (score >= 80)
    return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
  if (score >= 60)
    return "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400";
  return "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";
}

function MiniInfluencerCard({ influencer }: { influencer: Influencer }) {
  const detailUrl = `/workspace/influencer/${influencer.platform_uid}`;

  return (
    <Link
      href={detailUrl}
      className="border-border hover:border-primary/50 bg-background w-[180px] shrink-0 rounded-lg border p-3 transition-colors hover:shadow-sm"
    >
      <div className="flex items-start gap-2.5">
        <div className="relative shrink-0">
          <Avatar className="size-10">
            <AvatarImage
              src={influencer.avatar_url}
              alt={influencer.nickname}
            />
            <AvatarFallback className="text-xs">
              {getInitials(influencer.nickname)}
            </AvatarFallback>
          </Avatar>
          <span
            className={cn(
              "absolute -bottom-0.5 -right-0.5 rounded-full px-1 py-0.5 text-[9px] font-medium leading-none",
              "bg-[#ff4d4f] text-white",
            )}
            aria-label={influencer.platform}
          >
            {influencer.platform === "douyin"
              ? "抖"
              : influencer.platform.slice(0, 2)}
          </span>
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <span className="truncate text-sm font-medium">
              {influencer.nickname}
            </span>
            {influencer.total_score !== undefined && (
              <span
                className={cn(
                  "shrink-0 rounded-full px-1.5 py-0.5 text-[10px] font-medium",
                  getScoreColor(influencer.total_score),
                )}
              >
                {Math.round(influencer.total_score)}
              </span>
            )}
          </div>
          <div className="mt-1">
            <Badge variant="secondary" className="text-[10px]">
              {influencer.category}
            </Badge>
          </div>
        </div>
      </div>

      <div className="mt-2.5 grid grid-cols-3 gap-1 rounded-md bg-muted/50 px-2 py-1.5 text-center">
        <div>
          <div className="text-xs font-semibold">
            {formatFollowers(influencer.followers_count)}
          </div>
          <div className="text-muted-foreground text-[10px]">粉丝</div>
        </div>
        <div>
          <div className="text-xs font-semibold">
            {(influencer.engagement_rate * 100).toFixed(1)}%
          </div>
          <div className="text-muted-foreground text-[10px]">互动率</div>
        </div>
        <div>
          <div className="text-xs font-semibold">
            {formatPrice(influencer.avg_gmv)}
          </div>
          <div className="text-muted-foreground text-[10px]">场均GMV</div>
        </div>
      </div>
    </Link>
  );
}

export function SearchResultMsg({
  influencers,
  total,
}: SearchResultMsgProps) {
  const displayList = useMemo(() => influencers.slice(0, 20), [influencers]);

  if (influencers.length === 0) {
    return (
      <div className="text-muted-foreground rounded-lg border px-4 py-6 text-center text-sm">
        未找到匹配的达人，请尝试调整筛选条件
      </div>
    );
  }

  return (
    <div className="my-3 space-y-3">
      {/* Summary header */}
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">
          找到{" "}
          <span className="text-primary font-semibold">{total}</span>{" "}
          位匹配达人
        </p>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/workspace/influencer">查看全部 &rarr;</Link>
        </Button>
      </div>

      {/* Horizontally scrollable card row */}
      <div className="overflow-x-auto pb-2">
        <div className="flex gap-3" style={{ width: "max-content" }}>
          {displayList.map((inf) => (
            <MiniInfluencerCard
              key={`${inf.platform}-${inf.platform_uid}`}
              influencer={inf}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
