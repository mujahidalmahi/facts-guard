# Requirements Document

## Introduction

The Summarize track is a fifth mode added to the FactGuard multi-track platform. Users supply a URL and receive a structured AI-generated summary of the article at that URL. Content is fetched via the existing Bright Data extraction pipeline (Crawl API → Web Unlocker → Scraping Browser fallback chain), then summarised by the Gemini 2.5 Flash → Groq fallback chain. The result is returned asynchronously via the existing job-based polling pattern and displayed in a dedicated frontend result view.

## Glossary

- **Summarizer**: The backend service (`app/services/summarizer.py`) responsible for orchestrating URL content extraction and AI summarisation.
- **Summary_API**: The FastAPI route handler (`app/api/summarize.py`) that accepts requests and returns job IDs.
- **SummarizeRequest**: The Pydantic request model carrying the URL to summarise.
- **SummarizeResult**: The structured Pydantic response model returned when a job completes.
- **Extraction_Pipeline**: The ordered fallback chain — Bright Data Crawl API → Web Unlocker → Scraping Browser — used to retrieve article content.
- **AI_Chain**: The ordered AI fallback chain — Gemini 2.5 Flash → Groq llama-3.3-70b → heuristic — used to generate summaries.
- **Job**: An asynchronous unit of work identified by a UUID `jobId`, tracked in Redis and Supabase.
- **Key_Point**: A single discrete fact or claim extracted from the article, represented as a string.
- **Reading_Time**: An estimated reading time in minutes, calculated from article word count at 200 words per minute.

---

## Requirements

### Requirement 1: URL Input and Validation

**User Story:** As a FactGuard user, I want to submit a URL and have it validated before processing, so that I receive a clear error immediately if the URL is malformed or points to a non-HTTP(S) resource.

#### Acceptance Criteria

1. THE `SummarizeRequest` SHALL accept a `url` field with a minimum length of 10 characters and a maximum length of 2048 characters.
2. WHEN a `url` value is submitted that does not begin with `http://` or `https://`, THE `Summary_API` SHALL return HTTP 422 with a descriptive validation error before creating a job.
3. WHEN a `url` value contains SQL injection patterns as detected by `contains_sql_injection_pattern`, THE `SummarizeRequest` field validator SHALL raise a `ValueError` with the message `"URL contains invalid characters or patterns"`.
4. THE `SummarizeRequest` field validator SHALL normalise the URL by stripping leading and trailing whitespace before validation.
5. FOR ALL valid URL strings `u`, parsing `u` through `SummarizeRequest` and reading back `SummarizeRequest(url=u).url` SHALL produce a value equal to `u.strip()` (round-trip property).

---

### Requirement 2: Asynchronous Job Creation

**User Story:** As a FactGuard user, I want the summarisation to start immediately and return a job ID, so that the UI can poll for progress without blocking.

#### Acceptance Criteria

1. WHEN a valid `SummarizeRequest` is received, THE `Summary_API` SHALL respond with HTTP 202 and a `JobResponse` containing a UUID `jobId` within 500 ms.
2. WHEN a valid `SummarizeRequest` is received, THE `Summary_API` SHALL enqueue a background task that calls `Summarizer.process` with the `jobId` and URL.
3. THE `Summary_API` SHALL persist the job to Supabase via `create_claim` (reusing the existing claims table with `mode = "summarize"`) before returning the `JobResponse`.
4. WHILE a summarisation job is processing, THE `Summary_API` SHALL return `{"status": "processing", "jobId": "<id>", "progress": "<message>"}` for `GET /result/{jobId}` requests.
5. WHEN a summarisation job has fully completed and its result is stored in Redis or Supabase, THE `Summary_API` SHALL return `{"status": "done", "jobId": "<id>", ...SummarizeResult fields}` for `GET /result/{jobId}` requests; THE `Summary_API` SHALL NOT return `"status": "done"` while the background task is still running.
6. IF a summarisation job fails or times out after 120 seconds, THEN THE `Summary_API` SHALL return `{"status": "error", "jobId": "<id>"}` for `GET /result/{jobId}` requests.

---

### Requirement 3: Article Content Extraction

**User Story:** As a FactGuard user, I want the system to reliably fetch article content even from paywalled or JavaScript-rendered pages, so that I get a meaningful summary rather than an error.

#### Acceptance Criteria

