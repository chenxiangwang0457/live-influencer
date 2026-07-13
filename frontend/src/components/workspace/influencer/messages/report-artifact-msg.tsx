"use client";

import { ChevronDown, ChevronUp, Download } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { stripBasicMarkdown } from "@/core/influencer/types";
import { cn } from "@/lib/utils";

interface ReportArtifactMsgProps {
  title?: string;
  content: string;
}

const COLLAPSE_THRESHOLD = 2000;

export function ReportArtifactMsg({
  title,
  content,
}: ReportArtifactMsgProps) {
  const [collapsed, setCollapsed] = useState(
    content.length > COLLAPSE_THRESHOLD,
  );

  const displayContent = useMemo(() => {
    if (collapsed) {
      const truncated = content.slice(0, COLLAPSE_THRESHOLD);
      return truncated + "\n\n...";
    }
    return content;
  }, [content, collapsed]);

  const isLong = content.length > COLLAPSE_THRESHOLD;
  const plainText = useMemo(() => stripBasicMarkdown(displayContent), [displayContent]);

  return (
    <div className="my-3 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">
          {title ?? "达人分析报告"}
        </p>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            disabled
            title="下载功能即将上线"
          >
            <Download className="mr-1.5 size-3.5" />
            下载报告
          </Button>
          {isLong && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCollapsed((prev) => !prev)}
            >
              {collapsed ? (
                <>
                  <ChevronDown className="mr-1 size-3.5" />
                  展开
                </>
              ) : (
                <>
                  <ChevronUp className="mr-1 size-3.5" />
                  收起
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Content */}
      <div
        className={cn(
          "border-border bg-muted/30 overflow-auto rounded-lg border p-4",
          collapsed && "max-h-80",
        )}
      >
        <pre className="text-muted-foreground whitespace-pre-wrap break-words font-sans text-sm leading-relaxed">
          {plainText}
        </pre>
      </div>
    </div>
  );
}
