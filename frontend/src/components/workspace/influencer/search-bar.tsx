"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SearchBarProps {
  keyword: string;
  onKeywordChange: (value: string) => void;
  onSearch: () => void;
}

export function SearchBar({
  keyword,
  onKeywordChange,
  onSearch,
}: SearchBarProps) {
  return (
    <div className="flex gap-2">
      <Input
        placeholder="搜索达人名称、品类..."
        value={keyword}
        onChange={(e) => onKeywordChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") onSearch();
        }}
        className="flex-1"
      />
      <Button onClick={onSearch}>搜索</Button>
    </div>
  );
}
