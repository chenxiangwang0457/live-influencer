"use client";

import { Star } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const TAG_OPTIONS = [
  "专业度高",
  "配合度好",
  "转化率高",
  "内容质量好",
  "性价比高",
  "粉丝精准",
  "沟通顺畅",
  "效果一般",
  "性价比低",
  "不推荐",
];

interface FeedbackFormProps {
  influencerName: string;
  influencerId: string;
  selectionId?: string;
  onSubmit: (data: {
    influencer_id: string;
    selection_id?: string;
    rating: number;
    review?: string;
    tags?: string[];
  }) => Promise<unknown>;
}

export function FeedbackForm({
  influencerName,
  influencerId,
  selectionId,
  onSubmit,
}: FeedbackFormProps) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [review, setReview] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    );
  };

  const handleSubmit = async () => {
    if (rating === 0) {
      toast.error("请先评分");
      return;
    }
    setSubmitting(true);
    try {
      await onSubmit({
        influencer_id: influencerId,
        selection_id: selectionId,
        rating,
        review: review.trim() || undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
      });
      toast.success("反馈已提交");
      setRating(0);
      setReview("");
      setSelectedTags([]);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "提交失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">
          合作反馈 - {influencerName}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Star rating */}
        <div>
          <p className="mb-2 text-sm font-medium">评分</p>
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                className="cursor-pointer p-0.5"
                onMouseEnter={() => setHoverRating(star)}
                onMouseLeave={() => setHoverRating(0)}
                onClick={() => setRating(star)}
              >
                <Star
                  className={cn(
                    "size-6 transition-colors",
                    (hoverRating || rating) >= star
                      ? "fill-yellow-400 text-yellow-400"
                      : "text-muted-foreground/30",
                  )}
                />
              </button>
            ))}
            <span className="text-muted-foreground ml-2 text-sm">
              {rating > 0 ? `${rating} 星` : "点击评分"}
            </span>
          </div>
        </div>

        {/* Tags */}
        <div>
          <p className="mb-2 text-sm font-medium">评价标签 (可选)</p>
          <div className="flex flex-wrap gap-1.5">
            {TAG_OPTIONS.map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => toggleTag(tag)}
                className={cn(
                  "rounded-full border px-2.5 py-1 text-xs transition-colors cursor-pointer",
                  selectedTags.includes(tag)
                    ? "bg-primary text-primary-foreground border-primary"
                    : "text-muted-foreground hover:border-primary/50",
                )}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* Review text */}
        <div>
          <p className="mb-2 text-sm font-medium">文字评价 (可选)</p>
          <Textarea
            rows={3}
            value={review}
            onChange={(e) => setReview(e.target.value)}
            placeholder="描述合作体验、达人表现、带货效果..."
          />
        </div>

        <Button onClick={handleSubmit} disabled={rating === 0 || submitting}>
          {submitting ? "提交中..." : "提交反馈"}
        </Button>
      </CardContent>
    </Card>
  );
}
