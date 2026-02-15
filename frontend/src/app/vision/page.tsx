"use client";

import { useState, useRef, useCallback } from "react";
import { FiCamera, FiUpload, FiX, FiLoader, FiArrowLeft } from "react-icons/fi";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "@/lib/api";
import AppLayout from "@/components/layout/AppLayout";

export default function VisionPage() {
  const router = useRouter();
  const [imageData, setImageData] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [prompt, setPrompt] = useState(
    "This is an educational problem. Solve it step-by-step and provide a clear explanation."
  );
  const [answer, setAnswer] = useState<string | null>(null);
  const [modelUsed, setModelUsed] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [videoReady, setVideoReady] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // ── File Upload ────────────────────────────────────────
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setPreview(dataUrl);
      const base64 = dataUrl.split(",")[1];
      setImageData(base64);
      setAnswer(null);
      setError(null);
    };
    reader.readAsDataURL(file);
  };

  // ── Camera ─────────────────────────────────────────────
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
        };
        videoRef.current.onplaying = () => {
          setVideoReady(true);
        };
      }
      setCameraActive(true);
      setVideoReady(false);
    } catch {
      setError("Camera access denied or not available.");
    }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setCameraActive(false);
    setVideoReady(false);
  }, []);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    // Guard: ensure video has valid dimensions before capture
    if (video.readyState < 2 || video.videoWidth === 0 || video.videoHeight === 0) {
      setError("Camera is still loading. Please wait a moment and try again.");
      return;
    }
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/png");
    setPreview(dataUrl);
    setImageData(dataUrl.split(",")[1]);
    setAnswer(null);
    setError(null);
    stopCamera();
  }, [stopCamera]);

  // ── Clear ──────────────────────────────────────────────
  const clearImage = () => {
    setImageData(null);
    setPreview(null);
    setAnswer(null);
    setError(null);
    setModelUsed("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ── Solve ──────────────────────────────────────────────
  const handleSolve = async () => {
    if (!imageData || loading) return;
    setLoading(true);
    setError(null);
    setAnswer(null);
    try {
      const res = await api.visionSolve(imageData, prompt);
      setAnswer(res.answer);
      setModelUsed(res.model_used);
    } catch (e: any) {
      setError(e.message || "Vision analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto p-4 md:p-6 space-y-5">
        {/* Header */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-lg bg-bg-tertiary hover:bg-border-default text-text-secondary hover:text-text-primary transition border border-border-default"
            title="Go back"
          >
            <FiArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-text-primary">
              Live Vision Solver
            </h1>
            <p className="text-text-secondary text-sm">
              Snap a photo or upload an image of a problem. AI will analyze and solve it!
            </p>
          </div>
        </div>

        {/* Image Input Area */}
        <div className="glass-card space-y-4">
          {!preview && !cameraActive && (
            <div className="flex flex-col items-center gap-4">
              <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                <button
                  onClick={startCamera}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-accent-blue hover:bg-accent-blue/80 text-white rounded-lg transition-colors w-full sm:w-auto"
                >
                  <FiCamera size={20} /> Use Camera
                </button>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors w-full sm:w-auto"
                >
                  <FiUpload size={20} /> Upload Image
                </button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                className="hidden"
                onChange={handleFileUpload}
              />
              <p className="text-text-secondary text-sm text-center">
                Supports JPG, PNG, WebP. Max recommended: 4MB.
              </p>
            </div>
          )}

          {/* Camera View */}
          {cameraActive && (
            <div className="space-y-3">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full max-h-[60vh] rounded-lg object-contain bg-black"
              />
              <div className="flex gap-3 justify-center">
                <button
                  onClick={capturePhoto}
                  disabled={!videoReady}
                  className="px-6 py-2 bg-accent-green hover:bg-accent-greenHover text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {videoReady ? "Capture" : "Loading..."}
                </button>
                <button
                  onClick={stopCamera}
                  className="px-6 py-2 bg-bg-tertiary hover:bg-border-default text-text-primary rounded-lg transition-colors border border-border-default"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Preview */}
          {preview && (
            <div className="space-y-3">
              <div className="relative inline-block w-full">
                <img
                  src={preview}
                  alt="Captured"
                  className="max-h-[50vh] w-auto rounded-lg border border-border-default mx-auto block"
                />
                <button
                  onClick={clearImage}
                  className="absolute top-2 right-2 p-1.5 bg-red-600 hover:bg-red-500 rounded-full text-white"
                >
                  <FiX size={16} />
                </button>
              </div>
            </div>
          )}

          <canvas ref={canvasRef} className="hidden" />
        </div>

        {/* Prompt & Solve */}
        {imageData && (
          <div className="glass-card space-y-4">
            <label className="text-sm text-text-secondary font-medium">
              Prompt (optional — customize what the AI should do)
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={2}
              className="w-full px-4 py-2 bg-bg-primary border border-border-default rounded-lg text-text-primary resize-none focus:outline-none focus:border-accent-blue transition"
            />
            <button
              onClick={handleSolve}
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-accent-blue to-purple-600 hover:from-accent-blue/80 hover:to-purple-500 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <FiLoader className="animate-spin" size={18} /> Analyzing...
                </>
              ) : (
                "Solve & Explain"
              )}
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Result */}
        {answer && (
          <div className="glass-card space-y-3">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h2 className="text-lg font-semibold text-text-primary">Solution</h2>
              {modelUsed && (
                <span className="text-xs bg-bg-tertiary px-2 py-1 rounded text-text-secondary border border-border-default">
                  {modelUsed.split("/").pop()}
                </span>
              )}
            </div>
            <div className="markdown-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {answer}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
