#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# pip install numpy
# pip install pandas
# pip install matplotlib
# pip install seaborl


# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# In[2]:


df = pd.read_excel("Expanded_data_with_more_features.excel")
print(df.head)


# In[3]:


df = pd.read_excel("C:\Users\lenovo\Downloads\archive.zip")
print(df.head())


# In[4]:


df = pd.read_zip("archive.zip")
print(df.head())


# In[5]:


df = pd.read_csv("Expanded_data_with_more_features.csv")
print(df.head())


# In[7]:


df=pd.read_csv("Expanded_data_with_more_features.csv.zip")
print(df.head())


# In[8]:


df.describe()


# In[9]:


df.info()


# In[10]:


df.df.idnull().sum()


# In[11]:


df.isnull().sum()


# # drop unnamed column

# In[13]:


df = df.drop("Unnamed: 0",axis= 1)
print(df.head())


# # change weekly studies hour

# In[15]:


df["WklyStudyHours"] = df["WklyStudyHours"].str.replace("5 - 10","5-15")
df.head()


# # gender distribution

# In[1]:


cns.countplot(data = df, x = "Gender")
plt.show()


# In[2]:


sns.countplot(data = df, x = "Gender")
plt.show()


# In[5]:


import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_csv("Expanded_data_with_more_features.csv.zip")
print(df.head())
sns.countplot(data = df, x = "Gender")
plt.show()


# In[6]:


df.describe()
print(df.head())


# In[7]:


df.describe()


# # change weekly

# In[8]:


df["WklyStudyHours"] = df["WklyStudyHours"].str.replace("5 - 10","5-15")
df.head()


# In[22]:


plt.figure(figsize=(5,5))
ax=sns.countplot(data = df, x = "Gender")
ax.bar_label(ax.containers[0])
plt.title("Gender Count")
plt.show()


# #from the above chart we have analyzed that the number of females is grater than males

# # chart based on how parent education is affecting

# In[13]:


gb = df.groupby("ParentEduc").agg({"MathScore":'mean',"ReadingScore":'mean',"WritingScore":'mean'})
print(gb)


# In[25]:


sns.heatmap(gb,annot=True)
plt.figure(figsize=(4,4))
plt.show()

# from the above chart the education of the parents have a good impact  on their chil
# # Chart based on parentt marital status

# In[19]:


gb1 = df.groupby("ParentMaritalStatus").agg({"MathScore":'mean',"ReadingScore":'mean',"WritingScore":'mean'})
print(gb1)


# In[27]:


sns.heatmap(gb1,annot=True)
plt.figure(figsize=(4,4))
plt.show()

# negligible impact on their children
# In[ ]:




