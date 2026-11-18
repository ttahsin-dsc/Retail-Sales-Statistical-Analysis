import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

#Task 1 - Data Integration

#set the file path 
file_path = Path(__file__).resolve().parent
output_folder = file_path

#Import the 4 datasets given 
store_a = pd.read_csv(file_path / "Store_A.csv")
store_b = pd.read_csv(file_path / "Store_B.csv")
store_c = pd.read_csv(file_path / "Store_C.csv")
pricing = pd.read_csv(file_path / "ProductPricing.csv")

#checking the first few rows of each dataset
print("Store A preview:")
print(store_a.head())

print("\nStore B preview:")
print(store_b.head())

print("\nStore C Preview:")
print(store_c.head())

print("\nProduct Pricing Preview: ")
print(pricing.head())

#merge the three store datasets into single dataset
combined_stores = pd.concat([store_a, store_b, store_c], ignore_index=True) 
#convert date column to datetime format
combined_stores["Date"] = pd.to_datetime(combined_stores["Date"],errors="coerce") 

#merge the combined store dataset with the pricing dataset
final_dataset = pd.merge(
    combined_stores,
    pricing,
    on="Product",
    how="left"
)

#creating sales column using Quantity and sellingprice
final_dataset["Sales"] = final_dataset["Quantity"] * final_dataset["SellingPrice"]

#creating a profit column
final_dataset["Profit"] = final_dataset["Quantity"] * (
    final_dataset["SellingPrice"] - final_dataset["CostPrice"]
)

#check final dataset structure
print("\nCombined Stores Shape:", combined_stores.shape)
print("Pricing Data Shape:", pricing.shape)
print("Final Dataset Shape:", final_dataset.shape)

print("\nFinal Dataset Preview:")
print(final_dataset.head())

print("\nFinal Dataset Information:")
print(final_dataset.info())

#check for missing values after merging
print("\nMissing values in Final Dataset:")
print(final_dataset.isnull().sum())

#check for duplicated rows
print("\nNumber of Duplicate Rows in Final Dataset: ")
print(final_dataset.duplicated().sum())

print("\nFinal Dataset Data Types:")
print(final_dataset.dtypes)


# !! TASK 2 - Exploratory Data Analysis and summary statistics

#  Total sales per product and store

total_sales_pivot = pd.pivot_table(
    final_dataset,
    values="Sales",
    index="Product",
    columns = "Store",
    aggfunc="sum",
    margins=True,
    margins_name = "Total"
)

print("\nTotal Sales per product and store:")
print(total_sales_pivot)

# Average sales per product and store using pivot table
average_sales_pivot = pd.pivot_table(
    final_dataset,
    values="Sales",
    index="Product",
    columns="Store",
    aggfunc="mean",
    margins=True,
    margins_name="Average"
)

print("\nAverage Sales per product and store:")
print(average_sales_pivot.round(2))

#2(a) (ii) Total daily sales across all stores using pivot table

daily_sales_pivot = pd.pivot_table(
    final_dataset,
    values="Sales",
    index="Date",
    aggfunc="sum"
)

#renaming the sales column to total daily sales
daily_sales_pivot = daily_sales_pivot.rename(columns={"Sales": "Total_Daily_Sales"})

print("\nTotal Daily sales across all stores:")
print(daily_sales_pivot)

#identifying the  best and worst performing product

product_performance = final_dataset.groupby("Product")["Sales"].sum().sort_values(ascending=False)

best_product = product_performance.idxmax()
best_product_sales = product_performance.max()

worst_product = product_performance.idxmin()
worst_product_sales = product_performance.min()

print("\nProduct Performance Based on Total Sales:")
print(product_performance)

print("\nBest Performing product:")
print(f"{best_product} with total sales of £{best_product_sales:,.2f}")

print("\nWorst Performing Product:")
print(f"{worst_product} with total sales of £{worst_product_sales:,.2f}")

#differences in store performance

store_performance = final_dataset.groupby("Store").agg(
    Total_Sales=("Sales", "sum"),
    Average_Sales=("Sales", "mean"),
    Total_Quantity=("Quantity", "sum"),
    Total_Profit=("Profit", "sum")
).sort_values(by="Total_Sales", ascending=False)

#Add percentage contribution of each store to total sales
store_performance["Sales_Contribution_%"] = (
    store_performance["Total_Sales"] / store_performance["Total_Sales"].sum()
) * 100

