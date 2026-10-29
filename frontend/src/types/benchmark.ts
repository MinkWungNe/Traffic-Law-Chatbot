export interface BenchmarkMetadata {
  framework?: string;
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

export interface BenchmarkQueryItem {
  id: number;
  question: string;
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
  reciprocal_rank?: number;
  is_passed?: boolean;
  status?: string;
}

export interface BenchmarkReportResponse {
  metadata: BenchmarkMetadata;
  summary_metrics: BenchmarkSummaryMetrics;
  detailed_results: BenchmarkQueryItem[];
}
