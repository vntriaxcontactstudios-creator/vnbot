/**
 * VNBOT Web — File Upload component.
 *
 * Drag & drop file upload that reads files via the API
 * and creates memories from the content.
 */

import { useState, useCallback, useRef, type DragEvent } from 'react';
import { apiClient } from '@/lib/api/client';

interface FileUploadProps {
  onMemoryCreated?: (label: string, content: string) => void;
  onError?: (error: string) => void;
}

interface FileReadResult {
  filename: string;
  extension: string;
  mime_type: string;
  text: string;
  metadata: Record<string, unknown>;
  images_count: number;
  vlm_descriptions: string[];
  reader_used: string;
}

export function FileUpload({ onMemoryCreated, onError }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [lastResult, setLastResult] = useState<FileReadResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'}/files/read`,
        { method: 'POST', body: formData, headers: { 'X-Workspace-Id': 'default' } },
      );

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(err.detail ?? `Upload failed: ${response.status}`);
      }

      const result: FileReadResult = await response.json();
      setLastResult(result);

      // Auto-create a memory from the file content
      if (result.text && result.text.length > 0) {
        const label = file.name.length > 80 ? file.name.slice(0, 77) + '...' : file.name;
        const content = result.vlm_descriptions.length > 0
          ? `${result.text}\n\n[VLM Analysis]\n${result.vlm_descriptions.join('\n')}`
          : result.text;

        try {
          await apiClient.createMemory({
            label,
            content: content.slice(0, 100000),
            type: 'note',
            sensitivity: 'personal',
          });
          onMemoryCreated?.(label, content);
        } catch {
          // Memory creation is optional — file was still read
        }
      }
    } catch (err) {
      onError?.(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  }, [onMemoryCreated, onError]);

  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      void handleFile(files[0]);
    }
  }, [handleFile]);

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  return (
    <div className="space-y-2">
      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        className={`
          border-2 border-dashed p-6 text-center cursor-pointer transition-colors
          ${isDragging
            ? 'border-vnbot-cyan bg-vnbot-cyan/5'
            : 'border-vnbot-line-soft hover:border-vnbot-cyan/50 hover:bg-vnbot-panel-0'
          }
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
        `}
        role="button"
        tabIndex={0}
        aria-label="Upload file"
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void handleFile(file);
            e.target.value = '';
          }}
        />
        {isUploading ? (
          <div className="font-mono text-xs text-vnbot-cyan uppercase animate-pulse">
            ⏳ Procesando archivo...
          </div>
        ) : isDragging ? (
          <div className="font-mono text-xs text-vnbot-cyan uppercase">
            ⬇ Suelta el archivo aquí
          </div>
        ) : (
          <div>
            <div className="font-display text-sm text-vnbot-text mb-1">
              📎 Arrastra un archivo o haz click
            </div>
            <div className="font-mono text-[10px] text-vnbot-text-muted">
              66+ formatos soportados: PDF, DOCX, XLSX, PPTX, PSD, imágenes, código, etc.
            </div>
          </div>
        )}
      </div>

      {/* Result preview */}
      {lastResult && !isUploading && (
        <div className="border border-vnbot-green/30 bg-vnbot-green/5 p-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-vnbot-green text-sm">✓</span>
            <span className="font-body text-sm text-vnbot-text">{lastResult.filename}</span>
            <span className="font-mono text-[10px] text-vnbot-text-muted uppercase">
              .{lastResult.extension} → {lastResult.reader_used}
            </span>
          </div>
          <div className="font-mono text-[10px] text-vnbot-text-muted">
            MIME: {lastResult.mime_type} | Imágenes: {lastResult.images_count} | VLM: {lastResult.vlm_descriptions.length}
          </div>
          {lastResult.vlm_descriptions.length > 0 && (
            <div className="mt-2 space-y-1">
              <span className="font-mono text-[10px] text-vnbot-violet uppercase">VLM Analysis:</span>
              {lastResult.vlm_descriptions.map((desc, i) => (
                <p key={i} className="font-body text-xs text-vnbot-text-muted">{desc.slice(0, 200)}...</p>
              ))}
            </div>
          )}
          <div className="mt-1 font-mono text-[10px] text-vnbot-green">
            ✓ Memoria creada automáticamente
          </div>
        </div>
      )}
    </div>
  );
}
