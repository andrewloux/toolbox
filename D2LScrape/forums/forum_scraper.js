const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const https = require('https');

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function downloadFile(page, url, filename, retries = 3) {
    // Create Q3 directory in the current working directory
    const downloadDir = path.join(process.cwd(), 'Q3');
    if (!fs.existsSync(downloadDir)) {
        fs.mkdirSync(downloadDir, { recursive: true });
    }

    const filePath = path.join(downloadDir, filename);
    console.log(`Saving to: ${filePath}`);
    
    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            // Use fetch to get the file content
            const response = await page.evaluate(async (url) => {
                const response = await fetch(url);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const buffer = await response.arrayBuffer();
                return Array.from(new Uint8Array(buffer));
            }, url);

            // Write the file
            fs.writeFileSync(filePath, Buffer.from(response));
            console.log(`Downloaded: ${filename}`);
            return true;
        } catch (error) {
            console.log(`Attempt ${attempt} failed for ${filename}:`, error.message);
            if (attempt === retries) {
                console.log(`Failed to download ${filename} after ${retries} attempts`);
                return false;
            }
            // Wait before retrying
            await sleep(2000 * attempt);
        }
    }
    return false;
}

async function getThreadLinks(page) {
    return await page.evaluate(() => {
        const links = Array.from(document.querySelectorAll('.d2l-linkheading-link.d2l-clickable.d2l-link'));
        return links.map(link => ({
            url: link.href,
            title: link.textContent.trim()
        }));
    });
}

async function scrapeThreadContent(page) {
    const threadData = await page.evaluate(() => {
        console.log('Starting to scrape thread content...');
        
        // Get the question first
        const questionElement = document.querySelector('.d2l-htmlblock-untrusted d2l-html-block');
        console.log('Question element found:', !!questionElement);
        const question = questionElement ? questionElement.getAttribute('html') : '';
        console.log('Question content:', question ? 'Yes' : 'No');

        // Get attachments
        const attachments = [];
        const attachmentElements = document.querySelectorAll('.d2l-filelink-text.d2l-link');
        attachmentElements.forEach(attachment => {
            attachments.push({
                url: attachment.href,
                filename: attachment.textContent.trim()
            });
        });
        console.log(`Found ${attachments.length} attachments`);

        // Get all the responses
        const posts = [];
        const postElements = document.querySelectorAll('.d2l-le-disc-post-border');
        console.log('Found post elements:', postElements.length);
        
        postElements.forEach((post, index) => {
            console.log(`Processing post ${index + 1}`);
            
            const authorElement = post.querySelector('.d2l-heading');
            const contentElement = post.querySelector('.d2l-htmlblock-untrusted d2l-html-block');
            
            // Get attachments for this post
            const postAttachments = Array.from(post.querySelectorAll('.d2l-filelink-text.d2l-link')).map(attachment => ({
                url: attachment.href,
                filename: attachment.textContent.trim()
            }));
            
            console.log(`Post ${index + 1} - Author element:`, !!authorElement);
            console.log(`Post ${index + 1} - Content element:`, !!contentElement);
            console.log(`Post ${index + 1} - Attachments:`, postAttachments.length);
            
            const author = authorElement ? authorElement.textContent.trim() : 'Unknown Author';
            console.log('Author:', author);
            
            const content = contentElement ? contentElement.getAttribute('html') : '';
            console.log(`Post ${index + 1} content found:`, !!content);
            
            if (content && author !== 'Unknown Author') {
                posts.push({
                    author,
                    content,
                    attachments: postAttachments,
                    timestamp: new Date().toISOString()
                });
                console.log(`Added post ${index + 1} to results`);
            }
        });
        
        console.log(`Total posts processed: ${posts.length}`);
        return {
            question,
            attachments,
            responses: posts
        };
    });
    
    // Download attachments with error handling
    console.log('Downloading attachments...');
    const failedDownloads = [];
    
    for (const attachment of threadData.attachments) {
        const success = await downloadFile(page, attachment.url, attachment.filename);
        if (!success) {
            failedDownloads.push(attachment.filename);
        }
    }
    
    // Download attachments from responses
    for (const post of threadData.responses) {
        for (const attachment of post.attachments) {
            const success = await downloadFile(page, attachment.url, attachment.filename);
            if (!success) {
                failedDownloads.push(attachment.filename);
            }
        }
    }
    
    if (failedDownloads.length > 0) {
        console.log('Failed to download the following files:', failedDownloads);
    }
    
    console.log('Thread data retrieved:', {
        hasQuestion: !!threadData.question,
        responseCount: threadData.responses.length,
        attachmentCount: threadData.attachments.length,
        failedDownloads: failedDownloads.length
    });
    
    return threadData;
}

async function scrapeD2LContent() {
    console.log('Connecting to Chrome...');
    const browser = await puppeteer.connect({
        browserURL: 'http://localhost:9222',
        defaultViewport: null
    });

    const allThreads = [];

    try {
        const page = await browser.newPage();
        // Start at the main forum page
        await page.goto('https://michbrite.michener.ca/d2l/le/7298/discussions/topics/783/View', {
            waitUntil: 'networkidle0'
        });

        console.log('\n=== LOGIN REQUIRED ===');
        console.log('Please login if necessary');
        console.log('Press Enter when ready...\n');

        await new Promise(resolve => process.stdin.once('data', resolve));
        await sleep(2000);

        // Get all thread links
        const threadLinks = await getThreadLinks(page);
        console.log(`Found ${threadLinks.length} threads to process`);

        // Process each thread
        for (let i = 0; i < threadLinks.length; i++) {
            const thread = threadLinks[i];
            console.log(`\nProcessing thread ${i + 1}/${threadLinks.length}: ${thread.title}`);
            
            // Navigate to the thread
            await page.goto(thread.url, { waitUntil: 'networkidle0' });
            await sleep(2000); // Wait for content to load

            // Scrape the thread content
            const posts = await scrapeThreadContent(page);
            
            if (posts.responses.length > 0) {
                allThreads.push({
                    threadTitle: thread.title,
                    threadUrl: thread.url,
                    question: posts.question,
                    responses: posts.responses
                });
                console.log(`Found ${posts.responses.length} responses in this thread`);
            } else {
                console.log('No responses found in this thread');
            }
        }

        // Save the results
        fs.writeFileSync('forum_threads.json', JSON.stringify(allThreads, null, 2));
        console.log(`\nSaved ${allThreads.length} threads to forum_threads.json`);

    } catch (error) {
        console.error('An error occurred:', error);
    } finally {
        await browser.disconnect();
    }
}

scrapeD2LContent().catch(console.error);