import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path


# project path
project_dir = Path(__file__).resolve().parent.parent
data_path = project_dir / "Data" / "Online Retail.csv"
visuals_dir = project_dir / "Visuals"

visuals_dir.mkdir(exist_ok=True)


# loading the dataset
df = pd.read_csv(data_path)


# formatting column name 
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)


# standardize text values
df["stockcode"] = df["stockcode"].str.strip().str.upper()
df["description"] = df["description"].str.strip().str.upper()

# correcting data types
df["invoicedate"] = pd.to_datetime(df["invoicedate"])
df["customerid"] = df["customerid"].astype("Int64")


# inspecting the dataset
df.info()

print("\nMissing values:")
print(df.isna().sum())

missing_description = df[df["description"].isna()]
print(missing_description.head(10))
print(missing_description["unitprice"].value_counts())
# inspecting these NaN rows, they all contain unit prices of 0, since they dont contribute to the revenue, we can drop them from the dataset

# make a new df and double check the rows have been dropped
clean_df = df.dropna(subset=["description"]).copy()
print("rows before:", len(df))
print("rows after:", len(clean_df))
print("\nmissing values:")
print(clean_df.isna().sum())

#checking NaN values in customer id, but since they have unit values we keep them in our dataset regardles of missing customer id
missing_customer = clean_df[clean_df["customerid"].isna()]
print(missing_customer.head(10))

# check for duplicates
duplicate_count = clean_df.duplicated().sum()
print("duplicate rows:", duplicate_count)


#inspect duplicate rows
duplicate_rows = clean_df[clean_df.duplicated(keep=False)]

print(
    duplicate_rows
    .sort_values(["invoiceno", "stockcode"])
    .head(10)
)
#since theyre exact duplicates we can drop them 
clean_df = clean_df.drop_duplicates().copy()

# double check all the duplicates have been dropped
print(len(clean_df))
print(clean_df.duplicated().sum())

# find and inspect negative vales  

negative_quantity_count = (clean_df["quantity"] < 0).sum()
zero_quantity_count = (clean_df["quantity"] == 0).sum()

print("negative quantities:", negative_quantity_count)
print("zero quantities:", zero_quantity_count)


# inspecting negatives
negative_quantity_rows = clean_df[clean_df["quantity"] < 0]

print(
    negative_quantity_rows[
        ["invoiceno", "stockcode", "description", "quantity", "unitprice"]
    ].head(10)
)

# all these contain a C in the invoice number which tells us cancellations, but we should check if theres any without the C  
negative_without_c = clean_df[
    (clean_df["quantity"] < 0) &
    (~clean_df["invoiceno"].str.startswith("C"))
]

print("negative quantities without C:", len(negative_without_c))
print(negative_without_c.head(10))

print(negative_without_c["unitprice"].value_counts())
# we find some rows without c have 0 unit price, not contrivuting to revenue, with descrptions saying 'check', 'damages', most likley inventory adjustments, we can drop these rows

#check if cancelations have noneagtive quantities 
cancelled_with_nonnegative_quantity = clean_df[
    clean_df["invoiceno"].str.startswith("C") &
    (clean_df["quantity"] >= 0)
]
# all are 0 unit price 


print(
    "cancelled invoices with nonnegative quantities:",
    len(cancelled_with_nonnegative_quantity)
)

print(cancelled_with_nonnegative_quantity.head())

negative_price_count = (clean_df["unitprice"] < 0).sum()
zero_price_count = (clean_df["unitprice"] == 0).sum()

print("negative unit prices:", negative_price_count)
print("zero unit prices:", zero_price_count)

# two rows contain negative prices, further inspection is needed to find out why theyre negative 


negative_price_rows = clean_df[clean_df["unitprice"] < 0]

print(negative_price_rows)
# theyre just accounting adjustment, not sales 

zero_price_rows = clean_df[clean_df["unitprice"] == 0]

print(zero_price_rows.head(20))

#not any correlation betwee the zero priced rows, further inspection is needed to find out why theyre zero priced and if not to drop them from the dataset 
print("positive quantity:", (zero_price_rows["quantity"] > 0).sum())
print("negative quantity:", (zero_price_rows["quantity"] < 0).sum())
print("missing customer ID:", zero_price_rows["customerid"].isna().sum())
print("known customer ID:", zero_price_rows["customerid"].notna().sum())

#mixture of damages, check, and ?. seperating them into their own dataset can allow data preservation while not effecting the overall analysis of our dataset

# completed paid sales
sales_df = clean_df[
    (clean_df["quantity"] > 0) &
    (clean_df["unitprice"] > 0)
].copy()

