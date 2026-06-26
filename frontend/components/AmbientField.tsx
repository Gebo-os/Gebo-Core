"use client";

import { useEffect, useRef } from "react";
import { useGebo } from "@/lib/GeboProvider";

interface Blob {
  baseX: number;
  baseY: number;
  driftX: number;
  driftY: number;
  radius: number;
  phase: number;
  speed: number;
}

export function AmbientField({ calm = false }: { calm?: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { geboStatus, online, motionEnabled } = useGebo();

  const stateRef = useRef({ geboStatus, online, calm });
  stateRef.current = { geboStatus, online: online === true, calm };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const prefersReduced =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const reduce = prefersReduced || !motionEnabled;

    let raf = 0;
    let width = 0;
    let height = 0;
    let t = 0;
    const blobs: Blob[] = [];

    const rgb = () => {
      const s = stateRef.current;
      if (!s.online) return "232,85,85";
      if (s.geboStatus === "Awake") return "61,255,110";
      if (s.geboStatus === "Resting") return "46,204,85";
      return "212,160,23";
    };

    const build = () => {
      blobs.length = 0;
      const spots = [
        { x: 0.18, y: 0.12 },
        { x: 0.82, y: 0.28 },
        { x: 0.5, y: 0.85 },
      ];
      for (const s of spots) {
        blobs.push({
          baseX: width * s.x,
          baseY: height * s.y,
          driftX: width * (0.04 + Math.random() * 0.05),
          driftY: height * (0.04 + Math.random() * 0.05),
          radius: Math.max(width, height) * (0.28 + Math.random() * 0.12),
          phase: Math.random() * Math.PI * 2,
          speed: 0.0015 + Math.random() * 0.0015,
        });
      }
    };

    const resize = () => {
      // Backdrop is heavily blurred, so render at 1x to keep gradient fills cheap.
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.max(1, Math.round(width));
      canvas.height = Math.max(1, Math.round(height));
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      build();
    };

    const draw = () => {
      const color = rgb();
      const s = stateRef.current;
      const calm = s.calm || s.geboStatus !== "Awake";
      ctx.clearRect(0, 0, width, height);
      ctx.globalCompositeOperation = "lighter";

      for (const b of blobs) {
        const x = b.baseX + Math.cos(t * b.speed + b.phase) * b.driftX;
        const y = b.baseY + Math.sin(t * b.speed * 0.8 + b.phase) * b.driftY;
        const pulse = 0.5 + 0.5 * Math.sin(t * 0.01 + b.phase);
        const alpha = (calm ? 0.03 : 0.05) * (0.7 + 0.3 * pulse);
        const g = ctx.createRadialGradient(x, y, 0, x, y, b.radius);
        g.addColorStop(0, `rgba(${color},${alpha.toFixed(3)})`);
        g.addColorStop(1, `rgba(${color},0)`);
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(x, y, b.radius, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.globalCompositeOperation = "source-over";
    };

    const FRAME_MS = 1000 / 24;
    let last = 0;
    const loop = (now: number) => {
      raf = requestAnimationFrame(loop);
      if (now - last < FRAME_MS) return;
      last = now;
      t += 1;
      draw();
    };

    const start = () => {
      if (reduce) {
        draw();
        return;
      }
      cancelAnimationFrame(raf);
      last = 0;
      raf = requestAnimationFrame(loop);
    };

    const onVisibility = () => {
      if (document.hidden) cancelAnimationFrame(raf);
      else start();
    };

    resize();
    start();

    window.addEventListener("resize", resize);
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [motionEnabled, calm]);

  return <canvas ref={canvasRef} className="ambient-field" aria-hidden="true" />;
}
