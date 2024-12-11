const puppeteer = require('puppeteer');
const fs = require('fs');

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function findIframesAndContext(page) {
    const iframesWithContext = await page.evaluate(() => {
        function findSlidoIframesRecursive(element, path = '') {
            let results = [];
            
            if (element.shadowRoot) {
                const shadowIframes = element.shadowRoot.querySelectorAll('iframe[src*="sli.do"]');
                if (shadowIframes.length > 0) {
                    shadowIframes.forEach(iframe => {
                        // Find the html-content span
                        let htmlContent = iframe.closest('.html-content');
                        let contextText = '';
                        
                        if (htmlContent) {
                            // Get all p elements in the html-content
                            const pElements = Array.from(htmlContent.querySelectorAll('p'));
                            console.log(`Found ${pElements.length} p elements in html-content`);
                            
                            // The context should be in the second p element
                            if (pElements.length >= 2) {
                                contextText = pElements[1].textContent.trim();
                                console.log('Found context text:', contextText);
                            }
                        }
                        
                        results.push({
                            src: iframe.src,
                            path: path,
                            contextText: contextText
                        });
                    });
                    console.log('Found Slido iframes at path: ', path);
                }
                
                const shadowChildren = element.shadowRoot.children;
                Array.from(shadowChildren).forEach(child => {
                    results = results.concat(
                        findSlidoIframesRecursive(child, `${path} > ${child.tagName}`)
                    );
                });
            }
            
            const children = element.children;
            Array.from(children).forEach(child => {
                results = results.concat(
                    findSlidoIframesRecursive(child, `${path} > ${child.tagName}`)
                );
            });
            
            return results;
        }

        return findSlidoIframesRecursive(document.documentElement);
    });

    return iframesWithContext;
}

async function waitForContent(page) {
    let attempts = 0;
    const maxAttempts = 10;
    
    while (attempts < maxAttempts) {
        const hasContent = await page.evaluate(() => {
            const content = document.body.innerText.trim();
            console.log('Current content:', content);
            return content.length > 0;
        });

        if (hasContent) {
            console.log('Content found!');
            return true;
        }

        console.log(`Attempt ${attempts + 1}: Waiting for content to load...`);
        await sleep(1000);
        attempts++;
    }

    return false;
}

async function scrapeD2LContent() {
    console.log('Connecting to Chrome...');
    const browser = await puppeteer.connect({
        browserURL: 'http://localhost:9222',
        defaultViewport: null
    });

    const questions = new Set();

    try {
        const page = await browser.newPage();
        await page.goto('https://michbrite.michener.ca/d2l/home/7298', {
            waitUntil: 'networkidle0'
        });

        console.log('\n=== LOGIN REQUIRED ===');
        console.log('Please login if necessary');
        console.log('Press Enter when ready...\n');

        await new Promise(resolve => process.stdin.once('data', resolve));
        await sleep(2000);

        let attempts = 0;
        let iframesData = [];
        
        while (attempts < 5 && iframesData.length === 0) {
            console.log(`Attempt ${attempts + 1} to find iframes...`);
            iframesData = await findIframesAndContext(page);
            console.log('Found iframes with context:', JSON.stringify(iframesData, null, 2));
            
            if (iframesData.length === 0) {
                await sleep(2000);
                attempts++;
            }
        }

        if (iframesData.length > 0) {
            console.log(`Processing ${iframesData.length} Slido iframes...`);
            
            for (const iframeData of iframesData) {
                const iframePage = await browser.newPage();
                try {
                    console.log(`Processing iframe: ${iframeData.src}`);
                    console.log(`Context text: ${iframeData.contextText}`);
                    await iframePage.goto(iframeData.src, { waitUntil: 'networkidle0', timeout: 30000 });
                    
                    if (await waitForContent(iframePage)) {
                        const pageContent = await iframePage.evaluate(() => ({
                            text: document.body.innerText.trim(),
                            url: window.location.href
                        }));

                        if (pageContent.text) {
                            const fullContent = {
                                ...pageContent,
                                contextText: iframeData.contextText
                            };
                            questions.add(JSON.stringify(fullContent));
                            console.log('Found content:', pageContent.text.substring(0, 100) + '...');
                        }
                    } else {
                        console.log(`No content found for iframe: ${iframeData.src}`);
                    }
                } catch (error) {
                    console.error(`Error processing iframe: ${iframeData.src}`, error.message);
                } finally {
                    await iframePage.close();
                }
            }
        } else {
            console.log('No iframes found after multiple attempts');
        }

        const questionsArray = Array.from(questions).map(q => JSON.parse(q));
        fs.writeFileSync('slido_questions.json', JSON.stringify(questionsArray, null, 2));
        console.log(`\nSaved ${questionsArray.length} questions to slido_questions.json`);

    } catch (error) {
        console.error('An error occurred:', error);
    } finally {
        await browser.disconnect();
    }
}

scrapeD2LContent().catch(console.error);