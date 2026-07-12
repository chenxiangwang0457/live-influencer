"use client";

import type { Message } from "@langchain/langgraph-sdk";

import type { Influencer } from "@/core/influencer/types";
import { extractTextFromMessage } from "@/core/messages/utils";

import { CompareTableMsg } from "./compare-table-msg";
import { ReportArtifactMsg } from "./report-artifact-msg";
import { SearchResultMsg } from "./search-result-msg";

/** Parse a tool message's content as JSON, falling back to null. */
function parseToolContent(content: string): Record<string, unknown> | null {
  try {
    const trimmed = content.trim();
    if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
      return JSON.parse(trimmed) as Record<string, unknown>;
    }
  } catch {
    // Not valid JSON — treat as plain text
  }
  return null;
}

/** Try to extract an array of Influencer objects from parsed data. */
function extractInfluencers(
  data: Record<string, unknown>,
): Influencer[] {
  const candidates = data.influencers ?? data.data ?? data.results ?? [];
  if (Array.isArray(candidates)) {
    return candidates as Influencer[];
  }
  return [];
}

interface InfluencerResultRendererProps {
  message: Message;
}

export function InfluencerResultRenderer({
  message,
}: InfluencerResultRendererProps) {
  const influencerType = message.additional_kwargs?.type as
    | string
    | undefined;
  const rawContent = extractTextFromMessage(message);

  if (!influencerType || !rawContent) {
    return null;
  }

  if (influencerType === "influencer:search_result") {
    const data = parseToolContent(rawContent);
    const influencers = data ? extractInfluencers(data) : [];
    const total =
      (data?.total as number) ?? (data?.count as number) ?? influencers.length;

    return <SearchResultMsg influencers={influencers} total={total} />;
  }

  if (influencerType === "influencer:compare") {
    const data = parseToolContent(rawContent);
    const influencers = data ? extractInfluencers(data) : [];

    return <CompareTableMsg influencers={influencers} />;
  }

  if (influencerType === "influencer:report") {
    const data = parseToolContent(rawContent);
    const title = (data?.title as string) ?? undefined;
    const markdown = (data?.content ?? data?.markdown ?? rawContent) as string;

    return <ReportArtifactMsg title={title} content={markdown} />;
  }

  return null;
}

/** Check if a message is an influencer result tool message. */
export function isInfluencerToolMessage(message: Message): boolean {
  const type = message.additional_kwargs?.type;
  return (
    message.type === "tool" &&
    typeof type === "string" &&
    type.startsWith("influencer:")
  );
}
