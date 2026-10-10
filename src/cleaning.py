import html
import pandas as pd

def dataframe_cleaner(raw_df, clean_dataframe_filepath):
    """
    Function cleaning a raw dataframe and saving it in a json file
    :params: pandas.DataFrame
    Returns pandas.DataFrame
    """
    clean_df = raw_df.drop_duplicates(subset=['postcode', 'price', 'livable_surface', 'address'])

    # A listing with no surface, or a surface of 0, has no price per m2. Dividing
    # by it gave `inf`, which then sat at the top of every outlier chart and in
    # every mean. NaN is the honest value: "not computable", which the plots and
    # pandas aggregations both skip.
    surface = clean_df['livable_surface'].where(clean_df['livable_surface'] > 0)
    clean_df['price_per_m2'] = clean_df['price'] / surface

    rows_to_Int64 = ["postcode", "price", "build_year", "bedroom_count", "livable_surface", "total_surface", "garage", "terrace", "swimming_pool", "peb_category", "Preschool_distance", "Train_station_distance", "Supermarket_distance"]

    for row in rows_to_Int64:
        if clean_df[row].dtype == "float64":
            clean_df[row] = clean_df[row].astype("Int64")
    
    new_column_names = {"peb_category": "energy_consumption_kWh/m2/year",
                    "Preschool_distance": "preschool_distance_m",
                    "Train_station_distance": "train_station_distance_m",
                    "Supermarket_distance": "supermarket_distance_m",
                    "distance_nearest_city": "nearest_city_distance_km"}

    clean_df = clean_df.rename(columns=new_column_names)

    for col in ['city', 'province', 'address', 'nearest_city']:
        clean_df[col] = clean_df[col].apply(lambda x: html.unescape(x) if isinstance(x, str) else x)

    # An imputation, stated as one: a listing that does not mention a garage or
    # a pool is treated as having none. That is the usual meaning of silence in
    # a property listing, but it is an assumption, and it biases both columns
    # towards zero. Any figure built on them should say "declared".
    clean_df.fillna(value={'garage': 0, 'swimming_pool': 0}, inplace=True)

    clean_df["property_state"] = clean_df["property_state"].replace("To be renovated", "To renovate")

    clean_df.to_json(clean_dataframe_filepath, orient="records", force_ascii=False, indent=4)

    return clean_df