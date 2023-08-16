import matplotlib.pyplot as plt
import numpy as np



def line_chart(categories,values,unit,xlabel,ylabel,title,location):
    # Chart data
    categories = categories
    values = values
    
    # Generate color variants from color maps
    # colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(categories)))
    
    # Create line chart
    plt.figure()
    plt.plot(categories, values, marker='o', color='g')
    
    # Add labels and title
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.xticks(rotation=45)
    
    # Add annotations for x-axis labels
    for i, value in enumerate(values):
        plt.annotate(unit+str(value), (categories[i], value), ha='center', va='bottom')
    
    # Automatically adjust the layout
    plt.tight_layout()

    location = '../static/images/charts/Line_'+ location + ".png"
    plt.savefig(location)

def bar_chart(products,values,unit,xlabel,ylabel,title,location):
    
    # Generate color variants from color maps
    # colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(products)))
    
    # Create line chart
    plt.figure()  # Create a new figure
    plt.bar(products, values, color = 'g')
    
    # Add labels and title
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.xticks(rotation=45, ha="right")
    
    # Add annotations for x-axis labels
    for i, value in enumerate(values):
        plt.annotate(unit+str(value), (products[i], value), ha='center', va='bottom')
    
    # Automatically adjust the layout
    plt.tight_layout()
    
    location = '../static/images/charts/Bar_'+ location + ".png"
    plt.savefig(location)
    
    return location

def pie_chart(categories,values,title,location):
    
    total = sum(values)
    sizes = [round(i*100/total, 2) for i in values] if total != 0 else values
    # print(categories)
    # print(sizes)
    # Generate color variants from color maps
    colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(categories)))
    
    # Create pie chart
    plt.figure()
    plt.pie(sizes, labels=categories, colors=colors, autopct='%1.1f%%', startangle=90)
    
    # Add a title
    plt.title(title)
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis('equal')
    
    # Automatically adjust the layout
    plt.tight_layout()
    
    location = '../static/images/charts/Pie_'+ location + ".png"
    plt.savefig(location)
    
    return location