# zero-priced records for documentation or separate analysis
zero_price_df = clean_df[
    clean_df["unitprice"] == 0
].copy()

# double checking our sales dataset has no zer or negative values 
print("rows in clean dataset:", len(clean_df))
print("rows in paid-sales dataset:", len(sales_df))
print("negative quantities:", (sales_df["quantity"] < 0).sum())
print("zero or negative prices:", (sales_df["unitprice"] <= 0).sum())

# creating a new column for revenue  

sales_df["revenue"] = sales_df["quantity"] * sales_df["unitprice"]

# making sure the revenue column is working correctly

print(
    sales_df[
        ["invoiceno", "description", "quantity", "unitprice", "revenue"]
    ].head(10)
)

print(sales_df["revenue"].describe())
# this shows the distrubtion of revenue, we can see a pattern of small number of high revnue transacation that could be skewing the data, further investigation is needed

largest_revenue_rows = sales_df.nlargest(10, "revenue")

print(
    largest_revenue_rows[
        [
            "invoiceno",
            "stockcode",
            "description",
            "quantity",
            "unitprice",
            "customerid",
            "country",
            "revenue"
        ]
    ]
)

# a few transactions that werent related to sales were included in our datraset, further filtering must be needed

nonstandard_codes = sales_df[
    ~sales_df["stockcode"].str.match(r"^\d")
]  
print("\nNonstandard stock codes:")
print(nonstandard_codes["stockcode"].value_counts())

nonstandard_summary = (
    nonstandard_codes
    .groupby("stockcode")
    .agg(
        rows=("stockcode", "size"),
        example_description=("description", "first"),
        total_quantity=("quantity", "sum"),
        total_revenue=("revenue", "sum")
    )
    .sort_values("total_revenue", ascending=False)
)

print(nonstandard_summary.to_string())

non_product_codes = [
    "DOT",
    "POST",
    "M",
    "AMAZONFEE",
    "B",
    "C2",
    "BANK CHARGES",
    "S",
    "GIFT_0001_10",
    "GIFT_0001_20",
    "GIFT_0001_30",
    "GIFT_0001_40",
    "GIFT_0001_50"
]

product_sales_df = sales_df[
    ~sales_df["stockcode"].isin(non_product_codes)
].copy()


print("Paid transaction rows:", len(sales_df))
print("Product-sale rows:", len(product_sales_df))
print("Excluded non-product rows:", len(sales_df) - len(product_sales_df))

# anaylsis of product sales data

print("Start date:", product_sales_df["invoicedate"].min())
print("End date:", product_sales_df["invoicedate"].max())
print("Total product revenue:", product_sales_df["revenue"].sum())
print("Unique invoices:", product_sales_df["invoiceno"].nunique())
print("Unique products:", product_sales_df["stockcode"].nunique())
print("Countries:", product_sales_df["country"].nunique())


product_sales_df["year_month"] = (
    product_sales_df["invoicedate"].dt.to_period("M")
)

monthly_revenue = (
    product_sales_df
    .groupby("year_month")["revenue"]
    .sum()
)

print(monthly_revenue) 

# convert the grouped results into a dataframe for plotting
monthly_revenue_df = monthly_revenue.reset_index()

# convert period values into timestamps
monthly_revenue_df["year_month"] = (
    monthly_revenue_df["year_month"].dt.to_timestamp()
)

plt.figure(figsize=(12, 6))

sns.lineplot(
    data=monthly_revenue_df,
    x="year_month",
    y="revenue",
    marker="o"
)

plt.title("Monthly Product Revenue")
plt.xlabel("Month")
plt.ylabel("Revenue (£)")
plt.xticks(rotation=45)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
# the sharp decline in the last part of the graph is misleading since only 9 days of that month are avaible giving us an uncomplete picure of the revenue in month 12

monthly_orders = (
    product_sales_df
    .groupby("year_month")["invoiceno"]
    .nunique()
)

print(monthly_orders)

# creating a monthly average revenue

monthly_aov = monthly_revenue / monthly_orders

print(monthly_aov.round(2))

# visulizing monthy order volume

monthly_orders_df = monthly_orders.reset_index()
monthly_orders_df["year_month"] = (
    monthly_orders_df["year_month"].dt.to_timestamp()
)

plt.figure(figsize=(12, 6))

sns.lineplot(
    data=monthly_orders_df,
    x="year_month",
    y="invoiceno",
    marker="o",
    color="orange"
)

