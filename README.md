# E-commerce Customer Segmentation Dashboard

![Dashboard Screenshot](<URL_TO_YOUR_SCREENSHOT_HERE>)  <!-- Optional: Add a screenshot of your app -->

An interactive web application designed to analyze customer behavior from a raw e-commerce sales log. This dashboard turns transactional data into strategic insights by performing RFM (Recency, Frequency, Monetary) analysis to identify and segment key customer groups.

This project was built to demonstrate a full data analysis pipeline, from cleaning raw data to deploying a live, interactive visualization tool.

---

### Key Features

*   **Interactive Tabs:** Data is organized into three clear sections: a high-level **Global Overview**, a detailed **Product Analysis**, and an insightful **Customer Segmentation** view.
*   **Dynamic Filtering:** Users can filter the entire dashboard by **Country** to drill down into specific market performance.
*   **RFM Analysis:** Automatically calculates Recency, Frequency, and Monetary scores for each customer and groups them into actionable segments like "Champions," "Loyal Customers," and "At-Risk."
*   **Actionable Visualizations:** Includes clear, minimalist charts showing monthly sales trends, top-selling products (by revenue and volume), and the distribution of customer segments.
*   **Performance Optimized:** Uses a pre-processing script to handle heavy, one-time data cleaning and analysis, ensuring the live dashboard loads quickly and remains responsive.

---

### Tech Stack

*   **Language:** Python
*   **Data Manipulation:** Pandas
*   **Dashboard Framework:** Plotly Dash & Dash Bootstrap Components
*   **Data Visualization:** Plotly Express
*   **Deployment:** Gunicorn / Railway (or your hosting service)

---

### How to Run Locally

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/ecommerce-dashboard.git
    cd ecommerce-dashboard
    ```

2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  (If applicable) Run the pre-processing script first:
    ```bash
    python preprocess.py
    ```

5.  Run the application:
    ```bash
    python app.py
    ```

6.  Open your browser and navigate to `http://127.0.0.1:8050`.