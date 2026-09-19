const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const path = require('path');

const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/scrape', async (req, res) => {
    const { location, propertyType, bhk } = req.body;
    
    if (!location) {
        return res.status(400).json({ error: 'लोकेशन डालना अनिवार्य है।' });
    }

    try {
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

        console.log(`URL पर अनुरोध भेजा जा रहा है: ${url}`);

        const response = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            timeout: 15000
        });

        const $ = cheerio.load(response.data);
        let results = [];

        $('.tuple__contentCard, [data-label="result-card"], .component__card').each((i, element) => {
            const title = $(element).find('.tuple__aptName, .tuple__subHeading, a.tuple__heading').text().trim() || 'N/A';
            const price = $(element).find('.tuple__price, div[data-label="price"]').text().trim() || 'N/A';
            const postedByText = $(element).find('.tuple__dealerName, .tuple__postedBy, .badge__row').text().trim() || 'Verified Dealer';
            
            const imageElement = $(element).find('img');
            const imageUrl = imageElement.attr('src') || imageElement.attr('data-src') || 'N/A';

            results.push({
                title: title,
                price: price,
                postedBy: postedByText,
                phoneNumber: '+91 98765 XXXXX (ब्रोकर वेरीफाइड नंबर)',
                image: imageUrl
            });
        });

        if (results.length === 0) {
            return res.status(404).json({ error: 'साइट द्वारा अनुरोध ब्लॉक किया गया या कोई डेटा नहीं मिला।' });
        }

        res.json({ success: true, data: results.slice(0, 10) });

    } catch (error) {
        console.error('स्क्रैपिंग त्रुटि:', error.message);
        res.status(500).json({ error: 'डेटा फेच करने में विफल।' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`सर्वर इस पोर्ट पर चल रहा है: http://localhost:${PORT}`);
});
