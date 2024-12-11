"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const database_1 = require("./services/database");
const scraper_1 = require("./services/scraper");
const yargs_1 = __importDefault(require("yargs"));
const helpers_1 = require("yargs/helpers");
async function main() {
    const argv = await (0, yargs_1.default)((0, helpers_1.hideBin)(process.argv))
        .usage('Usage: $0 --url <url> [options]')
        .options({
        url: {
            type: 'string',
            describe: 'URL of the job posting to analyze',
            demandOption: true
        },
        topN: {
            type: 'number',
            describe: 'Number of top results to return',
            default: 5
        },
        headless: {
            type: 'boolean',
            describe: 'Run browser in headless mode',
            default: false
        },
        resume: {
            type: 'string',
            describe: 'Path to the resume PDF file',
            default: 'resume.pdf'
        }
    })
        .example('$0 --url https://example.com/job', 'Analyze job posting with default settings')
        .example('$0 --url https://example.com/job --topN 10 --headless', 'Analyze job with custom settings')
        .help()
        .alias('h', 'help')
        .argv;
    try {
        const scraper = new scraper_1.ScraperService(argv.headless);
        await scraper.analyzeJobs(argv.url, argv.resume, { topN: argv.topN });
    }
    catch (error) {
        console.error('An error occurred:', error);
    }
    finally {
        await database_1.dbService.close();
    }
}
main().catch(console.error);