1. WHEN extracting content for a URL, THE `Summarizer` SHALL first attempt extraction via the Bright Data Crawl API (`brightdata.crawl_extract`), tagged with `bright_data_product = "crawl"`.
2. IF the Crawl API returns `None` or an empty body, THEN THE `Summarizer` SHALL attempt extraction via the Bright Data Web Unlocker (`brightdata.unlocker_scrape`), tagged with `bright_data_product = "web_unlocker"`.
3. IF the Web Unlocker also returns `None` or fewer than 200 characters of content, THEN THE `Summarizer` SHALL attempt extraction via the Bright Data Scraping Browser (`brightdata.browser_extract_text`), tagged with `bright_data_product = "scraping_browser"`.
4. IF all three extraction tiers fail to return at least 200 characters of content, THEN THE `Summarizer` SHALL set the job status to `error` and record the reason `"content_extraction_failed"` in the job result.
5. WHEN content is successfully extracted, THE `Summarizer` SHALL truncate the body to a maximum of 8000 characters before passing it to the AI_Chain, to stay within model context limits.
6. THE `Summarizer` SHALL record which `bright_data_product` tier was used in the `SummarizeResult` as an `extraction_tier` field.

---

### Requirement 4: AI Summarisation

**User Story:** As a FactGuard user, I want the article to be summarised into a structured format with key points and metadata, so that I can quickly understand the article without reading it in full.

#### Acceptance Criteria

1. WHEN article content is available, THE `Summarizer` SHALL first attempt summarisation using Gemini 2.5 Flash via `gemini.generate_summary`.
2. IF Gemini 2.5 Flash is unavailable or returns an error, THEN THE `Summarizer` SHALL fall back to Groq llama-3.3-70b via `groq_service.generate_summary`.
3. IF both AI providers fail, THEN THE `Summarizer` SHALL produce a heuristic summary by extracting the first 3 sentences of the article body and setting `confidence = "Low"`.
4. THE `Summarizer` SHALL instruct the AI to return a structured JSON object containing: `title` (string), `summary` (string, 2–4 sentences), `key_points` (array of 3–7 strings), `topics` (array of 1–5 topic strings), `sentiment` (`"Positive"` | `"Negative"` | `"Neutral"`), `reading_time_minutes` (integer), and `confidence` (`"High"` | `"Medium"` | `"Low"`).
5. WHEN the AI returns a `reading_time_minutes` value, THE `Summarizer` SHALL validate that it is a positive integer; IF the value is missing or non-positive, THEN THE `Summarizer` SHALL compute it as `max(1, word_count // 200)`.
6. THE `Summarizer` SHALL set `confidence = "High"` when Gemini succeeds, `confidence = "Medium"` when Groq succeeds, and `confidence = "Low"` for the heuristic fallback.

---

### Requirement 5: Result Schema

**User Story:** As a frontend developer, I want a well-defined response schema for summarisation results, so that I can build a consistent result view without guessing field names.

#### Acceptance Criteria

1. THE `SummarizeResult` SHALL extend `BaseModel` and include the following required fields: `jobId` (str), `url` (str), `title` (str), `summary` (str), `key_points` (list[str]), `topics` (list[str]), `sentiment` (Literal["Positive", "Negative", "Neutral"]), `reading_time_minutes` (int), `confidence` (Literal["High", "Medium", "Low"]), `extraction_tier` (str), `createdAt` (str, ISO-8601).
2. THE `SummarizeResult` SHALL include an optional `author` field (str | None) and an optional `published_date` field (str | None) populated from article metadata when available.
3. FOR ALL valid `SummarizeResult` instances `r`, serialising `r` to JSON via `r.model_dump()` and deserialising back via `SummarizeResult.model_validate(r.model_dump())` SHALL produce an object equal to `r` (round-trip property).
4. THE `SummarizeResult` `key_points` field SHALL contain between 1 and 10 items; IF the AI returns fewer than 1 or more than 10 key points, THEN THE `Summarizer` SHALL clamp the list to that range.

---

### Requirement 6: Caching

**User Story:** As a FactGuard operator, I want repeated requests for the same URL to be served from cache, so that Bright Data and AI API costs are minimised.

#### Acceptance Criteria

