from .scraper import KBAScraper
from .config import fz11


client = KBAScraper()
print(client.discover_files(fz11))

def main() -> None:
    print("Hello from kba-dashboard!")

main()