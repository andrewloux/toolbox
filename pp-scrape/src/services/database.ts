import { PrismaClient } from "@prisma/client";
import type { Company, Role } from ".prisma/client";
import { CompanyInfo, JobStatus, JOB_STATUSES } from "../types";

interface SaveJobAnalysisParams {
  url: string;
  title: string;
  company: string | null;
  location: string | null;
  salary: string | null;
  similarityScore: number;
  sectionScores: string;
  analysisJson: string;
  status: string;
}

type RoleWithCompany = {
  id: number;
  company_id: number;
  title: string;
  link: string;
  location: string | null;
  pay_range: string | null;
  similarity_score: number;
  status: string;
  disliked: boolean;
  created_at: Date;
  section_scores: string | null;
  analysis_json: string | null;
  company: Company;
};

class DatabaseService {
  private prisma: PrismaClient;

  constructor() {
    this.prisma = new PrismaClient({
      log: ["query", "error", "warn"],
    });
  }

  private validateJobStatus(status: JobStatus): void {
    if (!JOB_STATUSES.includes(status)) {
      throw new Error(
        `Invalid job status: ${status}. Must be one of: ${JOB_STATUSES.join(", ")}`,
      );
    }
  }

  private parseJSON<T>(jsonString: string | null): T | null {
    if (!jsonString) return null;
    try {
      return JSON.parse(jsonString) as T;
    } catch (e) {
      console.warn('Failed to parse JSON:', e);
      return null;
    }
  }

  public async insertCompany(company: CompanyInfo): Promise<number> {
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

  public async insertRole(params: {
    companyId: number;
    title: string;
    link: string;
    location?: string;
    payRange?: string;
    similarityScore: number;
    sectionScores?: string;
    resumeChecksum: string;
  }): Promise<void> {
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

  public async findExistingRole(link: string): Promise<number | null> {
    const role = await this.prisma.role.findFirst({
      where: { link },
    });
    return role?.id ?? null;
  }

  public async updateJobStatus(id: number, status: JobStatus): Promise<void> {
    this.validateJobStatus(status);
    await this.prisma.role.update({
      where: { id },
      data: { status },
    });
  }

  public async dislikeJob(id: number): Promise<void> {
    await this.prisma.role.update({
      where: { id },
      data: { disliked: true },
    });
  }

  public async getJobsByStatus(status: JobStatus): Promise<RoleWithCompany[]> {
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

  public async getRecentJobs(limit: number): Promise<RoleWithCompany[]> {
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

  public async getAllCompanies(): Promise<Company[]> {
    return await this.prisma.company.findMany({
      orderBy: { name: "asc" },
    });
  }

  public async getCompanyJobs(companyId: number): Promise<RoleWithCompany[]> {
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

  public async isJobProcessed(resumeChecksum: string, jobLink: string): Promise<boolean> {
    const role = await this.prisma.role.findFirst({
      where: {
        link: jobLink,
        resume_checksum: resumeChecksum,
      }
    });
    return !!role;
  }

  public async close(): Promise<void> {
    await this.prisma.$disconnect();
  }

  public async saveJobAnalysis(params: SaveJobAnalysisParams): Promise<void> {
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
    } else {
      // Create new role with company reference and link
      await this.prisma.role.create({
        data: {
          ...roleData,
          link: params.url  // Required for new roles
        }
      });
    }
  }
}

export const dbService = new DatabaseService();