1. WHEN a summarisation job completes successfully, THE `Summarizer` SHALL store the result in Redis using a cache key derived from the SHA-256 hash of the normalised URL, with a TTL equal to `settings.CACHE_TTL`.
2. WHEN a new summarisation request arrives for a URL whose hash matches an existing Redis cache entry, THE `Summarizer` SHALL return the cached result without calling the Extraction_Pipeline or AI_Chain.
3. IF the Redis cache is unavailable, THEN THE `Summarizer` SHALL skip all cache read and write operations, call the full Extraction_Pipeline and AI_Chain regardless of whether the URL might have been cached, and SHALL NOT raise an exception to the caller.
4. WHILE the Redis cache is unavailable, THE `Summarizer` SHALL log a warning with the message `"Redis unavailable — proceeding without cache"`.

---

### Requirement 7: Frontend — Summarize Mode Entry Point

**User Story:** As a FactGuard user, I want to see a "Summarize" option in the mode switcher, so that I can navigate to the Summarize track from anywhere in the app.

#### Acceptance Criteria

1. THE `ModeSwitcher` component SHALL render a fifth button with `id = "summarize"`, label `"Summarize"`, and a `FileText` icon from Lucide React.
2. WHEN the `"summarize"` mode button is clicked, THE `ModeSwitcher` SHALL call `onChange("summarize")` and the animated `mode-pill` SHALL transition to the new button.
3. THE `AppMode` type in `types/index.ts` SHALL include `"summarize"` as a valid union member.
4. THE `MODE_META` record in `types/index.ts` SHALL include an entry for `"summarize"` with `label = "Summarize"`, `sublabel = "Article Intelligence"`, `color = "#10B981"`, and `icon = "file-text"`.

---

### Requirement 8: Frontend — Summarize Mode Input

**User Story:** As a FactGuard user, I want a URL input panel in Summarize mode with example URLs, so that I can quickly start a summarisation without knowing the exact format.

#### Acceptance Criteria

1. THE `MODE_CONFIG` record in `app/page.tsx` SHALL include a `"summarize"` entry with `heading = "Article Intelligence"`, `subtitle = "SummarizeGuard engine · Bright Data extraction"`, `endpoint = "/summarize"`, `field = "url"`, `maxLength = 2048`, and `buttonLabel = "Summarise Article"`.
2. THE `MODE_CONFIG` `"summarize"` entry SHALL include at least 3 example URLs pointing to publicly accessible news articles.
3. WHEN the user submits a URL in Summarize mode, THE home page SHALL POST `{ "url": "<value>" }` to `/summarize` and redirect to `/loading?job=<jobId>&mode=summarize` on success.
4. THE `VALID_MODES` array in `app/page.tsx` SHALL include `"summarize"` so that `?mode=summarize` in the query string activates Summarize mode.

---

### Requirement 9: Frontend — Summarize Result View

**User Story:** As a FactGuard user, I want to see the article summary, key points, topics, and metadata in a clear result view, so that I can quickly assess the article's content.

#### Acceptance Criteria

1. THE `SummarizeResultView` component SHALL display the article `title`, `summary`, `reading_time_minutes`, `sentiment`, `confidence`, and `createdAt` fields.
2. THE `SummarizeResultView` component SHALL render each item in `key_points` as a distinct list item.
3. THE `SummarizeResultView` component SHALL render each item in `topics` as a pill/badge element.
4. WHEN `author` or `published_date` is present in the result, THE `SummarizeResultView` component SHALL display those fields; WHEN they are absent, THE component SHALL omit those fields without rendering empty placeholders; THE component SHALL include explicit null/undefined checks before rendering each optional field to prevent accidental display of falsy values.
5. THE `SummarizeResultView` component SHALL display the `extraction_tier` value as a data label to indicate which Bright Data product was used.
6. THE result page (`app/result/[jobId]/page.tsx`) SHALL render `SummarizeResultView` WHEN the job result contains `mode = "summarize"`.

---

### Requirement 10: Rate Limiting and API Registration

**User Story:** As a FactGuard operator, I want the Summarize endpoint to be subject to the same rate limiting and API key protection as all other tracks, so that the platform's security posture is consistent.

#### Acceptance Criteria

1. THE `Summary_API` router SHALL be registered in `app/main.py` with `dependencies=[Depends(require_api_key)]`, consistent with all other track routers.
2. WHILE the `RateLimitMiddleware` is active, THE `Summary_API` SHALL be subject to the 30 requests per minute per IP limit applied to all routes; THE `Summary_API` router SHALL be registered after `RateLimitMiddleware` is added to the app so that rate limiting is always enforced regardless of middleware configuration changes.
3. THE `Summary_API` route SHALL be included in the `AuditMiddleware` request log, consistent with all other routes.
