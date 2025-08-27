import random
import math

firm_names = ["Alpha", "Beta"]
firm_positions = []
firm_prices = []

while len(firm_positions) < 2:
    try:
        firm_name = firm_names[len(firm_positions)]
        pos = float(input(f"Enter position for Firm {firm_name} (0-1) "))

        if 0 <= pos <= 1:
            firm_positions.append(pos)
        else:
            print("Positions must be between 0 and 1")
    except ValueError:
        print("Enter a valid number")

while len(firm_prices) < 2:
    try:
        firm_name = firm_names[len(firm_prices)]
        price = int(input(f"Enter price for Firm {firm_name} "))

        if 0 <= price:
            firm_prices.append(price)
        else:
            print("Enter a positive number ")
    except ValueError:
        print("Enter a valid number")

transport_cost = int(input("Transport Cost? "))
line_length = 1
num_simulations = int(input("Number of simulations? "))

while True:
    num_consumers = int(input("How many Consumers? "))
    if num_consumers > 0:
        break
    else:
        print("Enter a positive Number")

def consumer_choice(consumer_position, firm_positions, firm_prices, transport_cost):
    """Finds the firm with the lowest total cost for a given consumer, returns index of chosen firm"""
    costs = []
    for i in range(len(firm_positions)):
        distance = abs(consumer_position - firm_positions[i])
        total_cost = firm_prices[i] + (distance * transport_cost)
        costs.append(total_cost)
    return costs.index(min(costs))

def generate_consumers(num_consumers):
    """Populates a 0-1 number line with consumers along it."""
    consumers = []
    for i in range(num_consumers):
        position = random.uniform(0, 1)
        consumers.append(position)
    return consumers
consumers = generate_consumers(num_consumers)

def simulate_market(consumers, firm_positions, firm_prices, transport_cost):
    """Assigns consumers to firms based on their choice, populating the firm_customers list, assumes firms have no capacity restrictions."""
    firm_customers = [0] * len(firm_positions)

    for consumer_pos in consumers:
        chosen_firm = consumer_choice(consumer_pos, firm_positions, firm_prices, transport_cost)
        firm_customers[chosen_firm] += 1
    return firm_customers

def calculate_firm_profit(firm_positions, firm_prices, consumers, transport_cost):
    """Find firm profits (customers * Price) and assumes no production costs."""
    customers_per_firm = simulate_market(consumers, firm_positions, firm_prices, transport_cost)

    firm_profits = []
    for i in range(len(firm_positions)):
        profit = customers_per_firm[i] * firm_prices[i]
        firm_profits.append(profit)
    return firm_profits


def monte_carlo_optimization(existing_positions, existing_prices, consumers, transport_cost, num_simulations):
    """Finds the best position and price for a new entrant to the market."""
    best_profit = 0
    best_position = 0
    best_price = 0 

    for simulation in range(num_simulations):
        new_position = random.uniform(0, 1)
        new_price = random.uniform (5, 20)

        test_positions = existing_positions + [new_position]
        test_prices = existing_prices + [new_price]

        all_profits = calculate_firm_profit(test_positions, test_prices, consumers, transport_cost)
        new_firm_profit = all_profits[2]

        if new_firm_profit > best_profit:
            best_profit = new_firm_profit
            best_position = new_position
            best_price = new_price
    return best_position, best_price, best_profit



optimal_position, optimal_price, optimal_profit = monte_carlo_optimization(firm_positions, firm_prices, consumers, transport_cost, num_simulations)
final_positions = firm_positions + [optimal_position]
final_prices = firm_prices + [optimal_price] 

customers_per_firm = simulate_market(consumers, final_positions, final_prices, transport_cost)
firm_profit = calculate_firm_profit(final_positions, final_prices, consumers, transport_cost)

print(f"Optimal 3rd Firm Position: {optimal_position}")
print(f"Optimal 3rd Firm Price: {optimal_price}")
print(f"Optimal 3rd Firm Profit: {optimal_profit}")
print(f"Firm Alpha Profit: {firm_profit[0]}")
print(f"Firm Beta Profit: {firm_profit[1]}")
print(f"Firm Gamma Profit: {firm_profit[2]}")