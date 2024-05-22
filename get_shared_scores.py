def aggregate_rankings(rankings):
    all_rankings = {item: [] for item in items}
    for ranking in rankings.values():
        for item, rank in ranking.items():
            all_rankings[item].append(rank)
    
    aggregated_ranking = {item: int(np.median(ranks)) for item, ranks in all_rankings.items()}
    return aggregated_ranking

def save_shared_ranking(shared_ranking, filename):
    with open(filename, "w") as f:
        json.dump(shared_ranking, f, indent=4)

# Load individual rankings from JSON files
rankings = load_rankings()

# Simulate discussions among agents
rankings_after_discussion = simulate_discussion(rankings)

# Aggregate rankings using the democratic voting scheme (median of rankings)
shared_ranking = aggregate_rankings(rankings_after_discussion)

# Save the shared ranking to a JSON file
shared_ranking_filename = os.path.join(output_folder, "shared_ranking.json")
save_shared_ranking(shared_ranking, shared_ranking_filename)

print("Shared ranking saved to shared_ranking.json")
