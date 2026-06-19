from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)

# Global variables for the model
cosine_sim = None
player_names = None
player_info = None

def load_data():
    global cosine_sim, player_names, player_info
    try:
        with open('similarity_model.pkl', 'rb') as f:
            data = pickle.load(f)
            cosine_sim = data['cosine_sim']
            player_names = data['player_names']
            
        player_info = pd.read_csv('player_info.csv')
        player_info['search_name'] = player_info['Player'].str.lower()
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '').lower()
    if not query or player_info is None:
        return jsonify([])
    
    # Simple search
    matches = player_info[player_info['search_name'].str.contains(query, na=False)]
    
    # Return top 10 matches
    results = []
    for _, row in matches.head(10).iterrows():
        results.append({
            'name': row['Player'],
            'squad': row['Squad'],
            'pos': row['Pos']
        })
        
    return jsonify(results)

@app.route('/api/recommend')
def recommend():
    player_name = request.args.get('player')
    if not player_name or player_names is None or cosine_sim is None:
        return jsonify({'error': 'Missing player name or model not loaded'})
    
    # Find player index
    try:
        idx = np.where(player_names == player_name)[0][0]
    except IndexError:
        return jsonify({'error': 'Player not found'})
    
    # Get similarity scores
    scores = list(enumerate(cosine_sim[idx]))
    
    # Sort and get top 5 (excluding self)
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]
    
    recommendations = []
    for i, score in scores:
        rec_name = player_names[i]
        rec_info = player_info[player_info['Player'] == rec_name].iloc[0]
        recommendations.append({
            'name': rec_name,
            'similarity': round(float(score) * 100, 2),
            'squad': rec_info['Squad'],
            'league': rec_info['League'],
            'pos': rec_info['Pos']
        })
        
    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    load_data()
    app.run(debug=True, port=5000)
