from tkinter import *
from bs4 import BeautifulSoup
import requests
import pandas as pd
from tkinter import messagebox
import matplotlib.pyplot as plt



scraped_books = []
current_dataset = []  # Tracks either the full dataset or filtered results for charts/recommendations

def scrape():
        try: 
            global scraped_books, current_dataset

            page_num = int(page_en.get())
            
            scraped_books = get_page(page_num)
            current_dataset = scraped_books  # Default to full dataset upon fresh scrape

            lstbox.delete(0,END)
            for book in scraped_books:
                 lstbox.insert(END,book['Title'])

            print(f"Scraped {len(scraped_books)} books from {page_num} pages.")

            page_en.delete(0,END)
        except ValueError:
            messagebox.showerror('Error', 'Please type in a valid integer!!')


def detail_to_textbox(event):
     listbox_selection = lstbox.curselection()
     if not listbox_selection:
          return
     index = listbox_selection[0]
     # Use current_dataset so details match whatever is currently shown in the listbox (filtered or full)
     book = current_dataset[index]

     details_textbox.config(state='normal')
     details_textbox.delete('1.0', END)
     details_textbox.insert(END, f"Title: {book['Title']}\n")
     details_textbox.insert(END, f"Category: {book['Category']}\n")
     details_textbox.insert(END, f"Price: £{book['Price']}\n")
     details_textbox.insert(END, f"Rating: {book['Rating']} / 5\n")
     details_textbox.insert(END, f"URL: {book['URL']}")
     details_textbox.config(state='disabled')


def get_page(n):
    all_books = []
    for page in range(1,n+1):
        url = f'https://books.toscrape.com/catalogue/page-{page}.html'

        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            rating_dict = {'One':1,
                           'Two': 2,
                           'Three': 3,
                           'Four': 4,
                           'Five':5}
            for book in soup.find_all('article', class_ = 'product_pod'):
                title = book.find('h3').find('a')['title']

                ratings_all = book.find('p', class_ = 'star-rating')
                ratings_class = ratings_all['class']

                rating = ratings_class[1]

                for ratings in rating_dict.keys():
                    if rating == ratings:
                        rating = rating_dict[ratings]

                price = book.find('p',class_ = 'price_color').text
                price = float(price.replace("Â£","").replace("£",""))

                link_tag = book.find('h3').find('a')
                book_url = link_tag['href']

                book_url = "https://books.toscrape.com/catalogue/" + book_url.replace('../', '')
                book_response = requests.get(book_url)

                if book_response.status_code == 200:
                    book_soup = BeautifulSoup(book_response.text,'html.parser')

                    breadcrumb = book_soup.find('ul',class_ = 'breadcrumb')
                    book_category = breadcrumb.find_all('li')[2].text.strip()
                     
                all_books.append({'Title': title,
                                  'Price': price,
                                  'Rating': rating,
                                  'Category': book_category,
                                  'URL': book_url})
        else:
            print(f"Couldn't get response")
    return all_books


def apply_filters():
        global current_dataset
        filtered_books = []       

        try: 
            user_max_price = maxprice_en.get()
            user_min_price = minprice_en.get()
            user_min_rating = minrate_en.get()
            
            if not scraped_books:
                messagebox.showerror('Error', 'Please scrape some books first!')
                return

            max_price_dataset = max(book['Price'] for book in scraped_books)
            
            max_price = float(user_max_price) if user_max_price!='' else float(max_price_dataset)
            min_price = float(user_min_price) if user_min_price != '' else 0.0
            min_rating = int(user_min_rating) if user_min_rating!= '' else 0

            for book in scraped_books:
                    if min_rating <= book['Rating'] and (min_price <= book['Price'] <= max_price):
                        filtered_books.append(book)
            
            if len(filtered_books) == 0:
                messagebox.showerror('Error', 'No books found with the selected criteria!')
            else:
                current_dataset = filtered_books  # Update active dataset context
                lstbox.delete(0,END)
                for books in filtered_books:
                    lstbox.insert(END,books['Title'])

                minprice_en.delete(0,END)
                maxprice_en.delete(0,END)
                minrate_en.delete(0,END)

        except ValueError:
            messagebox.showerror('Error', 'Please input a valid number!')


def ratingchart_plot():
        data_to_use = current_dataset if current_dataset else scraped_books
        if not data_to_use:
            messagebox.showerror('Error', 'No data available to plot!')
            return

        rating_dict = {1:0, 2:0, 3:0, 4:0, 5:0}
        for books in data_to_use:
            books_rating = books['Rating']
            if books_rating in rating_dict:
                rating_dict[books_rating] += 1 

        plt.figure()
        plt.title('Rating Distribution')
        plt.xlabel('Ratings')
        plt.ylabel('Number of Books')
        plt.bar(rating_dict.keys(), rating_dict.values(), color='g')
        plt.show()


