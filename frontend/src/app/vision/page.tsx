"use client";

import { useState, useRef, useCallback } from "react";
import { FiCamera, FiUpload, FiX, FiLoader } from "react-icons/fi";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "@/lib/api";

export default function VisionPage() {
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
      // Extract base64 without data:...;base64, prefix
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
        video: { facingMode: "environment" },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraActive(true);
    } catch {
      setError("Camera access denied or not available.");
    }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setCameraActive(false);
  }, []);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx?.drawImage(video, 0, 0);
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
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">
          Live Vision Solver
        </h1>
        <p className="text-gray-400">
          Snap a photo or upload an image of a math problem, diagram, or code
          snippet. The AI will analyze and solve it!
        </p>
      </div>

      {/* Image Input Area */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 space-y-4">
        {!preview && !cameraActive && (
          <div className="flex flex-col items-center gap-4">
            <div className="flex gap-4">
              <button
                onClick={startCamera}
                className="flex items-center gap-2 px-6 py-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors"
              >
                <FiCamera size={20} /> Use Camera
              </button>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors"
              >
                <FiUpload size={20} /> Upload Image
              </button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileUpload}
            />
            <p className="text-gray-500 text-sm">
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
              className="w-full max-h-[400px] rounded-lg object-contain bg-black"
            />
            <div className="flex gap-3 justify-center">
              <button
                onClick={capturePhoto}
                className="px-6 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg transition-colors"
              >
                Capture
              </button>
              <button
                onClick={stopCamera}
                className="px-6 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Preview */}
        {preview && (
          <div className="space-y-3">
            <div className="relative inline-block">
              <img
                src={preview}
                alt="Captured"
                className="max-h-[350px] rounded-lg border border-gray-600"
              />
              <button
                onClick={clearImage}
                className="absolute top-2 right-2 p-1 bg-red-600 hover:bg-red-500 rounded-full text-white"
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
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 space-y-4">
          <label className="text-sm text-gray-300 font-medium">
            Prompt (optional — customize what the AI should do)
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={2}
            className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white resize-none focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={handleSolve}
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 text-red-300">
          {error}
        </div>
      )}

      {/* Result */}
      {answer && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Solution</h2>
            {modelUsed && (
              <span className="text-xs bg-gray-700 px-2 py-1 rounded text-gray-400">
                {modelUsed.split("/").pop()}
              </span>
            )}
          </div>
          <div className="prose prose-invert max-w-none text-gray-200">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {answer}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
