###########  DATA VISUALIZATION  ##########

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# read file
data = pd.read_excel(r"C:\Users\prash\OneDrive\Desktop\Medical_Inventory_Masked raw.xlsx")

data.info()

#### UNIVARIATE  ######

# histogram

# Histogram of Quantity 
plt.figure(figsize =( 8,5))
sns.histplot(data['Quantity'],bins =10 ,kde =True)
plt.title('Histogram of Quantity')
plt.xlabel('Quantity')
plt.show()

# Box plot
# Department vs Final Sales
plt.figure(figsize =(8 ,5))
sns.boxplot(x='Dept',y='Final_Sales',data=data)
plt.title('Final Sales Distribution by Department')
plt.xlabel('Dept')
plt.ylabel('Final_Sales')
plt.show()

# Detpartment vs Quantity
plt.figure(figsize =(8 ,5))
sns.boxplot(x='Dept',y='Quantity',data=data)
plt.title('Quantity Distribution by Department')
plt.xlabel('Dept')
plt.ylabel('Quantity')
plt.show()



# KDE plot
#  KDE Plot of Quantity

plt.figure(figsize=(8,5))
sns.kdeplot(data['Quantity'],shade =True ,color='pink')
plt.title('KDE Plot of Quantity')
plt.xlabel('Quantity')
plt.ylabel('Density')
plt.show()

####### BIVARIATE  #######

# Scatter plot
grouped = (
    data.groupby(['Dept' ,'SubCat' ,'Typeofsales'])
      .agg({
          'Quantity':'sum',
          'Final_Cost':'sum',
          'Final_Sales':'sum',
          'ReturnQuantity':'sum'
       })
       .reset_index() 
)
grouped.head()

# Generate the clear plot using alpha blending and hue 
# Quantity vs Final Sales
plt.figure(figsize=(10,6))
sns.scatterplot(data=grouped ,x='Quantity',y='Final_Sales',hue ='SubCat',size=100)
plt.title('Quantity vs Final_Sales by SubCat')
plt.xlabel('Total Quantity Sold')
plt.ylabel('Total Final Sales')
plt.legend(bbox_to_anchor=(1.05,1),loc ='upper left')
plt.tight_layout()
plt.show()


# Quantity vs ReturnQuantity
plt.figure(figsize=(10,6))
sns.scatterplot(data=grouped ,x='Quantity',y='ReturnQuantity',hue ='Dept',size=120)
plt.title('Return Quantity vs Quantity by Department')
plt.xlabel('Total Quantity')
plt.ylabel('Total Return Quantity')
plt.tight_layout()
plt.show()


# Quantity vs  Final Cost
plt.figure(figsize=(10,6))
sns.scatterplot(data=grouped ,x='Quantity',y='Final_Cost',hue ='Typeofsales',size=120)
plt.title('Final Cost vs Quantity by Department')
plt.xlabel('Total Quantity')
plt.ylabel('Total Final Cost')
plt.tight_layout()
plt.show()





######### MULTIVAIATE #######

# Pairs plot

numeric_cols =['Quantity', 'ReturnQuantity', 'Final_Cost', 'Final_Sales', 'RtnMRP']

plt.figure(figsize=(10, 8))
sns.pairplot(data[numeric_cols], diag_kind='kde', plot_kws={'alpha':0.8, 's':80, 'edgecolor':'k'})
plt.suptitle('Pair Plot of Numeric Variables', y=1.02, fontsize=14)
plt.show()




# Heatmap Plot

corr = data[numeric_cols].corr()

plt.figure(figsize=(8,6))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Heatmap of Correlations Between Numeric Variables', fontsize=14)
plt.show()










