import { motion } from 'framer-motion';
import {
  BrainCircuit,
  BarChart3,
  Clock,
  Cpu,
  TrendingUp,
  TrendingDown,
  ShieldCheck,
  Activity,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';

/* ── Summary card for one metric ── */
function StatCard({ icon: Icon, label, children, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.06, duration: 0.25 }}
    >
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <Icon className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              {label}
            </span>
          </div>
          {children}
        </CardContent>
      </Card>
    </motion.div>
  );
}

/* ── Mini confidence bar for secondary classes ── */
function ConfidenceBar({ label, score }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-[90px] shrink-0 text-xs text-muted-foreground">{label}</span>
      <Progress value={score} className="h-1.5 flex-1" />
      <span className="w-9 text-right text-xs font-mono tabular-nums text-muted-foreground">
        {score.toFixed(1)}%
      </span>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════
   StatsPanel
   ══════════════════════════════════════════════════════════ */
export default function StatsPanel({ analysis, isProcessing }) {
  const {
    prediction,
    predictionLabel,
    confidence,
    timeSaved,
    modelStatus,
    secondaryPredictions = [],
  } = analysis;

  const isMalignant = predictionLabel === 'Malignant';

  return (
    <section className="space-y-4">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {/* 1 — Prediction */}
        <StatCard icon={BrainCircuit} label="Prediction" delay={0}>
          {isProcessing ? (
            <div className="space-y-2">
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-4 w-20" />
            </div>
          ) : (
            <div className="space-y-2.5">
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight">{prediction}</span>
                <Badge
                  variant={isMalignant ? 'destructive' : 'secondary'}
                  className="gap-1 text-[10px]"
                >
                  {isMalignant ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  {predictionLabel}
                </Badge>
              </div>
              {secondaryPredictions.length > 0 && (
                <div className="space-y-1.5">
                  {secondaryPredictions.map((p) => (
                    <ConfidenceBar key={p.label} label={p.label} score={p.score} />
                  ))}
                </div>
              )}
            </div>
          )}
        </StatCard>

        {/* 2 — Confidence */}
        <StatCard icon={BarChart3} label="Confidence" delay={1}>
          {isProcessing ? (
            <Skeleton className="h-6 w-20" />
          ) : (
            <div className="space-y-2.5">
              <div className="flex items-baseline gap-1">
                <span className="text-xl font-bold tracking-tight">
                  {confidence.toFixed(1)}
                </span>
                <span className="text-sm text-muted-foreground">%</span>
              </div>
              <div>
                <div className="mb-1 flex justify-between text-[10px] text-muted-foreground">
                  <span>Low</span>
                  <span>High</span>
                </div>
                <Progress value={confidence} />
              </div>
            </div>
          )}
        </StatCard>

        {/* 3 — Time Saved */}
        <StatCard icon={Clock} label="Time Saved" delay={2}>
          {isProcessing ? (
            <Skeleton className="h-6 w-16" />
          ) : (
            <div className="space-y-2.5">
              <div className="flex items-baseline gap-1">
                <span className="text-xl font-bold tracking-tight">{timeSaved}</span>
                <span className="text-sm text-muted-foreground">%</span>
              </div>
              <p className="text-xs text-muted-foreground">
                vs. manual pathologist review
              </p>
            </div>
          )}
        </StatCard>

        {/* 4 — Model Status */}
        <StatCard icon={Cpu} label="Status" delay={3}>
          {isProcessing ? (
            <Skeleton className="h-6 w-24" />
          ) : (
            <div className="space-y-2.5">
              <div className="flex items-center gap-2">
                <span
                  className={`inline-block h-2 w-2 rounded-full ${
                    modelStatus === 'live' ? 'bg-emerald-500' : 'bg-muted-foreground'
                  }`}
                />
                <span className="text-lg font-semibold capitalize tracking-tight">
                  {modelStatus}
                </span>
              </div>
              <Badge variant="secondary" className="gap-1 text-[10px] font-mono">
                <ShieldCheck className="h-3 w-3" />
                v4.1.0
              </Badge>
            </div>
          )}
        </StatCard>
      </div>

      {/* Pipeline ~processing banner */}
      {isProcessing && (
        <Card className="border-dashed">
          <CardContent className="flex items-center gap-3 p-3">
            <Activity className="h-4 w-4 animate-pulse text-primary" />
            <div>
              <p className="text-sm font-semibold">AI Pipeline Running</p>
              <p className="text-xs text-muted-foreground">
                Preprocessing → Patch extraction → Inference → Grad-CAM
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </section>
  );
}