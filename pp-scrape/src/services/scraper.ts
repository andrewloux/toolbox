import { connect } from "puppeteer-real-browser";
import type { Browser, Page } from "rebrowser-puppeteer-core";
import { JobDetails, JobMatch } from "../types";
import { dbService } from "./database";
import { textExtractor } from "./textExtractor";
import Logger from "../utils/logger";
import { jobAnalyzer } from "./jobAnalyzer";
import { rateLimiter } from "./rateLimiter";
import { 
  PageNavigationAction, 
  PageAnalysisResult,
  NavigationResult
} from "./jobAnalyzerModels";

const SERVICE_NAME = "ScraperService";
const PAGE_LOAD_TIMEOUT = 30000;
const NAVIGATION_TIMEOUT = 30000;
const MAX_RETRIES = 3;
const MAX_NAVIGATION_STEPS = 3;

interface SiteConfig {
  headers?: Record<string, string>;
  timeout: number;
  waitTime: number;
  retryDelay: number;
  needsExtraWait: boolean;
}

const DEFAULT_SITE_CONFIG: SiteConfig = {
  timeout: NAVIGATION_TIMEOUT,
  waitTime: 1000,
  retryDelay: 2000,
  needsExtraWait: false
};

const SITE_CONFIGS: Record<string, Partial<SiteConfig>> = {
  // 'openai.com': {
  //   headers: {
  //     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  //     'Accept-Language': 'en-US,en;q=0.5',
  //     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  //   },
  //   timeout: NAVIGATION_TIMEOUT * 2,
  //   waitTime: 2000,
  //   retryDelay: 5000,
  //   needsExtraWait: true
  // },
  // 'linkedin.com': {
  //   waitTime: 2000,
  //   needsExtraWait: true
  // },
  // 'greenhouse.io': {
  //   waitTime: 1500,
  //   needsExtraWait: true
  // }
};

export class ScraperService {
  private browser: Browser | null = null;
  private isHeadless: boolean;

  constructor(isHeadless: boolean = false) {
    this.isHeadless = isHeadless;
  }

  private getSiteConfig(url: string): SiteConfig {
    const domain = new URL(url).hostname.replace('www.', '');
    const siteConfig = SITE_CONFIGS[domain] || {};
    return { ...DEFAULT_SITE_CONFIG, ...siteConfig };
  }

  private async initializePage(url: string): Promise<Page> {
    const page = await this.browser!.newPage();
    const config = this.getSiteConfig(url);
    
    if (config.headers) {
      await page.setExtraHTTPHeaders(config.headers);
    }
    
    await page.setDefaultNavigationTimeout(config.timeout);
    await page.setDefaultTimeout(PAGE_LOAD_TIMEOUT);
    
    return page;
  }



  private async navigateToJobDescription(
    page: Page,
    startUrl: string
  ): Promise<{ url: string; content: JobDetails | null }> {
    let currentUrl = startUrl;
    let navigationStep = 0;
    const config = this.getSiteConfig(startUrl);
    
    while (navigationStep < MAX_NAVIGATION_STEPS) {
      await new Promise(resolve => setTimeout(resolve, config.waitTime));

      // Extract text content instead of raw HTML
      const pageContent = await page.evaluate(() => {
        // Remove script and style elements
        const scripts = document.querySelectorAll('script, style');
        scripts.forEach(s => s.remove());

        // Try to find the main job description container
        const mainContent = document.querySelector('main') || document.body;
        return mainContent.innerText
          .replace(/\s+/g, ' ')
          .replace(/\n\s*\n/g, '\n')
          .trim();
      });

      const currentPageDetails: JobDetails = {
        url: currentUrl,
        description: pageContent,  // Now using clean text instead of HTML
        title: null,
        company: null,
        location: null,
        salary: null
      };

      // Analyze the page content
      const pageAnalysis = await jobAnalyzer.analyzeJobMatch(currentPageDetails);

      // Check if we found a job description
      if (pageAnalysis.analysis.fullAnalysis?.matchScore) {
        return {
          url: currentUrl,
          content: currentPageDetails
        };
      }

      // No more navigation actions available
      if (navigationStep >= MAX_NAVIGATION_STEPS - 1) {
        Logger.warn(SERVICE_NAME, "Max navigation steps reached", { 
          url: currentUrl,
          step: navigationStep
        });
        break;
      }

      navigationStep++;
    }

    return { url: currentUrl, content: null };
  }

  private createJobDetails(url: string, content: PageAnalysisResult): JobDetails {
    return {
      url,
      title: content.title || "Untitled Position",
      description: content.description || "",
      company: content.company,
      location: content.location,
      salary: content.salary
    };
  }

