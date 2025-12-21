# Product Review Analytics Dashboard

## Objective
A Streamlit-powered analytics dashboard that transforms product review data into actionable insights with NPS scoring, best/worst product analysis, sentiment trends, and role-based access control for Admin/Analyst users.

## Key Features
- **Real-time NPS calculation** with Happy Curve visualization
- **Best/Worst product ranking** (overlap prevention logic)
- **Sentiment analysis** with interactive pie charts
- **Role-based access** (Admin assigns category permissions)
- **Chatbot analytics** (ratings, satisfaction, summaries)
- **PDF report generation** with user-isolated history
- **SQLite BLOB storage** for secure report management

## Technology Stack
- Frontend: Streamlit 1.28+
= Backend: SQLite3 (BLOB storage)
- Analytics: Pandas 2.0+, Plotly 5.15+, TextBlob
- PDF: FPDF2 2.7.5+, Kaleido 0.2.1+
- Deployment: Streamlit Cloud


## Language Used
**Python 3.11+**

## Screenshots
### Dashboard Analytics
<img width="1916" height="853" alt="Image" src="https://github.com/user-attachments/assets/e858da09-80e0-40f5-8612-d5c21693f38a" />


### Downloaded PDF Report
<img width="554" height="693" alt="Image" src="https://github.com/user-attachments/assets/66fcabf3-caea-4fa4-86ed-5fbb9dd5e223" />


## Room for Improvement
- Date-range analytics (month-over-month trends)
- OpenAI GPT-4 integration for advanced NLP
- Professional ReportLab PDF templates
- PostgreSQL multi-tenancy support
- Scheduled email reporting
- Mobile-responsive PWA

## Presentation
[View Presentation](https://drive.google.com/file/d/1AjIXf21TxRqc-znKgh5IKDvGq0Kcpd3U/view?usp=sharing)

## Detailed Report
[Download Detailed Report](https://drive.google.com/file/d/1Bhz2UFerYmCn5PJhIiEmlCKayvsfem66/view?usp=sharing)

## Deployed Application
🔴 [Live Demo](https://jd-analyticalboard-app.streamlit.app)  


**Analyst:** Any username

## 📊 Dataset Used
Review data from Amazon products and services (CSV format)

### Datasets
- [Products Reviews](https://www.kaggle.com/datasets/yasserh/amazon-product-reviews-dataset)
- [Services Reviews](https://www.kaggle.com/datasets/dongrelaxman/amazon-reviews-dataset)

## 📦 Quick Start
```
pip install -r requirements.txt
streamlit run app.py
```


## 🏢 Project Under
**Elimentary** 
[Website](https://elimentary.com/)

---

⭐ **Star this repo if you found it useful!**  
💬 **Issues/Pull Requests welcome!**