print("\nStore Performance Summary:")
print(store_performance.round(2))

best_store = store_performance["Total_Sales"].idxmax()
worst_store = store_performance["Total_Sales"].idxmin()

print("\nBest Performing Store:")
print(f"{best_store} generated the highest total sales")

print("\nWorst Performing Store:")
print(f"{worst_store} generated the lowest total sales.")


#Daily sales across all stores using pivot table

daily_store_sales_pivot = pd.pivot_table(
    final_dataset,
    values="Sales",
    index="Date",
    columns="Store",
    aggfunc="sum"
)

print("\nDaily Sales by Store:")
print(daily_store_sales_pivot)




# !! Task 3 - Distribution Analysis !!

sales_data = final_dataset["Sales"].dropna()

#summary statistics
mean_sales = sales_data.mean()
median_sales = sales_data.median()
std_sales = sales_data.std()
skew_sales = stats.skew(sales_data) #skewness
kurt_sales = stats.kurtosis(sales_data, fisher=False) #kurtosis

print("\nSales Distribution summary")
print("Mean:", round(mean_sales, 2))
print("Median:", round(median_sales, 2))
print("Standard Deviation:", round(std_sales, 2))
print("Skewness:", round(skew_sales, 2))
print("Kurtosis:", round(kurt_sales, 2))

# 3(a) Visualisation of sales distribution through appropriate plots
#Histogram and normal density curve

plt.figure(figsize=(8,5))

plt.hist(
    sales_data,
    bins=20,
    density=True,
    edgecolor="black"
)

#creating normal distribution curve using its two main parameters - mean and standard deviation
x = np.linspace(sales_data.min(), sales_data.max(), 100)
y = stats.norm.pdf(x,mean_sales, std_sales)

plt.plot(x,y, label="Normal Density Curve")
plt.axvline(mean_sales, linestyle="--", label="Mean")
plt.axvline(median_sales, linestyle=":", label="Median")

plt.title("Histogram and Normal Density Curve of Sales")
plt.xlabel("Sales(£)")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()

#save figure

sales_histogram_path = output_folder / "sales_histogram_density.png"
plt.savefig(sales_histogram_path)
plt.show()

print("Sales histogram saved at:", sales_histogram_path)

#Boxplot for outlier checking

plt.figure(figsize=(8,4))

plt.boxplot(
    sales_data,
    vert=False,
    patch_artist=True
)

plt.title("Boxplot of Sales")
plt.xlabel("Sales (£)")
plt.tight_layout()

#save figure
sales_boxplot_path = output_folder / "sales_boxplot.png"
plt.savefig(sales_boxplot_path)
plt.show()

print("Sales boxplot saved at:", sales_boxplot_path)


# 3(b) - Q-Q plot to assess normality

plt.figure(figsize=(6,6))

stats.probplot(
    sales_data,
    dist="norm",
    plot=plt
)

plt.title("Q-Q Plot of Sales")
plt.xlabel("Theoretical Quantiles")
plt.ylabel("Sample Quantiles")
plt.tight_layout()

#save figure
sales_qqplot_path = output_folder / "sales_qqplot.png"
plt.savefig(sales_qqplot_path)
plt.show()

print("Sales Q-Q plot saved at:", sales_qqplot_path)

# 3(c) - Statistical test - Shapiro-Wilk test

stat, p = stats.shapiro(sales_data)

print("\nShapiro-Wilk Normality Test:")
print("H0: The sales data is normally distributed")
print("H1: The sales data is not normally distributed.")
print(f"Statistic = {stat:.4f}")
print(f"P-value = {p:.6e}")

#Interpretation
if p > 0.05:
    print("The data seems to be normally distributed approximately. Hence, I fail to reject H0")
else:
    print("The data is not normally distributed. Reject H0.")

#Z-score to detetct outliers
sales_zscore_data = final_dataset.copy()
sales_zscore_data["Sales_Zscore"] = stats.zscore(sales_zscore_data["Sales"])

# Quartiles to detect outliers
q1 = np.percentile(sales_zscore_data["Sales"], 25)
q2 = np.percentile(sales_zscore_data["Sales"], 50)
q3 = np.percentile(sales_zscore_data["Sales"], 75)

