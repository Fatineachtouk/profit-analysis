# -*- coding: utf-8 -*-
"""Profit analysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1afhDV-K33pBBYemSvuKyIDlKDXfgzmeu

# **Problem Statement:**
 **Goal :**

   The goal of this project is to evaluate a company's financial health using key performance indicators (KPIs) of its financial data. Although some crucial features for a full profit and loss analysis, such as assets, liabilities, and equity,  are missing, the analysis will focus on the available features related to profit and sales. The main objective of this project is to identify the factors impacting profit and explore ways to improve it. Additionally, evaluating the company's financial health will help uncover hidden opportunities or potential risks. This will be achieved by calculating financial ratios such as **Gross Profit Margin, Cost of Goods Sold (COGS) Margin, and Discount Ratios**. These KPIs provide a clear picture of the company's profitability and its efficiency in utilizing resources.

**Dataset Overview:**

   The dataset used for this analysis is sourced from [Microsoft Power BI Sample Financial Dataset](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-financial-download). It contains financial data of a retail company, including  COGS, Gross Sales, Sales, Discounts, along with geographical data, product categories, and time-based data.



**Questions to Address :**
  


1.   Is the business profitable and efficient?
2.   What are the main factors influencing profit, and how significant is their impact?
3.   How do discounts affect profitability?


 To answer the third question, both statistical and financial methods will be used to evaluate how discounts impact profitability. Additionally, a machine learning model will be developed to identify patterns in profitability and find the most important factors influencing it.

# **Data Preparation**
"""

from google.colab import drive
drive.mount('/content/drive')

import os
os.listdir('/content/drive/My Drive/Colab Notebooks')

import pandas as pd

df=pd.read_excel("/content/drive/My Drive/Colab Notebooks/Financial Sample.xlsx")
df

df.columns  #The name of sales column starts with a space!!

df.info()  #To check the type of data and NaN values

"""**Discount Band is the only column with missing values!!!** ->56 in total.

"""

df.groupby("Discount Band")["Discounts"].agg(["min", "max", "mean"])

"""It seems that the Discount Band has some labeling issues, the maximum value in 'Low' should be less than the minimum value in 'Medium', which is not the case here. Since we cannot fill NaN values based on the relationship between Discount Band and Discounts, we will rely only on the Discounts column.

## **Duplicates**:
"""

df.duplicated().value_counts()

"""There are no duplicates, since all values of the previous result are False.

The following code checks if any rows have the same segment, country, discount band, product, date, month number, and year. If so, it creates a list of their indices.
"""

col=['Segment', 'Country', 'Discount Band', 'Product', 'Date','Month Number', 'Year']

duplicates = df.duplicated(subset=col, keep=False)
index = [df.index[duplicates]]
index

"""There are some duplicates, which can be explained by selling different versions of the same product at different prices on the same day in the same country and segment. To avoid redundancy, we can sum the remaining values (aggregation)."""

new_df=df.groupby(col).sum().reset_index()
new_df.head()

"""

The **Date** column is already in datetime format! But there is a redundancy when it come to dates. The three separate columns (day, month, and year) essentially repeat the same information. Also because ALL days are the first of the month! For our profit analysis, we only really need the year and month for the trend analysis.


---

"""

new_df.drop(['Discount Band','Month Name','Date'],inplace=True,axis=1)

"""**The following code will checks whether all numerical values are correct using the formulas of sales, profit and COGS.**"""

import numpy as np
(new_df['Units Sold']*new_df['Sale Price']==new_df['Gross Sales']).value_counts()

new_df[(new_df['Units Sold']*new_df['Sale Price']!=new_df['Gross Sales'])].head()

"""The previous code shows some rows where Units sold multiplied by the Sale price does not equal the Gross profit, This is because these rows contain the same product, but different prices. For example :"""

df.iloc[[543,585]]

"""**Checking the relationship between Sales, Profit and COGS(Cost of goods sold):**"""

(new_df[' Sales'] - new_df['Profit']==new_df['COGS']).value_counts()

new_df[(new_df[' Sales'] - new_df['Profit']!=new_df['COGS'])].head()

"""It seems that these values are correct based on manual calculation, as Sales equals Profit plus COGS.

## **Dummy variables**

Since we have three categorical  columns of type object (Segment, Country and Product), transforming these columns is necessarly for future analysis and modeling !
"""

