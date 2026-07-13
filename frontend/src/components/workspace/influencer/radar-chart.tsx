"use client";

import { cn } from "@/lib/utils";

// ── Shared helpers ──

interface PolarPoint {
  x: number;
  y: number;
}

function polarToCartesian(
  cx: number,
  cy: number,
  radius: number,
  angleRad: number,
): PolarPoint {
  return {
    x: cx + radius * Math.cos(angleRad),
    y: cy + radius * Math.sin(angleRad),
  };
}

function buildPolygonPoints(
  cx: number,
  cy: number,
  values: number[],
  maxValue: number,
  maxRadius: number,
  startAngle: number,
  angleStep: number,
): string {
  return values
    .map((v, i) => {
      const angle = startAngle + i * angleStep;
      const r = Math.max(0, (v / maxValue) * maxRadius);
      const p = polarToCartesian(cx, cy, r, angle);
      return `${p.x},${p.y}`;
    })
    .join(" ");
}

// ── Single radar chart ──

interface RadarChartProps {
  data: { label: string; value: number; maxValue?: number }[];
  size?: number;
  className?: string;
  color?: string;
}

const DEFAULT_COLOR = "#3b82f6";
const LEVELS = [0.25, 0.5, 0.75, 1.0];
const LABEL_GAP = 18;

export function RadarChart({
  data,
  size = 280,
  className,
  color = DEFAULT_COLOR,
}: RadarChartProps) {
  if (data.length === 0) return null;

  const cx = size / 2;
  const cy = size / 2;
  const maxRadius = size / 2 - 40;
  const angleStep = (2 * Math.PI) / data.length;
  const startAngle = -Math.PI / 2; // first axis points up

  const dataMax = data[0]?.maxValue ?? 100;

  // Data polygon points
  const dataPoints = data.map((d, i) => {
    const angle = startAngle + i * angleStep;
    const r = Math.max(0, (d.value / dataMax) * maxRadius);
    return polarToCartesian(cx, cy, r, angle);
  });
  const dataPolygonStr = dataPoints.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <div className={cn("flex justify-center", className)}>
      <svg
        viewBox={`0 0 ${size} ${size}`}
        className="h-auto w-full"
        style={{ maxWidth: size }}
        role="img"
        aria-label="四维雷达图"
      >
        {/* Background concentric polygons */}
        {LEVELS.map((level) => {
          const levelValues = data.map(() => level * 100);
          const points = buildPolygonPoints(
            cx,
            cy,
            levelValues,
            100,
            maxRadius,
            startAngle,
            angleStep,
          );
          return (
            <polygon
              key={level}
              points={points}
              fill="none"
              stroke="hsl(var(--border))"
              strokeWidth={1}
              opacity={level === 1 ? 0.6 : 0.35}
            />
          );
        })}

        {/* Axis lines from center to each vertex */}
        {data.map((_, i) => {
          const angle = startAngle + i * angleStep;
          const outer = polarToCartesian(cx, cy, maxRadius, angle);
          return (
            <line
              key={`axis-${i}`}
              x1={cx}
              y1={cy}
              x2={outer.x}
              y2={outer.y}
              stroke="hsl(var(--border))"
              strokeWidth={1}
              opacity={0.25}
            />
          );
        })}

        {/* Data polygon fill + stroke */}
        <polygon
          points={dataPolygonStr}
          fill={color}
          fillOpacity={0.15}
          stroke={color}
          strokeWidth={2}
          strokeLinejoin="round"
        />

        {/* Data point dots */}
        {dataPoints.map((p, i) => (
          <circle
            key={`dot-${i}`}
            cx={p.x}
            cy={p.y}
            r={3.5}
            fill={color}
            stroke="#fff"
            strokeWidth={1.5}
          />
        ))}

        {/* Axis labels */}
        {data.map((d, i) => {
          const angle = startAngle + i * angleStep;
          const labelPos = polarToCartesian(cx, cy, maxRadius + LABEL_GAP, angle);

          // Adjust alignment based on label position
          let textAnchor: "start" | "middle" | "end" = "middle";
          let dy = "0.35em";

          if (labelPos.x < cx - 15) {
            textAnchor = "end";
          } else if (labelPos.x > cx + 15) {
            textAnchor = "start";
          }

          if (labelPos.y < cy - 15) {
            dy = "-0.35em";
          }

          return (
            <text
              key={`label-${i}`}
              x={labelPos.x}
              y={labelPos.y}
              textAnchor={textAnchor}
              dy={dy}
              className="fill-foreground select-none text-xs font-medium"
              fontSize={12}
            >
              {d.label}
            </text>
          );
        })}
      </svg>
    </div>
  );
}

