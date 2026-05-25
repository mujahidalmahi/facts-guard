export type Verdict =
  | 'Verified'
  | 'Likely True'
  | 'Mixed Evidence'
  | 'Likely Misleading'
  | 'Unverified';

export type Confidence =
  | 'High'
  | 'Medium'
  | 'Low';

export interface Source {
  url: string;
  title: string;
  author?: string;
  date?: string;
  stance: 'supports' | 'contradicts' | 'neutral';
  relevance: number;
  summary: string;
  quote?: string;
}

export interface VerifyResult {
  jobId: string;
  claim: string;
  verdict: Verdict;
  confidence: Confidence;
  summary: string;
  supports: number;
  contradicts: number;
  neutral: number;
  sources: Source[];
  createdAt: string;
}

export interface ProductListing {
  title: string;
  price: number | null;
  currency: string;
  merchant: string;
  trustLevel: string;
  url: string;
  image: string | null;
  condition: string | null;
}

export interface ProductVariant {
  model: string;
  specs: string | null;
  priceRange: string;
}

export interface PriceCheckResult {
  status: string;
  jobId: string;
  product: string;
  createdAt: string;
  listings: ProductListing[];
  variants: ProductVariant[];
}

// =========================
// App Modes
// =========================
export type AppMode =
  | 'verify'
  | 'financial'
  | 'cart';

// =========================
// Financial Types
// =========================
export interface GraphDataPoint {
  date: string;
  price: number;
  volume?: number;
}

export interface GraphData {
  label: string;
  unit: string;
  current_price: number;
  change_24h: string;
  change_7d: string;
  all_time_high?: number;
  data: GraphDataPoint[];
}

export interface FinancialAnalysis {
  signal:
    | 'BUY'
    | 'SELL'
    | 'HOLD'
    | 'WATCH';

  signal_strength:
    | 'Strong'
    | 'Moderate'
    | 'Weak';

  price_trend:
    | 'Bullish'
    | 'Bearish'
    | 'Sideways';

  summary: string;
  key_factors: string[];

  risk_level:
    | 'Low'
    | 'Medium'
    | 'High';

  prediction_30d: string;
  confidence: string;
}

export interface FinancialSource {
  title: string;
  url: string;
  domain?: string;

  credibility:
    | 'High'
    | 'Medium'
    | 'Low';

  stance:
    | 'Bullish'
    | 'Bearish'
    | 'Neutral';

  summary: string;
  date?: string;
}

export interface FinancialResult {
  jobId: string;
  mode: 'financial';
  query: string;

  graph_data: GraphData;
  analysis: FinancialAnalysis;
  sources: FinancialSource[];
}

// =========================
// Cart Types
// =========================
export interface CartListing {
  platform: string;
  title: string;
  url: string;
  snippet: string;

  trust_signal:
    | 'green'
    | 'yellow'
    | 'red';
}

export interface CartAnalysis {
  best_deal: {
    platform: string;
    price: string;
    why: string;
  };

  verdict: string;

  price_range: {
    low: string;
    high: string;
  };

  recommendation: string;
  warnings: string[];
  market_average: string;
}

export interface CartResult {
  jobId: string;
  mode: 'cart';
  product: string;

  listings: CartListing[];
  analysis: CartAnalysis;
}