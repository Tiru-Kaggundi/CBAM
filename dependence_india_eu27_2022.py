import pandas as pd
import matplotlib.pyplot as plt

# Load the data from both sheets
sheet1 = pd.read_excel(
    "/Users/tiru/Documents/Documents_new/ML/Research/CBAM/India_EU_bilateral_2022.xlsx",
    sheet_name=0)
sheet2 = pd.read_excel(
    "/Users/tiru/Documents/Documents_new/ML/Research/CBAM/India_EU_bilateral_2022.xlsx",
    sheet_name=1)

# Remove the row with 'TOTAL' before converting the 'Product_code' column to numeric
sheet1 = sheet1[sheet1['Product_code'] != "'TOTAL"]

# Convert 'Product_code' to numeric
sheet1['Product_code'] = pd.to_numeric(sheet1['Product_code'].str.strip("'"))

# Merge the two sheets on the ITC HS 2 digit/Product_code
merged_data = pd.merge(sheet1,
                       sheet2,
                       left_on='Product_code',
                       right_on='ITC HS 2 digit',
                       how='left')

# Normalize the PCI values
min_pci = merged_data['PCI'].min()
max_pci = merged_data['PCI'].max()
merged_data['PCI_normalized'] = (merged_data['PCI'] - min_pci) / (max_pci -
                                                                  min_pci)

# Identifying chapters for labeling
merged_data_filtered = merged_data[merged_data['Product_code'] != 'TOTAL']
top_chapters = merged_data_filtered.sort_values(
    by="European Union (EU 27)'s exports to India in 2022",
    ascending=False).head(12)
high_india_dependence = merged_data_filtered[
    merged_data_filtered['Indias_dependence on EU\'s exports'] > 30]
high_eu_dependence = merged_data_filtered[
    merged_data_filtered['EU27s_dependence on India for its exports'] > 2]
high_pci = merged_data_filtered[merged_data_filtered['PCI_normalized'] > 0.8]
label_chapters = pd.concat(
    [top_chapters, high_india_dependence, high_eu_dependence,
     high_pci]).drop_duplicates()

# Save the merged_data dataframe to an Excel file
merged_data.to_excel(
    "/Users/tiru/Documents/Documents_new/ML/Research/CBAM/merged_India_EU27_bilateral.xlsx",
    index=False)

# Setting the size of the figure
plt.figure(figsize=(15, 10))

# Creating the bubble plot
scatter = plt.scatter(
    merged_data_filtered['Indias_dependence on EU\'s exports'],
    merged_data_filtered['EU27s_dependence on India for its exports'],
    s=merged_data_filtered[
        'European Union (EU 27)\'s exports to India in 2022'] / 1000,
    c=merged_data_filtered['PCI_normalized'],
    cmap='viridis',
    alpha=0.6)

# Annotating the selected chapters
for index, row in label_chapters.iterrows():
    x = row['Indias_dependence on EU\'s exports']
    y = row['EU27s_dependence on India for its exports']
    label = row['Product_code']

    # If label is one of the overlapping ones, adjust its position
    if label in [10, 38]:
        y += .05  # adjust as necessary
    if label in [43, 82]:
        y -= .05  # adjust as necessary

    plt.text(x,
             y,
             label,
             horizontalalignment='center',
             verticalalignment='top',
             fontsize=10,
             color='black',
             fontweight='bold')

# Find a value close to 1 billion USD in EU's exports to India
exports = merged_data['European Union (EU 27)\'s exports to India in 2022']
closest_to_billion = exports.iloc[(exports - 1e6).abs().argsort()[:1]]

# Setting the title, axis labels, and legend
plt.title('EU27\'s Export Dependence on India - CY2022', fontsize=16)
plt.xlabel('Share of Indian Imports from EU27 in total imports by India (%)',
           fontsize=14)
plt.ylabel('Share of EU27\'s Exports to India in total Exports from EU (%)',
           fontsize=14)
size_value = closest_to_billion.values[
    0] / 1000  # scaled down by the same factor as the scatter plot
legend_label = '1 billion USD'
handle = plt.Line2D([0], [0],
                    marker='o',
                    color='maroon',
                    markersize=size_value / 31.62,
                    linestyle='')  # adjust the size as necessary
plt.legend(
    [handle],
    [legend_label],
    #title='Trade Volume in USD',
    loc='lower right',
    labelspacing=2.5)

# Adding a colorbar for the PCI scale
cbar = plt.colorbar(scatter)
cbar.set_label('Product Complexity Index (PCI)', fontsize=14)

# Save the plot with 300 dpi
plt.tight_layout()
plt.savefig(
    "/Users/tiru/Documents/Documents_new/ML/Research/CBAM/India_EU27_trade_dependence_chart.png",
    dpi=300)
plt.show()
