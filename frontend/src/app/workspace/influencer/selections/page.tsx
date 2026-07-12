"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import {
  WorkspaceBody,
  WorkspaceContainer,
  WorkspaceHeader,
} from "@/components/workspace/workspace-container";
import {
  createSelection,
  listSelections,
} from "@/core/influencer/api";
import {
  SELECTION_STATUS_LABELS,
  type Selection,
} from "@/core/influencer/types";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 10;

const STATUS_OPTIONS = [
  { value: "all", label: "全部" },
  { value: "draft", label: "草稿" },
  { value: "in_progress", label: "进行中" },
  { value: "completed", label: "已完成" },
  { value: "archived", label: "已归档" },
];

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

function formatDate(dateStr?: string): string {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  if (Number.isNaN(date.getTime())) return dateStr;
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function TableSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 rounded-lg border p-4">
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-4 w-24" />
          </div>
          <Skeleton className="h-6 w-16 rounded-full" />
        </div>
      ))}
    </div>
  );
}

export default function SelectionsPage() {
  const [selections, setSelections] = useState<Selection[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newGoal, setNewGoal] = useState("");
  const [creating, setCreating] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const fetchSelections = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, unknown> = {
        page,
        page_size: PAGE_SIZE,
      };
      if (statusFilter !== "all") {
        params.status = statusFilter;
      }
      const data = await listSelections(params);
      if (!signal?.aborted) {
        setSelections(data.data);
        setTotal(data.total);
      }
    } catch (err: unknown) {
      if (signal?.aborted) return;
      const message = err instanceof Error ? err.message : "加载选人任务失败";
      setError(message);
      toast.error(message);
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [page, statusFilter]);

  useEffect(() => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    void fetchSelections(controller.signal);
    return () => controller.abort();
  }, [fetchSelections]);

  // Reset page when filter changes
  useEffect(() => {
    setPage(1);
  }, [statusFilter]);

  useEffect(() => {
    document.title = "选人任务 - DeerFlow";
  }, []);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      await createSelection({
        title: newTitle.trim(),
        goal: newGoal.trim() || undefined,
      });
      toast.success("创建成功");
      setNewTitle("");
      setNewGoal("");
      setCreateOpen(false);
      void fetchSelections();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "创建失败");
    } finally {
      setCreating(false);
    }
  };

  return (
    <WorkspaceContainer>
      <WorkspaceHeader />
      <WorkspaceBody>
        <div className="mx-auto flex w-full max-w-(--container-width-md) flex-col gap-4 p-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold">选人任务</h1>
            <Button onClick={() => setCreateOpen(true)}>新建任务</Button>
          </div>

          {/* Status filter */}
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground text-sm">状态筛选：</span>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STATUS_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {error && !loading && (
            <div className="text-destructive text-sm">加载失败: {error}</div>
          )}

          {loading && <TableSkeleton />}

          {!loading && !error && selections.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <p className="text-lg">暂无选人任务</p>
              <p className="mt-1 text-sm">点击&quot;新建任务&quot;开始创建选人任务</p>
            </div>
          )}

          {!loading && selections.length > 0 && (
            <>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-3 text-left font-medium">任务名称</th>
                      <th className="hidden px-4 py-3 text-left font-medium sm:table-cell">
                        状态
                      </th>
                      <th className="hidden px-4 py-3 text-left font-medium md:table-cell">
                        创建时间
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {selections.map((sel) => (
                      <tr
                        key={sel.id}
                        className="border-b hover:bg-muted/50"
                      >
                        <td className="px-4 py-3">
                          <Link
                            href={`/workspace/influencer/selections/${sel.id}`}
                            className="hover:text-primary font-medium transition-colors"
                          >
                            {sel.title}
                          </Link>
                        </td>
                        <td className="hidden px-4 py-3 sm:table-cell">
                          <Badge
                            variant="outline"
                            className={cn("text-xs", getStatusClassName(sel.status))}
                          >
                            {SELECTION_STATUS_LABELS[sel.status] ?? sel.status}
                          </Badge>
                        </td>
                        <td className="text-muted-foreground hidden px-4 py-3 md:table-cell">
                          {formatDate(sel.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-4 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                  >
                    上一页
                  </Button>
                  <span className="text-muted-foreground text-sm">
                    第 {page} / {totalPages} 页 (共 {total} 个任务)
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= totalPages}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    下一页
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </WorkspaceBody>

      {/* Create dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新建选人任务</DialogTitle>
            <DialogDescription>
              创建一个新的达人选拔任务，后续可添加候选达人并进行 AI 匹配分析。
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium">任务名称</label>
              <Input
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="例如: 618美妆达人选拔"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">选人目标 (可选)</label>
              <Textarea
                rows={3}
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                placeholder="描述本次选人的目标和标准..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCreateOpen(false)}
              disabled={creating}
            >
              取消
            </Button>
            <Button
              onClick={handleCreate}
              disabled={!newTitle.trim() || creating}
            >
              {creating ? "创建中..." : "创建"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </WorkspaceContainer>
  );
}
