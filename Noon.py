#!/usr/bin/env python
# coding: utf-8

# ## تحميل المكتبات المطلوبة

# In[1]:


# Install required libraries
get_ipython().system('pip install google_play_scraper')
get_ipython().system('pip install pandas')
get_ipython().system('pip install matplotlib')
get_ipython().system('pip install wordcloud')
get_ipython().system('pip install arabic_reshaper')
get_ipython().system('pip install nbconvert[webpdf]')

print("Done successfully!")


# ## تجهيز الأدوات المستخدمة

# In[2]:


import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from google_play_scraper import app, reviews, Sort
import arabic_reshaper
from collections import Counter


# ## كتابة رابط التطبيق وحجم البيانات المطلوب

# In[3]:


# Specify the app ID for the desired app
app_id = 'com.noon.buyerapp'  # Replace with the app ID

# Set the number of reviews to extract
num_reviews = 80000


# In[4]:


# Scrape the reviews from Google Play (supporting Arabic content)
result, _ = reviews(
    app_id=app_id,
    lang='ar',  # Set the language to Arabic
    country='us',
    sort=Sort.NEWEST,
    count=num_reviews
)


# ## تجهيز البيانات وحفظ نسخها منها بصيغة

# In[5]:


# Convert the result to a list of reviews
reviews_list = list(result)

# Create a data frame from the scraped reviews
df = pd.DataFrame(reviews_list)

# Save the reviews as a CSV file with UTF-8 encoding
df.to_csv('Noon-reviews1.csv', index=False, encoding='utf-8-sig')

print("Reviews extracted and saved successfully!")


# ###### تستخدم النسخة المحفوظة CSV
# للمراجعة وربط البيانات مع الأدوات الأخرى مثل  Power BI

# ## تحديد الشهور التي حازت على اكثر التعليقات

# In[6]:


import calendar

# Number of content per Month
df['at_month'] = pd.to_datetime(df['at']).dt.month
content_per_month = df['at_month'].value_counts().sort_index()

month_names = [calendar.month_name[i] for i in content_per_month.index]

plt.figure(figsize=(10, 5))
bars = plt.bar(month_names, content_per_month.values)
plt.xlabel('Month')
plt.ylabel('Number of Content')  
plt.title(' ') # Remove the Title from the Chart
plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability

# Remove the numbers from the y-axis
plt.gca().axes.yaxis.set_ticklabels([])

# Remove the chart frame
plt.box(False)

# Add labels above the month columns
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + height * 0.05, str(height),
             ha='center', va='bottom', fontweight='bold')

plt.show()


# In[7]:


df.info()


# #### نجد هنا ان أكثر التعلقيات والمراجعات جاءت في شهر فبراير 

# ## تحديد أوقات تفاعل المستخدمين خلال اليوم

# In[8]:


# Convert Arabic content to readable format
df['content_reshaped'] = df['content'].apply(lambda x: arabic_reshaper.reshape(x))

# Number of content per Hour
df['at_hour'] = pd.to_datetime(df['at']).dt.strftime('%H')  # Format the hour as 24-hour format
content_per_hour = df['at_hour'].value_counts().sort_index()

plt.figure(figsize=(10, 5))
plt.plot(content_per_hour.index, content_per_hour.values, marker='o')
plt.xlabel('Hour')
plt.ylabel('Number of Content')
plt.title('')

# Remove the numbers from the y-axis
plt.gca().axes.yaxis.set_ticklabels([])

# Remove the chart frame
plt.box(False)

# Add labels above the line with bolder font and padding
for i, content in enumerate(content_per_hour.values):
    plt.text(content_per_hour.index[i], content + content * 0.02, content, ha='center', va='bottom', fontweight='bold')

plt.show()


# #### تأتي نسبة 33% من المراجعات على التطبيق خلال الساعة 4م إلى 9م 

# ## نستعرض عدد التقييمات  بحيث عدد النجوم

# In[9]:


# Number of content per score
content_per_score = df['score'].value_counts().sort_index()
plt.figure(figsize=(10, 5))
bars = plt.bar(content_per_score.index, content_per_score.values)
plt.xlabel('Score')
plt.ylabel('Number of Content')
plt.title('Number of Content per Score')

# Remove the numbers from the y-axis
plt.gca().axes.yaxis.set_ticklabels([])

# Remove the chart frame
plt.box(False)

# Add labels above the columns
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 5, str(int(height)), ha='center', va='bottom')

plt.show()


# ## نقسيم التتقييمات إلى إيجابي وسلبي ومحايد

# ##### التقسيم يتم من خلال تحديد التقييم من 1 إلى 2 (سلبي) ومن 3 إلى 4 (محايد) و5 إجابي

# In[10]:


df['sentiment'] = df['score'].apply(lambda score: 'Negative' if score <= 2 else 'Natural' if score <= 4 else 'Positive')
sentiment_counts = df['sentiment'].value_counts()

plt.figure(figsize=(8, 8))
colors = ['#4CAF50', '#FF5252', '#FFC107']
patches, texts, autotexts = plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90,
                                    colors=colors, wedgeprops={'edgecolor': 'white'}, textprops={'color': 'white', 'weight': 'bold'})
plt.title('Sentiment Distribution')
plt.setp(autotexts, backgroundcolor='gray')

# Add numbers beside the legend
legend_labels = [f'{label} ({count})' for label, count in zip(sentiment_counts.index, sentiment_counts.values)]
plt.legend(patches, legend_labels, title='Sentiment', loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=3)

plt.axis('equal')
plt.show()


# ## نوضح أكثر الجمل المستخدمة في المراجعات

# In[11]:


# Top 10 repeated paragraphs
top_10_paragraphs = df['content_reshaped'].value_counts().head(10).reset_index()
top_10_paragraphs.columns = ['Paragraph', 'Count']

# Display the top 10 repeated paragraphs
for index, row in top_10_paragraphs.iterrows():
    print(f"{row['Paragraph']}: {row['Count']}")


# ## نجد بعض الجمل التي تتكرر في جميع التقييمات

# In[12]:


import pandas as pd

# Create a pivot table to count the occurrences of each paragraph for each score
top_10_paragraphs = pd.pivot_table(df, index='content_reshaped', columns='score', aggfunc='size', fill_value=0)
top_10_paragraphs.columns = ['Score ' + str(col) for col in top_10_paragraphs.columns]

# Sort the paragraphs by the total count across all scores
top_10_paragraphs['Total Count'] = top_10_paragraphs.sum(axis=1)
top_10_paragraphs = top_10_paragraphs.sort_values(by='Total Count', ascending=False).head(10)

# Display the top 10 repeated paragraphs for each score as a table
print(top_10_paragraphs)