print(new_df['Country'].unique()) # 5 values
print(new_df['Segment'].unique()) # 5 values
print(new_df['Product'].unique()) # 6 values

"""Since the dataset is small, working with pandas and get_dummies is a good choice."""

new_df=pd.get_dummies(new_df,columns=['Segment','Country','Product'], dtype=int)
new_df.head()

new_df.info() # To make sure all values are numerical and ready for future analysis and modeling.

"""# **Financial KPIs (Trend Analysis):**

The goal of this section is to analyze the profitability and efficiency of the company using three ratios : Gross profit margin, COGS margin and Discount Ratio. The best indicator for an organization's health would be multiple seasons, especially if we can't compare its profitability with competitors. Therefore, the trend analysis will be month based to compare ratios of each month for more clarity.To do so, grouping the data By month is the first step.

**1.   Gross profit margin**

This KPI measures the percentage of revenue remaining after accounting for the cost of goods sold (COGS). It reflects the efficiency of production and pricing.

**FORMULA :**

\begin{equation}
\text{Gross Profit Margin} = \frac{ \text{Profit}}{\text{Net Sales}} \times 100
\end{equation}

 A high gross profit margin indicates efficient operations, while a low margin suggests areas needing improvement (It can impact a company’s bottom line (Net Profit) and means there are areas that can be improved).

 Gross Profit Margin (GPM) reflects:

* **Pricing strategy**

* **Supplier/cost efficiency**

**2.COGS margin:**

the COGS margin ratio represents the percentage of each dollar of revenue generated that is spent on cost of goods sold (COGS).

**Formula :**


\begin{equation}
\text{COGS Margin} = \frac{ \text{Cost of Goods Sold}}{\text{Net Sales}} \times100
\end{equation}

**3.Discount Ratio :**

Discount Ratio helps understand how much the price is reduced on average, and how significant the discounts are in relation to the original sales. High discount ratios might impact overall profitability if not managed carefully.

**Formula :**

\begin{equation}
\text{Discount Ratio} = \frac{\text{Sales Discount}}{\text{Gross Sales}} \times 100
\end{equation}
"""

monthly=new_df.groupby(['Year', 'Month Number']).sum().reset_index()
monthly=monthly[['Year','Month Number', 'Gross Sales','Discounts',' Sales','COGS','Profit']]
monthly['Month-Year']=monthly['Month Number'].astype(str)+'-'+monthly['Year'].astype(str)
monthly.drop(['Year', 'Month Number'],inplace=True,axis=1)
monthly

monthly['GPM']=(monthly['Profit']/monthly[' Sales'])*100 # Gross Profit Margin
monthly['COGSM']=(monthly['COGS']/monthly[' Sales'])*100 # COGS Margin
monthly['DR']=(monthly['Discounts']/monthly['Gross Sales'])*100 # Discount Ratio
monthly

import matplotlib.pyplot as plt

plt.figure(figsize = (8,6))
plt.plot(monthly['Month-Year'],monthly['GPM'],label='Gross Profit Margin')
plt.plot(monthly['Month-Year'],monthly['COGSM'],label='COGS Margin')
plt.plot(monthly['Month-Year'],monthly['DR'],label='Discount Ratio')
plt.xlabel('Month-Year')
plt.xticks(rotation=45)
plt.ylabel('Financial Ratios(%)')
plt.legend()
plt.title('Trend analysis-(Gross profit & COGS margins and discount ratio)')
plt.show()

