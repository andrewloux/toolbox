import { JobDetails, JobMatch } from "../types";
import {
  JobMatchAnalysis,
  jobMatchTools,
  PageNavigationAction,
  PageAnalysisResult,
  PageAnalysisParams,
  pageAnalysisTools,
} from "./jobAnalyzerModels";
import { textExtractor } from "./textExtractor";
import OpenAI from "openai";
import Logger from "../utils/logger";
import { dbService } from "./database";

const SERVICE_NAME = "JobAnalyzerService";
const GPT_MODEL = "gpt-4o" as const;

interface QuickScreenResult {
  shouldProceed: boolean;
  title: string;
  reason?: string;
}

interface TitleScreeningConfig {
  includePatterns?: string[];
  excludePatterns?: string[];
  batchSize?: number;
}

export class JobAnalyzer {
  private openai: OpenAI;
  private resumeContext: string | null = null;

  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  async initializeWithResume(resumePath: string) {
    this.resumeContext = await textExtractor.getResumeText(resumePath);
  }

  async analyzeJobPage(page: any): Promise<{
    content: PageAnalysisResult;
    nextAction?: PageNavigationAction;
  }> {
    const pageContent = await page.content();

    const response = await this.openai.chat.completions.create({
      model: GPT_MODEL,
      messages: [
        {
          role: "system",
          content: "You are an expert at analyzing job posting pages.",
        },
        {
          role: "user",
          content: `Analyze this job page content:\n${pageContent}`,
        },
      ],
      tools: [...pageAnalysisTools],
      tool_choice: { type: "function", function: { name: "analyze_job_page" } },
      temperature: 0.1,
    });

    const toolCall = response.choices[0].message?.tool_calls?.[0];
    if (!toolCall?.function) {
      throw new Error("No analysis result from OpenAI");
    }

    const analysis = JSON.parse(
      toolCall.function.arguments,
    ) as PageAnalysisParams;

    return {
      content: {
        hasJobDescription: analysis.isJobDescription,
        title: analysis.content.title,
        description: analysis.content.description,
        company: analysis.content.company,
        location: analysis.content.location,
        salary: analysis.content.salary,
      },
      nextAction: analysis.nextAction || undefined,
    };
  }

