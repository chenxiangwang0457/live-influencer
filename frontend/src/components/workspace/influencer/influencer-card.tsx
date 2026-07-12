"use client";

import Link from "next/link";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { Influencer } from "@/core/influencer/types";
import { formatFollowers, formatPrice } from "@/core/influencer/types";
import { cn } from "@/lib/utils";

interface InfluencerCardProps {
  influencer: Influencer;
}

function getScoreColor(score: number): string {
  if (score >= 80) return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
  if (score >= 60) return "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400";
  return "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";
}

function getInitials(nickname: string): string {
  return nickname.slice(0, 2) || "?";
}

export function InfluencerCard({ influencer }: InfluencerCardProps) {
  const detailUrl = `/workspace/influencer/${influencer.platform_uid}`;

  return (
    <Link href={detailUrl} className="block">
      <Card
        className={cn(
          "hover:border-primary/50 cursor-pointer transition-all hover:shadow-md",
          "h-full",
        )}
      >
        <CardContent className="flex flex-col gap-3 p-4">
          {/* Avatar + Platform Badge + Nickname + Category */}
          <div className="flex items-start gap-3">
            <div className="relative shrink-0">
              <Avatar className="size-12">
                <AvatarImage
                  src={influencer.avatar_url}
                  alt={influencer.nickname}
                />
                <AvatarFallback>{getInitials(influencer.nickname)}</AvatarFallback>
              </Avatar>
              <span
                className={cn(
                  "absolute -bottom-1 -right-1 rounded-full px-1.5 py-0.5 text-[10px] font-medium leading-none",
                  "bg-[#ff4d4f] text-white",
                )}
                aria-label={influencer.platform}
              >
                {influencer.platform === "douyin" ? "抖" : influencer.platform.slice(0, 2)}
              </span>
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="truncate font-medium text-sm">
                  {influencer.nickname}
                </span>
                {influencer.total_score !== undefined && (
                  <span
                    className={cn(
                      "shrink-0 rounded-full px-1.5 py-0.5 text-xs font-medium",
                      getScoreColor(influencer.total_score),
                    )}
                  >
                    {Math.round(influencer.total_score)}
                  </span>
                )}
              </div>
              <div className="mt-1">
                <Badge variant="secondary" className="text-xs">
                  {influencer.category}
                </Badge>
              </div>
            </div>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-3 gap-2 rounded-md bg-muted/50 p-2">
            <div className="text-center">
              <div className="text-sm font-semibold">
                {formatFollowers(influencer.followers_count)}
              </div>
              <div className="text-muted-foreground text-[11px]">
                粉丝
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm font-semibold">
                {(influencer.engagement_rate * 100).toFixed(1)}%
              </div>
              <div className="text-muted-foreground text-[11px]">
                互动率
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm font-semibold">
                {formatPrice(influencer.avg_gmv)}
              </div>
              <div className="text-muted-foreground text-[11px]">
                场均GMV
              </div>
            </div>
          </div>

          {/* Detail Link */}
          <div className="text-muted-foreground text-xs">
            查看详情 &rarr;
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
