import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Layers,
  Eye,
  Maximize2,
  Download,
  Info,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

/* ── Colour legend (area-of-interest key) ── */
function ColorLegend() {
  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <span>Low</span>
      <span
        className="h-2.5 w-28 rounded-full"
        style={{ background: 'linear-gradient(to right, #2563EB, #D97706, #DC2626)' }}
      />
      <span className="font-medium text-foreground">High · Area of interest</span>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════
   HeatmapViewer
   ══════════════════════════════════════════════════════════ */
export default function HeatmapViewer({ uploadedFile, prediction, confidence, heatmapBase64 }) {
  const [activeTab, setActiveTab] = useState('heatmap');
  const [zoom, setZoom] = useState(1);

  const zoomIn = () => setZoom((z) => Math.min(z + 0.25, 3));
  const zoomOut = () => setZoom((z) => Math.max(z - 0.25, 0.5));
  const zoomReset = () => setZoom(1);

  // Object URL for the original upload — create AND revoke in the same effect
  // (StrictMode-safe; the old useMemo+separate-cleanup version revoked the URL
  // without recreating it, which broke the Original image)
  const [originalUrl, setOriginalUrl] = useState(null);
  useEffect(() => {
    if (!uploadedFile) {
      setOriginalUrl(null);
      return;
    }
    const url = URL.createObjectURL(uploadedFile);
    setOriginalUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [uploadedFile]);

  const hasHeatmap = !!heatmapBase64;
  const hasOriginal = !!originalUrl;

  return (
    <Card>
      {/* Header */}
      <CardHeader className="pb-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle className="text-sm font-semibold">Grad-CAM Explainability</CardTitle>
            <p className="text-xs text-muted-foreground">
              {prediction} — {confidence.toFixed(1)}% confidence
            </p>
          </div>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-fit print:hidden">
            <TabsList className="h-7">
              <TabsTrigger value="heatmap" className="text-[11px] gap-1 px-2.5 h-6">
                <Layers className="h-3 w-3" />
                Heatmap
              </TabsTrigger>
              <TabsTrigger value="original" className="text-[11px] gap-1 px-2.5 h-6">
                <Eye className="h-3 w-3" />
                Original
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>

      {/* Viewer */}
      <CardContent className="p-0">
        <div className="relative bg-muted/30 border-y print:hidden">
          {/* Toolbar */}
          <div className="absolute right-3 top-3 z-20 flex flex-col gap-0.5">
            {[
              { icon: ZoomIn, action: zoomIn, label: 'Zoom in' },
              { icon: ZoomOut, action: zoomOut, label: 'Zoom out' },
              { icon: RotateCcw, action: zoomReset, label: 'Reset' },
            ].map((btn) => (
              <Button
                key={btn.label}
                variant="outline"
                size="icon-xs"
                onClick={btn.action}
                title={btn.label}
                className="h-7 w-7 bg-background/80 backdrop-blur-sm"
              >
                <btn.icon className="h-3 w-3" />
              </Button>
            ))}
          </div>

          {/* Zoom readout */}
          <span className="absolute bottom-3 left-3 z-20 rounded-md border bg-background/90 px-2 py-0.5 text-[10px] font-mono tabular-nums backdrop-blur-sm">
            {Math.round(zoom * 100)}%
          </span>

          {/* Image canvas */}
          <div className="relative overflow-hidden" style={{ height: '420px' }}>
            {activeTab === 'heatmap' ? (
              <motion.div
                className="relative h-full w-full origin-center"
                animate={{ scale: zoom }}
                transition={{ type: 'spring', stiffness: 260, damping: 22 }}
              >
                {hasHeatmap ? (
                  <img
                    src={`data:image/png;base64,${heatmapBase64}`}
                    alt="Grad-CAM heatmap overlay"
                    className="h-full w-full object-contain"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center">
                    <p className="text-sm text-muted-foreground">
                      Heatmap not available — run prediction first
                    </p>
                  </div>
                )}
              </motion.div>
            ) : (
              <motion.div
                className="relative h-full w-full origin-center"
                animate={{ scale: zoom }}
                transition={{ type: 'spring', stiffness: 260, damping: 22 }}
              >
                {hasOriginal ? (
                  <img
                    src={originalUrl}
                    alt="Original slide"
                    className="h-full w-full object-contain"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center">
                    <p className="text-sm text-muted-foreground">
                      No image uploaded
                    </p>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        </div>

        {/* Print-only: include BOTH original + heatmap in the exported report */}
        <div className="hidden print:block px-4 py-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-semibold mb-1.5">Original slide</p>
              {hasOriginal ? (
                <img
                  src={originalUrl}
                  alt="Original slide"
                  className="w-full rounded-md border object-contain"
                />
              ) : (
                <p className="text-xs text-muted-foreground">No image uploaded</p>
              )}
            </div>
            <div>
              <p className="text-xs font-semibold mb-1.5">Grad-CAM heatmap · area of interest</p>
              {hasHeatmap ? (
                <img
                  src={`data:image/png;base64,${heatmapBase64}`}
                  alt="Grad-CAM heatmap"
                  className="w-full rounded-md border object-contain"
                />
              ) : (
                <p className="text-xs text-muted-foreground">Heatmap not available</p>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex flex-col gap-2 px-4 py-2.5 sm:flex-row sm:items-center sm:justify-between">
          <ColorLegend />
          <div className="flex items-center gap-2 print:hidden">
            <Badge variant="secondary" className="gap-1 text-[10px]">
              <Info className="h-3 w-3" />
              {activeTab === 'heatmap' ? 'Grad-CAM overlay' : 'Original slide'}
            </Badge>
            <Button variant="ghost" size="icon-xs">
              <Download className="h-3.5 w-3.5" />
            </Button>
            <Button variant="ghost" size="icon-xs">
              <Maximize2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}