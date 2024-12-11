import { dbService } from './services/database';
import { ScraperService } from './services/scraper';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

async function main() {
    const argv = await yargs(hideBin(process.argv))
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
        const scraper = new ScraperService(argv.headless);
        await scraper.analyzeJobs(argv.url, argv.resume, { topN: argv.topN });
    } catch (error) {
        console.error('An error occurred:', error);
    } finally {
        await dbService.close();
    }
}

main().catch(console.error); 