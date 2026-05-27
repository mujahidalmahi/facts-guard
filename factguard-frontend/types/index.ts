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

export type BiasSignal =
  | 'cherry_picking'
  | 'false_equivalence'
  | 'appeal_to_authority'
  | 'omission'
  | 'misleading_statistics'
  | 'emotional_language'
  | 'unverified_anecdote';

export type SourceDiversity =
  | 'High'
  | 'Medium'
  | 'Low';

export interface Source {
  url: string;
  title: string;
  author?: string;
  date?: string;
  stance: 'supports' | 'contradicts' | 'neutral';
  credibility: 'High' | 'Medium' | 'Low';
  tier: 1 | 2 | 3 | 4;
  relevance: number;
  summary: string;
  quote?: string;
  _hallucinated?: boolean;
}

export interface VerifyResult {
  jobId: string;
  claim: string;
  verdict: Verdict;
  confidence: Confidence;
  summary: string;
  narrative_frame?: string;
  supports: number;
  contradicts: number;
  neutral: number;
  bias_signals: BiasSignal[];
  source_diversity: SourceDiversity;
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
  | 'cart'
  | 'security';

export type TrackType =
  | 'gtm'
  | 'finance'
  | 'security'
  | 'cart';

export type ThreatType =
  | 'brand'
  | 'regulatory'
  | 'vendor'
  | 'disinformation'
  | 'general';

export type Severity =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical';

export type AlertStatus =
  | 'new'
  | 'acknowledged'
  | 'investigating'
  | 'resolved'
  | 'dismissed';

export interface ThreatResult {
  jobId: string;
  threat_type: ThreatType;
  severity: Severity;
  title: string;
  description: string;
  source_url: string;
  source_domain: string;
  confidence: number;
  alert_status: AlertStatus;
  detected_at: string;
}

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

export interface Prediction30d {
  bull_case: string;
  base_case: string;
  bear_case: string;
}

export interface FinancialAnalysis {
  signal:
    | 'Bullish'
    | 'Bearish'
    | 'Neutral';

  signal_strength: number;

  asset: string;
  current_price: string;

  price_trend:
    | 'Up'
    | 'Down'
    | 'Sideways';

  trend_magnitude:
    | 'Strong'
    | 'Moderate'
    | 'Weak';

  risk_level:
    | 'Low'
    | 'Medium'
    | 'High';

  risk_catalysts: string[];
  key_factors: string[];
  summary: string;
  prediction_30d: Prediction30d;
  data_freshness: 'real-time' | 'intraday' | 'daily' | 'stale';
}

export interface FinancialSource {
  title: string;
  url: string;
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
export interface CartListingEntry {
  title: string;
  merchant: string;
  price: number;
  currency: string;
  url: string;
  trust_level: 'GREEN' | 'YELLOW' | 'RED';
  deal_score: number;
  trust_reason: string;
  counterfeit_risk: 'High' | 'Medium' | 'Low' | 'None';
  condition: 'New' | 'Refurbished' | 'Used' | 'Unknown';
  in_stock: boolean;
  image?: string | null;
  rating?: string | null;
}

export interface CartAnalysis {
  product_name: string;
  msrp: string | null;
  fair_market_range: { min: string; max: string; currency: string };
  best_deal: {
    merchant: string;
    price: string;
    url: string;
    reason: string;
  };
  listings: CartListingEntry[];
  analysis: {
    warnings: string[];
    recommendation: string;
    price_trend: 'Rising' | 'Stable' | 'Dropping';
    best_time_to_buy: 'Now' | 'Wait' | 'Urgent';
  };
}

export interface CartResult {
  jobId: string;
  mode: 'cart';
  product: string;
  listings: CartListingEntry[];
  analysis: CartAnalysis;
}

// =========================
// History Types
// =========================
export interface HistoryItem {
  jobId: string;
  mode: AppMode;
  query: string;
  verdict?: string;
  signal?: string;
  severity?: Severity;
  createdAt: string;
  display_text?: string;
  claim?: string;
  status?: string;
}

export interface ModeMeta {
  label: string;
  sublabel: string;
  color: string;
  icon: string;
}

export const MODE_META: Record<AppMode, ModeMeta> = {
  verify: { label: 'Verify', sublabel: 'Fact Intelligence', color: '#4F46E5', icon: 'shield' },
  financial: { label: 'Financial', sublabel: 'Market Signals', color: '#7C3AED', icon: 'trending' },
  security: { label: 'Security', sublabel: 'Threat Surface', color: '#F59E0B', icon: 'alert' },
  cart: { label: 'Cart', sublabel: 'Price Trust', color: '#06B6D4', icon: 'cart' },
};
