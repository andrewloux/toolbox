"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.textExtractor = exports.TextExtractorService = void 0;
const crypto_1 = require("crypto");
const fs_1 = require("fs");
const logger_1 = __importDefault(require("../utils/logger"));
const pdf_parse_1 = __importDefault(require("pdf-parse"));
const prisma_1 = require("../lib/prisma");
const SERVICE_NAME = "TextExtractorService";
class TextExtractorService {
    constructor() { }
    async getResumeChecksum(filePath) {
        const fileBuffer = (0, fs_1.readFileSync)(filePath);
        const hashSum = (0, crypto_1.createHash)("sha256");
        hashSum.update(fileBuffer);
        return hashSum.digest("hex");
    }
    async getResumeText(resumePath = "resume.pdf") {
        try {
            // Calculate checksum of the resume file
            const checksum = await this.getResumeChecksum(resumePath);
            // Check cache first
            const cachedResult = await prisma_1.prisma.resumeCache.findUnique({
                where: { fileChecksum: checksum },
            });
            if (cachedResult) {
                logger_1.default.info(SERVICE_NAME, "Using cached resume text");
                return cachedResult.processedText;
            }
            // If not in cache, process the resume
            const dataBuffer = (0, fs_1.readFileSync)(resumePath);
            const data = await (0, pdf_parse_1.default)(dataBuffer);
            const processedText = data.text;
            // Cache the result
            await prisma_1.prisma.resumeCache.create({
                data: {
                    fileChecksum: checksum,
                    processedText: processedText,
                },
            });
            logger_1.default.info(SERVICE_NAME, "Cached new resume text");
            return processedText;
        }
        catch (error) {
            logger_1.default.error(SERVICE_NAME, "Error processing resume", { error });
            throw error;
        }
    }
    async extractPdfText(filePath) {
        try {
            const dataBuffer = (0, fs_1.readFileSync)(filePath);
            const data = await (0, pdf_parse_1.default)(dataBuffer);
            return data.text;
        }
        catch (error) {
            logger_1.default.error(SERVICE_NAME, "Error extracting PDF text", {
                error,
                filePath,
            });
            throw error;
        }
    }
    async clearCache() {
        try {
            await prisma_1.prisma.resumeCache.deleteMany({});
            logger_1.default.info(SERVICE_NAME, "Resume cache cleared");
        }
        catch (error) {
            logger_1.default.error(SERVICE_NAME, "Error clearing cache", { error });
            throw error;
        }
    }
}
exports.TextExtractorService = TextExtractorService;
exports.textExtractor = new TextExtractorService();
