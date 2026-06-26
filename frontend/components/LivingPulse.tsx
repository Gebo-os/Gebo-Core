"use client";

import { useEffect, useRef } from "react";
import { useGebo } from "@/lib/GeboProvider";

interface Particle {
  angle: number;
  radius: number;
  speed: number;
  size: number;
  offset: number;
}

type Palette = { core: string; rgb: string; calm: boolean };

export function LivingPulse() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { geboStatus, status, online, motionEnabled, pulse } = useGebo();

  // Latest state for the animation loop to read each frame.
  const stateRef = useRef({ geboStatus, memoryCount: 0, online });
  stateRef.current = {
    geboStatus,
    memoryCount: status?.memory_count ?? 0,
    online: online === true,
  };

  // Reactive burst: a ring ripple triggered when `pulse` increments.
  const burstRef = useRef(0);
  const firstPulse = useRef(true);
  useEffect(() => {
    if (firstPulse.current) {
      firstPulse.current = false;
      return;
    }
    burstRef.current = 1;
  }, [pulse]);

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
    const particles: Particle[] = [];

    const palette = (): Palette => {
      const s = stateRef.current;
      if (!s.online) return { core: "#e85555", rgb: "232,85,85", calm: true };
      if (s.geboStatus === "Awake")
        return { core: "#3dff6e", rgb: "61,255,110", calm: false };
      if (s.geboStatus === "Resting")
        return { core: "#2ecc55", rgb: "46,204,85", calm: true };
      return { core: "#d4a017", rgb: "212,160,23", calm: false };
    };

    const targetCount = () =>
      Math.max(10, Math.min(52, 10 + stateRef.current.memoryCount));

    const buildParticles = () => {
      particles.length = 0;
      const maxR = Math.min(width, height) * 0.46;
      const count = targetCount();
      for (let i = 0; i < count; i++) {
        particles.push({
          angle: Math.random() * Math.PI * 2,
          radius: maxR * (0.32 + Math.random() * 0.68),
          speed: 0.0006 + Math.random() * 0.0014,
          size: 1 + Math.random() * 2,
          offset: Math.random() * 1000,
        });
      }
    };

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      width = rect.width;
      height = rect.height;
      canvas.width = Math.max(1, Math.round(width * dpr));
      canvas.height = Math.max(1, Math.round(height * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      buildParticles();
    };

    const draw = () => {
      const p = palette();
      const s = stateRef.current;
      const cx = width / 2;
      const cy = height / 2;
      const activity = s.geboStatus === "Awake" ? 1 : p.calm ? 0.4 : 0.7;

      if (particles.length !== targetCount()) buildParticles();

      ctx.clearRect(0, 0, width, height);

      const breathe = 0.5 + 0.5 * Math.sin(t * 0.018);
      const minDim = Math.min(width, height);

      // Ambient core glow (breathing).
      const glow = ctx.createRadialGradient(cx, cy, 0, cx, cy, minDim * 0.55);
      glow.addColorStop(0, `rgba(${p.rgb},${(0.32 + 0.22 * breathe).toFixed(3)})`);
      glow.addColorStop(0.35, `rgba(${p.rgb},0.08)`);
      glow.addColorStop(1, `rgba(${p.rgb},0)`);
      ctx.fillStyle = glow;
      ctx.fillRect(0, 0, width, height);

      // Compute particle positions.
      const pts = particles.map((pt) => {
        const ang = pt.angle + t * pt.speed * (activity * 2 + 0.3);
        const wob = Math.sin((t + pt.offset) * 0.01) * (minDim * 0.02);
        return {
          x: cx + Math.cos(ang) * (pt.radius + wob),
          y: cy + Math.sin(ang) * (pt.radius + wob) * 0.78,
          size: pt.size,
        };
      });

      // Constellation links.
      const linkDist = minDim * 0.22;
      const linkSq = linkDist * linkDist;
      ctx.lineWidth = 1;
      for (let i = 0; i < pts.length; i++) {
        for (let j = i + 1; j < pts.length; j++) {
          const dx = pts[i].x - pts[j].x;
          const dy = pts[i].y - pts[j].y;
          const d2 = dx * dx + dy * dy;
          if (d2 < linkSq) {
            const a = (1 - d2 / linkSq) * 0.22;
            ctx.strokeStyle = `rgba(${p.rgb},${a.toFixed(3)})`;
            ctx.beginPath();
            ctx.moveTo(pts[i].x, pts[i].y);
            ctx.lineTo(pts[j].x, pts[j].y);
            ctx.stroke();
          }
        }
      }

      // Particle nodes.
      for (const pt of pts) {
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, pt.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.rgb},0.65)`;
        ctx.fill();
      }

      // Core.
      const coreR = minDim * 0.05 * (0.85 + 0.3 * breathe);
      ctx.beginPath();
      ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
      ctx.fillStyle = p.core;
      ctx.globalAlpha = 0.9;
      ctx.fill();
      ctx.globalAlpha = 1;

      // Reactive burst ripple (fired on memory saved / action approved).
      if (burstRef.current > 0) {
        const prog = burstRef.current; // 1 -> 0
        const ringR = minDim * (0.08 + (1 - prog) * 0.5);
        ctx.beginPath();
        ctx.arc(cx, cy, ringR, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(${p.rgb},${(prog * 0.5).toFixed(3)})`;
        ctx.lineWidth = 2;
        ctx.stroke();
        burstRef.current = Math.max(0, prog - 0.03);
      }
    };

    const FRAME_MS = 1000 / 30;
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

    const ro = new ResizeObserver(resize);
    ro.observe(canvas);
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [motionEnabled]);

  return <canvas ref={canvasRef} className="living-pulse-canvas" aria-hidden="true" />;
}
