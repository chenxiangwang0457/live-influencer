"use client";

import { Download, FileText } from "lucide-react";
import { useCallback, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface Props {
  report: string;
  filename?: string;
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

export function ReportCard({ report, filename }: Props) {
  const [expanded, setExpanded] = useState(false);

  const handleDownload = useCallback(() => {
    const blob = new Blob([report], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename ?? "influencer-report.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [report, filename]);

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
          <Button variant="outline" size="sm" onClick={handleDownload}>
            <Download className="mr-1 size-3.5" />
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