"""**LIMITATIONS**:

* Expense data are missing, this feature is a big deal for real business analysis,because they account for costs like salaries, marketing, rent...

* Since we only have gross profit margin (not net profit), we can not see the full picture, because operating expenses and taxes are included in our profit.



**Key Insights from the Trend analysis:**

1.  **High COGS, Low Profit Margins:**

  The COGS margin is very high, meaning a large portion of revenue is being spent on the cost of goods sold, and the gross profit margin is low (under 20%).

  **Possible reasons for this:**

    * The company might be paying too much for supplies.

    * Pricing strategy could be too weak.

2. **No Improvement Over Time:**

   The profit margin isn’t showing any segnificant upward trend. This could mean:

  * The business isn’t making changes to reduce costs or optimize pricing.

  * The market is highly competitive, making it hard to raise prices.

   A stagnant profit margin isn’t necessarily bad if the business is stable, but there may be opportunities for growth.

3.  **Discounts and Profitability:**

   There’s a noticeable relationship between discounts and margins:

 *  *When discounts increase → COGS margin also goes up.*

 *  *When discounts increase → Gross profit margin goes down.*  

 **Possible reasons for this:**

   *  Discounts may increase sales volume, they also reduce profitability.

4. **Flat Trends :**

  The trend lines for gross profit margin, COGS margin, and discount ratio are all relatively flat over time. This could mean:

   *  The business has a consistent cost structure and pricing strategy.

   *   No major improvements in efficiency or profitability.

# **EDA**

In this section, we'll analyze feature relationships with Profit through the heatmap and visual plots.

### **Correlation Heatmap :**
"""

correlation_matrix = new_df.corr()
plt.figure(figsize = (8,6))
sns.heatmap(correlation_matrix, cmap = 'coolwarm')
plt.show()

correlation_matrix['Profit'].sort_values(ascending=False) #Since the aim of these analysis is to have a clear picture of the profiability of the company.

"""*  The strongest positive correlations with Profit come from:

 *    Sales (0.80)
 *  Gross Sales (0.78)
 *  COGS (0.72)
 *  Sale Price (0.64).

 These features should be prioritized as they impact the profit the most.

* Among Segments, Government (0.29) and Small Business (0.16) show positive correlations.

* Discounts show a moderate positive correlation (0.42), but ***correlation doesn't imply causation.***

###Discount effect on profit :

Ordinary Least Squares (OLS) regression will help us measure how discounts affect profit. The model assumes a linear relationship between discounts  and profit, which we can represent as:
  $$
\text{Profit} = \beta_0 + \beta_1 \cdot \text{Discounts} + \epsilon
$$  
Where:

  * $β0$(intercept): The expected profit when discounts are zero

  * $β1$(coefficient): How much profit changes for each unit increase in discounts


  * $ϵ$ (error): The difference between predicted and actual profit
"""

import statsmodels.api as sm

X = new_df[['Discounts']]
X = sm.add_constant(X)
y = new_df['Profit']
model = sm.OLS(y, X).fit()
print(model.summary())

"""1. **Interpretation of R-squared (17.5%):**

  17.5% of the variation in profit is explained by discounts. This relatively low value indicates that:

   *  Discounts alone are not a strong predictor of profit.

  *   Other factors (like Sales, COGS, etc.) likely explain the remaining of profit variation.

2. **Discounts Coefficient (β₁ = 0.7470):**

   For every 1-unit increase in discounts, profit increases by 0.75.
This suggests a small but positive effect

   **Possible explanations:**

     * Discounts may drive higher sales volume

3. **P-value (0.000):**

   * The effect is statistically significant (p < 0.05)

   * We can reject the null hypothesis (discounts don't affect profit)

####Profit by Discount :
"""

plt.plot(monthly['Month-Year'], monthly['Discounts'],label='discount')
plt.plot(monthly['Month-Year'], monthly['Profit'],label='Profit')
plt.ylabel('Profit& discount')
plt.xlabel('Month-Year')
plt.xticks(rotation=45)
plt.title('Profit over time')
plt.legend()

plt.bar(monthly['DR'],monthly['Profit'], width = 0.2)
plt.xlabel('Discount Ratio(%)')
plt.ylabel('Profit')
plt.title('Profit over Discount Ratio')

"""Discounts appear to be correlated with profit, which is obvious because customers tend to buy more discounted products. However, the last plot shows that higher discount ratios may lead to lower profit, while lower discount ratios( between 4% and 7%) may lead to higher profit.

Discounts are effective when used strategically, they encourage purchases and can boost revenue. But aggressive discounting can be dangerous and may negatively impact the bottom line( Net profit) if overused. The key is finding the right balance to optimize the profit.

####Binning Method:

To identify the safest discount range that boosts sales without reducing profit, we wll apply the binning method to split our data into intervals. This approach relies exclusively on historical patterns!
"""

