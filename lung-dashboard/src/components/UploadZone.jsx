import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  CheckCircle2,
  Clock,
  FileWarning,
  Loader2,
  AlertCircle,
  FileText,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';

const ALLOWED_TYPES = {
  'image/tiff': ['.tiff', '.tif'],
  'image/x-tiff': ['.tiff', '.tif'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'application/octet-stream': ['.svs'],
};
const ALLOWED_EXTENSIONS = ['.svs', '.tiff', '.tif', '.png', '.jpg', '.jpeg'];
const FORMAT_PILLS = ['.svs', '.tiff', '.png', '.jpg'];

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function getExtension(filename) {
  const lastDot = filename.lastIndexOf('.');
  return lastDot === -1 ? '' : filename.slice(lastDot).toLowerCase();
}

/* ── Drop zone (idle & drag states) ── */
function DropZone({ getRootProps, getInputProps, isDragActive, isDragReject, rejectReason }) {
  const state = rejectReason || isDragReject ? 'reject' : isDragActive ? 'active' : 'idle';

  const border = {
    idle: 'border-dashed border-muted-foreground/25 hover:border-primary/50 hover:bg-accent/30',
    active: 'border-solid border-primary bg-primary/5',
    reject: 'border-solid border-destructive/50 bg-destructive/5',
  }[state];

  return (
    <Card className={`transition-colors duration-200 ${border}`}>
      <div
        {...getRootProps()}
        className="flex cursor-pointer flex-col items-center justify-center px-6 py-14 text-center"
      >
        <input {...getInputProps()} />

        <div
          className={`mb-4 flex h-12 w-12 items-center justify-center rounded-lg border ${
            state === 'reject'
              ? 'border-destructive/20 bg-destructive/10 text-destructive'
              : state === 'active'
                ? 'border-primary/20 bg-primary/10 text-primary'
                : 'border-border bg-muted text-muted-foreground'
          }`}
        >
          {state === 'reject' ? (
            <FileWarning className="h-5 w-5" />
          ) : (
            <Upload className="h-5 w-5" />
          )}
        </div>

        {state === 'reject' ? (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-destructive">Cannot accept this file</p>
            {rejectReason && (
              <p className="mx-auto max-w-sm text-xs text-destructive/70">{rejectReason}</p>
            )}
          </div>
        ) : (
          <div className="space-y-1.5">
            <p className="text-sm font-semibold">
              {isDragActive ? 'Drop to analyse' : 'Drop a whole-slide image'}
            </p>
            <p className="text-sm text-muted-foreground">
              or <span className="font-medium text-primary underline underline-offset-2">browse files</span>
            </p>
            <div className="flex items-center justify-center gap-1.5 pt-2">
              {FORMAT_PILLS.map((ext) => (
                <Badge key={ext} variant="secondary" className="text-[10px] font-mono">
                  {ext}
                </Badge>
              ))}
              <span className="ml-1 text-xs text-muted-foreground">up to 2 GB</span>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

/* ── File uploaded card ── */
function FileCard({ uploadedFile, isProcessing, onReset, error }) {
  const ext = getExtension(uploadedFile.name).replace('.', '').toUpperCase();

  return (
    <Card>
      <CardContent className="p-0">
        <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3 min-w-0">
            {isProcessing ? (
              <Loader2 className="h-5 w-5 animate-spin text-primary shrink-0" />
            ) : (
              <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
            )}
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">{uploadedFile.name}</p>
              <p className="text-xs text-muted-foreground font-mono">
                {formatBytes(uploadedFile.size)} · {ext}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {isProcessing && (
              <Badge variant="secondary" className="gap-1">
                <Clock className="h-3 w-3" />
                Analysing…
              </Badge>
            )}
            <Button
              variant="outline"
              size="xs"
              onClick={onReset}
              disabled={isProcessing}
            >
              <X className="h-3 w-3 mr-1" />
              Reset
            </Button>
          </div>
        </div>

        {/* Progress / complete bar */}
        <div className="h-0.5 w-full bg-muted">
          {isProcessing ? (
            <motion.div
              className="h-full bg-primary"
              initial={{ width: '0%' }}
              animate={{ width: '100%' }}
              transition={{ duration: 2.1, ease: 'easeInOut' }}
            />
          ) : (
            <div className="h-full w-full bg-emerald-500" />
          )}
        </div>

        {/* API error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <Alert variant="destructive" className="m-4">
                <AlertDescription className="text-xs">{error}</AlertDescription>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
}

/* ══════════════════════════════════════════════════════════
   UploadZone
   ══════════════════════════════════════════════════════════ */
export default function UploadZone({ onUpload, uploadedFile, isProcessing, onReset, error }) {
  const [rejectReason, setRejectReason] = useState(null);

  const onDrop = useCallback(
    (acceptedFiles, rejectedFiles) => {
      setRejectReason(null);
      if (rejectedFiles.length > 0) {
        const r = rejectedFiles[0];
        const ext = getExtension(r.file.name);
        if (!ALLOWED_EXTENSIONS.includes(ext)) {
          setRejectReason(`${ext || 'That format'} is not supported.`);
        } else if (r.errors.some((e) => e.code === 'file-too-large')) {
          setRejectReason('File exceeds the 2 GB size limit.');
        } else {
          setRejectReason('This file could not be accepted.');
        }
        return;
      }
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    },
    [onUpload],
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ALLOWED_TYPES,
    maxSize: 2 * 1024 * 1024 * 1024,
    multiple: false,
    onDropAccepted: () => setRejectReason(null),
    disabled: isProcessing,
  });

  return (
    <AnimatePresence mode="wait">
      {!uploadedFile ? (
        <motion.div
          key="dropzone"
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          <DropZone
            getRootProps={getRootProps}
            getInputProps={getInputProps}
            isDragActive={isDragActive}
            isDragReject={isDragReject}
            rejectReason={rejectReason}
          />
        </motion.div>
      ) : (
        <motion.div
          key="filecard"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          <FileCard
            uploadedFile={uploadedFile}
            isProcessing={isProcessing}
            onReset={onReset}
            error={error}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}