import { createHash } from 'crypto';
import { readFileSync } from 'fs';
import Logger from '../utils/logger';
import pdf from 'pdf-parse';
import { prisma } from '../lib/prisma';

const SERVICE_NAME = "TextExtractorService";

export class TextExtractorService {
  constructor() {}

  async getResumeChecksum(filePath: string): Promise<string> {
    const fileBuffer = readFileSync(filePath);
    const hashSum = createHash('sha256');
    hashSum.update(fileBuffer);
    return hashSum.digest('hex');
  }

  async getResumeText(resumePath: string = 'resume.pdf'): Promise<string> {
    try {
      // Calculate checksum of the resume file
      const checksum = await this.getResumeChecksum(resumePath);
      
      // Check cache first
      const cachedResult = await prisma.resumeCache.findUnique({
        where: { fileChecksum: checksum }
      });

      if (cachedResult) {
        Logger.info(SERVICE_NAME, 'Using cached resume text');
        return cachedResult.processedText;
      }

      // If not in cache, process the resume
      const dataBuffer = readFileSync(resumePath);
      const data = await pdf(dataBuffer);
      const processedText = data.text;
      
      // Cache the result
      await prisma.resumeCache.create({
        data: {
          fileChecksum: checksum,
          processedText: processedText,
        }
      });

      Logger.info(SERVICE_NAME, 'Cached new resume text');
      return processedText;
    } catch (error) {
      Logger.error(SERVICE_NAME, 'Error processing resume', { error });
      throw error;
    }
  }

  async extractPdfText(filePath: string): Promise<string> {
    try {
      const dataBuffer = readFileSync(filePath);
      const data = await pdf(dataBuffer);
      return data.text;
    } catch (error) {
      Logger.error(SERVICE_NAME, 'Error extracting PDF text', { error, filePath });
      throw error;
    }
  }

  async clearCache(): Promise<void> {
    try {
      await prisma.resumeCache.deleteMany({});
      Logger.info(SERVICE_NAME, 'Resume cache cleared');
    } catch (error) {
      Logger.error(SERVICE_NAME, 'Error clearing cache', { error });
      throw error;
    }
  }
}

export const textExtractor = new TextExtractorService();
