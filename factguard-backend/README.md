# FactGuard

AI-powered misinformation detection tool. Submit a claim, and FactGuard analyses it using Google Gemini 2.5 Flash, returning a verdict with supporting evidence.

## Architecture

```
news-guard/
├── factguard-backend/       # Python FastAPI backend
│   └── app/
│       ├── main.py          # FastAPI app, CORS, routes
│       ├── api/verify.py    # POST /verify endpoint
│       └── services/gemini.py  # Gemini integration
├── factguard-frontend/      # Next.js 16 frontend
│   ├── app/                 # App Router pages
│   ├── components/          # React components
│   ├── lib/                 # API client, utils
│   └── types/               # TypeScript types
├── .env                     # Backend secrets (GEMINI_API_KEY)
├── requirements.txt         # Python dependencies
└── package.json             # Root package.json (stub)
```

## Backend

Python FastAPI server using Google Gemini 2.5 Flash.

### Setup

```bash
cd factguard-backend
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r ..\requirements.txt
```

### Environment

Create `.env` at the project root:

```
GEMINI_API_KEY=your_key_here
FRONTEND_URL=http://localhost:3000
```

### Run

```bash
uvicorn app.main:app --reload --port 8000
```

### API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/verify` | Submit a claim for analysis |
| `GET`  | `/health` | Health check |

`POST /verify` accepts `{ "claim": "string" }` and returns:

```json
{
  "verdict": "Likely True | Likely False | Misleading | Unverified",
  "confidence": "Low | Medium | High",
  "summary": "2 sentence explanation",
  "supports": 3,
  "contradicts": 1,
  "neutral": 0,
  "sources": [{ "title": "...", "url": "...", "stance": "supports", ... }]
}
```

## Frontend

Next.js 16 + Tailwind CSS v4 + TypeScript + shadcn/ui + framer-motion.

### Setup

```bash
cd factguard-frontend
pnpm install
cp .env.example .env.local   # fill in your env vars
pnpm dev                     # http://localhost:3000
```

### Environment

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend base URL (e.g. `http://localhost:8000`) |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon/public key |

### Pages

| Route | File | Description |
|---|---|---|
| `/` | `app/page.tsx` | Landing — claim input + example list |
| `/loading?job=:id` | `app/loading/page.tsx` | Polls backend every 2 s while processing |
| `/result/:jobId` | `app/result/[jobId]/page.tsx` | Verdict, agreement meter, sources, share |

### Commands

```bash
pnpm dev       # dev server
pnpm build     # production build
pnpm lint      # ESLint
pnpm start     # start production server
```

## Data flow

1. User enters a claim on the landing page
2. Frontend sends `POST /verify` to the backend
3. Backend analyses the claim via Gemini 2.5 Flash
4. Response is stored in localStorage with a `jobId`
5. Loading page polls `GET /result/:jobId` (mock polling — currently returns 200 immediately)
6. On completion, redirects to `/result/:jobId` with the verdict

## Stack

- **Backend**: Python, FastAPI, Google Generative AI (Gemini 2.5 Flash)
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS v4
- **UI**: shadcn/ui (Radix Nova), lucide-react, framer-motion
- **Database**: Supabase (Postgres)