  async analyzeJobMatch(jobDetails: JobDetails): Promise<JobMatch> {
    if (!this.resumeContext) {
      throw new Error(
        "Resume context not initialized. Call initializeWithResume first.",
      );
    }

    Logger.debug(SERVICE_NAME, "Analyzing job match", {
      jobTitle: jobDetails.title,
      descriptionLength: jobDetails.description?.length ?? 0,
      resumeLength: this.resumeContext.length,
      descriptionPreview: jobDetails.description
        ? jobDetails.description.slice(0, 200) + "..."
        : "No description available",
      resumePreview: this.resumeContext.slice(0, 200) + "...",
    });

    const response = await this.openai.chat.completions.create({
      model: GPT_MODEL,
      messages: [
        {
          role: "system",
          content: `You are a legendary technical recruiter with an extraordinary ability to identify perfect role-candidate matches. With 20+ years of experience placing engineers at top tech companies, you've developed an uncanny intuition for technical talent assessment, for reading the subtle nuances of the job description, the story between the lines of a resume, and a gift for finding the right place for the right people.`,
        },
        {
          role: "user",
          content: `Analyze this job-resume pair:

Job Description:
${jobDetails.description}

Resume:
${this.resumeContext}

Technical Alignment:
  1. Core technical requirements vs. candidate's proven skills
  2. Architecture and system scale experience
  3. Technical stack depth and breadth
  4. Relevant technical accomplishments and their impact

Experience Calibration:
  5. Years of relevant experience
  6. Leadership/ownership scope
  7. Project complexity and scale handled
  8. Industry-specific knowledge depth

Role Fit Indicators:
  9. Primary role responsibilities vs. demonstrated experience
  10. Team size and structure alignment
  11. Development methodology familiarity 
  12. Cross-functional collaboration history

Growth & Potential:
  13. Career progression trajectory
  14. Learning agility signals
  15. Adjacent skill adaptability
  16. Technical breadth vs. depth balance

Red Flags & Differentiators:
  17. Critical missing requirements
  18. Unique technical strengths
  19. Pattern of innovation/improvement
  20. Potential culture fit signals`,
        },
      ],
      tools: [...jobMatchTools] as const,
      tool_choice: {
        type: "function",
        function: { name: "analyze_job_match" },
      },
      temperature: 0.3,
    });

    Logger.debug(SERVICE_NAME, "Raw OpenAI Response", {
      responseChoices: response.choices,
      firstChoice: response.choices[0],
      messageContent: response.choices[0].message,
      toolCalls: response.choices[0].message?.tool_calls,
    });

    const toolCall = response.choices[0].message?.tool_calls?.[0];

    if (!toolCall?.function) {
      Logger.error(SERVICE_NAME, "No tool call found in response", {
        response: JSON.stringify(response),
      });
      throw new Error("No tool call found in response");
    }

    Logger.debug(SERVICE_NAME, "Tool Call Arguments", {
      functionName: toolCall.function.name,
      rawArguments: toolCall.function.arguments,
      parsedArguments: JSON.parse(toolCall.function.arguments),
    });

    let analysis: JobMatchAnalysis;
    try {
      const parsedResponse = JSON.parse(toolCall.function.arguments);

      // Validate the response has the expected structure
      if (
        !parsedResponse?.matchScore ||
        typeof parsedResponse.matchScore !== "object"
      ) {
        throw new Error("Invalid analysis result: missing match score object");
      }

      // Calculate overall score based on other dimensions
      let overallScore: number;
      try {
        const dimensions = [
          "technicalAlignment",
          "experienceLevel",
          "domainExpertise",
          "roleResponsibility",
        ];
        const scores = dimensions
          .map((d) => parsedResponse.matchScore[d])
          .filter((score): score is number => typeof score === "number");

        overallScore = calculateOverallScore(scores);

        if (isNaN(overallScore)) {
          throw new Error("Overall score calculation resulted in NaN");
        }

        // Set the overall score in the matchScore object
        parsedResponse.matchScore.overall = overallScore;
      } catch (error) {
        Logger.error(SERVICE_NAME, "Failed to calculate overall score", {
          matchScore: parsedResponse.matchScore,
          error: error instanceof Error ? error.message : "Unknown error",
        });
        throw error;
      }

      // Remove the type field assignment
      analysis = parsedResponse as JobMatchAnalysis;

      console.log("overall score", overallScore);

      // Save the complete analysis to the database
      try {
        await dbService.saveJobAnalysis({
          url: jobDetails.url || "",
          title: jobDetails.title || "Untitled Position",
          company: jobDetails.company,
          location: jobDetails.location,
          salary: jobDetails.salary,
          similarityScore: overallScore,
          sectionScores: JSON.stringify(analysis.matchScore),
          analysisJson: JSON.stringify(analysis),
          status: "analyzed",
        });
      } catch (error) {
        Logger.error(SERVICE_NAME, "Failed to save job analysis", {
          url: jobDetails.url,
          error: error instanceof Error ? error.message : "Unknown error",
          analysis: JSON.stringify(analysis),
        });
        throw error;
      }

      return {
        url: jobDetails.url || "",
        similarity: overallScore,
        title: jobDetails.title || "Untitled Position",
        company: jobDetails.company ?? null,
        location: jobDetails.location ?? null,
        salary: jobDetails.salary ?? null,
        analysis: {
          reasoning:
            analysis.detailedAnalysis?.applicationStrategy?.differentiators ??
            [],
          requirements: {
            met:
              analysis.detailedAnalysis?.skillAnalysis?.criticalMatches ?? [],
            missing:
              analysis.detailedAnalysis?.skillAnalysis?.missingCritical ?? [],
          },
          improvements: [],
          fullAnalysis: analysis,
        },
      };
    } catch (error) {
      Logger.error(SERVICE_NAME, "Failed to parse analysis result", {
        error: error instanceof Error ? error.message : "Unknown error",
        arguments: toolCall.function.arguments,
      });
      throw error;
    }
  }