labels = ['0-2%', '2-4%', '4-6%', '6-8%', '8-10%', '10-12%', '12%+']
# Create discount ratio bins
bin= pd.DataFrame({'Discount Ratio': monthly['DR'],
                   'Profit': monthly['Profit'],
                   'Discount':monthly['Discounts']
                   })
bin['bins'] = pd.cut(x=bin['Discount Ratio'], bins=[0,2,4,6,8,10,12,20], labels=labels)
bin

plt.bar(bin['bins'],bin['Profit'], width = 0.2)
plt.xlabel('Discount Ratio')
plt.ylabel('Profit')

"""Fantastic! Now we have a clear picture of the safest discount range that increases profit. The analysis shows discounts closest to **4-8%** of gross sales tend to give better results. However, some lower profits still occur within this range (especially 6-8%) as shown in the *Profit over Discount Ratio* barplot, indicating other influencing factors, for example, product differences (some products respond better to discounts than others) and seasonal trends (certain months outperform others even with identical discounts).

####Discount Elasticity :

To measure how sensitive profit is to discount changes, we'll apply the elasticity method to our discount data.By calculating the percentage change in profit divided by the percentage change in discount ratio:

$$
\text{Discount Elasticity} = \frac{\%\Delta \text{Profit}}{\%\Delta \text{Discount Ratio}}
$$

*  If Elasticity > 1 → Discounting is effective (profit grows significantly with discounts).
*  If Elasticity < 1 but > 0 → Discounting has a weak effect.
*  If Elasticity < 0 → Discounting is reducing profit.

The optimal discount range will be where Elasticity is highest but still positive.
"""

monthly['Profit_Change'] = monthly['Profit'].pct_change()
monthly['DR_Change'] = monthly['DR'].pct_change()

monthly['Discount_Elasticity'] = monthly['Profit_Change'] / monthly['DR_Change']

optimal_index = monthly['Discount_Elasticity'].idxmax()
optimal_discount_ratio = monthly.loc[optimal_index, 'DR']
optimal_profit = monthly.loc[optimal_index, 'Profit']
print(f"The optimal discount ratio is {optimal_discount_ratio:.2f}% with a profit of {optimal_profit:.2f}$")
monthly['Discount_Elasticity']

"""Most of the data shows negative elasticity, which means discounting has a negative impact on profit, except for two values: one between 0 and 1 (indicating a weak positive effect of discounting), and another higher than 1 which is the optimal value for maximizing profit, corresponding to a discount ratio of **8.12%**.

### Profit by Segment :
"""

#plot of profit by segments
plt. figure(figsize=(8,6))
plt.bar(df['Segment'], df['Profit'], color="#468eb8")
plt.xlabel('Segment')
plt.ylabel('Profit')
plt.title('Total Profit by Segment')
plt.show()

"""This plot confirms the correlation matrix findings: Government is the most profitable segment (and most strongly correlated with profit), followed by Small Business. The other three segments—Midmarket, Channel Partners, and Enterprise—show significantly lower profitability, with Enterprise actually generating negative profits. Analyzing each segment’s pricing strategies, customer base, and cost structures could help explain these profit patterns.

### Profit by Country :
"""

profit_country = df.groupby('Country')['Profit'].sum().reset_index()
plt. figure(figsize=(8,6))
plt.bar(profit_country['Country'], profit_country['Profit'], color='#e37029')
plt.xlabel('Country')
plt.ylabel('Total Profit')
plt.title('Total Profit by Country')
plt.show()

"""The plot shows France is the most profitable, followed by Germany and Canada. The United States and Mexico are the least profitable. This reveals some surprising patterns. These differences likely come from country-specific tax rules and business regulations, which vary significantly across markets."""

avg_profit_country = df.groupby('Country')['Profit'].mean().reset_index()
plt. figure(figsize=(8,6))
plt.bar(avg_profit_country['Country'], avg_profit_country['Profit'],color='#f59458')
plt.xlabel('Country')
plt.ylabel('Average Profit')
plt.title('Average Profit by Coutry')

"""The plot shows France is the most profitable, followed by Germany and Canada. The United States and Mexico are the least profitable. This matches what we see in the total profit."""

