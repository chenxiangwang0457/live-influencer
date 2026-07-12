"use client";

import { ArrowUpDown, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  CANDIDATE_STATUSES,
  type Candidate,
  type Influencer,
} from "@/core/influencer/types";
import { formatFollowers, formatPrice, getInitials } from "@/core/influencer/types";
import { cn } from "@/lib/utils";

interface CandidateTableProps {
  candidates: Candidate[];
  influencers: Record<string, Influencer>;
  onUpdateStatus: (
    candidateId: string,
    status: string,
  ) => void;
  onRemove: (candidateId: string) => void;
  onCompare: (influencers: Influencer[]) => void;
}

function getScoreColor(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-yellow-500";
  return "bg-gray-400";
}

function getScoreBarClass(score: number): string {
  if (score >= 80) return "bg-green-100 dark:bg-green-900/30";
  if (score >= 60) return "bg-yellow-100 dark:bg-yellow-900/30";
  return "bg-gray-100 dark:bg-gray-800";
}

function getStatusLabel(status: string): string {
  return (
    CANDIDATE_STATUSES.find((s) => s.value === status)?.label ?? status
  );
}

export function CandidateTable({
  candidates,
  influencers,
  onUpdateStatus,
  onRemove,
  onCompare,
}: CandidateTableProps) {
  const [sortAsc, setSortAsc] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const sorted = useMemo(() => {
    const sorted = [...candidates];
    sorted.sort((a, b) => {
      const diff = b.match_score - a.match_score;
      return sortAsc ? -diff : diff;
    });
    return sorted;
  }, [candidates, sortAsc]);

  const toggleSort = () => setSortAsc((prev) => !prev);

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleCompare = () => {
    const selected: Influencer[] = [];
    for (const id of selectedIds) {
      const candidate = candidates.find((c) => c.id === id);
      if (candidate) {
        const inf = influencers[candidate.influencer_id];
        if (inf) {
          selected.push(inf);
        }
      }
    }
    onCompare(selected);
  };

  if (candidates.length === 0) {
    return (
      <div className="text-muted-foreground py-12 text-center text-sm">
        暂无候选达人
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      {selectedIds.size > 0 && (
        <div className="mb-2 flex items-center gap-2">
          <span className="text-muted-foreground text-sm">
            已选 {selectedIds.size} 位达人
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCompare}
            disabled={selectedIds.size < 2}
          >
            对比
          </Button>
        </div>
      )}
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b">
            <th className="px-2 py-3 text-left">
              <span className="sr-only">选择</span>
            </th>
            <th className="px-3 py-3 text-left font-medium">达人</th>
            <th className="hidden px-3 py-3 text-left font-medium sm:table-cell">
              品类
            </th>
            <th className="hidden px-3 py-3 text-right font-medium md:table-cell">
              粉丝数
            </th>
            <th className="hidden px-3 py-3 text-right font-medium md:table-cell">
              互动率
            </th>
            <th className="hidden px-3 py-3 text-right font-medium lg:table-cell">
              场均GMV
            </th>
            <th className="px-3 py-3 text-left font-medium">
              <button
                type="button"
                onClick={toggleSort}
                className="inline-flex items-center gap-1 hover:underline"
              >
                匹配度
                <ArrowUpDown className="size-3" />
              </button>
            </th>
            <th className="hidden px-3 py-3 text-left font-medium xl:table-cell">
              匹配理由
            </th>
            <th className="px-3 py-3 text-left font-medium">状态</th>
            <th className="px-3 py-3 text-center font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((candidate) => {
            const inf = influencers[candidate.influencer_id];
            if (!inf) return null;

            return (
              <tr
                key={candidate.id}
                className={cn("border-b hover:bg-muted/50", {
                  "bg-muted/30": selectedIds.has(candidate.id),
                })}
              >
                <td className="px-2 py-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(candidate.id)}
                    onChange={() => toggleSelect(candidate.id)}
                    className="size-4 cursor-pointer rounded"
                  />
                </td>
                <td className="px-3 py-3">
                  <div className="flex items-center gap-2">
                    <Avatar className="size-8 shrink-0">
                      <AvatarImage src={inf.avatar_url} alt={inf.nickname} />
                      <AvatarFallback className="text-xs">
                        {getInitials(inf.nickname)}
                      </AvatarFallback>
                    </Avatar>
                    <span className="truncate font-medium">
                      {inf.nickname}
                    </span>
                  </div>
                </td>
                <td className="hidden px-3 py-3 sm:table-cell">
                  <Badge variant="secondary" className="text-xs">
                    {inf.category}
                  </Badge>
                </td>
                <td className="hidden px-3 py-3 text-right md:table-cell">
                  {formatFollowers(inf.followers_count)}
                </td>
                <td className="hidden px-3 py-3 text-right md:table-cell">
                  {(inf.engagement_rate * 100).toFixed(1)}%
                </td>
                <td className="hidden px-3 py-3 text-right lg:table-cell">
                  {formatPrice(inf.avg_gmv)}
                </td>
                <td className="px-3 py-3">
                  <div className="flex min-w-[100px] items-center gap-2">
                    <div
                      className={cn("h-2 flex-1 overflow-hidden rounded-full", getScoreBarClass(candidate.match_score))}
                    >
                      <div
                        className={cn(
                          "h-full rounded-full",
                          getScoreColor(candidate.match_score),
                        )}
                        style={{
                          width: `${Math.min(100, Math.max(0, candidate.match_score))}%`,
                        }}
                      />
                    </div>
                    <span className="w-9 shrink-0 text-right text-xs font-medium">
                      {Math.round(candidate.match_score)}
                    </span>
                  </div>
                </td>
                <td className="hidden max-w-[140px] px-3 py-3 xl:table-cell">
                  <span className="text-muted-foreground truncate text-xs" title={candidate.match_reason ?? undefined}>
                    {candidate.match_reason ?? "-"}
                  </span>
                </td>
                <td className="px-3 py-3">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <button
                        type="button"
                        className="text-muted-foreground hover:text-foreground cursor-pointer text-xs underline underline-offset-2"
                      >
                        {getStatusLabel(candidate.status)}
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="start">
                      {CANDIDATE_STATUSES.map((s) => (
                        <DropdownMenuItem
                          key={s.value}
                          onClick={() =>
                            onUpdateStatus(candidate.id, s.value)
                          }
                          className={cn({
                            "font-medium": s.value === candidate.status,
                          })}
                        >
                          {s.label}
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </td>
                <td className="px-3 py-3 text-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onRemove(candidate.id)}
                    className="text-muted-foreground hover:text-destructive"
                    aria-label="移除"
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
