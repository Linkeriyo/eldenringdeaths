token_file_name = "token"
deaths_file_name = "deaths.txt"
log_file_name = "log.txt"


def read_token_from_file() -> str:
    with open(token_file_name, "r") as f:
        lines = f.readlines()
        return lines[0].strip()


def read_deaths_and_day_from_file(players: list[str]) -> (dict[str, int], str):
    try:
        with open(deaths_file_name, "r") as file:
            lines = file.readlines()
            deaths = {}
            day = ""
            for line in lines:
                key = line.split(":")[0].strip()
                value = int(line.split(":")[1].strip())
                if key == "day":
                    day = value
                    continue
                deaths[key] = value
        return deaths, day
    except FileNotFoundError:
        deaths = {}
        for player in players:
            deaths[player] = 0
        return deaths, "0"


def write_deaths_and_day_to_file(deaths: dict[str, int], day: int) -> None:
    with open(deaths_file_name, "w+") as file:
        file.write(f"day: {day}\n")
        for player in deaths:
            file.write(f"{player}: {deaths[player]}\n")


def add_to_log_file(string: str) -> None:
    with open(log_file_name, "a+") as file:
        file.write(string + "\n")
