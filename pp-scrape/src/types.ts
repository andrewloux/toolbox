export interface JobDetails {
    url: string;
    description: string;
    title: string | null;
    company: string | null;
    location: string | null;
    salary: string | null;
}

export interface JobMatch {
    url: string;
    similarity: number;
    title: string;
    company: string | null;
    location: string | null;
    salary: string | null;
    analysis: {
        reasoning: string[];
        requirements: {
            met: string[];
            missing: string[];
        };
        improvements: string[];
        fullAnalysis: any; // Full analysis object from OpenAI
    };
}

export interface CompanyInfo {
    name: string;
    website: string;
}

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export const JOB_STATUSES: JobStatus[] = [
    'pending',
    'processing',
    'completed',
    'failed'
];

export interface RateLimits {
    maxRequests: number;
    timeWindow: number;
    requestsPerMin: number;
    requestsRemaining: number;
    resetTime: number;
    queue: any[];
    processing: boolean;
    lastRequestTime: number;
}