print("\nSales Quartiles:")
print("Q1:", round(q1,2))
print("Q2/Median:", round(q2,2))
print("Q3:", round(q3, 2))


z_threshold = 3 #z-score threshold
outlier_condition = (
    (sales_zscore_data["Sales_Zscore"] > z_threshold) |
    (sales_zscore_data["Sales_Zscore"] < -z_threshold)
)

sales_zscore_outliers = sales_zscore_data[outlier_condition]

print("\nZ-score outlier check:")
print("z-score threshold used:", z_threshold)
print("Number of extreme outliers detected:", len(sales_zscore_outliers))

if len(sales_zscore_outliers) > 0:
    print("\nExtreme outliers detected:")
    print(sales_zscore_outliers[["Date", "Product", "Store", "Sales", "Sales_Zscore"]])
else:
    print("No outliers were detected using z-score method")



# !! Task 4 - Time series Analysis

# 4(a) Daily totals - aggregate sales by date

daily_sales = final_dataset.groupby("Date")["Sales"].sum().reset_index()
daily_sales = daily_sales.rename(columns={"Sales": "Total_Daily_Sales"}) # renaming sales column
daily_sales = daily_sales.sort_values("Date") #sorting by date so that time series shows in correct order

print("\nDaily Sales Totals:")
print(daily_sales)

#summary statistics for daily sales
print("\nDaily Sales Summary Statistics:")
print(daily_sales["Total_Daily_Sales"].describe())

print("\nHighest Daily Sales:")
print(daily_sales.loc[daily_sales["Total_Daily_Sales"].idxmax()])

print("\nLowest Daily Sales:")
print(daily_sales.loc[daily_sales["Total_Daily_Sales"].idxmin()])



# 4(b) Plot daily sales time series

plt.figure(figsize=(10,5))

plt.plot(
    daily_sales["Date"],
    daily_sales["Total_Daily_Sales"],
    marker="o",
    label="Daily Sales"
)

plt.title("Daily total sales across all stores")
plt.xlabel("Date")
plt.ylabel("Total Sales (£)")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

daily_sales_plot_path = output_folder / "daily_sales_time_series.png"
plt.savefig(daily_sales_plot_path)
plt.show()

print("Daily sales time series plot saved at:", daily_sales_plot_path)


# Moving average

daily_sales["7_Day_Moving_Average"] = (
    daily_sales["Total_Daily_Sales"].rolling(window=7, min_periods=7).mean()
)

plt.figure(figsize=(10,5))

plt.plot(
    daily_sales["Date"],
    daily_sales["Total_Daily_Sales"],
    marker="o",
    label="Daily Sales"
)

plt.plot(
    daily_sales["Date"],
    daily_sales["7_Day_Moving_Average"],
    linewidth=2,
    label="7 Day Moving Average"
)

plt.title("Daily Sales with 7 Day Moving Average")
plt.xlabel("Date")
plt.ylabel("Total Sales (£)")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

moving_average_plot_path = output_folder / "daily_sales_moving_average.png"
plt.savefig(moving_average_plot_path)
plt.show()

print("Moving average plot saved at:", moving_average_plot_path)


#comparing first and last week average 
first_week_avg = daily_sales["Total_Daily_Sales"].head(7).mean()
last_week_avg = daily_sales["Total_Daily_Sales"].tail(7).mean()

print("\nTrend Check:")
print("Average sales in first 7 days:", round(first_week_avg, 2))
print("Average sales in last 7 days:", round(last_week_avg, 2))

if last_week_avg > first_week_avg:
    print("The average daily sales increased from the first week to the last week")
elif last_week_avg < first_week_avg:
    print("The average daily sales decreased from the first week to the last week")
else:
    print("The average daily sales remained the same from the first week to the last week")

#seasonality(weekly patterns)
daily_sales["Day_of_Week"] = daily_sales["Date"].dt.day_name() #creating a column named 'day of week'
day_order = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]

weekly_pattern = daily_sales.groupby("Day_of_Week")["Total_Daily_Sales"].mean()
weekly_pattern = weekly_pattern.reindex(day_order)

print("\nAverage Daily Sales by Day of Week:")
print(weekly_pattern.round(2))


#plot

plt.figure(figsize=(8,5))

plt.bar(
    weekly_pattern.index,
    weekly_pattern.values
)

