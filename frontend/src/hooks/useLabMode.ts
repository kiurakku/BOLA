import { useEffect, useState } from "react";
import { apiBase } from "../config";

export function useLabMode(): { mode: "vulnerable" | "secure" | null; loading: boolean } {
  const [mode, setMode] = useState<"vulnerable" | "secure" | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${apiBase}/api/mode`);
        if (!res.ok) {
          throw new Error("mode");
        }
        const data = (await res.json()) as { reports_authz_mode?: string };
        const m = data.reports_authz_mode;
        if (!cancelled && (m === "vulnerable" || m === "secure")) {
          setMode(m);
        }
      } catch {
        if (!cancelled) {
          setMode(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { mode, loading };
}