  async quickJobScreening(jobTitle: string): Promise<QuickScreenResult> {
    if (!this.resumeContext) {
      throw new Error(
        "Resume context not initialized. Call initializeWithResume first.",
      );
    }

    const response = await this.openai.chat.completions.create({
      model: GPT_MODEL,
      messages: [
        {
          role: "system",
          content: `You are a technical job title screener focused on individual contributor roles requiring strong technical or quantitative skills. Look for roles that involve programming, data analysis, mathematical modeling, or complex technical systems.

Your task is to analyze job titles and determine if they are likely to be a good fit for the candidate based on their resume. You should err on the side of including titles, as the full job description will be analyzed later.

**Specifically, you should filter out:**

1. **Pure Management Roles:** Titles that clearly indicate a purely management or leadership position (e.g., "Manager", "Director", "Head of").
2. **Non-Technical Roles:** Titles that are clearly not technical in nature (e.g., "Sales", "Marketing", "HR", "Operations").
3. **Support or Administrative Roles:** Titles that suggest a support or administrative function rather than a core technical role (e.g., "Coordinator", "Assistant", "Specialist" - unless combined with a technical term like "Data Specialist").
4. **Non-Software Engineering Roles:** Titles that are in engineering fields outside of software (e.g., "Mechanical Engineer", "Civil Engineer", "Chemical Engineer").
5. **Frontend Developer Roles:** Titles that explicitly mention "Frontend Developer" or "Frontend Engineer."

**You should focus on roles that involve:**

1. **Software Development:** Titles like "Software Engineer", "Developer", "Programmer", and variations that include specific technologies or areas (e.g., "Backend Developer", "Full Stack Engineer", "Python Developer"). Also include technical leadership roles that still involve significant coding (e.g., "Technical Lead", "Staff Engineer").
2. **Data Science and Analysis:** Titles like "Data Scientist", "Data Analyst", "Machine Learning Engineer", "Quantitative Analyst".
3. **Research and Development:** Titles that involve research, especially in technical or scientific fields (e.g., "Research Scientist", "Research Engineer").
4. **Systems and Infrastructure:** Titles related to systems, infrastructure, and DevOps (e.g., "Systems Engineer", "DevOps Engineer", "Cloud Engineer").

**Examples of titles to INCLUDE:**

*   Software Engineer
*   Senior Software Engineer
*   Technical Lead Manager
*   Data Scientist
*   Machine Learning Engineer
*   Research Scientist (AI/ML)
*   Quantitative Analyst
*   Backend Developer (Python)
*   Full Stack Engineer (Node.js/React)
*   Systems Engineer
*   DevOps Engineer

**Examples of titles to EXCLUDE:**

*   Engineering Manager
*   Product Manager
*   Project Manager
*   Business Analyst
*   Marketing Specialist
*   HR Coordinator
*   Mechanical Engineer
*   Civil Engineer
*   Account Director
*   Frontend Developer
*   Frontend Engineer

**Remember**: This is a quick initial screening based on the job title only. The full job description will be analyzed later to determine the actual fit. When in doubt, it's better to include a title than to exclude it.`,
        },
        {
          role: "user",
          content: `Job Title: ${jobTitle}

Resume Summary:
${this.resumeContext.slice(0, 500) + "..."}`,
        },
      ],
      functions: [
        {
          name: "screen_job_title",
          description:
            "Quickly assess if we should look into this job based on title",
          parameters: {
            type: "object",
            properties: {
              shouldProceed: {
                type: "boolean",
                description:
                  "Whether we should click through to read more about this job",
              },
              reason: {
                type: "string",
                description:
                  "If shouldProceed is false, provide a brief reason why the title was filtered out.",
              },
            },
            required: ["shouldProceed"],
          },
        },
      ],
      function_call: { name: "screen_job_title" },
      temperature: 0.5,
    });

    console.log("Raw OpenAI response for quickJobScreening:", response);

    const result = JSON.parse(
      response.choices[0].message?.function_call?.arguments ||
        '{"shouldProceed":true}',
    );

    return {
      shouldProceed: result.shouldProceed,
      title: jobTitle,
      reason: result.reason,
    };
  }

  async suggestSelectors(
    pageContent: string,
  ): Promise<{ jobTitleSelector: string; jobLinkSelector: string }> {
    const response = await this.openai.chat.completions.create({
      model: GPT_MODEL,
      messages: [
        {
          role: "system",
          content: `You are an expert web scraper. Your task is to analyze the HTML content of a web page and suggest the most accurate CSS selectors for identifying job titles and job links.

Consider the following:

- **Job Title Selectors:** Selectors that uniquely identify elements containing job titles. Prefer selectors that are specific and unlikely to match non-job title elements.
- **Job Link Selectors:** Selectors that uniquely identify elements containing links to job descriptions. Prefer selectors that target \`<a>\` tags with \`href\` attributes.

Provide the selectors in a JSON format as follows:

\`\`\`json
{
  "jobTitleSelector": "your_job_title_selector",
  "jobLinkSelector": "your_job_link_selector"
}
\`\`\``,
        },
        {
          role: "user",
          content: `Here is the HTML content of the page:\n\n${pageContent}`,
        },
      ],
      functions: [
        {
          name: "return_selectors",
          description:
            "Returns the suggested CSS selectors for job titles and job links.",
          parameters: {
            type: "object",
            properties: {
              jobTitleSelector: {
                type: "string",
                description: "CSS selector for job titles",
              },
              jobLinkSelector: {
                type: "string",
                description: "CSS selector for job links",
              },
            },
            required: ["jobTitleSelector", "jobLinkSelector"],
          },
        },
      ],
      function_call: { name: "return_selectors" },
      temperature: 0.1,
    });

    const result = JSON.parse(
      response.choices[0].message?.function_call?.arguments || "{}",
    );
    return {
      jobTitleSelector: result.jobTitleSelector,
      jobLinkSelector: result.jobLinkSelector,
    };
  }
}

function calculateOverallScore(scores: number[]): number {
  if (scores.length === 0) {
    throw new Error("No valid dimension scores found");
  }

  // Calculate mean
  const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;

  // Calculate standard deviation
  const squareDiffs = scores.map((score) => Math.pow(score - mean, 2));
  const avgSquareDiff =
    squareDiffs.reduce((sum, diff) => sum + diff, 0) / scores.length;
  const standardDev = Math.sqrt(avgSquareDiff);

  // Calculate overall: 0.7 * mean + 0.3 * (1 - SD/0.5)
  const overall = 0.7 * mean + 0.3 * (1 - standardDev / 0.5);

  // Clamp between 0 and 1
  return Math.max(0, Math.min(1, overall));
}

export const jobAnalyzer = new JobAnalyzer();
