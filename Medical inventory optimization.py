################ Data preprocessing ##################
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
from spicy import stats
from sklearn.preprocessing import PowerTransformer


# Step 1: Load dataset
data = pd.read_excel(r"C:\Users\prash\OneDrive\Desktop\Medical_Inventory_Masked raw.xlsx")
data.info()

data.shape


# Step 2: TYPE CASTING 


# Typecating Columns

#change the data types of multiple columns at same time
data=data.astype({
     'Quantity':'int',
     'ReturnQuantity':'int',
     'Final_Cost':'int',
     'Final_Sales':'int',
     'RtnMRP':'int'
     })
print(data.dtypes)
data['Dateofbill'] =pd.to_datetime(data['Dateofbill'],errors ='coerce')

# Verify data type
print(data.dtypes)


# Step 3: HANDLE DUPLICATES

# Check for duplicates

duplicate_count = data.duplicated().sum()
print("Number of duplicate rows:",duplicate_count)

# View Duplicate rows
duplicate = data[data.duplicated(keep=False)]
print("Duplicate rows:")
print(duplicate)



# Step 4 : Missing value
# Check missing values
data.isnull().sum()

(data.isnull().sum()/data.shape[0])*100

#finding missing values
missing_values=data.isnull().sum()
print(missing_values)

#select only those column which have missing values
only_missing_columns=missing_values[missing_values>0]
print(only_missing_columns)

#handling the missing values using mode imputation from SimpleImputer from sklearn
mode_imputer=SimpleImputer(missing_values=np.nan,strategy='most_frequent')
data[['Formulation','DrugName','SubCat','SubCat1']]=mode_imputer.fit_transform(data[['Formulation','DrugName','SubCat','SubCat1']])

#again check the missing values handeled or not
missing_values=data.isnull().sum()
print(missing_values)



# Step 5: Outlier

# Select the numeric columns
numeric_cols =['Quantity','ReturnQuantity','Final_Cost','Final_Sales','RtnMRP']


# Ensure all Numeric cols are numeric type
for col in numeric_cols:
    data[col] = pd.to_numeric(data[col],errors ='coerce')


