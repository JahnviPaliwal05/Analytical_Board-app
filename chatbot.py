import openai
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob


openai.api_key = "OPENAI_API_KEY"

def ask_chatbot(question, context_text=""):
    prompt = (
        "Answer the user question based on the following context:\n"
        f"{context_text}\n\nQuestion: {question}"
    )

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        temperature=0.5
    )

    return response.choices[0].text.strip()


def w_b(df, category, top_n=5):
    df.copy()
    df.columns = df.coloumns.str.strip()
    return df
def best_worst_products(dfp, category, top_n=1):
    df = dfp.copy()
    df_filtered = df[df['categories'] == category]
    short_df = (
        df_filtered[['categories', 'name', 'reviews.rating']]
        .dropna(subset=['categories', 'name', 'reviews.rating'])
        .groupby(['categories', 'name'], as_index=False)
        .agg(avg_review_rating=('reviews.rating', 'mean'),
             count_rating_1=('reviews.rating', lambda x: (x == 1).sum()),
             count_rating_5=('reviews.rating', lambda x: (x == 5).sum())
             )
        .reset_index()
        .sort_values(['categories', 'avg_review_rating'], ascending=[True, False])
    )
    # df.columns = df.columns.str.strip().str.lower()
    # df = df[df["categories"] == category]

    best = (
        short_df.sort_values("count_rating_5", ascending=False)
        .head(top_n)
    )

    worst = (
        short_df.sort_values("count_rating_1", ascending=False)
        .head(top_n)
    )
    if set(best['name'].tolist()) & set(worst['name'].tolist()):
        next_worst = (
            short_df.sort_values("count_rating_1", ascending=False)
            .head(top_n + 1)
            .iloc[1:]  
            .head(top_n) 
        )
        worst = next_worst

    return best, worst


def load_product_data():
    return pd.read_csv("data/products_reviews.csv")


def load_service_data():
    return pd.read_csv("data/services_reviews.csv")


def filter_by_category(df, category):
    if category == "ALL":
        return df
    return df[df["categories"] == category]



def filter_by_user(df, role, category):
    if role == "admin":
        return df
    return df[df["categories"] == category]



def rating_distribution(df, category):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df[df["categories"] == category]

    df["reviews.rating"] = pd.to_numeric(
        df["reviews.rating"], errors="coerce"
    ).dropna()

    fig, ax = plt.subplots()
    df["reviews.rating"].value_counts().sort_index().plot(
        kind="bar", ax=ax
    )
    ax.set_title(f"Rating Distribution - {category}")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Count")

    return fig


def satisfaction_curve(df, category):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df[df["categories"] == category]

    df["reviews.text"] = df["reviews.text"].fillna("")

    df["satisfaction"] = df["reviews.text"].apply(
        lambda x: "Happy" if TextBlob(str(x)).sentiment.polarity > 0 else "Unhappy"
    )

    counts = df["satisfaction"].value_counts()

    fig, ax = plt.subplots()
    ax.plot(counts.index, counts.values, marker="o")
    ax.set_title(f"Satisfaction Curve - {category}")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Count")

    return fig


def category_context_summary(short_df, category):
    df = short_df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df[df["categories"] == category]

    summary = []
    for _, row in df.iterrows():
        summary.append(
            f"{row['name']} | Avg Rating: {row['avg_review_rating']:.2f} "
            f"| 5★: {row['count_rating_5']} | 1★: {row['count_rating_1']}"
        )

    return "\n".join(summary)

