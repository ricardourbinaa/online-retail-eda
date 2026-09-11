# Online Retail EDA

## About the Project

For this project, I analyzed an online retail dataset with over 500,000 transaction records. I used Python to clean the data and look for patterns in sales, products, countries, and customers.

The dataset comes from a UK-based online retailer and covers transactions between December 2010 and December 2011.

## Tools

* Python
* pandas
* Matplotlib
* Seaborn

## Data Cleaning

Before starting the analysis, I:

* Fixed column names and data types
* Standardized product codes and descriptions
* Checked missing values
* Removed duplicate rows
* Investigated negative quantities and prices
* Separated cancellations and zero-priced records
* Removed postage, fees, and other non-product records from the product analysis
* Created a revenue column using quantity and unit price

After cleaning, the product-sales dataset contained 522,540 rows.

## Findings

* Gross product revenue was about £10.25 million.
* Revenue increased from September through November, mainly because the number of orders increased.
* November had the highest monthly revenue and order volume.
* The UK accounted for 85.14% of product revenue.
* The Netherlands was the largest international market by revenue.
* The top 10 customers accounted for 17.4% of revenue connected to known customers.
* Some products ranked highly because of one unusually large order, while others performed well across many different orders.

## Charts

### Monthly Product Revenue

![Monthly product revenue](Visuals/Monthly%20Product%20Revenue.png)

### Monthly Order Volume

![Monthly order volume](Visuals/Monthly%20Order%20Volume.png)

### Top Products by Revenue

![Top products](Visuals/Top%2010%20Products%20by%20Revenue.png)

### Top International Markets

![International markets](Visuals/Top%20International%20Markets%20by%20Product%20Revenue.png)

### Top Customers by Revenue

![Top customers](Visuals/Top%2010%20Customers%20by%20Product%20Revenue.png)

## Dataset

I used the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail).

The dataset is not included in this repository because the file is too large. To run the project, download the dataset, save it as `Online Retail.csv`, and place it inside the `Data` folder.

## Limitations

December 2011 only contains nine days of transactions, so it cannot be directly compared with the complete months. Also, 14.74% of product revenue does not have a customer ID and was excluded from the customer analysis.

## How to Run

Install the required libraries:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python Notebook/online_retail_eda.py
```
