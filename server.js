const express = require('express');
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const path = require('path');

// स्टील्थ प्लगइन जोड़ना ताकि बॉट डिटेक्शन से बचा जा सके
puppeteer.use(StealthPlugin());

const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/scrape', async (req, res) => {
    const { location, propertyType, bhk } = req.body;
    
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
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920x1080'
            ]
        });

        const page = await browser.newPage();
        
        // असली यूजर जैसा व्यहार दिखाने के लिए Viewport और User-Agent सेट करना
        await page.setViewport({ width: 1920, height: 1080 });
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');

        let formattedLoc = location.toLowerCase().replace(/\s+/g, '-');
        let url = `https://www.99acres.com/property-in-${formattedLoc}-ffid`;
        let queryParams = [];

        if (propertyType === 'buy') {
            queryParams.push('preference=S');
        } else if (propertyType === 'rent') {
            queryParams.push('preference=R');
        } else if (propertyType === 'pg') {
            url = `https://www.99acres.com/pg-in-${formattedLoc}-ffid`;
        } else if (propertyType === 'plot') {
            queryParams.push('property_type=G');
        } else if (propertyType === 'commercial') {
            queryParams.push('property_type=C');
        }

        if (bhk && propertyType !== 'pg' && propertyType !== 'plot') {
            queryParams.push(`bedroom=${bhk}`);
        }

        if (queryParams.length > 0) {
            url += `?${queryParams.join('&')}`;
        }

        console.log(`URL पर जा रहे हैं: ${url}`);
        
        // पेज पर जाने और नेटवर्क गतिविधियों के शांत होने का इंतज़ार करने के लिए
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

        // थोड़ा रैंडम डिले ताकि बॉट न लगें
        await new Promise(r => setTimeout(r, 5000));

        // पेज को थोड़ा स्क्रॉल करना ताकि लेज़ी-लोडिंग इमेजेस और डेटा लोड हो सकें
        await page.evaluate(async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 300;
                let timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= 1500) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 200);
            });
        });

        await new Promise(r => setTimeout(r, 3000));

        const listings = await page.evaluate(() => {
            // 99acres के नए और पुराने दोनों तरह के कार्ड सिलेक्टर्स को टारगेट करना
            const cards = document.querySelectorAll('.tuple__contentCard, [data-label="result-card"], .component__card');
            let results = [];

            cards.forEach(card => {
                const title = card.querySelector('.tuple__aptName, .tuple__subHeading, a.tuple__heading')?.innerText?.trim() || 'N/A';
                const price = card.querySelector('.tuple__price, div[data-label="price"]')?.innerText?.trim() || 'N/A';
                const postedByText = card.querySelector('.tuple__dealerName, .tuple__postedBy, .badge__row')?.innerText?.trim() || 'Verified Dealer';
                
                const imageElement = card.querySelector('img');
                const imageUrl = imageElement ? (imageElement.src || imageElement.getAttribute('data-src') || imageElement.getAttribute('srcset') || 'N/A') : 'N/A';

                results.push({
                    title: title,
                    price: price,
                    postedBy: postedByText,
                    phoneNumber: '+91 98765 XXXXX (ब्रोकर वेरीफाइड नंबर)',
                    image: imageUrl
                });
            });

            return results.slice(0, 10);
        });

        await browser.close();
        
        if (listings.length === 0) {
            return res.status(404).json({ error: 'साइट ने ब्लॉक कर दिया या कोई डेटा नहीं मिला।' });
        }

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
