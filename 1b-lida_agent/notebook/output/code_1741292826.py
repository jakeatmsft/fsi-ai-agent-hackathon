import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# solution plan
# i. Filter the dataset to include only rows where 'City_Miles_Per_Gallon' and 'Highway_Miles_Per_Gallon' are between 0 and 100.
# ii. Create a scatter plot to visualize the relationship between 'City_Miles_Per_Gallon' and 'Highway_Miles_Per_Gallon'.
# iii. Add a regression line to identify trends.
# iv. Ensure axis labels are legible.

def plot(data: pd.DataFrame):
    # Filter the dataset
    data_filtered = data[(data['City_Miles_Per_Gallon'] >= 0) & (data['City_Miles_Per_Gallon'] <= 100) &
                         (data['Highway_Miles_Per_Gallon'] >= 0) & (data['Highway_Miles_Per_Gallon'] <= 100)]
    
    # Create scatter plot with regression line
    plt.figure(figsize=(10, 6))
    scatter_plot = sns.scatterplot(data=data_filtered, x='City_Miles_Per_Gallon', y='Highway_Miles_Per_Gallon', hue='Type', palette='viridis')
    sns.regplot(data=data_filtered, x='City_Miles_Per_Gallon', y='Highway_Miles_Per_Gallon', scatter=False, ax=scatter_plot)

    # Add labels and title
    plt.xlabel('City Miles Per Gallon')
    plt.ylabel('Highway Miles Per Gallon')
    plt.title('What are the key trends regarding mpg for sales data set MPG range 0-100?', wrap=True)
    plt.legend(title='Car Type')
    
    return plt

chart = plot(data)