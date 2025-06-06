from typing import Callable, Any, Sequence, Dict
from collections import Counter

_FLIGHT_CATEGORY_RANK = {"Black": 0, "Platinum": 1, "Gold": 2, "Normal": 3}

def by_category(p):
    print(f"Received passenger data type: {type(p)}, value: {p}")
    return _FLIGHT_CATEGORY_RANK[p["flightCategory"]]

# ---------------- Rule 2: hasConnections --------------------
def by_has_connections(p):
    return 0 if p["hasConnections"] else 1  # True -> 0 (ahead), False -> 1

# ---------------- Rule 3: reservation group size ------------
def build_group_size_map(passengers) -> Dict[str, int]:
    counts = Counter(p["reservationId"] for p in passengers)
    return counts

def by_group_size_factory(group_sizes: Dict[str, int]) -> Callable:
    # Return a closure that captures pre-computed counts
    def _rule(p):
        return -group_sizes[p["reservationId"]]   # negative => bigger first
    return _rule

# ---------------- Rule 4: checked baggage -------------------
def by_checked_baggage(p):
    return 0 if p["hasCheckedBaggage"] else 1

# ---------------- Rule 5: age (oldest first) ----------------
def by_age_desc(p):
    return -p["age"]                              # older (higher age) first

PriorityRule = Callable[[Any], Any]
# Define the default rules in priority order
DEFAULT_RULES: Sequence[PriorityRule] = (
    by_category,           # Rule 1: Flight category (Black > Platinum > Gold > Normal)
    by_has_connections,    # Rule 2: Connections (has connections first)
    by_checked_baggage,    # Rule 4: Baggage (has checked baggage first)
    by_age_desc,           # Rule 5: Age (oldest first)
    # Note: Rule 3 (group size) is added dynamically in sort_passengers
)

def sort_passengers(passengers, rules: Sequence[PriorityRule] = DEFAULT_RULES):
    """
    Return passengers sorted by *all* rules in order.
    The group size rule is special - it's calculated from the full passenger list.
    """
    # Calculate group sizes for rule 3
    group_sizes = build_group_size_map(passengers)
    by_group_size = by_group_size_factory(group_sizes)
    
    # Add the group size rule to the provided rules
    combined_rules = list(rules)
    # Insert group size rule after connections but before checked baggage
    # This keeps the order matching our rule numbering (assuming DEFAULT_RULES)
    if len(combined_rules) >= 2:  # If we have at least category and connections
        combined_rules.insert(2, by_group_size)
    else:
        combined_rules.append(by_group_size)
    
    def composite_key(p):
        return tuple(rule(p) for rule in combined_rules)
    return sorted(passengers, key=composite_key)
