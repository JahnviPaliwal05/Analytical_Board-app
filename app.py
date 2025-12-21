import streamlit as st
import pandas as pd
import sqlite3
import csv
import plotly.express as px
from analytics import preprocess_reviews, compute_nps, add_sentiment, best_worst_products, summarize_reviews, plot_nps_happy_curve
from utils import *
from chatbot import *
from datetime import datetime

# ------------------ DATABASE ------------------

def get_connection():
    return sqlite3.connect("app.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            role TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            username TEXT,
            category TEXT,
            PRIMARY KEY (username, category)
        )
    """)
    cur.execute("""
            CREATE TABLE IF NOT EXISTS report_history1 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                category TEXT,
                report_name TEXT,
                pdf_data BLOB,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
    """)
    conn.commit()
    conn.close()

# ------------------ DATA LOADING ------------------

@st.cache_data
def load_data():
    services = pd.read_csv(
        "data/services_reviews.csv",
        engine="python",
        on_bad_lines="skip",
        encoding="ISO-8859-1",
        nrows=1000
    )

    products = pd.read_csv(
        "data/products_reviews.csv",
        engine="python",
        on_bad_lines="skip",
        encoding="ISO-8859-1",
        nrows=1000
    )

    return services, products

# ------------------ AUTH ------------------

def save_user(username, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?)",
        (username, role)
    )
    conn.commit()
    conn.close()

def login():
    st.header("Login")
    role = st.selectbox("Login as", ["User", "Admin"])
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if role == "Admin":
            if username == "admin" and password == "admin123apk":
                st.session_state["username"] = "admin"
                st.session_state["role"] = "admin"
                save_user("admin", "admin")
                st.rerun()
            else:
                st.error("Invalid admin credentials")
        else:
            if username:
                st.session_state["username"] = username
                st.session_state["role"] = "user"
                save_user(username, "user")
                st.rerun()
            else:
                st.error("Enter a username")

def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# ------------------ ANALYTICS ------------------

def show_category_report(products, category):
    df_p1 = products
    # products = load_reviews()
    products = preprocess_reviews(products)
    products = add_sentiment(products,category)

    df_filtered = df_p1[df_p1['categories'] == category]
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
    if df_p1.empty:
        st.warning("No data for this category")
        return

    st.subheader(f"Report: {category}")

    best = short_df.sort_values("count_rating_5", ascending=False).head(2)
    worst = short_df.sort_values("count_rating_1", ascending=True).head(2)

    st.write("ALL Products")
    st.dataframe(short_df)

    nps = compute_nps(short_df,category)
    st.metric("NPS Score", f"{nps:.2f}%")

    st.write("Best Products")
    st.dataframe(best[["name", "avg_review_rating"]])

    st.write("⚠ Worst Products")
    st.dataframe(worst[["name", "avg_review_rating"]])




    df_category = products[products['categories'] == category].copy()
    df_category = df_category.dropna(subset=['reviews.rating', 'name'])

    # if df_category.empty:
    #     st.warning("No data for this category")
    #     return
    #
    # # Add sentiment column if not present
    # if 'sentiment' not in df_category.columns:
    #     df_category = add_sentiment(df_category)

    st.subheader(f"Analytics for Category: {category}")

    #NPS
    # nps = compute_nps(df_category)
    # st.metric("NPS Score", f"{nps:.2f}%")

    # Happy curve plot
    fig_curve, _ = plot_nps_happy_curve(
        df_category,
        category,
        text_col='reviews.text',
        rating_col='reviews.rating',
        name_col='name',
        title=f"NPS & Satisfaction Curve: {category}"
    )
    st.plotly_chart(fig_curve, use_container_width=True)

    # # Best & Worst Products
    # best, worst = best_worst_products(df_category)
    # st.write("⭐ Top 5 Best Products")
    # st.dataframe(best)
    # st.write("⚠ Top 5 Worst Products")
    # st.dataframe(worst)

    # Sentiment pie chart
    fig_pie = px.pie(df_category, names='sentiment', title="Sentiment Distribution")
    st.plotly_chart(fig_pie)

    # Summary
    st.subheader("Summary of Unhappy Reviews")
    summary = summarize_reviews(df_category,category)
    st.write(summary)
    return category, short_df,nps,best,worst,fig_curve,fig_pie,summary


# ------------------ ADMIN DASHBOARD ------------------

def admin_dashboard(products):
    st.header("Admin Dashboard")
    # print(products["categories"].head())

    # categories = products["categories"].dropna().unique()
    categories = ['Amazon Devices,mazon.co.uk', 'Kindle Store,Amazon Devices,Electronics',
                  'Categories,Amazon Devices,Streaming Media Players', 'Amazon Devices',
                  'Categories,Amazon Devices,Electronics Features,Streaming Media Players,Consumer Electronics,See more Amazon Fire TV Digital HD Media Streamer (Late...',
                  'Amazon Devices & Accessories,Amazon Device Accessories,Power Adapters & Cables,Kindle Store,Kindle E-Reader Accessories,Kindle Paperwhite Accessories',
                  'Amazon Devices,Kindle Store', 'Electronics,Amazon Devices',
                  'Amazon Devices,Kindle Accessories',
                  'Amazon Devices,Electronics,Kindle Store',
                  'Amazon Devices,Electronics,Kindle Store,Amazon Echo',
                  'Amazon Devices,Kindle Store,Kindle Accessories',
                  'Amazon Devices,Kindle Store,buy a kindle',
                  'Amazon Devices,Home,Smart Home & Connected Living,Smart Hubs & Wireless Routers,Smart Hubs,Home Improvement,Home Safety & Security,Alarms & Sensors,Home Security,Amazon Echo,Home, Garage & Office,Smart Home,Voice Assistants,Amazon Tap,Electronics Features,TVs & Electronics,Portable Audio & Electronics,MP3 Player Accessories,Home Theater & Audio,Speakers,Featured Brands,Electronics,Kindle Store,Frys,Electronic Components,Home Automation,Electronics, Tech Toys, Movies, Music,Audio,Bluetooth Speakers']
    conn = get_connection()
    cur = conn.cursor()

    users = cur.execute(
        "SELECT username FROM users WHERE role='user'"
    ).fetchall()

    for (user,) in users:
        st.subheader(f" {user}")

        for cat in categories:
            allowed = cur.execute(
                "SELECT 1 FROM permissions WHERE username=? AND category=?",
                (user, cat)
            ).fetchone()

            if st.checkbox(
                    cat,
                    value=bool(allowed),
                    key=f"{user}_{cat}"
            ):
                cur.execute(
                    "INSERT OR IGNORE INTO permissions VALUES (?, ?)",
                    (user, cat)
                )
            else:
                cur.execute(
                    "DELETE FROM permissions WHERE username=? AND category=?",
                    (user, cat)
                )

    conn.commit()
    conn.close()


# ------------------ USER DASHBOARD ------------------

def user_dashboard(products):
    username = st.session_state["username"]
    conn = get_connection()
    cur = conn.cursor()
    selected_category,short_df,nps,best,worst,fig_curve,fig_pie,summary=0
    
    categories = cur.execute(
        "SELECT category FROM permissions WHERE username=?",
        (username,)
    ).fetchall()
    bool = 'True'
    categories = [c[0] for c in categories]

    if not categories:
        st.warning("Admin has not given access yet")
        bool = 'False'
        return selected_category,short_df,nps,best,worst,fig_curve,fig_pie,summary

    category = st.selectbox("Select Category", categories)

    selected_category,short_df,nps,best,worst,fig_curve,fig_pie,summary=show_category_report(products, category)
    
    return selected_category,short_df,nps,best,worst,fig_curve,fig_pie,summary

def show_history():
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT category, viewed_at FROM report_history1 WHERE username=? ORDER BY viewed_at DESC",
        (st.session_state["username"],)
    ).fetchall()
    st.subheader("Past Reports")
    for cat, t in rows:
        st.write(f"• {cat} — {t}")

# ------------------ CHATBOT ------------------

def chatbot_section(df):
    st.header("Chatbot")
    username = st.session_state["username"]
    conn = get_connection()
    cur = conn.cursor()

    categories = cur.execute(
        "SELECT category FROM permissions WHERE username=?",
        (username,)
    ).fetchall()

    categories = [c[0] for c in categories]

    if not categories:
        st.warning("Admin has not given access yet")
        return

    category = st.selectbox("Select Category", categories)

    st.header("Ask Questions to the Chatbot")
    # question = st.text_input("Enter your question")
    # if st.button("Ask"):
    #     context_text = "Overall review summary:\n" + summarize_reviews(df)
    #     answer = ask_chatbot(question, context_text)
    #     st.write(answer)
    # df = load_product_data()
    # df = filter_by_category(df, st.session_state.categories)
    # df["satisfaction"] = df["reviews.rating"].apply(classify_satisfaction)

    question = st.text_input("Ask a question about reviews:")

    if st.button("Ask"):
        # log_event(st.session_state.user, question, "query")

        if "rating" in question.lower():
            fig = rating_distribution(df, category)
            st.pyplot(fig)

        elif "satisfaction" in question.lower():
            fig = satisfaction_curve(df, category)
            st.pyplot(fig)

        elif "best" in question.lower() or "worst" in question.lower():
            best, worst = best_worst_products(df, category)
            st.subheader("Best Products")
            st.dataframe(best)
            st.subheader("Worst Products")
            st.dataframe(worst)

        elif "summary" in question.lower():
            summary = summarize_reviews(df, category)
            st.write(summary)

        else:
            st.info("Try asking about ratings, satisfaction, best or worst products.")

    conn.close()
    # question = st.text_input("Ask a question about reviews:")
    # if st.button("Ask Chatbot"):
    #     if question.strip() != "":
    #         context_text = "Overall review summary:\n" + summarize_reviews(df)
    #         answer = ask_chatbot(question, context_text)
    #         st.write(answer)
    #     else:
    #         st.info("Enter a question to ask the chatbot")


def show_user_reports():
    
    conn = get_connection()
    cur = conn.cursor()

    # Fetch only this user's reports
    rows = cur.execute("""
        SELECT report_name, saved_at FROM report_history1 
        WHERE username=? 
        ORDER BY saved_at DESC
    """, (st.session_state["username"],)).fetchall()

    if not rows:
        st.info("No reports saved yet.")
        return

    for report_name, saved_at in rows:
        with st.expander(f"{report_name} ({saved_at})"):
            # Retrieve PDF from database
            pdf_data = cur.execute("""
                SELECT pdf_data FROM report_history1 
                WHERE username=? AND report_name=?
            """, (st.session_state["username"], report_name)).fetchone()

            if pdf_data:
                st.download_button(
                    label="⬇Download PDF",
                    data=pdf_data[0],
                    file_name=f"{report_name}.pdf",
                    mime="application/pdf"
                )

    conn.close()


# ------------------ MAIN ------------------



def main():
    st.set_page_config(page_title="Integrated Product Dashboard", layout="wide")
    init_db()
    st.title("Integrated Product Review Dashboard")

    if "role" not in st.session_state:
        login()
        return

    st.sidebar.write(f"{st.session_state['username']}")
    st.sidebar.button("Logout", on_click=logout)

    _, products = load_data()

    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Go to", ["Dashboard", "Chatbot", "Past Reports"])

    if st.session_state["role"] == "admin":
        admin_dashboard(products)
    else:
        if option == "Dashboard":
            selected_category,short_df,nps,best,worst,fig_curve,fig_pie,summary = user_dashboard(products)
            if st.button("Save Report"):
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                username = st.session_state["username"]
                report_name = f"{username}-{selected_category}-{timestamp}"

                pdf_file, pdf_bytes = save_category_report_pdf(
                    report_name=report_name,
                    category=selected_category,
                    short_df=short_df,
                    nps=nps,
                    best=best,
                    worst=worst,
                    fig_curve=fig_curve,
                    fig_pie=fig_pie,
                    summary=summary
                )

                # Save to database
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO report_history1 (username, category, report_name, pdf_data)
                    VALUES (?, ?, ?, ?)
                """, (username, selected_category, report_name, pdf_bytes))
                conn.commit()
                conn.close()

                st.success(f"Report '{report_name}' saved!")

        elif option == "Chatbot":
            chatbot_section(products,)
        elif option == "Past Reports":
            st.header("Past Reports")
            show_user_reports()
            # selected = st.selectbox("Select a report", reports)
            # if selected:
            #     pdf_file = f"reports/{selected}.pdf"
            #     with open(pdf_file, "rb") as f:
            #         st.download_button("Download Report PDF", f, file_name=f"{selected}.pdf")


if __name__ == "__main__":
    main()





