"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.jobPreviewTools = exports.pageAnalysisTools = exports.jobMatchTools = void 0;
const jobMatchSchema = {
    type: "object",
    properties: {
        matchScore: {
            type: "object",
            properties: {
                technicalAlignment: { type: "number", minimum: 0, maximum: 1 },
                experienceLevel: { type: "number", minimum: 0, maximum: 1 },
                domainExpertise: { type: "number", minimum: 0, maximum: 1 },
                roleResponsibility: { type: "number", minimum: 0, maximum: 1 },
            },
            required: [
                "technicalAlignment",
                "experienceLevel",
                "domainExpertise",
                "roleResponsibility",
            ],
            additionalProperties: false,
        },
        detailedAnalysis: {
            type: "object",
            properties: {
                technicalDepth: {
                    type: "object",
                    properties: {
                        yearsRelevantExperience: { type: "number" },
                        systemScale: {
                            type: "object",
                            properties: {
                                usersServed: { type: "string" },
                                dataProcessed: { type: "string" },
                                transactionVolume: { type: "string" },
                            },
                        },
                        technicalLeadership: {
                            type: "object",
                            properties: {
                                teamSize: { type: "number" },
                                projectScope: { type: "string" },
                                architectureOwnership: { type: "boolean" },
                            },
                        },
                    },
                },
                skillAnalysis: {
                    type: "object",
                    properties: {
                        criticalMatches: { type: "array", items: { type: "string" } },
                        missingCritical: { type: "array", items: { type: "string" } },
                        additionalStrengths: { type: "array", items: { type: "string" } },
                        growthAreas: { type: "array", items: { type: "string" } },
                    },
                },
                careerTrajectory: {
                    type: "object",
                    properties: {
                        promotionVelocity: { type: "number" },
                        scopeProgression: { type: "array", items: { type: "string" } },
                        impactTrend: {
                            type: "array",
                            items: {
                                type: "object",
                                properties: {
                                    metric: { type: "string" },
                                    value: { type: "string" },
                                    timeFrame: { type: "string" },
                                },
                            },
                        },
                    },
                },
                applicationStrategy: {
                    type: "object",
                    properties: {
                        keyHighlights: { type: "array", items: { type: "string" } },
                        differentiators: { type: "array", items: { type: "string" } },
                        riskMitigations: { type: "array", items: { type: "string" } },
                        talkingPoints: { type: "array", items: { type: "string" } },
                    },
                },
            },
            required: ["technicalDepth", "skillAnalysis", "applicationStrategy"],
        },
    },
    required: ["matchScore", "detailedAnalysis"],
    additionalProperties: false,
};
const pageAnalysisSchema = {
    type: "object",
    properties: {
        isJobDescription: { type: "boolean" },
        content: {
            type: "object",
            properties: {
                title: { type: "string", nullable: true },
                description: { type: "string", nullable: true },
                company: { type: "string", nullable: true },
                location: { type: "string", nullable: true },
                salary: { type: "string", nullable: true },
            },
            required: ["title", "description", "company", "location", "salary"],
        },
        nextAction: {
            type: "object",
            nullable: true,
            properties: {
                type: { type: "string", enum: ["click", "href"] },
                target: { type: "string" },
                reason: { type: "string" },
            },
            required: ["type", "target", "reason"],
        },
    },
    required: ["isJobDescription", "content"],
};
const jobPreviewSchema = {
    type: "object",
    properties: {
        scores: {
            type: "array",
            items: { type: "number", minimum: 0, maximum: 1 },
        },
        explanations: {
            type: "array",
            items: { type: "string" },
        },
    },
    required: ["scores", "explanations"],
};
// Tool Definitions
exports.jobMatchTools = [
    {
        type: "function",
        function: {
            name: "analyze_job_match",
            description: `
1.0: Perfect - Exceeds, mastery
0.8-0.9: Strong - Meets all core needs, minor gaps
0.6-0.7: Good - Meets most needs, clear growth potential
0.4-0.5: Partial - Some needs met, major gaps
0.2-0.3: Weak - Few needs met, major gaps
0.0-0.1: Unfit

Apply this scale:
• technicalAlignment: Assess technical expertise depth/breadth, hands-on production experience, system complexity, decision-making, and tradeoff navigation. Include adjacent tech experience showing quick learning.
• experienceLevel: Focus on impact, scope, progression, systems owned, problems solved, and technical growth velocity. Prioritize readiness for complex challenges.
• domainExpertise: Examine domain challenges, patterns, scaling, data models, and system design. Consider transferable insights from related fields.
• roleResponsibility: Map ownership, initiative, mentoring, end-to-end delivery, autonomy, and influence on outcomes.
`,
            parameters: jobMatchSchema,
        },
    },
];
exports.pageAnalysisTools = [
    {
        type: "function",
        function: {
            name: "analyze_job_page",
            description: "For matches with overall score < 0.8, only provide basic match score. For scores >= 0.8, populate additional properties.",
            parameters: pageAnalysisSchema,
        },
    },
];
exports.jobPreviewTools = [
    {
        type: "function",
        function: {
            name: "score_job_previews",
            description: "Score job titles based on relevance to candidate's background",
            parameters: jobPreviewSchema,
        },
    },
];
