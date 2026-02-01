from flask import Blueprint, jsonify, render_template, request, session
import math
import random

trucking_bp = Blueprint('trucking', __name__)

player = {
    "money": 2000,
    "day": 1,
    "driver_wage": 50,
    "game_over": False,
    "ending": None,
    "fleet": [
        {
            "truckId": 1,
            "type": "small",
            "location": "Louisville",
            "status": "idle",
            "destination": None,
            "days_remaining": 0,
            "current_job": None
        }
    ]
}

truckInfo = {
    "small": {"price": 1000, "mpg": 15, "tank": 150},
    "big": {"price": 3000, "mpg": 7, "tank": 300}
}

gasRate = 3.5
daily_speed = 400

# routes data structure remains exactly as provided in the previous message
# constants for route calculation
smallTrucksMPG = 15
bigTrucksMPG = 7
gasRate = 3.5
bigTruckMultiplier = 1.5

routes = { 
    "Louisville": [ 
        {"to": "Cincinnati", "description": "Cincinnati Celery Co. needs a truckload of celery", "distance": 105, "due": 2, "size": "small", "cost": (105 / smallTrucksMPG) * gasRate, "payout": 100}, 
        {"to": "Indianapolis", "description": "Indianapolis Ink, Inc. needs a truckload of ballpoint pens", "distance": 114, "due": 2, "size": "small", "cost": (114 / smallTrucksMPG) * gasRate, "payout": 110}, 
        {"to": "Saint Louis", "description": "Saint Louis Logging Service needs a truckload of chainsaws", "distance": 260, "due": 2, "size": "small", "cost": (260 / smallTrucksMPG) * gasRate, "payout": 240}, 
    ], 
    "Cincinnati": [ 
        {"to": "Pittsburgh", "description": "Pittsburgh Pitchery needs a truckload of glass pitchers", "distance": 289, "due": 2, "size": "big", "cost": (289 / bigTrucksMPG) * gasRate, "payout": 290}, 
        {"to": "Indianapolis", "description": "Indianapolis Ink, Inc. needs a truckload of ballpoint pens", "distance": 112, "due": 2, "size": "small", "cost": (112 / smallTrucksMPG) * gasRate, "payout": 110}, 
        {"to": "Louisville", "description": "Louisville Landscaping needs a truckload of lawnmowers", "distance": 105, "due": 2, "size": "small", "cost": (105 / smallTrucksMPG) * gasRate, "payout": 100}, 
    ], 
    "Indianapolis": [ 
        {"to": "Saint Louis", "description": "Saint Louis Logging Service needs a truckload of chainsaws", "distance": 248, "due": 2, "size": "small", "cost": (248 / smallTrucksMPG) * gasRate, "payout": 235}, 
        {"to": "Chicago", "description": "Chicago Shrimp Shack needs a truckload of shrimp", "distance": 183, "due": 2, "size": "small", "cost": (183 / smallTrucksMPG) * gasRate, "payout": 175}, 
        {"to": "Pittsburgh", "description": "Pittsburgh Pitchery needs glass pitchers", "distance": 360, "due": 2, "size": "small", "cost": (360 / smallTrucksMPG) * gasRate, "payout": 340}, 
    ], 
    "Saint Louis": [ 
        {"to": "Chicago", "description": "Chicago Shrimp Shack needs a truckload of shrimp", "distance": 300, "due": 2, "size": "small", "cost": (300 / smallTrucksMPG) * gasRate, "payout": 280}, 
        {"to": "Nashville", "description": "Nashville Guitar Industries needs guitars", "distance": 300, "due": 2, "size": "small", "cost": (300 / smallTrucksMPG) * gasRate, "payout": 285}, 
        {"to": "Dallas", "description": "Dallas Door Depot needs doorknobs", "distance": 660, "due": 3, "size": "big", "cost": (660 / bigTrucksMPG) * gasRate, "payout": 620 * bigTruckMultiplier}, 
    ], 
    "Chicago": [ 
        {"to": "Denver", "description": "Denver Drapes needs curtains", "distance": 1000, "due": 4, "size": "big", "cost": (1000 / bigTrucksMPG) * gasRate, "payout": 950 * bigTruckMultiplier}, 
        {"to": "Washington, D.C.", "description": "Capitol Caps needs hats", "distance": 710, "due": 3, "size": "big", "cost": (710 / bigTrucksMPG) * gasRate, "payout": 680 * bigTruckMultiplier}, 
        {"to": "Detroit", "description": "Detroit Drum Dealer needs drums", "distance": 283, "due": 2, "size": "small", "cost": (283 / smallTrucksMPG) * gasRate, "payout": 270}, 
    ], 
    "Pittsburgh": [ 
        {"to": "Philadelphia", "description": "Phili Food Mart needs shopping carts", "distance": 305, "due": 2, "size": "small", "cost": (305 / smallTrucksMPG) * gasRate, "payout": 290}, 
        {"to": "New York City", "description": "New York Apple Co. Needs apples", "distance": 370, "due": 2, "size": "big", "cost": (370 / bigTrucksMPG) * gasRate, "payout": 350 * bigTruckMultiplier}, 
        {"to": "Washington, D.C.", "description": "Capitol Caps needs hats", "distance": 250, "due": 2, "size": "big", "cost": (250 / bigTrucksMPG) * gasRate, "payout": 240 * bigTruckMultiplier}, 
    ], 
    "Nashville": [ 
        {"to": "Atlanta", "description": "Atlanta Acrylics needs paint", "distance": 250, "due": 2, "size": "big", "cost": (250 / bigTrucksMPG) * gasRate, "payout": 230 * bigTruckMultiplier}, 
        {"to": "New Orleans", "description": "New Orleans Oysters needs oysters", "distance": 530, "due": 3, "size": "small", "cost": (530 / smallTrucksMPG) * gasRate, "payout": 500}, 
        {"to": "Houston", "description": "Houston Hanger Manufacturing needs hangers", "distance": 800, "due": 4, "size": "big", "cost": (800 / bigTrucksMPG) * gasRate, "payout": 760 * bigTruckMultiplier}, 
    ], 
    "Dallas": [ 
        {"to": "Houston", "description": "Houston Hanger Manufacturing needs hangers", "distance": 240, "due": 2, "size": "small", "cost": (240 / smallTrucksMPG) * gasRate, "payout": 220}, 
        {"to": "Phoenix", "description": "Phoenix Fashion needs cloth", "distance": 1060, "due": 4, "size": "big", "cost": (1060 / bigTrucksMPG) * gasRate, "payout": 1000 * bigTruckMultiplier}, 
        {"to": "New Orleans", "description": "New Orleans Oysters needs oysters", "distance": 500, "due": 3, "size": "small", "cost": (500 / smallTrucksMPG) * gasRate, "payout": 480}, 
    ], 
    "Denver": [ 
        {"to": "Portland", "description": "Portland Pizza Parlor needs pepperoni", "distance": 1300, "due": 5, "size": "big", "cost": (1300 / bigTrucksMPG) * gasRate, "payout": 1250 * bigTruckMultiplier}, 
        {"to": "Chicago", "description": "Chicago Shrimp Shack needs shrimp", "distance": 1000, "due": 4, "size": "big", "cost": (1000 / bigTrucksMPG) * gasRate, "payout": 950 * bigTruckMultiplier}, 
        {"to": "Phoenix", "description": "Phoenix Fashion needs cloth", "distance": 830, "due": 4, "size": "big", "cost": (830 / bigTrucksMPG) * gasRate, "payout": 800 * bigTruckMultiplier}, 
    ], 
    "Washington, D.C.": [ 
        {"to": "Philadelphia", "description": "Phili Food Mart needs shopping carts", "distance": 140, "due": 2, "size": "small", "cost": (140 / smallTrucksMPG) * gasRate, "payout": 130}, 
        {"to": "Charlotte", "description": "Charlotte Shears needs metal", "distance": 400, "due": 2, "size": "big", "cost": (400 / bigTrucksMPG) * gasRate, "payout": 380 * bigTruckMultiplier}, 
        {"to": "New York City", "description": "New York Apple Co. Needs apples", "distance": 225, "due": 2, "size": "big", "cost": (225 / bigTrucksMPG) * gasRate, "payout": 210 * bigTruckMultiplier}, 
    ], 
    "Detroit": [ 
        {"to": "Chicago", "description": "Chicago Shrimp Shack needs a truckload of shrimp", "distance": 237, "due": 2, "size": "small", "cost": (237 / smallTrucksMPG) * gasRate, "payout": 230}, 
        {"to": "Cincinnati", "description": "Cincinnati Celery Co. needs a truckload of celery", "distance": 260, "due": 2, "size": "small", "cost": (260 / smallTrucksMPG) * gasRate, "payout": 250}, 
        {"to": "Pittsburgh", "description": "Pittsburgh Pitchery needs glass pitchers", "distance": 285, "due": 2, "size": "small", "cost": (285 / smallTrucksMPG) * gasRate, "payout": 270}, 
    ], 
    "Philadelphia": [ 
        {"to": "New York City", "description": "New York Apple Co. Needs apples", "distance": 95, "due": 2, "size": "small", "cost": (95 / smallTrucksMPG) * gasRate, "payout": 90}, 
        {"to": "Washington, D.C.", "description": "Capitol Caps needs hats", "distance": 140, "due": 2, "size": "small", "cost": (140 / smallTrucksMPG) * gasRate, "payout": 135}, 
        {"to": "Charlotte", "description": "Charlotte Shears needs metal", "distance": 540, "due": 3, "size": "big", "cost": (540 / bigTrucksMPG) * gasRate, "payout": 510 * bigTruckMultiplier}, 
    ], 
    "New York City": [ 
        {"to": "Washington, D.C.", "description": "Capitol Caps needs hats", "distance": 225, "due": 2, "size": "big", "cost": (225 / bigTrucksMPG) * gasRate, "payout": 215 * bigTruckMultiplier}, 
        {"to": "Chicago", "description": "Chicago Shrimp Shack needs shrimp", "distance": 790, "due": 3, "size": "big", "cost": (790 / bigTrucksMPG) * gasRate, "payout": 750 * bigTruckMultiplier}, 
        {"to": "Philadelphia", "description": "Phili Food Mart needs shopping carts", "distance": 95, "due": 2, "size": "small", "cost": (95 / smallTrucksMPG) * gasRate, "payout": 90}, 
    ], 
    "Atlanta": [ 
        {"to": "Miami", "description": "Miami Meat Packaging needs meat", "distance": 660, "due": 3, "size": "big", "cost": (660 / bigTrucksMPG) * gasRate, "payout": 630 * bigTruckMultiplier}, 
        {"to": "New Orleans", "description": "New Orleans Oysters needs oysters", "distance": 470, "due": 3, "size": "big", "cost": (470 / bigTrucksMPG) * gasRate, "payout": 450 * bigTruckMultiplier}, 
        {"to": "Nashville", "description": "Nashville Guitar Industries needs guitars", "distance": 250, "due": 2, "size": "small", "cost": (250 / smallTrucksMPG) * gasRate, "payout": 240}, 
    ], 
    "New Orleans": [ 
        {"to": "Houston", "description": "Houston Hanger Manufacturing needs hangers", "distance": 350, "due": 2, "size": "small", "cost": (350 / smallTrucksMPG) * gasRate, "payout": 330}, 
        {"to": "Dallas", "description": "Dallas Door Depot needs doorknobs", "distance": 510, "due": 3, "size": "big", "cost": (510 / bigTrucksMPG) * gasRate, "payout": 480 * bigTruckMultiplier}, 
        {"to": "Miami", "description": "Miami Meat Packaging needs meat", "distance": 860, "due": 4, "size": "big", "cost": (860 / bigTrucksMPG) * gasRate, "payout": 820 * bigTruckMultiplier}, 
    ], 
    "Houston": [ 
        {"to": "Dallas", "description": "Dallas Door Depot needs doorknobs", "distance": 240, "due": 2, "size": "small", "cost": (240 / smallTrucksMPG) * gasRate, "payout": 230}, 
        {"to": "New Orleans", "description": "New Orleans Oysters needs oysters", "distance": 350, "due": 2, "size": "big", "cost": (350 / bigTrucksMPG) * gasRate, "payout": 330 * bigTruckMultiplier}, 
        {"to": "Phoenix", "description": "Phoenix Fashion needs cloth", "distance": 1170, "due": 4, "size": "big", "cost": (1170 / bigTrucksMPG) * gasRate, "payout": 1100 * bigTruckMultiplier}, 
    ], 
    "Phoenix": [ 
        {"to": "Los Angeles", "description": "L.A. Chargers needs cables", "distance": 370, "due": 2, "size": "big", "cost": (370 / bigTrucksMPG) * gasRate, "payout": 350 * bigTruckMultiplier}, 
        {"to": "Denver", "description": "Denver Drapes needs curtains", "distance": 830, "due": 4, "size": "big", "cost": (830 / bigTrucksMPG) * gasRate, "payout": 790 * bigTruckMultiplier}, 
        {"to": "Dallas", "description": "Dallas Door Depot needs doorknobs", "distance": 1060, "due": 4, "size": "big", "cost": (1060 / bigTrucksMPG) * gasRate, "payout": 1000 * bigTruckMultiplier}, 
    ], 
    "Portland": [ 
        {"to": "Seattle", "description": "Seattle Salmon Seller needs knives", "distance": 174, "due": 2, "size": "small", "cost": (174 / smallTrucksMPG) * gasRate, "payout": 165}, 
        {"to": "San Francisco", "description": "San Francisco Slime Factory needs glitter", "distance": 635, "due": 3, "size": "big", "cost": (635 / bigTrucksMPG) * gasRate, "payout": 600 * bigTruckMultiplier}, 
        {"to": "Denver", "description": "Denver Drapes needs curtains", "distance": 1300, "due": 5, "size": "big", "cost": (1300 / bigTrucksMPG) * gasRate, "payout": 1240 * bigTruckMultiplier}, 
    ], 
    "Charlotte": [ 
        {"to": "Atlanta", "description": "Atlanta Acrylics needs paint", "distance": 245, "due": 2, "size": "big", "cost": (245 / bigTrucksMPG) * gasRate, "payout": 230 * bigTruckMultiplier}, 
        {"to": "Washington, D.C.", "description": "Capitol Caps needs hats", "distance": 400, "due": 2, "size": "big", "cost": (400 / bigTrucksMPG) * gasRate, "payout": 380 * bigTruckMultiplier}, 
        {"to": "Louisville", "description": "Louisville Landscaping needs lawnmowers", "distance": 470, "due": 3, "size": "big", "cost": (470 / bigTrucksMPG) * gasRate, "payout": 450 * bigTruckMultiplier}, 
    ], 
    "Miami": [ 
        {"to": "Atlanta", "description": "Atlanta Acrylics needs paint", "distance": 660, "due": 3, "size": "big", "cost": (660 / bigTrucksMPG) * gasRate, "payout": 620 * bigTruckMultiplier}, 
        {"to": "New Orleans", "description": "New Orleans Oysters needs oysters", "distance": 860, "due": 4, "size": "big", "cost": (860 / bigTrucksMPG) * gasRate, "payout": 810 * bigTruckMultiplier}, 
        {"to": "Charlotte", "description": "Charlotte Shears needs metal", "distance": 700, "due": 3, "size": "big", "cost": (700 / bigTrucksMPG) * gasRate, "payout": 670 * bigTruckMultiplier}, 
    ], 
    "Los Angeles": [ 
        {"to": "San Francisco", "description": "San Francisco Slime Factory needs glitter", "distance": 380, "due": 2, "size": "big", "cost": (380 / bigTrucksMPG) * gasRate, "payout": 360 * bigTruckMultiplier}, 
        {"to": "Phoenix", "description": "Phoenix Fashion needs cloth", "distance": 370, "due": 2, "size": "big", "cost": (370 / bigTrucksMPG) * gasRate, "payout": 350 * bigTruckMultiplier}, 
        {"to": "Portland", "description": "Portland Pizza Parlor needs pepperoni", "distance": 960, "due": 4, "size": "big", "cost": (960 / bigTrucksMPG) * gasRate, "payout": 910 * bigTruckMultiplier}, 
    ], 
    "Seattle": [ 
        {"to": "Portland", "description": "Portland Pizza Parlor needs pepperoni", "distance": 174, "due": 2, "size": "small", "cost": (174 / smallTrucksMPG) * gasRate, "payout": 165}, 
        {"to": "San Francisco", "description": "San Francisco Slime Factory needs glitter", "distance": 807, "due": 4, "size": "big", "cost": (807 / bigTrucksMPG) * gasRate, "payout": 760 * bigTruckMultiplier}, 
        {"to": "Denver", "description": "Denver Drapes needs curtains", "distance": 1300, "due": 5, "size": "big", "cost": (1300 / bigTrucksMPG) * gasRate, "payout": 1230 * bigTruckMultiplier}, 
        {"to": "Chicago", "description": "Chicago Shrimp Shack needs shrimp", "distance": 2060, "due": 7, "size": "big", "cost": (2060 / bigTrucksMPG) * gasRate, "payout": 1950 * bigTruckMultiplier}, 
    ], 
    "San Francisco": [ 
        {"to": "Los Angeles", "description": "L.A. Chargers needs cables", "distance": 380, "due": 2, "size": "big", "cost": (380 / bigTrucksMPG) * gasRate, "payout": 360 * bigTruckMultiplier}, 
        {"to": "Portland", "description": "Portland Pizza Parlor needs pepperoni", "distance": 635, "due": 3, "size": "big", "cost": (635 / bigTrucksMPG) * gasRate, "payout": 600 * bigTruckMultiplier}, 
        {"to": "Denver", "description": "Denver Drapes needs curtains", "distance": 1250, "due": 5, "size": "big", "cost": (1250 / bigTrucksMPG) * gasRate, "payout": 1180 * bigTruckMultiplier}, 
    ] 
}

