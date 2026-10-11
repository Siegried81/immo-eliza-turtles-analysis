from src import export_most_least_expensive_municipalities_regions_report, dataframe_cleaner, correlations_matrix, price_vs_property_states, inventory_by_province, surface_distribution, make_outlier_graph, make_build_year_price_m2_graph
import argparse
import pandas as pd
import os

def main():
    """
    Clean the raw listings, then produce the reports.

    Interactive by default (the numbered menu). `--report` runs one report or
    all of them without a prompt, which is what a CI job or a `make reports`
    needs: `input()` on a machine with no terminal attached hangs forever.
    """
    parser = argparse.ArgumentParser(description="Immo Eliza market analysis reports")
    parser.add_argument(
        "--report", choices=[str(i) for i in range(1, 8)] + ["all"],
        help="run one numbered report (see the menu) or all of them, then exit",
    )
    args = parser.parse_args()

    # ---------------------------------------
    # Load configuration file
    # ---------------------------------------
    # Get project base directory
    base_dir = os.path.dirname(__file__)
    clean_dataframe_filepath = os.path.join(base_dir, "./data/cleaned/clean_dataframe.json")
    raw_dataframe_filepath = os.path.join(base_dir, "./data/raw/dataframe.json")

    # ---------------------------------------
    # Cleaning process
    # ---------------------------------------
    raw_df = pd.read_json(raw_dataframe_filepath)
    df = dataframe_cleaner(raw_df, clean_dataframe_filepath)

    # ---------------------------------------
    # Colour palette we'll reuse 
    # ---------------------------------------
    BLUE   = '#2166ac'
    ORANGE = '#d6604d'
    GREEN  = '#4dac26'
    GREY   = '#878787'
    PALETTE = [BLUE, ORANGE, GREEN, '#9970ab', '#bf812d']

    # One place that says which number runs which report, shared by the menu
    # below and by --report, so the two cannot drift apart.
    reports = {
        "1": lambda: make_outlier_graph(df, base_dir),
        "2": lambda: make_build_year_price_m2_graph(df, base_dir),
        "3": lambda: correlations_matrix(df, base_dir),
        "4": lambda: price_vs_property_states(df, base_dir, PALETTE),
        "5": lambda: inventory_by_province(df, base_dir),
        "6": lambda: surface_distribution(df, base_dir),
        "7": lambda: export_most_least_expensive_municipalities_regions_report(clean_dataframe_filepath, base_dir),
    }
    if args.report:
        for number in (reports if args.report == "all" else [args.report]):
            print(f"Report {number} is generating")
            reports[number]()
        return

    # ---------------------------------------
    # Choose URL source mode
    # ---------------------------------------
    print("\n=== Choose report ===")
    print("'1' : Most common outlier")
    print("'2' : Build year vs price")
    print("'3' : Correlation matrix")
    print("'4' : Price/m2 vs property states")
    print("'5' : Nb of Houses vs Apartments by Regions")
    print("'6' : Distribution of properties vs surface")
    print("'7' : Most & least expensive municipalities/regions")
    print("'8' : To exit")


    while True:
        option = input("Choose an option: ")

        if option in reports:
            print("Report is generating")
            reports[option]()
        elif option == "8":
            break
        else:
            print("Options are 1 to 8. Please choose again.")
         


# ---------------------------------------
# Program entry point
# ---------------------------------------
if __name__ == "__main__":
    main()
