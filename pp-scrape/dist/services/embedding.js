"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.embeddingService = exports.EmbeddingService = void 0;
const openai_1 = require("openai");
const fs_1 = __importDefault(require("fs"));
const crypto_1 = __importDefault(require("crypto"));
const pdf_parse_1 = __importDefault(require("pdf-parse"));
const constants_1 = require("../config/constants");
const logger_1 = __importDefault(require("../utils/logger"));
const SERVICE_NAME = "EmbeddingService";
class EmbeddingService {
    constructor() {
        this.openai = new openai_1.OpenAI();
        this.rateLimits = {
            maxRequests: 100,
            timeWindow: 60000,
            requestsPerMin: 3500,
            requestsRemaining: 3500,
            resetTime: Date.now() + 60000,
            queue: [],
            processing: false,
            lastRequestTime: Date.now(),
        };
        if (!fs_1.default.existsSync(constants_1.CACHE_DIR)) {
            fs_1.default.mkdirSync(constants_1.CACHE_DIR);
            logger_1.default.info(SERVICE_NAME, `Created cache directory: ${constants_1.CACHE_DIR}`);
        }
    }
    async updateRateLimits(headers) {
        const oldLimits = { ...this.rateLimits };
        if (headers["x-ratelimit-limit-requests"]) {
            this.rateLimits.requestsPerMin = parseInt(headers["x-ratelimit-limit-requests"]);
        }
        if (headers["x-ratelimit-remaining-requests"]) {
            this.rateLimits.requestsRemaining = parseInt(headers["x-ratelimit-remaining-requests"]);
        }
        if (headers["x-ratelimit-reset-requests"]) {
            this.rateLimits.resetTime =
                Date.now() + parseInt(headers["x-ratelimit-reset-requests"]) * 1000;
        }
        logger_1.default.debug(SERVICE_NAME, "Rate limits updated", {
            old: oldLimits,
            new: this.rateLimits,
        });
    }
    async waitForRateLimit() {
        if (this.rateLimits.requestsRemaining <= 0) {
            const waitTime = Math.max(0, this.rateLimits.resetTime - Date.now());
            if (waitTime > 0) {
                logger_1.default.warn(SERVICE_NAME, `Rate limit reached, waiting ${(waitTime / 1000).toFixed(1)} seconds`);
                await new Promise((resolve) => setTimeout(resolve, waitTime));
            }
        }
    }
    async getEmbedding(text) {
        logger_1.default.debug(SERVICE_NAME, "Generating embedding", {
            textLength: text.length,
            model: constants_1.EMBEDDING_MODEL,
        });
        await this.waitForRateLimit();
        const response = (await this.openai.embeddings.create({
            model: constants_1.EMBEDDING_MODEL,
            input: text,
            dimensions: constants_1.EMBEDDING_DIMENSIONS,
        }));
        if (response.response?.headers) {
            await this.updateRateLimits(response.response.headers);
        }
        logger_1.default.debug(SERVICE_NAME, "Embedding generated successfully", {
            dimensions: response.data[0].embedding.length,
        });
        return response.data[0].embedding;
    }
    getChecksum(text) {
        return crypto_1.default.createHash("md5").update(text).digest("hex");
    }
    async getCachedResumeEmbedding(resumePath) {
        logger_1.default.info(SERVICE_NAME, `Processing resume: ${resumePath}`);
        const dataBuffer = fs_1.default.readFileSync(resumePath);
        const data = await (0, pdf_parse_1.default)(dataBuffer);
        const resumeText = data.text;
        const checksum = this.getChecksum(resumeText);
        const cachePath = `${constants_1.CACHE_DIR}/resume_${checksum}_${constants_1.EMBEDDING_MODEL}.json`;
        if (fs_1.default.existsSync(cachePath)) {
            logger_1.default.info(SERVICE_NAME, "Found cached resume embedding");
            const cached = JSON.parse(fs_1.default.readFileSync(cachePath, "utf-8"));
            if (cached.model === constants_1.EMBEDDING_MODEL &&
                cached.embedding.length === constants_1.EMBEDDING_DIMENSIONS) {
                return cached.embedding;
            }
            logger_1.default.warn(SERVICE_NAME, "Cached embedding is invalid, regenerating", {
                expectedDimensions: constants_1.EMBEDDING_DIMENSIONS,
                actualDimensions: cached.embedding.length,
                model: cached.model,
            });
        }
        logger_1.default.info(SERVICE_NAME, "Generating new resume embedding");
        const embedding = await this.getEmbedding(resumeText);
        fs_1.default.writeFileSync(cachePath, JSON.stringify({
            model: constants_1.EMBEDDING_MODEL,
            embedding: embedding,
            timestamp: Date.now(),
        }));
        return embedding;
    }
    async cosineSimilarity(embedding1, embedding2) {
        if (embedding1.length !== constants_1.EMBEDDING_DIMENSIONS ||
            embedding2.length !== constants_1.EMBEDDING_DIMENSIONS) {
            const error = `Invalid embedding dimensions. Expected ${constants_1.EMBEDDING_DIMENSIONS} but got ${embedding1.length} and ${embedding2.length}`;
            logger_1.default.error(SERVICE_NAME, error);
            throw new Error(error);
        }
        const dotProduct = embedding1.reduce((sum, a, i) => sum + a * embedding2[i], 0);
        const norm1 = Math.sqrt(embedding1.reduce((sum, a) => sum + a * a, 0));
        const norm2 = Math.sqrt(embedding2.reduce((sum, a) => sum + a * a, 0));
        const similarity = dotProduct / (norm1 * norm2);
        logger_1.default.debug(SERVICE_NAME, "Calculated similarity score", { similarity });
        return similarity;
    }
    async getResumeText(resumePath) {
        logger_1.default.info(SERVICE_NAME, `Reading resume text: ${resumePath}`);
        const dataBuffer = fs_1.default.readFileSync(resumePath);
        const data = await (0, pdf_parse_1.default)(dataBuffer);
        return data.text;
    }
    async createChatCompletion(messages, options = {
        model: "gpt-4o",
    }) {
        return await this.openai.chat.completions.create({
            messages,
            ...options,
            stream: false,
        });
    }
}
exports.EmbeddingService = EmbeddingService;
exports.embeddingService = new EmbeddingService();
