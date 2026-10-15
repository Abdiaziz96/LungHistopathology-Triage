import { useState, useCallback, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Microscope,
  ShieldCheck,
  Info,
  Sparkles,
  User,
  FileText,
  ChevronDown,
  Bell,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import UploadZone from './components/UploadZone';
import StatsPanel from './components/StatsPanel';
import HeatmapViewer from './components/HeatmapViewer';
import { predictImage, checkHealth } from './lib/classifier';

/* ══════════════════════════════════════════════════════════
   Inference runs client-side in the browser via ONNX Runtime (wasm).
   See src/lib/classifier.js. No backend or API_BASE required.
   ══════════════════════════════════════════════════════════ */

/* ══════════════════════════════════════════════════════════
   Header — clinical, no glass, no noise, just structure
   ══════════════════════════════════════════════════════════ */
function Header({ status }) {
  const isLive = status === 'live';

  return (
    <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <div className="flex h-14 items-center gap-4 px-6">
        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <div
            className="flex h-8 w-8 items-center justify-center rounded-md"
            style={{ backgroundColor: '#005EB8' }}
          >
            <Microscope className="h-4 w-4 text-primary-foreground" />
          </div>
          <div className="hidden sm:block">
            <p className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground">
              NHS · Digital Pathology
            </p>
            <p className="text-sm font-semibold leading-tight tracking-tight">
              Lung Triage
            </p>
          </div>
        </div>

        {/* Status */}
        <div className="flex items-center gap-2 ml-4">
          <span
            className={`inline-block h-2 w-2 rounded-full ${
              isLive ? 'bg-emerald-500' : 'bg-amber-500'
            }`}
          />
          <span className="text-xs font-medium text-muted-foreground">
            {isLive ? 'Model Live' : 'Ready'}
          </span>
        </div>

        <div className="flex-1" />

        {/* Right */}
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="hidden md:inline-flex gap-1">
            <ShieldCheck className="h-3 w-3" />
            NHS Trust
          </Badge>
          <Button variant="ghost" size="icon-sm">
            <Bell className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" className="gap-1.5">
            <User className="h-3.5 w-3.5" />
            <span className="hidden sm:inline text-xs">Pathologist</span>
            <ChevronDown className="h-3 w-3 opacity-50" />
          </Button>
        </div>
      </div>
    </header>
  );
}

/* ══════════════════════════════════════════════════════════
   Footer — clinical disclaimer, understated
   ══════════════════════════════════════════════════════════ */
function Footer() {
  return (
    <footer className="border-t bg-muted/30">
      <div className="flex h-12 items-center justify-between px-6">
        <p className="text-xs text-muted-foreground">
          &copy; {new Date().getFullYear()} NHS Trust
        </p>
        <div className="flex items-center gap-1.5 text-xs font-medium text-destructive/70">
          <Info className="h-3 w-3" />
          Retrospective validation only — not for clinical use
        </div>
      </div>
    </footer>
  );
}

/* ══════════════════════════════════════════════════════════
   App
   ══════════════════════════════════════════════════════════ */
export default function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [modelStatus, setModelStatus] = useState('ready');
  const [apiError, setApiError] = useState(null);
  const abortRef = useRef(null);

  useEffect(() => {
    checkHealth().then(setModelStatus);
  }, []);

  const handleUpload = useCallback(async (file) => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsProcessing(true);
    setUploadedFile(file);
    setApiError(null);

    try {
      const data = await predictImage(file);
      if (controller.signal.aborted) return;

      setAnalysis({
        prediction: data.prediction,
        predictionLabel: data.prediction_label,
        confidence: data.confidence,
        timeSaved: data.time_saved_pct,
        modelStatus: data.model_status,
        secondaryPredictions: data.secondary_predictions,
        probabilities: data.probabilities,
        heatmapBase64: data.heatmap_base64,
      });
      checkHealth().then(setModelStatus);
    } catch (err) {
      if (controller.signal.aborted) return;
      setApiError(err.message);
    } finally {
      if (!controller.signal.aborted) setIsProcessing(false);
    }
  }, []);

  const handleReset = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    setUploadedFile(null);
    setIsProcessing(false);
    setAnalysis(null);
    setApiError(null);
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header status={modelStatus} />

      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-6 py-8">
          {/* Page title */}
          <div className="mb-6 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Badge variant="secondary" className="text-[10px] font-medium uppercase tracking-wider">
                  <Sparkles className="h-3 w-3 mr-1" />
                  AI-Assisted Triage
                </Badge>
              </div>
              <h1 className="text-2xl font-bold tracking-tight">
                Precision Lung Cancer Screening
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Upload a whole-slide image for AI-assisted classification with Grad-CAM visualisation.
              </p>
            </div>
            <div className="hidden sm:flex items-center gap-2">
              <Button variant="outline" size="sm" className="gap-1.5" onClick={() => window.print()}>
                <FileText className="h-3.5 w-3.5" />
                Export Report
              </Button>
            </div>
          </div>

          {/* Upload Zone */}
          <div className="mb-6">
            <UploadZone
              onUpload={handleUpload}
              uploadedFile={uploadedFile}
              isProcessing={isProcessing}
              onReset={handleReset}
              error={apiError}
            />
          </div>

          {/* Results */}
          <AnimatePresence mode="wait">
            {analysis && (
              <motion.div
                key="results"
                className="space-y-6"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.25 }}
              >
                <StatsPanel analysis={analysis} isProcessing={isProcessing} />
                <HeatmapViewer
                  uploadedFile={uploadedFile}
                  prediction={analysis.prediction}
                  confidence={analysis.confidence}
                  heatmapBase64={analysis.heatmapBase64}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Empty state */}
          {!uploadedFile && (
            <div className="mt-16 flex flex-col items-center justify-center text-center">
              <Microscope className="h-10 w-10 text-muted-foreground/30" />
              <p className="mt-4 text-sm font-medium text-muted-foreground">
                Upload a histopathology slide to begin analysis
              </p>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}