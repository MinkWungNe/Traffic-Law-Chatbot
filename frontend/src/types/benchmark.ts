export interface BenchmarkMetadata {
  framework?: string;
  dataset_file?: string;
  total_questions: number;
  evaluated_samples: number;
  top_k: number;
  evaluation_time_seconds: number;
  timestamp: string;
}

export interface BenchmarkSummaryMetrics {
  hit_rate: number;
  hit_rate_percentage: string;
  recall_at_k: number;
  recall_percentage: string;
  mrr: number;
  avg_latency_per_query_ms: number;
}

export interface QualityMetrics {
  faithfulness_score: number;
  faithfulness_percentage?: string;
  answer_relevance_score: number;
  answer_relevance_percentage?: string;
  ragas_harmonic_mean?: number;
}

export interface BenchmarkQueryItem {
  id: number;
  question: string;
  ground_truth_answer?: string;
  ground_truth_citations: string[];
  retrieved_sources?: string[];
  retrieved_docs?: Array<{
    document?: string;
    source?: string;
    score?: number;
    metadata?: Record<string, any>;
  }>;
  hit: number;
  recall: number;
  first_rank: number;
  rank?: number;
  reciprocal_rank?: number;
  is_passed?: boolean;
  status?: string;
  faithfulness?: number;
  answer_relevance?: number;
  matched_citations?: string[];
}

export interface BenchmarkReportResponse {
  metadata: BenchmarkMetadata;
  summary_metrics: BenchmarkSummaryMetrics;
  quality_metrics?: QualityMetrics;
  detailed_results: BenchmarkQueryItem[];
  samples?: BenchmarkQueryItem[];
}

export interface BenchmarkSummaryResponse {
  metadata: BenchmarkMetadata;
  summary_metrics: BenchmarkSummaryMetrics;
  quality_metrics?: QualityMetrics;
}

export interface BenchmarkSamplesResponse {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  items: BenchmarkQueryItem[];
}
