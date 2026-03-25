import sqlite3
import json

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wood Pellets Price Tracker</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7fa;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        header {
            background-color: #2c3e50;
            color: white;
            width: 100%;
            padding: 20px 0;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { margin: 0; font-size: 24px; }
        .container {
            width: 90%;
            max-width: 1000px;
            margin: 40px auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }
        .stat-card {
            background: #fdfdfd;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 20px;
            flex: 1;
            min-width: 200px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: transform 0.2s;
        }
        .stat-card:hover { transform: translateY(-2px); }
        .stat-title { font-size: 14px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px;}
        .stat-value { font-size: 32px; font-weight: bold; color: #2ecc71; margin-top: 10px;}
        .chart-container {
            position: relative;
            height: 50vh;
            width: 100%;
        }
    </style>
</head>
<body>

<header>
    <h1>Wood Pellets Price Tracker</h1>
</header>

<div class="container">
    <div class="stats">
        <div class="stat-card">
            <div class="stat-title">GABBY PLUS (BWT)</div>
            <div class="stat-value" id="gabbyplus-val">-- €</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">GABBY (BWT)</div>
            <div class="stat-value" id="gabby-val">-- €</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">Staļi</div>
            <div class="stat-value" id="stali-val">-- €</div>
        </div>
    </div>

    <div class="chart-container">
        <canvas id="priceChart"></canvas>
    </div>
</div>

<script>
    const chartData = {CHART_DATA};
    
    // Sort dates
    const allDates = new Set();
    Object.values(chartData).forEach(prodData => {
        Object.keys(prodData).forEach(date => allDates.add(date));
    });
    const dates = [...allDates].sort();
    
    const getProductDataMap = (key) => dates.map(d => chartData[key]?.[d] || null);
    
    const gabbyPlusData = getProductDataMap("BalticWoodTrade - GABBY PLUS");
    const gabbyData = getProductDataMap("BalticWoodTrade - GABBY");
    const staliData = getProductDataMap("Stali");

    // Because we just switched from single BalticWoodTrade to specific, map the old one to Gabby Plus if needed
    // or just let it be empty
    const oldBwtData = getProductDataMap("BalticWoodTrade");
    if(oldBwtData.some(d => d !== null)) {
        // Just fill Gabby Plus with old BWT data where missing
        for(let i = 0; i < dates.length; i++) {
            if(gabbyPlusData[i] === null && oldBwtData[i] !== null) {
                gabbyPlusData[i] = oldBwtData[i];
            }
        }
    }

    // Update Latest Values
    const lastGabbyPlus = gabbyPlusData.filter(v => v !== null).pop();
    const lastGabby = gabbyData.filter(v => v !== null).pop();
    const lastStali = staliData.filter(v => v !== null).pop();
    
    if(lastGabbyPlus) document.getElementById('gabbyplus-val').innerText = lastGabbyPlus + ' €';
    if(lastGabby) document.getElementById('gabby-val').innerText = lastGabby + ' €';
    if(lastStali) document.getElementById('stali-val').innerText = lastStali + ' €';

    const ctx = document.getElementById('priceChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'GABBY PLUS (BWT)',
                    data: gabbyPlusData,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#3498db',
                    pointRadius: 5,
                    fill: false,
                    tension: 0.3,
                    spanGaps: true
                },
                {
                    label: 'GABBY (BWT)',
                    data: gabbyData,
                    borderColor: '#f1c40f',
                    backgroundColor: 'rgba(241, 196, 15, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#f1c40f',
                    pointRadius: 5,
                    fill: false,
                    tension: 0.3,
                    spanGaps: true
                },
                {
                    label: 'Staļi',
                    data: staliData,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#e74c3c',
                    pointRadius: 5,
                    fill: false,
                    tension: 0.3,
                    spanGaps: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + ' €';
                        }
                    }
                },
                legend: {
                    labels: { font: { size: 14 } }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: { display: true, text: 'Price (€)' },
                    grid: { color: '#ecf0f1' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
</script>

</body>
</html>
"""

def generate():
    print("Generating dashboard...")
    conn = sqlite3.connect("prices.db")
    c = conn.cursor()
    
    data = {}
    
    try:
        # Group by date and website to get the latest (or min/avg) for each day
        c.execute("SELECT date, website, MIN(price) FROM prices GROUP BY date, website")
        rows = c.fetchall()
        for row in rows:
            date, website, price = row
            if website not in data:
                data[website] = {}
            data[website][date] = price
    except sqlite3.OperationalError:
        pass # table might not exist
        
    conn.close()
    
    html_content = HTML_TEMPLATE.replace("{CHART_DATA}", json.dumps(data))
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Dashboard generated at index.html")

if __name__ == "__main__":
    generate()
