from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
import pandas as pd
import os

try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False

app = Flask(__name__)

# Initialize OpenAI client if available and API key is set
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = None
if openai_available and OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

class AirlineDataAnalyzer:
    def __init__(self):
        self.aviation_api_key = os.getenv('AVIATION_API_KEY', 'demo-key')
        self.base_url = "http://api.aviationstack.com/v1"
        
    def fetch_flight_data(self, origin=None, destination=None, days_back=30):
        """Fetch flight data from aviation API"""
        try:
            # For demo purposes, we'll simulate data since free APIs have limitations
            # In production, you'd use: requests.get(f"{self.base_url}/flights", params=params)
            
            # Simulate realistic flight data
            sample_data = self.generate_sample_data(origin, destination, days_back)
            return sample_data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return self.generate_sample_data(origin, destination, days_back)
    
    def generate_sample_data(self, origin=None, destination=None, days_back=30):
        """Generate realistic sample flight data for demonstration"""
        routes = [
            ("Sydney", "Melbourne", 250, 400),
            ("Melbourne", "Brisbane", 180, 350),
            ("Brisbane", "Perth", 300, 500),
            ("Sydney", "Brisbane", 200, 380),
            ("Melbourne", "Perth", 280, 480),
            ("Adelaide", "Sydney", 220, 420),
            ("Perth", "Sydney", 350, 550),
            ("Brisbane", "Adelaide", 200, 380),
            ("Sydney", "Perth", 400, 600),
            ("Melbourne", "Adelaide", 150, 280)
        ]
        
        flights = []
        for i in range(200):  # Generate 200 sample flights
            route = routes[i % len(routes)]
            base_date = datetime.now() - timedelta(days=days_back)
            flight_date = base_date + timedelta(days=(i % days_back))
            
            # Add some price variation based on day of week and demand
            price_multiplier = 1.0
            if flight_date.weekday() in [4, 5, 6]:  # Weekend
                price_multiplier = 1.3
            if flight_date.day in [1, 15]:  # Peak travel days
                price_multiplier *= 1.2
                
            flights.append({
                'origin': route[0],
                'destination': route[1],
                'price': int(route[2] * price_multiplier),
                'max_price': int(route[3] * price_multiplier),
                'date': flight_date.strftime('%Y-%m-%d'),
                'airline': ['Jetstar', 'Virgin Australia', 'Qantas', 'Tigerair'][i % 4],
                'duration': f"{2 + (i % 4)}h {30 + (i % 30)}m"
            })
        
        # Filter by origin/destination if specified
        if origin:
            flights = [f for f in flights if f['origin'].lower() == origin.lower()]
        if destination:
            flights = [f for f in flights if f['destination'].lower() == destination.lower()]
            
        return flights
    
    def analyze_trends(self, flights):
        """Analyze flight data for trends and insights"""
        if not flights:
            # Return default values if no flights found
            return {
                'popular_routes': [],
                'price_trends': [],
                'daily_prices': [],
                'airline_share': [],
                'daily_demand': [],
                'total_flights': 0,
                'avg_price': 0,
                'price_range': "$0 - $0"
            }
        df = pd.DataFrame(flights)
        df['date'] = pd.to_datetime(df['date'])
        
        # Popular routes
        route_counts = df.groupby(['origin', 'destination']).size().sort_values(ascending=False)
        popular_routes = [(f"{route[0]} → {route[1]}", count) for route, count in route_counts.head(10).items()]
        
        # Average prices by route
        avg_prices = df.groupby(['origin', 'destination'])['price'].mean().sort_values(ascending=False)
        price_trends = [(f"{route[0]} → {route[1]}", round(price, 2)) for route, price in avg_prices.head(10).items()]
        
        # Price trends over time
        daily_prices = df.groupby('date')['price'].mean().reset_index()
        daily_prices['date_str'] = daily_prices['date'].dt.strftime('%Y-%m-%d')
        
        # Airline market share
        airline_counts = df['airline'].value_counts()
        airline_share = [(airline, count) for airline, count in airline_counts.items()]
        
        # High demand periods (by flight count)
        daily_demand = df.groupby('date').size().reset_index(name='flight_count')
        daily_demand['date_str'] = daily_demand['date'].dt.strftime('%Y-%m-%d')
        
        return {
            'popular_routes': popular_routes,
            'price_trends': price_trends,
            'daily_prices': daily_prices[['date_str', 'price']].to_dict('records'),
            'airline_share': airline_share,
            'daily_demand': daily_demand[['date_str', 'flight_count']].to_dict('records'),
            'total_flights': len(flights),
            'avg_price': round(df['price'].mean(), 2),
            'price_range': f"${df['price'].min()} - ${df['price'].max()}"
        }
    
    def get_ai_insights(self, analysis_data):
        """Use OpenAI to generate insights from the flight data"""
        if not client:
            return "AI analysis unavailable: OpenAI API key not set or openai package not installed."
        try:
            prompt = f"""
            Analyze this airline booking market data and provide key insights:
            
            Data Summary:
            - Total flights analyzed: {analysis_data.get('total_flights', 0)}
            - Average price: ${analysis_data.get('avg_price', 0)}
            - Price range: {analysis_data.get('price_range', 'N/A')}
            - Top routes: {analysis_data.get('popular_routes', [])[:5]}
            - Airlines: {analysis_data.get('airline_share', [])[:3]}
            
            Please provide:
            1. Market demand trends
            2. Pricing insights
            3. Route popularity analysis
            4. Recommendations for hostel businesses
            
            Keep the response concise and actionable.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"AI analysis unavailable: {str(e)}. Please check your OpenAI API configuration."

analyzer = AirlineDataAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    try:
        data = request.json
        origin = data.get('origin')
        destination = data.get('destination')
        days_back = int(data.get('days_back', 30))
        flights = analyzer.fetch_flight_data(origin, destination, days_back)
        analysis = analyzer.analyze_trends(flights)
        ai_insights = analyzer.get_ai_insights(analysis)
        analysis['ai_insights'] = ai_insights
        return jsonify(analysis)
    except Exception as e:
        print(f"Error in /api/analyze: {e}")
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

@app.route('/api/cities')
def get_cities():
    """Return list of available cities"""
    cities = [
        "Sydney", "Melbourne", "Brisbane", "Perth", 
        "Adelaide", "Darwin", "Hobart", "Canberra"
    ]
    return jsonify(cities)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
