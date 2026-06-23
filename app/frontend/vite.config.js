import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies the SPA's /api calls to the FastAPI Generate backend (TASK-050), so the
// browser talks same-origin and there is no CORS to configure. Point at a different backend
// with PDLC_BACKEND (e.g. when the API runs on another port/host).
const BACKEND = process.env.PDLC_BACKEND ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: BACKEND, changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") },
    },
  },
});
