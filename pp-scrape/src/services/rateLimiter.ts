import { RateLimits } from "../types";
import Logger from "../utils/logger";

const SERVICE_NAME = "RateLimiter";

export class RateLimiter {
  private lastRequestTime: number = 0;
  private defaultMeanDelay: number = 2000; // 2 seconds mean delay
  private openAIMeanDelay: number = 5000;  // 5 seconds mean delay for OpenAI
  private requestsRemaining: number = 100;
  private resetTime: number = Date.now();
  private maxRequests: number = 100;
  private timeWindow: number = 60000;
  private requestsPerMin: number = 60;
  private queue: any[] = [];
  private processing: boolean = false;

  private getPoissonDelay(meanDelay: number): number {
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

  public getRateLimits(): RateLimits {
    return {
      requestsRemaining: this.requestsRemaining,
      resetTime: this.resetTime,
      maxRequests: this.maxRequests,
      timeWindow: this.timeWindow,
      requestsPerMin: this.requestsPerMin,
      queue: this.queue,
      processing: this.processing,
      lastRequestTime: this.lastRequestTime
    };
  }

  public async waitForAvailability(isOpenAIRequest: boolean = false): Promise<void> {
    const now = Date.now();
    const meanDelay = isOpenAIRequest ? this.openAIMeanDelay : this.defaultMeanDelay;
    const timeSinceLastRequest = now - this.lastRequestTime;
    
    const poissonDelay = this.getPoissonDelay(meanDelay / 1000);
    
    if (timeSinceLastRequest < poissonDelay) {
      const waitTime = poissonDelay - timeSinceLastRequest;
      Logger.debug(SERVICE_NAME, `Waiting ${waitTime}ms before next request${isOpenAIRequest ? ' (OpenAI)' : ''}`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }

    this.lastRequestTime = Date.now();
  }

  public updateLimits(headers: any): void {
    const remaining = headers?.['x-ratelimit-remaining'];
    const reset = headers?.['x-ratelimit-reset'];

    if (remaining !== undefined && reset !== undefined) {
      Logger.debug(SERVICE_NAME, "Rate limit info", { remaining, reset });
      
      if (remaining < 10) {
        this.defaultMeanDelay *= 2;  // Double the delays
        this.openAIMeanDelay *= 2;
        Logger.warn(SERVICE_NAME, "Rate limit running low, increasing delays", {
          remaining,
          defaultMeanDelay: this.defaultMeanDelay,
          openAIMeanDelay: this.openAIMeanDelay
        });
      }
    }
  }
}

export const rateLimiter = new RateLimiter();
