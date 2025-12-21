import pandas as pd
from textblob import TextBlob
import plotly.express as px

def preprocess_reviews(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    required_cols = [
        'categories',
        'name',
        'avg_review_rating',
        'count_rating_1',
        'count_rating_5'
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = 0

    df['avg_review_rating'] = pd.to_numeric(df['avg_review_rating'], errors='coerce').fillna(1)
    df['count_rating_1'] = pd.to_numeric(df['count_rating_1'], errors='coerce').fillna(0)
    df['count_rating_5'] = pd.to_numeric(df['count_rating_5'], errors='coerce').fillna(0)

    return df


# -----------------------------
# NPS SCORE (CATEGORY-WISE, SHORT_DF)
# -----------------------------
def compute_nps(df, category):
    df = preprocess_reviews(df)
    df = df[df['categories'] == category]

    def nps_label(rating):
        if rating >= 4:
            return 'Promoter'
        elif rating <= 2:
            return 'Detractor'
        else:
            return 'Passive'

    df['nps_label'] = df['avg_review_rating'].apply(nps_label)

    total = len(df)
    if total == 0:
        return 0

    nps_score = (
        (df['nps_label'] == 'Promoter').sum() -
        (df['nps_label'] == 'Detractor').sum()
    ) / total * 100

    return nps_score


# -----------------------------
# SENTIMENT LABEL (RAW TEXT)
# -----------------------------
def sentiment_label(text):
    polarity = TextBlob(str(text)).sentiment.polarity
    return 'Happy' if polarity > 0 else 'Unhappy'


# -----------------------------
# ADD SENTIMENT (CATEGORY-WISE, ORIGINAL DF)
# -----------------------------
def add_sentiment(df, category):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df[df['categories'] == category]

    df['reviews.text'] = df['reviews.text'].fillna("")
    df['sentiment'] = df['reviews.text'].apply(sentiment_label)

    return df


# -----------------------------
# BEST & WORST PRODUCTS
# BASED ON COUNT OF 5★ AND 1★
# (CATEGORY-WISE, SHORT_DF)
# -----------------------------
def best_worst_products(df, category, top_n=2):
    df = preprocess_reviews(df)
    df = df[df['categories'] == category]

    best = df.sort_values('count_rating_5', ascending=False).head(top_n)
    worst = df.sort_values('count_rating_1', ascending=False).head(top_n)

    return best, worst


# -----------------------------
# UNHAPPY REVIEW SUMMARY
# (CATEGORY-WISE, ORIGINAL DF)
# -----------------------------
def summarize_reviews(df, category, n=5):
    df = add_sentiment(df, category)

    unhappy_reviews = df[df['sentiment'] == 'Unhappy']['reviews.text']

    words = " ".join(unhappy_reviews).lower().split()
    freq = pd.Series(words).value_counts().head(n)

    summary = "Top reasons for dissatisfaction: " + ", ".join(freq.index)
    return summary


# -----------------------------
# NPS + HAPPY CURVE
# (CATEGORY-WISE, ORIGINAL DF)
# -----------------------------
def plot_nps_happy_curve(
    df,
    category,
    text_col='reviews.text',
    rating_col='reviews.rating',
    name_col='name',
    title="NPS & Satisfaction Curve"
):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df[df['categories'] == category]

    df[text_col] = df[text_col].fillna("")
    df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce').fillna(3)

    df['sentiment'] = df[text_col].apply(sentiment_label)

    def nps_label(r):
        if r >= 4:
            return 'Promoter'
        elif r <= 2:
            return 'Detractor'
        else:
            return 'Passive'

    df['nps_label'] = df[rating_col].apply(nps_label)
    df['serial'] = range(1, len(df) + 1)

    promoters = detractors = happy = 0
    nps_scores = []
    happy_percent = []

    for i, row in df.iterrows():
        if row['nps_label'] == 'Promoter':
            promoters += 1
        elif row['nps_label'] == 'Detractor':
            detractors += 1
        if row['sentiment'] == 'Happy':
            happy += 1

        nps_scores.append((promoters - detractors) / (i + 1) * 100)
        happy_percent.append(happy / (i + 1) * 100)

    df['nps_score'] = nps_scores
    df['happy_pct'] = happy_percent

    fig = px.line(
        df,
        x='serial',
        y=['nps_score', 'happy_pct'],
        labels={'value': 'Percentage', 'serial': 'Index'},
        title=f"{title} - {category}"
    )

    return fig, df