def price_histogram_plot():
    data_to_use = current_dataset if current_dataset else scraped_books
    if not data_to_use:
        messagebox.showerror('Error', 'No data available to plot!')
        return

    prices = [book['Price'] for book in data_to_use]

    plt.figure()
    plt.title('Price Histogram')
    plt.xlabel('Price (£)')
    plt.ylabel('Number of Books')
    plt.hist(prices, bins=10, color='skyblue', edgecolor='black')
    plt.show()


def price_rating_plot(): 
    data_to_use = current_dataset if current_dataset else scraped_books
    if not data_to_use:
        messagebox.showerror('Error', 'No data available to plot!')
        return

    prices = [book['Price'] for book in data_to_use]
    ratings = [book['Rating'] for book in data_to_use]

    plt.figure()
    plt.title('Price vs Rating')
    plt.xlabel('Price (£)')
    plt.ylabel('Rating')
    plt.scatter(prices, ratings, color='purple', alpha=0.6)
    plt.show()
    
def recommend_top5():
    data_to_use = current_dataset if current_dataset else scraped_books
    if not data_to_use:
        messagebox.showerror('Error', 'No books available for recommendations!')
        return

    for book in data_to_use:
        book['Score'] = book['Rating'] / book['Price']

    top_5 = sorted(data_to_use, key=lambda b: b['Score'], reverse=True)[:5]

    recommend_txtbox.config(state='normal')
    recommend_txtbox.delete('1.0', END)
    for book in top_5:
        recommend_txtbox.insert(END, f"Title: {book['Title']}\nPrice: £{book['Price']} | Rating: {book['Rating']} | Score: {book['Score']:.2f}\n\n")
    recommend_txtbox.config(state='disabled')


root = Tk()

root.title('Book Recommendation & Filtering App')
root.geometry('900x600')

###################### LEFT SIDE
left_frame = Frame(root)
left_frame.pack(side = LEFT , fill = Y, padx = 10, pady = 10) 

Hist_Btn = Button(left_frame, text = 'Price Histogram', command = price_histogram_plot)
Hist_Btn.pack(side = BOTTOM, fill = X, padx = 3)

Rating_btn = Button(left_frame, text = 'Rating Chart', command = ratingchart_plot)
Rating_btn.pack(side = BOTTOM, fill = X, pady = 3)

Price_Rating_btn = Button(left_frame, text = 'Price vs Rating', command = price_rating_plot)
Price_Rating_btn.pack(side = BOTTOM, fill = X, pady = 3)

lstbox = Listbox(left_frame, height = 30, width = 50)
lstbox.pack(side = LEFT, fill = Y, padx = 5)
lstbox.bind('<<ListboxSelect>>', detail_to_textbox)

scrollbar = Scrollbar(left_frame)
scrollbar.pack(side = RIGHT , fill = Y)

scrollbar.config(command=lstbox.yview)
lstbox.config(yscrollcommand=scrollbar.set)

##################### RIGHT SIDE
right_frame = Frame(root)
right_frame.pack(side = RIGHT, fill = BOTH, expand= True, padx = 20, pady = 15)

row_pages = Frame(right_frame)
row_pages.pack(pady=10)

page_lbl = Label(row_pages, text = 'Page: ')
page_lbl.pack(side = LEFT, pady=2, padx=2)

page_en = Entry(row_pages, width=5)
page_en.pack(side = LEFT, pady=2, padx=2)

scrape_btn = Button(row_pages, text='Scrape', command = scrape)
scrape_btn.pack(side = LEFT, pady=2, padx=2)

row_minrate = Frame(right_frame)
row_minrate.pack(pady=10)

minrate_lbl = Label(row_minrate, text = 'Min Rating:')
minrate_lbl.pack(side = LEFT, padx=5)

minrate_en = Entry(row_minrate, width= 5)
minrate_en.pack(side = LEFT, padx = 5)

row_price = Frame(right_frame)
row_price.pack(pady=10)

minprice_lbl = Label(row_price, text = 'Min Price: ')
minprice_lbl.pack(side = LEFT, padx=5)
minprice_en = Entry(row_price, width=10)
minprice_en.pack(side = LEFT, padx=5)

maxprice_lbl = Label(row_price, text = 'Max Price: ')
maxprice_lbl.pack(side = LEFT, padx=5)
maxprice_en = Entry(row_price, width=10)
maxprice_en.pack(side = LEFT, padx=5)

applyfilter_btn = Button(row_price, text = 'Apply Filters', command = apply_filters)
applyfilter_btn.pack(side = LEFT, padx=5)

details_textbox = Text(right_frame, height = 10, width = 60, state = 'disabled')
details_textbox.pack(pady=10)

row_recommend = Frame(right_frame)
row_recommend.pack(pady=10)

recommend_btn = Button(row_recommend, text = 'Recommend Top 5', command = recommend_top5)
recommend_btn.pack(side = LEFT, padx=5)

recommend_txtbox = Text(right_frame, height = 10, width = 60, state = 'disabled')
recommend_txtbox.pack(pady=10)

root.mainloop()