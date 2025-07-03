class AirlineAnalyzer {
    constructor() {
        this.charts = {};
        this.initializeApp();
    }

    async initializeApp() {
        await this.loadCities();
        this.bindEvents();
    }

    async loadCities() {
        try {
            const response = await fetch('/api/cities');
            const cities = await response.json();
            
            const originSelect = document.getElementById('origin');
            const destinationSelect = document.getElementById('destination');
            
            cities.forEach(city => {
                const option1 = new Option(city, city);
                const option2 = new Option(city, city);
                originSelect.add(option1);
                destinationSelect.add(option2);
            });
        } catch (error) {
            console.error('Error loading cities:', error);
        }
    }

    bindEvents() {
        const analyzeBtn = document.getElementById('analyze-btn');
        analyzeBtn.addEventListener('click', () => this.analyzeData());
    }

    async analyzeData() {
        const origin = document.getElementById('origin').value;
        const destination = document.getElementById('destination').value;
        const daysBack = document.getElementById('days-back').value;

        this.showLoading();

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    origin: origin || null,
                    destination: destination || null,
                    days_back: daysBack
                })
            });

            const data = await response.json();
            this.displayResults(data);
        } catch (error) {
            console.error('Error analyzing data:', error);
            alert('Error analyzing data. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('results').classList.add('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    displayResults(data) {
        // Update summary cards
        document.getElementById('total-flights').textContent = data.total_flights;
        document.getElementById('avg-price').textContent = `$${data.avg_price}`;
        document.getElementById('price-range').textContent = data.price_range;

        // Display AI insights
        document.getElementById('ai-insights').textContent = data.ai_insights;

        // Create charts
        this.createRouteChart(data.popular_routes);
        this.createPriceChart(data.daily_prices);
        this.createAirlineChart(data.airline_share);
        this.createDemandChart(data.daily_demand);

        // Create tables
        this.createPopularRoutesTable(data.popular_routes);
        this.createPriceTrendsTable(data.price_trends);

        document.getElementById('results').classList.remove('hidden');
    }

    createRouteChart(routes) {
        const ctx = document.getElementById('routes-chart').getContext('2d');
        
        if (this.charts.routes) {
            this.charts.routes.destroy();
        }

        this.charts.routes = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: routes.slice(0, 10).map(route => route[0]),
                datasets: [{
                    label: 'Number of Flights',
                    data: routes.slice(0, 10).map(route => route[1]),
                    backgroundColor: 'rgba(52, 152, 219, 0.8)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createPriceChart(priceData) {
        const ctx = document.getElementById('price-chart').getContext('2d');
        
        if (this.charts.price) {
            this.charts.price.destroy();
        }

        this.charts.price = new Chart(ctx, {
            type: 'line',
            data: {
                labels: priceData.map(item => item.date_str),
                datasets: [{
                    label: 'Average Price ($)',
                    data: priceData.map(item => item.price),
                    borderColor: 'rgba(231, 76, 60, 1)',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createAirlineChart(airlineData) {
        const ctx = document.getElementById('airline-chart').getContext('2d');
        
        if (this.charts.airline) {
            this.charts.airline.destroy();
        }

        const colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)'
        ];

        this.charts.airline = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: airlineData.map(item => item[0]),
                datasets: [{
                    data: airlineData.map(item => item[1]),
                    backgroundColor: colors,
                    borderColor: colors.map(color => color.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createDemandChart(demandData) {
        const ctx = document.getElementById('demand-chart').getContext('2d');
        
        if (this.charts.demand) {
            this.charts.demand.destroy();
        }

        this.charts.demand = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: demandData.map(item => item.date_str),
                datasets: [{
                    label: 'Daily Flight Count',
                    data: demandData.map(item => item.flight_count),
                    backgroundColor: 'rgba(46, 204, 113, 0.8)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createPopularRoutesTable(routes) {
        const container = document.getElementById('popular-routes-table');
        
        let html = '<table class="data-table"><thead><tr><th>Route</th><th>Flight Count</th></tr></thead><tbody>';
        
        routes.slice(0, 10).forEach(route => {
            html += `<tr><td>${route[0]}</td><td>${route[1]}</td></tr>`;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
    }

    createPriceTrendsTable(priceData) {
        const container = document.getElementById('price-trends-table');
        
        let html = '<table class="data-table"><thead><tr><th>Route</th><th>Avg Price</th></tr></thead><tbody>';
        
        priceData.slice(0, 10).forEach(item => {
            html += `<tr><td>${item[0]}</td><td>$${item[1]}</td></tr>`;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AirlineAnalyzer();
});
