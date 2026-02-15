"use client";

import { useEffect, useRef, useCallback } from "react";

/**
 * Interactive particle field — floating shapes that drift and react
 * to cursor (desktop) or touch (mobile), like Google Antigravity.
 * Renders on a fixed full-screen canvas behind content.
 *
 * Enhanced with: stars, hexagons, triangles, crosses, pulsing glow,
 * orbital trails, brighter connections, and pointer glow ring.
 */

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  baseOpacity: number;
  color: string;
  shape: "circle" | "ring" | "dot" | "diamond" | "star" | "hexagon" | "triangle" | "cross";
  angle: number;
  angularV: number;
  pulsePhase: number;
  pulseSpeed: number;
  trail: { x: number; y: number }[];
}

const COLORS = [
  "rgba(162, 117, 227, ",   // purple (accent)
  "rgba(56, 189, 248, ",    // blue
  "rgba(16, 185, 129, ",    // green (accent-green)
  "rgba(251, 191, 36, ",    // amber
  "rgba(244, 114, 182, ",   // pink
  "rgba(99, 102, 241, ",    // indigo
  "rgba(34, 211, 238, ",    // cyan
  "rgba(168, 85, 247, ",    // violet
  "rgba(249, 115, 22, ",    // orange
];

const SHAPES: Particle["shape"][] = [
  "circle", "ring", "dot", "diamond", "star", "hexagon", "triangle", "cross",
];

