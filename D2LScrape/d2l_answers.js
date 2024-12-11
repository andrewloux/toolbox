const puppeteer = require("puppeteer");
const fs = require("fs");

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function scrapeQuizExplanations() {
  console.log("🌐 Connecting to Chrome...");
  const browser = await puppeteer.connect({
    browserURL: "http://localhost:9222",
    defaultViewport: null,
  });

  const allExplanations = [];

  try {
    const page = await browser.newPage();
    console.log("📱 Navigating to D2L...");
    await page.goto(
      "https://michbrite.michener.ca/d2l/le/7298/discussions/topics/783/View",
      {
        waitUntil: "networkidle0",
      },
    );

    console.log("\n=== LOGIN REQUIRED ===");
    await sleep(1000);
    console.log("Press Enter when ready...\n");
    await new Promise((resolve) => process.stdin.once("data", resolve));

    // Wait for iframe to load
    console.log("⌛ Waiting for iframe to load...");
    await page.waitForSelector('iframe[id^="d2l_"]', { timeout: 30000 });

    const frameHandle = await page.$('iframe[id^="d2l_"]');
    console.log("✅ Found iframe handle");

    const frame = await frameHandle.contentFrame();
    console.log("✅ Retrieved content frame");

    if (!frame) {
      throw new Error("Could not access iframe content");
    }

    console.log("✅ Successfully accessed iframe content");
    console.log("🔍 Finding navigation items in iframe...");

    // Wait for the navigation menu to be present
    console.log("⌛ Waiting for navigation menu...");
    await frame.waitForSelector(".navigation-menu", { timeout: 30000 });
    console.log("✅ Navigation menu found");

    // Execute the tested logic within the frame context
    console.log("🔍 Starting navigation item search...");
    const popupItems = await frame.evaluate(() => {
      const results = [];
      let popupCount = 0;

      // Debug logging function
      const log = (msg) => {
        console.log(`[Browser] ${msg}`);
      };

      // Helper function to find clickable elements
      const findClickable = (navItem) => {
        let clickable = navItem.querySelector(".unit-box");
        if (!clickable) {
          clickable = navItem.querySelector(".topic-box");
        }
        return clickable;
      };

      log("Starting DOM traversal...");

      // Get all main navigation items
      const mainItems = document.querySelectorAll(
        ".navigation-menu .navigation-item",
      );
      log(`Found ${mainItems.length} main navigation items`);

      mainItems.forEach((mainItem, mainIndex) => {
        const mainTitle =
          mainItem.querySelector(".title-text span")?.textContent.trim() || "";
        log(`Processing main item ${mainIndex + 1}: ${mainTitle}`);

        // Click main items to expand them
        const mainClickable = findClickable(mainItem);
        if (mainClickable) {
          log(`Found clickable element for: ${mainTitle}`);
          mainClickable.click();
          log(`Clicked main item: ${mainTitle}`);
        }

        // Find nested items
        const nestedItems = mainItem.querySelectorAll(".navigation-item");
        log(`Found ${nestedItems.length} nested items in ${mainTitle}`);

        nestedItems.forEach((nested, nestedIndex) => {
          const nestedTitle =
            nested.querySelector(".title-text span")?.textContent.trim() || "";
          log(`Checking nested item ${nestedIndex + 1}: "${nestedTitle}"`);

          if (nestedTitle.toLowerCase().includes("pop-up quiz explanation")) {
            log(`Found pop-up: "${nestedTitle}"`);

            const nestedClickable = findClickable(nested);
            if (nestedClickable) {
              log(`Found clickable element for pop-up: "${nestedTitle}"`);

              // Store the data-objectid attributes for more reliable selection
              results.push({
                mainTitle,
                popupText: nestedTitle,
                index: popupCount,
                mainId: mainItem.getAttribute("data-objectid"),
                nestedId: nested.getAttribute("data-objectid"),
                debug: {
                  mainClasses: mainItem.className,
                  nestedClasses: nested.className,
                  clickableClasses: nestedClickable.className,
                },
              });
              popupCount++;
            } else {
              log(`No clickable element found for pop-up: "${nestedTitle}"`);
            }
          }
        });
      });

      log(`Found ${results.length} total pop-ups`);
      return results;
    });

    console.log(`\n📊 Found ${popupItems.length} pop-up items to process`);
    console.log("Pop-up items found:", JSON.stringify(popupItems, null, 2));

    // Process each popup item sequentially
    for (let i = 0; i < popupItems.length; i++) {
      const item = popupItems[i];
      console.log(`\n📍 Processing pop-up ${i + 1}/${popupItems.length}`);
      console.log(`  Main section: "${item.mainTitle}"`);
      console.log(`  Pop-up: "${item.popupText}"`);
      console.log(`  Debug info:`, item.debug);

      try {
        // First, make sure we can see the main section's expand button
        console.log("  🔍 Finding main section's expand button...");
        const triangleSelector = `.navigation-menu .navigation-item[data-objectid="${item.mainId}"] .module-triangle`;
        console.log(`  Using triangle selector: ${triangleSelector}`);

        await frame.waitForSelector(triangleSelector, {
          visible: true,
          timeout: 5000,
        });

        // Check if it's already expanded
        const triangleState = await frame.evaluate((selector) => {
          const triangle = document.querySelector(selector);
          return {
            icon: triangle?.getAttribute("icon"),
            isVisible: triangle?.offsetParent !== null,
            classes: triangle?.className,
          };
        }, triangleSelector);
        console.log(`  Triangle state:`, triangleState);

        const isExpanded = triangleState.icon === "tier1:arrow-collapse-small";

        if (!isExpanded) {
          console.log("  ↪ Expanding main section...");
          await frame.click(triangleSelector);
          await sleep(1000);
        } else {
          console.log("  ℹ️ Main section already expanded");
        }
        console.log("  ✅ Main section expanded");

        // Now find and click the pop-up item
        console.log("  🔍 Finding pop-up link...");
        const popupSelector = `.navigation-item[data-objectid="${item.nestedId}"] .topic-box`;
        console.log(`  Using popup selector: ${popupSelector}`);

        // Debug: Check the element before clicking
        const popupState = await frame.evaluate(
          (selector, expectedText) => {
            const element = document.querySelector(selector);
            const titleSpan = element?.querySelector(".title-text span");
            return {
              exists: !!element,
              isVisible: element?.offsetParent !== null,
              classes: element?.className,
              text: titleSpan?.textContent?.trim(),
              matches: titleSpan?.textContent?.trim().includes(expectedText),
              rect: element?.getBoundingClientRect(),
            };
          },
          popupSelector,
          item.popupText,
        );
        console.log(`  Pop-up element state:`, popupState);

        if (!popupState.matches) {
          throw new Error(
            `Found wrong element. Expected "${item.popupText}" but found "${popupState.text}"`,
          );
        }

        await frame.waitForSelector(popupSelector, {
          visible: true,
          timeout: 5000,
        });

        console.log("  ↪ Clicking pop-up");
        await frame.click(popupSelector);
        await sleep(2000);
        console.log("  ✅ Clicked pop-up");

        // Wait longer after clicking
        console.log("  ⌛ Waiting for initial navigation...");
        await sleep(2000);

        // Wait for content to load
        console.log("  ⌛ Waiting for content structure...");

        // Wait for the wrapper and iframe structure
        await frame.waitForSelector(".resizing-iframe-container", {
          timeout: 5000,
        });
        await frame.waitForSelector("d2l-iframe-wrapper-for-react", {
          timeout: 5000,
        });

        console.log("  ✅ Found iframe wrapper");

        // Get the content from within the iframe
        const content = await frame.evaluate(async () => {
          // Helper function to wait for element
          const waitFor = async (selector, context, timeout = 5000) => {
            const start = Date.now();
            while (Date.now() - start < timeout) {
              const element = context.querySelector(selector);
              if (element) return element;
              await new Promise((r) => setTimeout(r, 100));
            }
            return null;
          };

          // First find the iframe
          const wrapper = await waitFor(
            "d2l-iframe-wrapper-for-react",
            document,
          );
          if (!wrapper) throw new Error("Could not find iframe wrapper");

          // Get the shadow root
          const shadow = wrapper.shadowRoot;
          if (!shadow) throw new Error("No shadow root found");

          // Find the iframe in the shadow DOM
          const iframe = await waitFor(
            "iframe.resizing-iframe.html-topic-iframe",
            shadow,
          );
          if (!iframe) throw new Error("Could not find content iframe");

          // Get the iframe's document content
          try {
            const iframeDocument = iframe.contentDocument;
            if (!iframeDocument)
              throw new Error("Could not access iframe document");

            // Get all text content from the iframe's body
            const text = iframeDocument.body.textContent.trim();

            if (!text) throw new Error("No text content found in iframe");

            return text;
          } catch (e) {
            console.error("Error accessing iframe content:", e);
            throw e;
          }
        });

        // Validate content
        if (!content || !content.trim()) {
          throw new Error(
            "Could not find any meaningful content in the iframe",
          );
        }

        console.log("  ✅ Content extracted from iframe");
        console.log("  Preview of content:", content.substring(0, 100) + "...");
        console.log("  Content length:", content.length);

        allExplanations.push({
          timestamp: new Date().toISOString(),
          mainSection: item.mainTitle,
          title: item.popupText,
          content: content,
        });
        console.log(`  ✅ Saved content for "${item.popupText}"`);
      } catch (error) {
        console.error(`  ❌ Error processing pop-up "${item.popupText}":`);
        console.error(`  Error details: ${error.message}`);
        console.error(`  Current selectors:
          Triangle: .navigation-menu .navigation-item[data-objectid="${item.mainId}"] .module-triangle
          Popup: .navigation-item[data-objectid="${item.nestedId}"] .topic-box
        `);
        if (error.stack) {
          console.error(`  Stack trace: ${error.stack}`);
        }
      }
    }

    // Save the results
    const outputPath = "quiz_explanations.json";
    fs.writeFileSync(outputPath, JSON.stringify(allExplanations, null, 2));
    console.log(
      `\n💾 Saved ${allExplanations.length} quiz explanation sets to ${outputPath}`,
    );
  } catch (error) {
    console.error("❌ An error occurred:");
    console.error(error.message);
    if (error.stack) {
      console.error("Stack trace:");
      console.error(error.stack);
    }
  } finally {
    await browser.disconnect();
    console.log("👋 Done!");
  }
}

scrapeQuizExplanations().catch(console.error);