plt.title("Monthly Order Volume")
plt.xlabel("Month")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# product summary 
product_summary = (
    product_sales_df
    .groupby(["stockcode", "description"])
    .agg(
        units_sold=("quantity", "sum"),
        total_revenue=("revenue", "sum"),
        number_of_orders=("invoiceno", "nunique")
    )
    .reset_index()
)

print(
    product_summary
    .sort_values("total_revenue", ascending=False)
    .head(10)
)

# top 10 products by revenue visualization 
top_products_revenue = (
    product_summary
    .nlargest(10, "total_revenue")
    .sort_values("total_revenue")
)

plt.figure(figsize=(12, 7))

sns.barplot(
    data=top_products_revenue,
    x="total_revenue",
    y="description",
    color="steelblue"
)

plt.title("Top 10 Products by Revenue")
plt.xlabel("Total Revenue (£)")
plt.ylabel("Product")
plt.tight_layout()
plt.show()

# country summary
country_summary = (
    product_sales_df
    .groupby("country")
    .agg(
        total_revenue=("revenue", "sum"),
        number_of_orders=("invoiceno", "nunique"),
        units_sold=("quantity", "sum"),
        unique_customers=("customerid", "nunique")
    )
    .sort_values("total_revenue", ascending=False)
)

print(country_summary.head(10))

# further analysis of each countries market

country_summary["revenue_share_pct"] = (
    country_summary["total_revenue"]
    / country_summary["total_revenue"].sum()
    * 100
)

country_summary["average_order_value"] = (
    country_summary["total_revenue"]
    / country_summary["number_of_orders"]
)

print(country_summary.head(10).round(2))

# splitting the markets would result in better visualization of the data, using an intenrational market and UK as the domestic market we can better understand the markets outside of the UK

international_countries = (
    country_summary
    .drop(index="United Kingdom")
    .nlargest(10, "total_revenue")
    .sort_values("total_revenue")
    .reset_index()
)

plt.figure(figsize=(11, 6))

sns.barplot(
    data=international_countries,
    x="total_revenue",
    y="country",
    color="seagreen"
)

plt.title("Top International Markets by Product Revenue")
plt.xlabel("Total Revenue (£)")
plt.ylabel("Country")
plt.tight_layout()
plt.show()

# analysis of customers can provide useful inisghts 
known_customer_revenue = product_sales_df.loc[
    product_sales_df["customerid"].notna(),
    "revenue"
].sum()

unknown_customer_revenue = product_sales_df.loc[
    product_sales_df["customerid"].isna(),
    "revenue"
].sum()

total_revenue = product_sales_df["revenue"].sum()

print("Known-customer revenue:", round(known_customer_revenue, 2))
print("Unknown-customer revenue:", round(unknown_customer_revenue, 2))
print(
    "Unknown-customer revenue percentage:",
    round((unknown_customer_revenue / total_revenue) * 100, 2),
    "%"
)
# our visualization only includes known customers representing 85.26% of our total product revenue

customer_sales_df = product_sales_df.dropna(
    subset=["customerid"]
).copy()

customer_summary = (
    customer_sales_df
    .groupby("customerid")
    .agg(
        country=("country", "first"),
        total_revenue=("revenue", "sum"),
        number_of_orders=("invoiceno", "nunique"),
        units_purchased=("quantity", "sum")
    )
)

customer_summary["average_order_value"] = (
    customer_summary["total_revenue"] /
    customer_summary["number_of_orders"]
)

print(
    customer_summary
    .sort_values("total_revenue", ascending=False)
    .head(10)
)

#finding the top 10 customers by revenue and visualizing

top_10_customers = (
    customer_summary
    .nlargest(10, "total_revenue")
)

top_10_revenue = top_10_customers["total_revenue"].sum()
all_known_customer_revenue = customer_summary["total_revenue"].sum()

top_10_share = (
    top_10_revenue / all_known_customer_revenue
) * 100

print("Top 10 customer revenue:", round(top_10_revenue, 2))
print("Top 10 share of known-customer revenue:", round(top_10_share, 2), "%")


top_customers_plot = (
    top_10_customers
    .reset_index()
    .sort_values("total_revenue")
)

top_customers_plot["customerid"] = (
    top_customers_plot["customerid"].astype(str)
)

plt.figure(figsize=(10, 6))

sns.barplot(
    data=top_customers_plot,
    x="total_revenue",
    y="customerid",
    color="mediumpurple"
)

plt.title("Top 10 Customers by Product Revenue")
plt.xlabel("Total Revenue (£)")
plt.ylabel("Customer ID")
plt.tight_layout()
plt.show()