export default function ParticleField({
  count = 70,
  className = "",
}: {
  count?: number;
  className?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const pointerRef = useRef<{ x: number; y: number; active: boolean }>({
    x: -1000,
    y: -1000,
    active: false,
  });
  const rafRef = useRef<number>(0);
  const timeRef = useRef<number>(0);

  const initParticles = useCallback(
    (w: number, h: number) => {
      const particles: Particle[] = [];
      for (let i = 0; i < count; i++) {
        const baseOp = Math.random() * 0.45 + 0.12;
        particles.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 5 + 2,
          opacity: baseOp,
          baseOpacity: baseOp,
          color: COLORS[Math.floor(Math.random() * COLORS.length)],
          shape: SHAPES[Math.floor(Math.random() * SHAPES.length)],
          angle: Math.random() * Math.PI * 2,
          angularV: (Math.random() - 0.5) * 0.03,
          pulsePhase: Math.random() * Math.PI * 2,
          pulseSpeed: 0.02 + Math.random() * 0.03,
          trail: [],
        });
      }
      particlesRef.current = particles;
    },
    [count]
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;
      ctx.scale(dpr, dpr);
      if (particlesRef.current.length === 0) {
        initParticles(window.innerWidth, window.innerHeight);
      }
    };

    resize();
    window.addEventListener("resize", resize);

    // Pointer tracking
    const onPointerMove = (e: PointerEvent) => {
      pointerRef.current = { x: e.clientX, y: e.clientY, active: true };
    };
    const onPointerLeave = () => {
      pointerRef.current.active = false;
    };
    const onTouchMove = (e: TouchEvent) => {
      if (e.touches.length > 0) {
        pointerRef.current = {
          x: e.touches[0].clientX,
          y: e.touches[0].clientY,
          active: true,
        };
      }
    };
    const onTouchEnd = () => {
      pointerRef.current.active = false;
    };

    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerleave", onPointerLeave);
    window.addEventListener("touchmove", onTouchMove, { passive: true });
    window.addEventListener("touchend", onTouchEnd);

    const INFLUENCE_RADIUS = 180;
    const REPEL_FORCE = 1.0;
    const FRICTION = 0.97;
    const MAX_TRAIL = 6;

    const drawStar = (ctxLocal: CanvasRenderingContext2D, size: number) => {
      const spikes = 5;
      const outerR = size;
      const innerR = size * 0.45;
      ctxLocal.beginPath();
      for (let i = 0; i < spikes * 2; i++) {
        const r = i % 2 === 0 ? outerR : innerR;
        const a = (Math.PI * i) / spikes - Math.PI / 2;
        if (i === 0) ctxLocal.moveTo(Math.cos(a) * r, Math.sin(a) * r);
        else ctxLocal.lineTo(Math.cos(a) * r, Math.sin(a) * r);
      }
      ctxLocal.closePath();
    };

    const drawHexagon = (ctxLocal: CanvasRenderingContext2D, size: number) => {
      ctxLocal.beginPath();
      for (let i = 0; i < 6; i++) {
        const a = (Math.PI / 3) * i - Math.PI / 6;
        if (i === 0) ctxLocal.moveTo(Math.cos(a) * size, Math.sin(a) * size);
        else ctxLocal.lineTo(Math.cos(a) * size, Math.sin(a) * size);
      }
      ctxLocal.closePath();
    };

    const drawTriangle = (ctxLocal: CanvasRenderingContext2D, size: number) => {
      ctxLocal.beginPath();
      ctxLocal.moveTo(0, -size);
      ctxLocal.lineTo(size * 0.866, size * 0.5);
      ctxLocal.lineTo(-size * 0.866, size * 0.5);
      ctxLocal.closePath();
    };

    const drawCross = (ctxLocal: CanvasRenderingContext2D, size: number) => {
      const t = size * 0.3;
      ctxLocal.beginPath();
      ctxLocal.moveTo(-t, -size);
      ctxLocal.lineTo(t, -size);
      ctxLocal.lineTo(t, -t);
      ctxLocal.lineTo(size, -t);
      ctxLocal.lineTo(size, t);
      ctxLocal.lineTo(t, t);
      ctxLocal.lineTo(t, size);
      ctxLocal.lineTo(-t, size);
      ctxLocal.lineTo(-t, t);
      ctxLocal.lineTo(-size, t);
      ctxLocal.lineTo(-size, -t);
      ctxLocal.lineTo(-t, -t);
      ctxLocal.closePath();
    };

    const draw = () => {
      timeRef.current += 1;
      const w = window.innerWidth;
      const h = window.innerHeight;
      ctx.clearRect(0, 0, w, h);

      const ptr = pointerRef.current;

      particlesRef.current.forEach((p) => {
        // Pulse opacity
        p.pulsePhase += p.pulseSpeed;
        p.opacity = p.baseOpacity + Math.sin(p.pulsePhase) * 0.12;

        // Pointer interaction — repel
        if (ptr.active) {
          const dx = p.x - ptr.x;
          const dy = p.y - ptr.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < INFLUENCE_RADIUS && dist > 0) {
            const force =
              ((INFLUENCE_RADIUS - dist) / INFLUENCE_RADIUS) * REPEL_FORCE;
            p.vx += (dx / dist) * force;
            p.vy += (dy / dist) * force;
          }
        }

        // Physics
        p.vx *= FRICTION;
        p.vy *= FRICTION;
        p.x += p.vx;
        p.y += p.vy;
        p.angle += p.angularV;

        // Trail
        const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
        if (speed > 0.5) {
          p.trail.push({ x: p.x, y: p.y });
          if (p.trail.length > MAX_TRAIL) p.trail.shift();
        } else if (p.trail.length > 0) {
          p.trail.shift();
        }

        // Wrap around edges
        if (p.x < -20) p.x = w + 20;
        if (p.x > w + 20) p.x = -20;
        if (p.y < -20) p.y = h + 20;
        if (p.y > h + 20) p.y = -20;

        // Draw trail
        if (p.trail.length > 1) {
          ctx.beginPath();
          ctx.moveTo(p.trail[0].x, p.trail[0].y);
          for (let t = 1; t < p.trail.length; t++) {
            ctx.lineTo(p.trail[t].x, p.trail[t].y);
          }
          ctx.strokeStyle = `${p.color}${p.opacity * 0.3})`;
          ctx.lineWidth = p.size * 0.4;
          ctx.lineCap = "round";
          ctx.stroke();
        }

        // Draw glow
        const glowSize = p.size * 3;
        const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, glowSize);
        grd.addColorStop(0, `${p.color}${p.opacity * 0.15})`);
        grd.addColorStop(1, `${p.color}0)`);
        ctx.fillStyle = grd;
        ctx.fillRect(p.x - glowSize, p.y - glowSize, glowSize * 2, glowSize * 2);

        // Draw shape
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.angle);
        ctx.globalAlpha = p.opacity;

        const fillColor = `${p.color}${p.opacity})`;
        const strokeColor = `${p.color}${Math.min(p.opacity + 0.2, 0.7)})`;

        switch (p.shape) {
          case "circle":
            ctx.beginPath();
            ctx.arc(0, 0, p.size, 0, Math.PI * 2);
            ctx.fillStyle = fillColor;
            ctx.fill();
            break;
          case "ring":
            ctx.beginPath();
            ctx.arc(0, 0, p.size, 0, Math.PI * 2);
            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = 1.2;
            ctx.stroke();
            break;
          case "dot":
            ctx.beginPath();
            ctx.arc(0, 0, p.size * 0.5, 0, Math.PI * 2);
            ctx.fillStyle = fillColor;
            ctx.fill();
            break;
          case "diamond":
            ctx.beginPath();
            ctx.moveTo(0, -p.size);
            ctx.lineTo(p.size * 0.6, 0);
            ctx.lineTo(0, p.size);
            ctx.lineTo(-p.size * 0.6, 0);
            ctx.closePath();
            ctx.fillStyle = fillColor;
            ctx.fill();
            break;
          case "star":
            drawStar(ctx, p.size);
            ctx.fillStyle = fillColor;
            ctx.fill();
            break;
          case "hexagon":
            drawHexagon(ctx, p.size);
            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = 1;
            ctx.stroke();
            break;
          case "triangle":
            drawTriangle(ctx, p.size);
            ctx.fillStyle = fillColor;
            ctx.fill();
            break;
          case "cross":
            drawCross(ctx, p.size);
            ctx.fillStyle = fillColor;
            ctx.fill();
            break;
        }

        ctx.restore();
      });

      // Draw connection lines between nearby particles
      const particles = particlesRef.current;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            const alpha = 0.12 * (1 - dist / 120);
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(162, 117, 227, ${alpha})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }

      // Draw pointer glow ring when active
      if (ptr.active) {
        const pr = INFLUENCE_RADIUS;
        const grd2 = ctx.createRadialGradient(ptr.x, ptr.y, pr * 0.3, ptr.x, ptr.y, pr);
        grd2.addColorStop(0, "rgba(162, 117, 227, 0.04)");
        grd2.addColorStop(1, "rgba(162, 117, 227, 0)");
        ctx.fillStyle = grd2;
        ctx.beginPath();
        ctx.arc(ptr.x, ptr.y, pr, 0, Math.PI * 2);
        ctx.fill();
      }

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(rafRef.current);
      window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerleave", onPointerLeave);
      window.removeEventListener("touchmove", onTouchMove);
      window.removeEventListener("touchend", onTouchEnd);
    };
  }, [initParticles]);

  return (
    <canvas
      ref={canvasRef}
      className={`fixed inset-0 pointer-events-none z-0 ${className}`}
      style={{ touchAction: "none" }}
    />
  );
}
