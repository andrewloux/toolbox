export const CACHE_DIR = ".cache";
export const DEFAULT_TOP_N = 5;
export const MAX_CONCURRENT_JOBS = 5;
export const EMBEDDING_MODEL = "text-embedding-3-large";
export const EMBEDDING_DIMENSIONS = 3072;
export const MEAN_REQUEST_INTERVAL = 2000;
export const MIN_SIMILARITY_THRESHOLD = 0.6;
export const DB_PATH = "./jobs.db";

export const JOB_SELECTORS = {
  title: ["h1", ".job-title", '[data-testid="job-title"]'],
  company: [".company-name", '[data-testid="company-name"]', ".employer"],
  location: [".location", '[data-testid="location"]', ".job-location"],
  salary: [".salary-range", '[data-testid="salary-range"]', ".compensation"],
};