#Identify the outlier using IQR method
print("\n Outlier Detection Results(IQR Method):\n")
Outlier_Summary ={}
def detect_outliers_iqr(data, cols):
    result = {}
    for col in cols:
        Q1 = data[col].quantile(0.25)
        Q3 = data[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = data[(data[col] < lower) | (data[col] > upper)][col]
        
        result[col] = {
            'Has_Outliers': not outliers.empty,
            'Outlier_Count': outliers.count(),
            'Outlier_Values': outliers.values.tolist()
        }
    return pd.data(result).T

#Identifying the outlier using visualization method
num_cols = data.select_dtypes(include=['float64', 'int64']).columns

#plot box plot for outlier detection
sns.set(style ='whitegrid' ,palette ='Set2') 

plt.figure(figsize =(12,8))
for i,col in enumerate(numeric_cols,1):
    plt.subplot(2,3,i)
    sns.boxplot(x=data[col],color ='skyblue')
    plt.title(f'Boxplt of {col}')
    

plt.tight_layout()
plt.show()

# Step 6: Zero-variance and Near Zero-variance
#check the zero variance and near zero variance column
data[['Quantity_T','ReturnQuantity_T','Final_Cost_T','Final_Sales_T','RtnMRP_T']].var==0

numeric_cols = data.select_dtypes(include ='number')
variance = numeric_cols.var()
print(variance)

# check the distribution of data
sns.kdeplot(data['Quantity_T'],fill =True,color ='Skyblue')
plt.show()

sns.kdeplot(data['ReturnQuantity_T'],fill =True,color ='skyblue')
plt.show()

sns.kdeplot(data['Final_Cost_T'],fill =True ,color ='skyblue')
plt.show()

sns.kdeplot(data['Final_Sales_T'],fill =True,color ='skyblue')
plt.show()

sns.kdeplot(data['RtnMRP_T'],fill = True,color ='skyblue')
plt.show()

numeric_col = data.select_dtypes(include = ['float64','int64']).columns
print(numeric_col)


#show all kde plot in one figure
plt.figure(figsize=(12,8))
for i,col in enumerate(numeric_col,1):
    plt.subplot(2,3,i)
    sns.kdeplot(data[col],fill=True)
    plt.title(f'KDE Plot: {col}')

plt.tight_layout()
plt.show()


# step 7 : Discritization

data['Quantity_T_bins'] = pd.qcut(data['Quantity_T'], q =3,labels =['low','Medium','High'])
print(data.Quantity_T_bins.value_counts())

data['ReturnQuantity_T_bins'] =pd.qcut(data['ReturnQuantity_T'],q = 3,labels=['low Returns','Moderate Returns','High Returns'])
print(data.ReturnQuantity_T_bins.value_counts())

data['Final_Cost_T_bins'] = pd.qcut(data['Final_Cost_T'],q =3,labels=['Low Cost','Medium Cost','High Cost'])
print(data.Final_Cost_T_bins.value_counts())

data['Final_Sales_T_bins'] =pd.qcut(data['Final_Sales_T'],q= 3,labels =['Low Sale','Medium Sale','High Sale'])
print(data.Final_Sales_T_bins.value_counts())

# View Discritized data
print(data[['Quantity_T', 'Quantity_T_bins', 'ReturnQuantity_T', 'ReturnQuantity_T_bins', 
          'Final_Cost_T', 'Final_Cost_T_bins', 'Final_Sales_T', 'Final_Sales_T_bins']].head())


# Step 8: Transformation

numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns

# Define subplot grid
plt.figure(figsize=(12, 8))

for i, col in enumerate(numeric_cols, 1):
    plt.subplot(2, 3, i)  # (rows, columns, index)
    stats.probplot(data[col], dist="norm", plot=plt)
    plt.title(f'Q–Q Plot: {col}', fontsize=12)

plt.tight_layout()
plt.show()


# Applying Transfromation
pt  = PowerTransformer(method ='yeo-johnson')

data['Quantity_T-YJ'] =pt.fit_transform(data[['Quantity_T']])
data['ReturnQuantity_T-YJ']=pt.fit_transform(data[['ReturnQuantity_T']])
data['Final_Cost_T-YJ']=pt.fit_transform(data[['Final_Cost_T']])
data['Final_Sales_T-YJ']=pt.fit_transform(data[['Final_Sales_T']])
data['RtnMRP_T-YJ']=pt.fit_transform(data[['RtnMRP_T']])

sns.histplot(data['Quantity_T-YJ'],kde =True)
plt.title("After Yeo-Johnson Transformation -Quantity_T")
plt.show()

sns.histplot(data['ReturnQuantity_T-YJ'],kde=True)
plt.title("After Yeo-johnson transformation -ReturnQuantity_T")
plt.show()    

sns.histplot(data['Final_Cost_T-YJ'],kde=True)
plt.title("After Yeo-johnson transformation -Final_Cost_T")
plt.show()    

sns.histplot(data['Final_Sales_T-YJ'],kde=True)
plt.title("After Yeo-johnson transformation -Final_Sales_T")
plt.show()    

sns.histplot(data['RtnMRP_T-YJ'],kde=True)
plt.title("After Yeo-johnson transformation -RtnMRP_T")
plt.show()


# Step 9: Standardisation
data['Quantity_T_std'] =(data['Quantity_T']-data['Quantity_T'].mean())/data['Quantity_T'].std()
data['ReturnQuantity_T_std']=(data['ReturnQuantity_T']-data['ReturnQuantity_T'].mean())/data['ReturnQuantity_T'].std()
data['Final_Cost_T_std']=(data['Final_Cost_T']-data['Final_Cost_T'].mean())/data['Final_Cost_T'].std()
data['Final_Sales_T_std']=(data['Final_Sales_T']-data['Final_Sales_T'].mean())/data['Final_Sales_T'].std()
data['RtnMRP_T_std']=(data['RtnMRP_T']-data['RtnMRP_T'].mean())/data['RtnMRP_T'].std()



# Save the excel file
data.to_excel(r"C:\Users\prash\OneDrive\Desktop\Medical_Inventory_Masked raw.xlsx",index =False)













