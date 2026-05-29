# Fix: Show WSS Enrichment Results on Frontend

## Problem
Phase 1 saves `"enriching": False` so the frontend stops polling immediately and never
picks up the WSS-enriched result from Phase 2.

## Changes

### 1. Backend — `factguard-backend/app/services/financial.py` line 649

```diff
-            "enriching": False,
+            "enriching": True,
```

Flags to the frontend that WSS enrichment is still pending in background.
The `_enrich_with_wss` function already saves the final result with
`"enriching": False` when done.

### 2. Frontend — `factguard-frontend/app/result/[jobId]/page.tsx` lines 137-148

After setting data for a non-processing response, check if enrichment is
still pending and continue polling if so:

```diff
        mountedRef.current && setData(result);
+
+        if (result.enriching === true) {
+          currentInterval = Math.min(currentInterval * 1.5, MAX_INTERVAL);
+          timer = setTimeout(poll, currentInterval);
+          return;
+        }
```

## Result
- User sees Phase 1 analysis immediately (same speed as today)
- Frontend polls 3-4 more cycles (exponential backoff 1.5s → 5s, ~15s max)
- When WSS completes, `enriching` flips to `false`, frontend stops
- If WSS finishes within the polling window, enriched data auto-updates in place
- If WSS is slow, user already has Phase 1 results — no regression