plt.title("Average Sales by Day of Week")
plt.xlabel("Day of Week")
plt.ylabel("Average Sales (£)")
plt.xticks(rotation=45)
plt.tight_layout()

weekly_pattern_plot_path = output_folder / "weekly_sales_pattern.png"
plt.savefig(weekly_pattern_plot_path)
plt.show()

print("Weekly sales pattern plot saved at:", weekly_pattern_plot_path)

#variability

daily_sales_range = (
    daily_sales["Total_Daily_Sales"].max() - daily_sales["Total_Daily_Sales"].min()
)

daily_sales_std = daily_sales["Total_Daily_Sales"].std()

print("\nVariability in Daily Sales:")
print("Range of daily sales:", round(daily_sales_range, 2))
print("Standard deviation of daily sales:", round(daily_sales_std, 2))



# !! Task 5 - Inferential Statistical Analysis !!

alpha = 0.05
print("\n Non-Parametric Test: Kruskal-Wallis Test")
print("\nTest 1: Do stores differ in average sales?")

#Hypotheses
print("H0: Store sales distribution are the same for Store_A, Store_B and Store_C")
print("H1: At least one store has a different sales distribution.")

store_a_sales = final_dataset[final_dataset["Store"] == "Store_A"]["Sales"]
store_b_sales = final_dataset[final_dataset["Store"] == "Store_B"]["Sales"]
store_c_sales = final_dataset[final_dataset["Store"] == "Store_C"]["Sales"]


#kruskal-Wallis Test
store_kruskal_result = stats.kruskal(
    store_a_sales,
    store_b_sales,
    store_c_sales
)

print("\nKruskal-Wallis Result for Stores:")
print("Test statistic:", round(store_kruskal_result.statistic, 4))
print("P-value:", round(store_kruskal_result.pvalue, 4))

#decision
if store_kruskal_result.pvalue < alpha:
    print("Decision: Reject H0")
    print("Interpretation: Store sales distributions are significantly different")
else:
    print("Decision:Fail to reject H0")
    print("Interpretation: Store sales distributions are not significantly different.")


#store summary for business interpretation
store_summary = final_dataset.groupby("Store").agg(
    Total_Sales=("Sales","sum"),
    Average_Sales=("Sales","mean"),
    Median_Sales=("Sales","median"),
    Total_Quantity=("Quantity","sum"),
    Total_Profit=("Profit","sum")
)
print("\nStore Summary for Business Interpretation:")
print(store_summary.round(2))



#Test 2 

print("\nTest 2: Do products differ in sales performance?")

# Hypotheses
print("H0: Product sales distributions are the same for all products")
print("H1: At least one product has a different sales distribution.")

# Separating sales data by product
p1_sales = final_dataset[final_dataset["Product"] == "P1"]["Sales"]
p2_sales = final_dataset[final_dataset["Product"] == "P2"]["Sales"]
p3_sales = final_dataset[final_dataset["Product"] == "P3"]["Sales"]
p4_sales = final_dataset[final_dataset["Product"] == "P4"]["Sales"]
p5_sales = final_dataset[final_dataset["Product"] == "P5"]["Sales"]
p6_sales = final_dataset[final_dataset["Product"] == "P6"]["Sales"]

# Applying Kruskal-Wallis Test
product_kruskal_result = stats.kruskal(
    p1_sales,
    p2_sales,
    p3_sales,
    p4_sales,
    p5_sales,
    p6_sales
)

print("\nKruskal-Wallis Result for Products:")
print("Test statistic:", round(product_kruskal_result.statistic, 4))
print("P-value:", round(product_kruskal_result.pvalue, 4))

# Decision
if product_kruskal_result.pvalue < alpha:
    print("Decision: Reject H0")
    print("Interpretation: Product sales distributions are significantly different.")
else:
    print("Decision: Fail to reject H0")
    print("Interpretation: Product sales distributions are not significantly different.")

# Product summary for business interpretation
product_summary = final_dataset.groupby("Product").agg(
    Total_Sales=("Sales", "sum"),
    Average_Sales=("Sales", "mean"),
    Median_Sales=("Sales", "median"),
    Total_Quantity=("Quantity", "sum"),
    Total_Profit=("Profit", "sum")
).sort_values(by="Total_Sales", ascending=False)

print("\nProduct Summary for Business Interpretation:")
print(product_summary.round(2))

