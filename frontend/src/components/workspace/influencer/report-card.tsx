"use client";

import { FileText } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface Props {
  report: string;
}

function stripBasicMarkdown(md: string): string {
  return md
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/\*(.+?)\*/g, "$1")
    .replace(/`(.+?)`/g, "$1")
    .replace(/\[(.+?)\]\(.+?\)/g, "$1")
    .replace(/^[-*+]\s+/gm, "• ")
    .replace(/^\d+\.\s+/gm, "")
    .replace(/^>\s?/gm, "")
    .replace(/---+/g, "─".repeat(40));
}

export function ReportCard({ report }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!report) return null;

  const lines = report.split("\n");
  const isLong = lines.length > 30 || report.length > 2000;
  const displayText = isLong && !expanded
    ? lines.slice(0, 30).join("\n") + "\n\n..."
    : report;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="size-4" />
            AI 推荐报告
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            disabled
            title="功能即将上线"
          >
            下载报告
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <pre className="text-muted-foreground whitespace-pre-wrap font-sans text-sm leading-relaxed">
          {stripBasicMarkdown(displayText)}
        </pre>
        {isLong && (
          <Button
            variant="link"
            size="sm"
            className="mt-2 px-0"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "收起" : "展开全部"}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