// ── Multi-series overlay radar chart ──

const SERIES_COLORS = [
  "#3b82f6",
  "#ef4444",
  "#22c55e",
  "#f59e0b",
  "#8b5cf6",
  "#ec4899",
];

interface RadarSeries {
  name: string;
  data: number[];
  color?: string;
}

interface MultiRadarChartProps {
  series: RadarSeries[];
  labels: string[];
  size?: number;
  className?: string;
}

export function MultiRadarChart({
  series,
  labels,
  size = 320,
  className,
}: MultiRadarChartProps) {
  if (series.length === 0 || labels.length === 0) return null;

  const cx = size / 2;
  const cy = size / 2;
  const maxRadius = size / 2 - 48;
  const angleStep = (2 * Math.PI) / labels.length;
  const startAngle = -Math.PI / 2;

  const maxValue = 100;

  return (
    <div className={cn("flex flex-col items-center gap-3", className)}>
      <svg
        viewBox={`0 0 ${size} ${size}`}
        className="h-auto w-full"
        style={{ maxWidth: size }}
        role="img"
        aria-label="多人雷达图叠加对比"
      >
        {/* Background concentric polygons */}
        {LEVELS.map((level) => {
          const levelValues = labels.map(() => level * 100);
          const points = buildPolygonPoints(
            cx,
            cy,
            levelValues,
            100,
            maxRadius,
            startAngle,
            angleStep,
          );
          return (
            <polygon
              key={level}
              points={points}
              fill="none"
              stroke="hsl(var(--border))"
              strokeWidth={1}
              opacity={level === 1 ? 0.6 : 0.35}
            />
          );
        })}

        {/* Axis lines */}
        {labels.map((_, i) => {
          const angle = startAngle + i * angleStep;
          const outer = polarToCartesian(cx, cy, maxRadius, angle);
          return (
            <line
              key={`axis-${i}`}
              x1={cx}
              y1={cy}
              x2={outer.x}
              y2={outer.y}
              stroke="hsl(var(--border))"
              strokeWidth={1}
              opacity={0.25}
            />
          );
        })}

        {/* Series polygons */}
        {series.map((s, si) => {
          const c = s.color ?? SERIES_COLORS[si % SERIES_COLORS.length]!;
          const points = buildPolygonPoints(
            cx,
            cy,
            s.data,
            maxValue,
            maxRadius,
            startAngle,
            angleStep,
          );

          return (
            <g key={`series-${si}`}>
              <polygon
                points={points}
                fill={c}
                fillOpacity={0.12}
                stroke={c}
                strokeWidth={2}
                strokeLinejoin="round"
              />
              {s.data.map((_, di) => {
                const angle = startAngle + di * angleStep;
                const r = Math.max(0, (s.data[di]! / maxValue) * maxRadius);
                const p = polarToCartesian(cx, cy, r, angle);
                return (
                  <circle
                    key={`dot-${si}-${di}`}
                    cx={p.x}
                    cy={p.y}
                    r={3}
                    fill={c}
                    stroke="#fff"
                    strokeWidth={1.5}
                  />
                );
              })}
            </g>
          );
        })}

        {/* Axis labels */}
        {labels.map((label, i) => {
          const angle = startAngle + i * angleStep;
          const labelPos = polarToCartesian(cx, cy, maxRadius + LABEL_GAP, angle);

          let textAnchor: "start" | "middle" | "end" = "middle";
          let dy = "0.35em";

          if (labelPos.x < cx - 15) {
            textAnchor = "end";
          } else if (labelPos.x > cx + 15) {
            textAnchor = "start";
          }

          if (labelPos.y < cy - 15) {
            dy = "-0.35em";
          }

          return (
            <text
              key={`label-${i}`}
              x={labelPos.x}
              y={labelPos.y}
              textAnchor={textAnchor}
              dy={dy}
              className="fill-foreground select-none text-xs font-medium"
              fontSize={12}
            >
              {label}
            </text>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1.5">
        {series.map((s, si) => {
          const c = s.color ?? SERIES_COLORS[si % SERIES_COLORS.length]!;
          return (
            <div key={`legend-${si}`} className="flex items-center gap-1.5">
              <span
                className="inline-block size-3 shrink-0 rounded-full"
                style={{ backgroundColor: c }}
              />
              <span className="text-muted-foreground text-xs">{s.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