  async screenJobTitles(
    titles: Array<{ title: string; link: string }>, 
    config?: {
      includePatterns?: string[];
      excludePatterns?: string[];
      batchSize?: number;
    }
  ): Promise<Array<{ title: string; link: string }>> {
    const results = [];
    const filteredOut = [];
    const batchSize = config?.batchSize || 10;
    
    // Log all roles at start
    Logger.info(SERVICE_NAME, "Starting job title screening", {
      totalRoles: titles.length,
      allTitles: titles.map(t => t.title),
      config: {
        includePatterns: config?.includePatterns,
        excludePatterns: config?.excludePatterns,
        batchSize
      }
    });

    // Process in batches
    for (let i = 0; i < titles.length; i += batchSize) {
      const batch = titles.slice(i, i + batchSize);
      const batchNumber = Math.floor(i / batchSize) + 1;
      const totalBatches = Math.ceil(titles.length / batchSize);

      Logger.info(SERVICE_NAME, `Processing batch ${batchNumber}/${totalBatches} of titles`);
      
      // Process batch in parallel
      const batchResults = await Promise.all(
        batch.map(async job => {
          const screening = await jobAnalyzer.quickJobScreening(job.title);
          return { job, screening };
        })
      );

      // Process results
      for (const { job, screening } of batchResults) {
        if (screening.shouldProceed) {
          Logger.info(SERVICE_NAME, "✅ Title passed", {
            title: screening.title,
            link: job.link
          });
          results.push(job);
        } else {
          Logger.info(SERVICE_NAME, "❌ Title filtered", {
            title: screening.title,
            link: job.link
          });
          filteredOut.push({
            title: job.title,
            link: job.link
          });
        }
      }

      // Log batch statistics
      Logger.info(SERVICE_NAME, `Batch ${batchNumber} complete`, {
        batchSize: batch.length,
        passed: batchResults.filter(r => r.screening.shouldProceed).length,
        filtered: batchResults.filter(r => !r.screening.shouldProceed).length
      });
    }

    // Log final summary statistics
    Logger.info(SERVICE_NAME, "Job title screening completed", {
      totalRoles: titles.length,
      passed: {
        count: results.length,
        titles: results.map(r => r.title)
      },
      filtered: {
        count: filteredOut.length,
        titles: filteredOut.map(f => f.title)
      }
    });

    return results;
  }

  private async processJobWithRetries(
    link: string,
    resumePath: string
  ): Promise<JobMatch | null> {
    let retries = 0;
    const config = this.getSiteConfig(link);

    while (retries < MAX_RETRIES) {
      try {
        const resumeChecksum = await textExtractor.getResumeChecksum(resumePath);
        const isProcessed = await dbService.isJobProcessed(resumeChecksum, link);
        
        if (isProcessed) {
          Logger.info(SERVICE_NAME, "Job already processed", { link });
          return null;
        }

        await rateLimiter.waitForAvailability(config.needsExtraWait);
        const page = await this.initializePage(link);

        try {
          await page.goto(link, { 
            waitUntil: "networkidle0",
            timeout: config.timeout
          });

          const { url, content } = await this.navigateToJobDescription(page, link);

          if (!content) {
            Logger.warn(SERVICE_NAME, "No job description found after navigation", { 
              finalUrl: url,
              attempts: retries + 1
            });
            return null;
          }

          const result = await jobAnalyzer.analyzeJobMatch(content);
          
          // The analysis is already saved in jobAnalyzer.analyzeJobMatch
          return result;

        } finally {
          await page.close();
        }

      } catch (error) {
        retries++;
        const isLastRetry = retries === MAX_RETRIES;
        
        if (error instanceof DOMException || (error as any)?.name === 'DOMException') {
          Logger.warn(SERVICE_NAME, `DOMException occurred (attempt ${retries}/${MAX_RETRIES})`, { 
            link,
            error: error instanceof Error ? error.message : 'Unknown error'
          });
          
          if (!isLastRetry) {
            await new Promise(resolve => setTimeout(resolve, config.retryDelay));
            continue;
          }
        }
        
        Logger.error(SERVICE_NAME, `Error processing job${isLastRetry ? ' (final attempt)' : ''}`, { 
          link, 
          error: error instanceof Error ? error.message : 'Unknown error',
          attempt: retries
        });
        
        if (isLastRetry) return null;
      }
    }
    
    return null;
  }

  public async initialize(): Promise<void> {
    Logger.info(SERVICE_NAME, `Initializing browser in ${this.isHeadless ? "headless" : "visible"} mode`);

    try {
      const { browser } = await connect({
        headless: this.isHeadless,
        args: ["--no-sandbox", "--disable-setuid-sandbox", "--start-maximized"],
        turnstile: true,
        customConfig: {},
        connectOption: {
          defaultViewport: null,
        },
      });

      this.browser = browser;
      Logger.info(SERVICE_NAME, "Browser initialized successfully");
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      Logger.error(SERVICE_NAME, "Failed to initialize browser", {
        error: errorMsg,
        mode: this.isHeadless ? "headless" : "visible",
      });
      throw error;
    }
  }

