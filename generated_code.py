import pandas as pd
import matplotlib.pyplot as plt

# Plot the second column of the RESPONSES.csv file as a scatterplot
plt.scatter(responses_df.index, responses_df.iloc[:, 1])
plt.xlabel("Index")
plt.ylabel("Second Column Value")
plt.title("Scatter plot of the second column of RESPONSES.csv")
plt.savefig("/app/resources/data/response_scatterplot.png")
plt.show()