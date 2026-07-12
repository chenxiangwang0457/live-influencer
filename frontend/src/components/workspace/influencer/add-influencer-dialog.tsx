"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  addCandidate,
  searchInfluencers,
} from "@/core/influencer/api";
import {
  formatFollowers,
  getInitials,
  type Influencer,
} from "@/core/influencer/types";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  selectionId: string;
  onAdded: () => void;
}

export function AddInfluencerDialog({
  open,
  onOpenChange,
  selectionId,
  onAdded,
}: Props) {
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState<Influencer[]>([]);
  const [loading, setLoading] = useState(false);
  const [adding, setAdding] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const fetchResults = useCallback(
    async (kw: string, signal?: AbortSignal) => {
      if (!kw.trim()) {
        setResults([]);
        return;
      }
      setLoading(true);
      try {
        const data = await searchInfluencers({
          keyword: kw,
          page_size: 10,
        });
        if (!signal?.aborted) {
          setResults(data.data);
        }
      } catch {
        if (!signal?.aborted) {
          toast.error("搜索失败");
        }
      } finally {
        if (!signal?.aborted) {
          setLoading(false);
        }
      }
    },
    [],
  );

  const handleKeywordChange = useCallback(
    (value: string) => {
      setKeyword(value);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        if (abortRef.current) abortRef.current.abort();
        const controller = new AbortController();
        abortRef.current = controller;
        void fetchResults(value, controller.signal);
      }, 300);
    },
    [fetchResults],
  );

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      if (abortRef.current) abortRef.current.abort();
    };
  }, []);

  const handleAdd = useCallback(
    async (inf: Influencer) => {
      setAdding(inf.platform_uid);
      try {
        await addCandidate(selectionId, {
          influencer_id: inf.platform_uid,
          added_by: "manual_add",
        });
        toast.success(`已添加${inf.nickname}`);
        onAdded();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "添加失败";
        toast.error(msg);
      } finally {
        setAdding(null);
      }
    },
    [selectionId, onAdded],
  );

  useEffect(() => {
    if (!open) {
      setKeyword("");
      setResults([]);
    }
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[80vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>手动添加达人</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Input
            placeholder="搜索达人名称..."
            value={keyword}
            onChange={(e) => handleKeywordChange(e.target.value)}
            autoFocus
          />

          {loading && (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-lg" />
              ))}
            </div>
          )}

          {!loading && keyword && results.length === 0 && (
            <p className="text-muted-foreground py-4 text-center text-sm">
              未找到匹配的达人
            </p>
          )}

          {!loading &&
            results.map((inf) => (
              <div
                key={inf.platform_uid}
                className="flex items-center gap-3 rounded-lg border p-3"
              >
                <Avatar className="size-10 shrink-0">
                  <AvatarImage src={inf.avatar_url} />
                  <AvatarFallback>{getInitials(inf.nickname)}</AvatarFallback>
                </Avatar>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">
                    {inf.nickname}
                  </p>
                  <div className="mt-0.5 flex flex-wrap gap-1">
                    <Badge variant="secondary" className="text-xs">
                      {inf.category}
                    </Badge>
                    <span className="text-muted-foreground text-xs">
                      {formatFollowers(inf.followers_count)} 粉丝
                    </span>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={adding === inf.platform_uid}
                  onClick={() => handleAdd(inf)}
                >
                  {adding === inf.platform_uid ? "添加中..." : "添加"}
                </Button>
              </div>
            ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
