"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.JOB_SELECTORS = exports.DB_PATH = exports.MIN_SIMILARITY_THRESHOLD = exports.MEAN_REQUEST_INTERVAL = exports.EMBEDDING_DIMENSIONS = exports.EMBEDDING_MODEL = exports.MAX_CONCURRENT_JOBS = exports.DEFAULT_TOP_N = exports.CACHE_DIR = void 0;
exports.CACHE_DIR = ".cache";
exports.DEFAULT_TOP_N = 5;
exports.MAX_CONCURRENT_JOBS = 5;
exports.EMBEDDING_MODEL = "text-embedding-3-large";
exports.EMBEDDING_DIMENSIONS = 3072;
exports.MEAN_REQUEST_INTERVAL = 2000;
exports.MIN_SIMILARITY_THRESHOLD = 0.6;
exports.DB_PATH = "./jobs.db";
exports.JOB_SELECTORS = {
    title: ["h1", ".job-title", '[data-testid="job-title"]'],
    company: [".company-name", '[data-testid="company-name"]', ".employer"],
    location: [".location", '[data-testid="location"]', ".job-location"],
    salary: [".salary-range", '[data-testid="salary-range"]', ".compensation"],
};