  public async analyzeJobs(
    url: string,
    resumePath: string,
    options: {
      topN?: number;
      screeningConfig?: {
        includePatterns?: string[];
        excludePatterns?: string[];
        batchSize?: number;
      };
    } = {}
  ): Promise<JobMatch[]> {
    const { topN = 5, screeningConfig } = options;

    Logger.info(SERVICE_NAME, "Starting job analysis", {
      url,
      resumePath,
      topN,
      screeningConfig
    });

    // Initialize job analyzer with resume
    await jobAnalyzer.initializeWithResume(resumePath);
    const resumeText = await textExtractor.getResumeText(resumePath);

    if (!this.browser) {
      await this.initialize();
    }

    const results: JobMatch[] = [];
    let page: Page | null = null;

    try {
      Logger.info(SERVICE_NAME, `Opening main page: ${url}`);
      page = await this.initializePage(url);

      Logger.debug(SERVICE_NAME, "Navigating to URL...");
      await page.goto(url, {
        waitUntil: "networkidle0",
        timeout: NAVIGATION_TIMEOUT,
      });

      // Get all career links with titles
      const careerLinks = await this.findCareerLinks(page);
      Logger.info(SERVICE_NAME, `Found ${careerLinks.length} career links`);

      // Screen titles first with config
      const filteredJobs = await this.screenJobTitles(careerLinks, screeningConfig);
      Logger.info(SERVICE_NAME, `${filteredJobs.length} jobs passed title screening`);

      // Process only the jobs that passed screening
      results.push(...(await this.processBatch(filteredJobs, resumeText, resumePath)));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      Logger.error(SERVICE_NAME, "Error during job analysis", {
        error: errorMsg,
        url,
        currentUrl: page ? await page.url() : "unknown",
      });
      throw error;
    } finally {
      if (page) await page.close();
      if (this.browser) {
        Logger.info(SERVICE_NAME, "Disconnecting from browser");
        await this.browser.disconnect();
        this.browser = null;
      }
    }

    return this.processResults(results, topN);
  }

  private async findCareerLinks(page: Page): Promise<Array<{ title: string; link: string }>> {
    Logger.debug(SERVICE_NAME, "Searching for career links...");
    
    return await page.evaluate(() => {
      const results = new Set<{ title: string; link: string }>();
      
      // Get all links
      document.querySelectorAll("a").forEach((link) => {
        if (link.href) {
          results.add({
            title: link.textContent?.trim() || "Untitled Position",
            link: link.href
          });
        }
      });

      // Get elements with role="link"
      document.querySelectorAll('[role="link"]').forEach((elem) => {
        const href = elem.getAttribute("href");
        if (href) {
          results.add({
            title: elem.textContent?.trim() || "Untitled Position",
            link: new URL(href, window.location.origin).href
          });
        }
      });

      const careerKeywords = [
        "career", "careers", "jobs", "positions", 
        "opportunities", "openings", "work"
      ];

      return Array.from(results).filter((item) => {
        const url = item.link.toLowerCase();
        return !url.includes("application") && 
               !url.includes("search") && 
               !url.includes("#") &&
               careerKeywords.some(keyword => url.includes(keyword)) &&
               url.startsWith("http");
      });
    });
  }

  private async processBatch(
    jobs: Array<{ title: string; link: string }>,
    resumeText: string,
    resumePath: string
  ): Promise<JobMatch[]> {
    const results: JobMatch[] = [];
    const batchSize = 5; // Process 5 jobs at a time
    const totalBatches = Math.ceil(jobs.length / batchSize);

    for (let i = 0; i < jobs.length; i += batchSize) {
      const batchNumber = Math.floor(i / batchSize) + 1;
      Logger.info(SERVICE_NAME, `Processing batch ${batchNumber}/${totalBatches}`);

      const batch = jobs.slice(i, i + batchSize);
      const batchResults = await Promise.all(
        batch.map(job => this.processJobWithRetries(job.link, resumePath))
      );

      const validResults = batchResults.filter((result): result is JobMatch => result !== null);
      Logger.info(SERVICE_NAME, `Batch ${batchNumber} complete`, {
        processed: batch.length,
        matched: validResults.length,
      });

      results.push(...validResults);
    }

    return results;
  }

  private processResults(results: JobMatch[], topN: number): JobMatch[] {
    const displayResults = topN === -1 ? results : results.slice(0, topN);
    Logger.info(SERVICE_NAME, `Analysis complete. Found ${results.length} matching jobs`, {
      displaying: displayResults.length,
    });
    return displayResults;
  }
}