@trucking_bp.route('/')
def interface():
    return render_template('trucking.html', player=player, routes=routes)

@trucking_bp.route('/move', methods=['POST'])
def move_truck():
    data = request.json
    truck_id = data.get('truckId')
    destination = data.get('to')
    target_truck = next((t for t in player['fleet'] if t['truckId'] == truck_id), None)
    if target_truck and target_truck['status'] == 'idle':
        origin = target_truck['location']
        route = next((r for r in routes.get(origin, []) if r['to'] == destination), None)
        if route:
            current_job = route.copy()
            current_job['final_deadline'] = player['day'] + route['due']
            distance = route['distance']
            travel_days = math.ceil(distance / daily_speed)
            target_truck['status'] = 'moving'
            target_truck['destination'] = destination
            target_truck['days_remaining'] = travel_days
            target_truck['current_job'] = current_job
            return jsonify({"status": "success", "destination": destination})
    return jsonify({"status": "error"}), 400

@trucking_bp.route('/next_day', methods=['POST'])
def next_day():
    if player['game_over']:
        return jsonify({"status": "game_over"})

    player['day'] += 1
    daily_report = []
    total_revenue = 0
    total_wage_cost = 0
    total_fuel_cost = 0
    
    wage_factor = player['driver_wage']
    quit_chance = max(0, (80 - wage_factor) / 1000)
    breakdown_chance = max(0, (80 - wage_factor) / 500)
    trucks_to_remove = []

    for truck in player['fleet']:
        wage_expense = player['driver_wage']
        player['money'] -= wage_expense
        total_wage_cost += wage_expense
        daily_report.append(f"Truck #{truck['truckId']}: Paid driver ${wage_expense}")

        if random.random() < quit_chance:
            trucks_to_remove.append(truck)
            daily_report.append(f"CRITICAL: Driver of Truck #{truck['truckId']} quit! Truck lost.")
            continue

        if truck['status'] == 'moving':
            if random.random() < breakdown_chance:
                truck['days_remaining'] += 1
                daily_report.append(f"DELAY: Truck #{truck['truckId']} broke down. +1 day travel.")
            else:
                truck['days_remaining'] -= 1

            if truck['days_remaining'] <= 0:
                job = truck['current_job']
                mpg = truckInfo[truck['type']]['mpg']
                fuel_cost = (job['distance'] / mpg) * gasRate
                player['money'] -= fuel_cost
                total_fuel_cost += fuel_cost
                payout = job['payout']
                if truck['type'] == 'big':
                    payout = payout * 1.5 if job['distance'] > 300 else payout * 0.8
                
                if player['day'] > job['final_deadline']:
                    payout = 0
                    daily_report.append(f"Truck #{truck['truckId']} LATE. Payout forfeited.")
                else:
                    daily_report.append(f"Truck #{truck['truckId']} arrived. Revenue: ${payout:.2f}")

                player['money'] += payout
                total_revenue += payout
                truck['location'] = truck['destination']
                truck['status'] = 'idle'
                truck['destination'] = None
                truck['current_job'] = None
    
    for t in trucks_to_remove:
        player['fleet'].remove(t)

    # ENDING LOGIC
    if player['money'] < 0:
        player['game_over'] = True
        player['ending'] = "BAD: You went bankrupt. Your trucks were taken and your business collapsed."
    elif player['money'] >= 15000:
        player['game_over'] = True
        player['ending'] = "GOOD: You've dominated the market! With $15,000 in the bank, you're the king of the roads."
    elif player['day'] > 31:
        player['game_over'] = True
        player['ending'] = "MEDIUM: A full month has passed. Your steady business survived."

    return jsonify({
        "status": "success",
        "day": player['day'],
        "money": player['money'],
        "report": daily_report,
        "revenue": total_revenue,
        "wage_cost": total_wage_cost,
        "fuel_cost": total_fuel_cost,
        "net": total_revenue - (total_wage_cost + total_fuel_cost),
        "game_over": player['game_over'],
        "ending_text": player['ending']
    })

@trucking_bp.route('/purchase/<truck_type>', methods=['POST'])
def purchase_truck(truck_type):
    selection = truckInfo.get(truck_type)
    if selection and player["money"] >= selection["price"]:
        player["money"] -= selection["price"]
        player["fleet"].append({
            "truckId": len(player["fleet"]) + 1,
            "type": truck_type, "location": "Louisville",
            "status": "idle", "destination": None, "days_remaining": 0, "current_job": None
        })
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400
@trucking_bp.route('/trucking/reset', methods=['POST'])
def reset_game():
    session.clear() # This wipes all player data, money, and fleet
    return jsonify({"status": "success", "message": "Game data wiped."})
@trucking_bp.route('/set_wage', methods=['POST'])
def set_wage():
    data = request.json
    player['driver_wage'] = int(data.get('wage', 50))
    return jsonify({"status": "success"})