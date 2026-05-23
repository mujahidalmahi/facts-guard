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