"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.rateLimiter = exports.RateLimiter = void 0;
const logger_1 = __importDefault(require("../utils/logger"));
const SERVICE_NAME = "RateLimiter";
class RateLimiter {
    constructor() {
        this.lastRequestTime = 0;
        this.defaultMeanDelay = 2000; // 2 seconds mean delay
        this.openAIMeanDelay = 5000; // 5 seconds mean delay for OpenAI
        this.requestsRemaining = 100;
        this.resetTime = Date.now();
        this.maxRequests = 100;
        this.timeWindow = 60000;
        this.requestsPerMin = 60;
        this.queue = [];
        this.processing = false;
    }
    getPoissonDelay(meanDelay) {
        // Generate Poisson distributed random number
        const L = Math.exp(-meanDelay);
        let k = 0;
        let p = 1;
        do {
            k++;
            p *= Math.random();
        } while (p > L);
        return Math.max(500, (k - 1) * 1000); // Ensure minimum 500ms delay
    }
    getRateLimits() {
        return {
            requestsRemaining: this.requestsRemaining,
            resetTime: this.resetTime,
            maxRequests: this.maxRequests,
            timeWindow: this.timeWindow,
            requestsPerMin: this.requestsPerMin,
            queue: this.queue,
            processing: this.processing,
            lastRequestTime: this.lastRequestTime,
        };
    }
    async waitForAvailability(isOpenAIRequest = false) {
        const now = Date.now();
        const meanDelay = isOpenAIRequest
            ? this.openAIMeanDelay
            : this.defaultMeanDelay;
        const timeSinceLastRequest = now - this.lastRequestTime;
        const poissonDelay = this.getPoissonDelay(meanDelay / 1000);
        if (timeSinceLastRequest < poissonDelay) {
            const waitTime = poissonDelay - timeSinceLastRequest;
            logger_1.default.debug(SERVICE_NAME, `Waiting ${waitTime}ms before next request${isOpenAIRequest ? " (OpenAI)" : ""}`);
            await new Promise((resolve) => setTimeout(resolve, waitTime));
        }
        this.lastRequestTime = Date.now();
    }
    updateLimits(headers) {
        const remaining = headers?.["x-ratelimit-remaining"];
        const reset = headers?.["x-ratelimit-reset"];
        if (remaining !== undefined && reset !== undefined) {
            logger_1.default.debug(SERVICE_NAME, "Rate limit info", { remaining, reset });
            if (remaining < 10) {
                this.defaultMeanDelay *= 2; // Double the delays
                this.openAIMeanDelay *= 2;
                logger_1.default.warn(SERVICE_NAME, "Rate limit running low, increasing delays", {
                    remaining,
                    defaultMeanDelay: this.defaultMeanDelay,
                    openAIMeanDelay: this.openAIMeanDelay,
                });
            }
        }
    }
}
exports.RateLimiter = RateLimiter;
exports.rateLimiter = new RateLimiter();
