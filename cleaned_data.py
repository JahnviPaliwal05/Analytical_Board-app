import pandas as pd


product_columns = [
    'id', 'asins', 'brand', 'categories', 'colors', 'dateAdded', 'dateUpdated', 'dimension',
    'ean', 'keys', 'manufacturer', 'manufacturerNumber', 'name', 'prices', 'reviews.date',
    'reviews.doRecommend', 'reviews.numHelpful', 'reviews.rating', 'reviews.sourceURLs',
    'reviews.text', 'reviews.title', 'reviews.userCity', 'reviews.userProvince',
    'reviews.username', 'sizes', 'upc', 'weight'
]

services_columns = [
    'Reviewer Name', 'Profile Link', 'Country', 'Review Count', 'Review Date', 'Rating',
    'Review Title', 'Review Text', 'Date of Experience'
]


product_numeric_cols = ['reviews.rating', 'reviews.numHelpful', 'prices', 'weight']
services_numeric_cols = ['Rating', 'Review Count']


def load_and_clean_products(path):
    df = pd.read_csv(path, sep=',', engine='python',nrows=1000)

    
    df.columns = df.columns.str.strip()

    
    df = df[[col for col in product_columns if col in df.columns]]

    
    for col in product_numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convert other columns to string and fill missing with empty string
    for col in df.columns:
        if col not in product_numeric_cols:
            df[col] = df[col].fillna("").astype(str)

    return df


def load_and_clean_services(path):
    df = pd.read_csv(path, sep=',', engine='python',nrows=1000)

   
    df.columns = df.columns.str.strip()

    
    df = df[[col for col in services_columns if col in df.columns]]

   
    for col in services_numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

   
    for col in df.columns:
        if col not in services_numeric_cols:
            df[col] = df[col].fillna("").astype(str)

    return df



products_df = load_and_clean_products("data/products_reviews.csv")
services_df = load_and_clean_services("data/services_reviews.csv")

print("Products DF shape:", products_df.shape)
print("Services DF shape:", services_df.shape)

