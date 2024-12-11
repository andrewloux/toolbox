export interface JobDetails {
  url: string;
  title: string | null;
  company: string | null;
  location: string | null;
  salary: string | null;
  description: string;
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
    requirements?: {
      met: string[];
      missing: string[];
    };
    improvements: string[];
    fullAnalysis: {
      matchScore: {
        overall: number;
        technicalAlignment: number;
        experienceLevel: number;
        domainExpertise: number;
        roleResponsibility: number;
      };
      technicalDepth?: {
        yearsRelevantExperience: number;
        systemScale: {
          usersServed: string;
          dataProcessed: string;
          transactionVolume: string;
        };
        technicalLeadership?: {
          teamSize: number;
          projectScope: string;
          architectureOwnership: boolean;
        };
      };
      skillAnalysis?: {
        criticalMatches: string[];
        missingCritical: string[];
        additionalStrengths: string[];
        growthAreas: string[];
      };
      careerTrajectory?: {
        promotionVelocity: number;
        scopeProgression: string[];
        impactTrend: Array<{
          metric: string;
          value: string;
          timeFrame: string;
        }>;
      };
      applicationStrategy?: {
        keyHighlights: string[];
        differentiators: string[];
        riskMitigations: string[];
        talkingPoints: string[];
      };
    };
  };
}

export interface CompanyInfo {
  name: string;
  website: string | null;
}

export const JOB_STATUSES = [
  "new",
  "applied",
  "rejected",
  "interviewing",
] as const;
export type JobStatus = (typeof JOB_STATUSES)[number];

export interface RateLimits {
  requestsPerMin: number;
  requestsRemaining: number;
  resetTime: number;
  queue: any[];
  processing: boolean;
  lastRequestTime: number;
}
