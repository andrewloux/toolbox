"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DefaultOpenAIProvider = void 0;
const logger_1 = __importDefault(require("../../utils/logger"));
const SERVICE_NAME = "OpenAIProvider";
const jobAnalysisTools = [
    {
        type: "function",
        function: {
            name: "analyze_job_fit",
            description: "Analyze job description and resume compatibility",
            parameters: {
                type: "object",
                properties: {
                    score: {
                        type: "number",
                        description: "Match score between 0 and 1",
                        minimum: 0,
                        maximum: 1,
                    },
                    reasoning: {
                        type: "array",
                        items: { type: "string" },
                        description: "List of reasons for the match score",
                    },
                    requirements: {
                        type: "object",
                        properties: {
                            met: {
                                type: "array",
                                items: { type: "string" },
                                description: "List of requirements met by the candidate",
                            },
                            missing: {
                                type: "array",
                                items: { type: "string" },
                                description: "List of requirements not met by the candidate",
                            },
                        },
                        required: ["met", "missing"],
                    },
                },
                required: ["score", "reasoning", "requirements"],
            },
        },
    },
];
class DefaultOpenAIProvider {
    constructor(apiKey, rateLimiter) {
        this.apiKey = apiKey;
        this.rateLimiter = rateLimiter;
    }
    async analyze(jobDescription, resumeText) {
        try {
            await this.rateLimiter.waitForAvailability();
            const response = await fetch("https://api.openai.com/v1/chat/completions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${this.apiKey}`,
                },
                body: JSON.stringify({
                    model: "gpt-4",
                    messages: [
                        {
                            role: "system",
                            content: "You are an expert at analyzing job descriptions and resumes for compatibility.",
                        },
                        {
                            role: "user",
                            content: `Analyze this job-resume pair:

Job Description:
${jobDescription}

Resume:
${resumeText}

Consider:
1. Skills match
2. Experience level
3. Domain expertise
4. Technical requirements
5. Cultural fit indicators`,
                        },
                    ],
                    tools: [...jobAnalysisTools],
                    tool_choice: {
                        type: "function",
                        function: { name: "analyze_job_fit" },
                    },
                    temperature: 0.3,
                }),
            });
            const headers = {};
            response.headers.forEach((value, key) => {
                headers[key] = value;
            });
            this.rateLimiter.updateLimits(headers);
            const result = await response.json();
            const toolCall = result.choices[0]?.message?.tool_calls?.[0];
            if (toolCall?.function) {
                try {
                    const analysis = JSON.parse(toolCall.function.arguments);
                    return {
                        score: analysis.score,
                        reasoning: analysis.reasoning,
                        requirements: analysis.requirements,
                    };
                }
                catch (error) {
                    logger_1.default.error(SERVICE_NAME, "Failed to parse analysis result", {
                        error,
                    });
                    throw error;
                }
            }
            else {
                logger_1.default.error(SERVICE_NAME, "No tool call found in response");
                throw new Error("Invalid response format from OpenAI");
            }
        }
        catch (error) {
            logger_1.default.error(SERVICE_NAME, "Error analyzing with OpenAI", { error });
            throw error;
        }
    }
    getRateLimits() {
        return this.rateLimiter.getRateLimits();
    }
}
exports.DefaultOpenAIProvider = DefaultOpenAIProvider;
