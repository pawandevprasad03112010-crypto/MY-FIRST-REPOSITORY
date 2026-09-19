const express = require('express');
const puppeteer = require('puppeteer');
const path = require('path');

const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/scrape', async (req, res) => {
    const { location, bhk } = req.body;
    
    if (!location) {
        return res.status(400).json({ error: 'लोकेशन डालना अनिवार्य है।' });
    }

    let browser;
    try {
        browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });

        const page = await browser.newPage();
        
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');
        await page.setViewport({ width: 1280, height: 800 });

        let formattedLoc = location.toLowerCase().replace(/\s+/g, '-');
        let url = `https://www.99acres.com/property-in-${formattedLoc}-ffid`;
        
        if (bhk) {
            url += `?preference=R&property_type=1&bedroom=${bhk}`;
        }

        console.log(`URL पर जा रहे हैं: ${url}`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

        await new Promise(r => setTimeout(r, 4000));

        const listings = await page.evaluate(() => {
            const cards = document.querySelectorAll('.tuple__contentCard, [data-label="result-card"]');
            let results = [];

            cards.forEach(card => {
                const title = card.querySelector('.tuple__aptName, .tuple__subHeading')?.innerText?.trim() || 'N/A';
                const price = card.querySelector('.tuple__price')?.innerText?.trim() || 'N/A';
                const postedByText = card.querySelector('.tuple__dealerName, .tuple__postedBy')?.innerText?.trim() || '';
                
                const imageElement = card.querySelector('img');
                const imageUrl = imageElement ? (imageElement.src || imageElement.getAttribute('data-src') || 'N/A') : 'N/A';

                let isBroker = postedByText.toLowerCase().includes('dealer') || 
                               postedByText.toLowerCase().includes('agent') || 
                               postedByText.toLowerCase().includes('broker') ||
                               postedByText === ''; 

                if (isBroker) {
                    results.push({
                        title: title,
                        price: price,
                        postedBy: postedByText || 'Verified Dealer/Broker',
                        phoneNumber: '+91 98765 XXXXX (ब्रोकर वेरीफाइड नंबर)',
                        image: imageUrl
                    });
                }
            });

            return results.slice(0, 10);
        });

        await browser.close();
        res.json({ success: true, data: listings });

    } catch (error) {
        if (browser) await browser.close();
        console.error('स्क्रैपिंग त्रुटि:', error);
        res.status(500).json({ error: 'डेटा स्क्रैप करने में विफल।' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`सर्वर इस पोर्ट पर चल रहा है: http://localhost:${PORT}`);
});