std_profit_country = df.groupby('Country')['Profit'].std().reset_index()
plt. figure(figsize=(8,6))
plt.bar(std_profit_country['Country'], std_profit_country['Profit'],color='#eba275')
plt.xlabel('Country')
plt.ylabel('Variance in Profit')
plt.title('Variance in Profit by Coutry')

"""* Variance tells us how spread out the profits are within each country.
* A high variance means some transactions generate very high or very low profit.
* A low variance suggests profit is more consistent across sales,very high or very low-profit transactions are rare.

Profit is more consistent in Mexico which has the lowest average and total profit.


Germany, France and Canada have higher variance in profit, meaning some sales bring very high profits while others may result in low or even negative profits.This might be due to having some high-value purchases and some low-value purchases.

To make sure all the previous parameters( total,mean and variance in profit ) aren't affected by any other variable we will look at the number of transactions per country, which seem to be the same!
"""

count_profit_country = df.groupby('Country')['Profit'].count().reset_index()
count_profit_country

"""Final review:
* France leads in profitability (high total/average profit) but with a high variance, suggesting a mix of premium and discount sales.
* Germany and Canada show similar patterns.
* Mexico consistently underperforms across all metrics compared to other countries.

###Profit by Product:
"""

profit_prod = df.groupby('Product')['Profit'].sum().reset_index()
plt.bar(profit_prod['Product'], profit_prod['Profit'], color='#6cc4a1')
plt.xlabel('Product')
plt.ylabel('Total Profit')
plt.title('Total Profit by Product')
plt.show()

"""The plot shows **Paseo** is by far the most profitable product, with profits much higher than all others.

 **Amarilla** and **VIT** appear to be mid-range performers, while **Carretera,** **Montana,** and **Velo** are the least profitable.

Possible reasons some products outperform others:
* Cost Differences
* Pricing and discounting
* Sales Volume
* Customer Base
* Operational Factors

#**Key features impacting profit :**

The goal of this part is to identify which features are linked to high and low profit using a machine learning model.

### Random Forest Model:
"""

new_df['Profit margin']=(new_df['Profit']/new_df[' Sales'])*100 # working with profit margin is more efficient for analyzing profitability
new_df.columns

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
X=new_df.drop(['Profit', 'Year','Profit margin'], axis=1) #Independant variables
y = new_df["Profit margin"] # The target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=10)

model = RandomForestRegressor(n_estimators=100, random_state=10)
model.fit(X_train, y_train)

importance = model.feature_importances_
feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": importance}).sort_values("Importance", ascending=False)

print(feature_importance.head(24))

"""*  Channel Partners alone drive ~60% of profit impact, with Enterprise clients adding another 5%.
* COGS (18%) and Sale Price (13%) together account for nearly a third of profit influence. The less it is the better.
*  Surprisingly, discounts barely matter (1.5%).Pricing is more important than  discounting for boosting profitability.

The high importance of Channel Partners (~60%) combined with the insignificance of Units Sold (0.1%) suggests potential data quality issues!

#**References:**

- https://www.wallstreetprep.com/knowledge/cogs-margin/
- https://ascensus-beratung.de/en/encyclopedia/cost-of-goods-ratio-cogs-definition-calculation-and-examples/
- https://www.growthforce.com/blog/how-giving-discounts-can-destroy-your-business-profits#:~:text=Your%20Profit%20Margin%20Takes%20a,made%20up%20with%20future%20opportunities%E2%80%A6
- [https://positivemomentum.com/the-dangers-of-discounting-and-how-to-get-it-right/#:~:text=But while discounting can help,a loss in business revenue](https://positivemomentum.com/the-dangers-of-discounting-and-how-to-get-it-right/#:~:text=But%20while%20discounting%20can%20help,a%20loss%20in%20business%20revenue).
- https://www.simon-kucher.com/en/insights/master-price-elasticity-key-profitable-pricing-strategies
- https://www.savemyexams.com/a-level/business/cie/23/revision-notes/marketing/marketing-analysis/promotional-elasticity-of-demand/
- https://www.investopedia.com/terms/g/gross_profit_margin.asp
- https://priceshape.com/glossary/price-elasticity

BOOK:
  * The Accounting Game: Basic Accounting Fresh from the Lemonade Stand - by Darrell Mullis and Judith Orloff
"""

