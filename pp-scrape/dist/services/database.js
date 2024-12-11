"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.dbService = void 0;
const client_1 = require("@prisma/client");
const types_1 = require("../types");
class DatabaseService {
    constructor() {
        this.prisma = new client_1.PrismaClient({
            log: ["query", "error", "warn"],
        });
    }
    validateJobStatus(status) {
        if (!types_1.JOB_STATUSES.includes(status)) {
            throw new Error(`Invalid job status: ${status}. Must be one of: ${types_1.JOB_STATUSES.join(", ")}`);
        }
    }
    parseJSON(jsonString) {
        if (!jsonString)
            return null;
        try {
            return JSON.parse(jsonString);
        }
        catch (e) {
            console.warn('Failed to parse JSON:', e);
            return null;
        }
    }
    async insertCompany(company) {
        const existing = await this.prisma.company.findFirst({
            where: {
                name: company.name,
                website: company.website,
            },
        });
        if (existing) {
            return existing.id;
        }
        const result = await this.prisma.company.create({
            data: {
                name: company.name,
                website: company.website,
            },
        });
        return result.id;
    }
    async insertRole(params) {
        await this.prisma.role.create({
            data: {
                company_id: params.companyId,
                title: params.title,
                link: params.link,
                location: params.location,
                pay_range: params.payRange,
                similarity_score: params.similarityScore,
                section_scores: params.sectionScores,
                resume_checksum: params.resumeChecksum,
            },
        });
    }
    async findExistingRole(link) {
        const role = await this.prisma.role.findFirst({
            where: { link },
        });
        return role?.id ?? null;
    }
    async updateJobStatus(id, status) {
        this.validateJobStatus(status);
        await this.prisma.role.update({
            where: { id },
            data: { status },
        });
    }
    async dislikeJob(id) {
        await this.prisma.role.update({
            where: { id },
            data: { disliked: true },
        });
    }
    async getJobsByStatus(status) {
        this.validateJobStatus(status);
        const roles = await this.prisma.role.findMany({
            where: { status },
            orderBy: { similarity_score: "desc" },
            include: { company: true },
        });
        return roles.map(role => ({
            ...role,
            section_scores: this.parseJSON(role.section_scores),
            analysis_json: this.parseJSON(role.analysis_json)
        }));
    }
    async getRecentJobs(limit) {
        const roles = await this.prisma.role.findMany({
            take: limit,
            orderBy: { created_at: "desc" },
            include: { company: true },
        });
        return roles.map(role => ({
            ...role,
            section_scores: this.parseJSON(role.section_scores),
            analysis_json: this.parseJSON(role.analysis_json)
        }));
    }
    async getAllCompanies() {
        return await this.prisma.company.findMany({
            orderBy: { name: "asc" },
        });
    }
    async getCompanyJobs(companyId) {
        const roles = await this.prisma.role.findMany({
            where: { company_id: companyId },
            orderBy: { created_at: "desc" },
            include: { company: true },
        });
        return roles.map(role => ({
            ...role,
            section_scores: this.parseJSON(role.section_scores),
            analysis_json: this.parseJSON(role.analysis_json)
        }));
    }
    async isJobProcessed(resumeChecksum, jobLink) {
        const role = await this.prisma.role.findFirst({
            where: {
                link: jobLink,
                resume_checksum: resumeChecksum,
            }
        });
        return !!role;
    }
    async close() {
        await this.prisma.$disconnect();
    }
    async saveJobAnalysis(params) {
        console.log("Saving job analysis", params);
        // Validate similarity score is a number
        if (typeof params.similarityScore !== 'number' || isNaN(params.similarityScore)) {
            throw new Error(`Invalid similarity score: ${params.similarityScore}. Must be a number.`);
        }
        // First upsert the company
        const companyResult = await this.prisma.company.upsert({
            where: {
                name_website: {
                    name: params.company || "Unknown",
                    website: new URL(params.url).origin
                }
            },
            update: {}, // No updates needed if exists
            create: {
                name: params.company || "Unknown",
                website: new URL(params.url).origin
            }
        });
        // Then try to find existing role
        const existingRole = await this.prisma.role.findFirst({
            where: { link: params.url }
        });
        // Base role data without the link field
        const roleData = {
            company_id: companyResult.id,
            similarity_score: params.similarityScore,
            section_scores: params.sectionScores,
            analysis_json: params.analysisJson,
            status: params.status,
            title: params.title,
            location: params.location,
            pay_range: params.salary
        };
        if (existingRole) {
            // Update existing role with analysis
            await this.prisma.role.update({
                where: { id: existingRole.id },
                data: {
                    ...roleData,
                    // Only update these if they were null before
                    title: existingRole.title || roleData.title,
                    location: existingRole.location || roleData.location,
                    pay_range: existingRole.pay_range || roleData.pay_range
                }
            });
        }
        else {
            // Create new role with company reference and link
            await this.prisma.role.create({
                data: {
                    ...roleData,
                    link: params.url // Required for new roles
                }
            });
        }
    }
}
exports.dbService = new DatabaseService();
