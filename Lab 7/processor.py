
def parse_walk_schedule(schedule_spec):
    if not isinstance(schedule_spec, str):
        return "Invalid walk schedule"

    try:
        parts = schedule_spec.strip().split('-')

        if len(parts) != 3:
            return "Invalid walk schedule"

        pets_str, mins_str, weekend_str = parts

        pets = int(pets_str)
        mins = int(mins_str)

        if pets <= 0 or mins <= 0:
            return "Invalid walk schedule"

        weekend_map = {"YES": 15.0, "NO": 0.0}
        weekend_code = weekend_str.strip().upper()

        if weekend_code not in weekend_map:
            return "Invalid walk schedule"

        weekend_fee = weekend_map[weekend_code]
        base_fee = 20.0 if mins <= 30 else 35.0
        total = base_fee + (pets * 5.0) + weekend_fee

        return f"Walk: {pets} pets, {mins} mins - Total ${total:.2f}"

    except ValueError:
        return "Invalid walk schedule"


def compute_pace_per_pet(walk_metrics_str):
    if not isinstance(walk_metrics_str, str):
        return None

    try:
        parts = walk_metrics_str.split('/')

        if len(parts) != 2:
            return None

        mins_str, pets_str = parts

        mins = float(mins_str)
        pets = float(pets_str)

        if mins <= 0 or pets <= 0:
            return None

        pace = mins / pets

        return round(pace, 2)

    except (ValueError, ZeroDivisionError):
        return None


def lookup_temperament_surcharge(temperament_code):
    if not isinstance(temperament_code, str):
        return None

    prefix = temperament_code.strip().upper()[:3]

    surcharges = {
        "CAL": 0.0,
        "PLY": 5.0,
        "REA": 12.0,
        "AGG": 20.0
    }

    return surcharges.get(prefix)


def main():
    print("==== Running parse_walk_schedule ====")
    s_input = input("Enter schedule (e.g. 2-30-YES): ")
    print(parse_walk_schedule(s_input))

    print("\n==== Running compute_pace_per_pet ====")
    p_input = input("Enter minutes/pets (e.g. 45/3): ")
    print("Pace (min/pet):", compute_pace_per_pet(p_input))

    print("\n==== Running lookup_temperament_surcharge ====")
    t_input = input("Enter temperament code (e.g. CALM, PLAYFUL, AGGRESSIVE): ")
    print("Surcharge: $", lookup_temperament_surcharge(t_input))


if __name__ == "__main__":
    main()
