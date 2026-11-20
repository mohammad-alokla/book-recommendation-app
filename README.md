# Book Scraper & Recommendation GUI App

A desktop Python application that scrapes live book catalog data, filters results by price and rating, visualizes dataset distributions, and recommends the best value-for-money books.

## Features
* **Multi-Page Web Scraping:** Crawls catalog and individual product pages using `requests` and `BeautifulSoup` to extract titles, prices, ratings, categories, and direct URLs.
* **Interactive Desktop UI:** Built with `Tkinter`, featuring dynamic filtering (min/max price, minimum rating) and live item inspection.
* **Data Visualization:** Generates real-time `Matplotlib` charts (Rating Distribution bar chart, Price Histogram, and Price vs. Rating scatter plot) synced to the active filtered dataset.
* **Value Recommendation Engine:** Ranks and displays the top 5 books based on a rating-to-price value score.

## Tech Stack
* Python 3
* `BeautifulSoup4` & `requests`
* `Tkinter`
* `Matplotlib` & `pandas`
