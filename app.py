import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import date
import numpy as np
import plotly.graph_objects as go

#FIGURES FOR DASHBOARD
# **************************************************************************************************************
data = pd.read_excel('data/clean_data.xlsx')

#Number Summaries
data['total_sales'] = data['MntWines'] + data['MntFruits'] + data['MntMeatProducts'] + data['MntFishProducts'] + data['MntSweetProducts'] + data['MntGoldProds']

total_sales = data['total_sales'].sum()
total_purchases = data['total_sales'].count()
wines_sales = data['MntWines'].sum()
fruits_sales = data['MntFruits'].sum()
meat_sales = data['MntMeatProducts'].sum()
fish_sales = data['MntFishProducts'].sum()
sweets_sales =data['MntSweetProducts'].sum()
gold_sales = data['MntGoldProds'].sum()

sales = pd.Series([round(wines_sales/total_sales*100,2), 
                   round(fruits_sales/total_sales*100,2), 
                   round(meat_sales/total_sales*100,2),
                   round(fish_sales/total_sales*100,2),
                   round(sweets_sales/total_sales*100,2),
                   round(gold_sales/total_sales*100,2)], index = ['Wines','Fruits','Meat','Fish','Sweets','Gold']).sort_values()

number_fig = go.Figure(go.Bar(
            x=sales[:],
            y=sales.index,
            orientation='h',
            marker_color='goldenrod'))
annotations = []
for i in sales.index:
    annotations.append(dict(xref='x', yref='y',
                            x=sales[i]*0.5, y=i,
                            text=str(sales[i]) + '%',
                            font=dict(family='Arial', size=14,
                                      color='DarkGreen'),
                            showarrow=False))

number_fig.update_layout(annotations=annotations)
number_fig.update_layout(title='Product Category Purchase Ratio')
number_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
number_fig.update_yaxes(showline=True, linewidth=2, linecolor='black')
number_fig.update_xaxes(visible=False)

number_fig.update_layout(
    font=dict(
        size=20,
        color="DarkGreen"
    )
)
#Product Sales vs Income
conditions = [
    (data['Income'] <= 25000),
    (data['Income'] > 25000) & (data['Income'] <= 75000),
    (data['Income'] > 75000)
    ]

values = ['Low Income', 'Middle Income', 'High Income']
data['Income_Level'] = np.select(conditions, values)

wines_income = pd.DataFrame(data.groupby('Income_Level').MntWines.sum())
fruits_income = pd.DataFrame(data.groupby('Income_Level').MntFruits.sum())
meats_income = pd.DataFrame(data.groupby('Income_Level').MntMeatProducts.sum())
fish_income = pd.DataFrame(data.groupby('Income_Level').MntFishProducts.sum())
sweet_income = pd.DataFrame(data.groupby('Income_Level').MntSweetProducts.sum())
gold_income = pd.DataFrame(data.groupby('Income_Level').MntGoldProds.sum())

merged_data=wines_income.merge(fruits_income, on='Income_Level',how='left') \
    .merge(meats_income, on='Income_Level',how='left') \
    .merge(fish_income, on='Income_Level',how='left')\
    .merge(sweet_income, on='Income_Level',how='left')\
    .merge(gold_income, on='Income_Level',how='left')
merged_data['Income_Level']=merged_data.index
long=merged_data.melt( 
        id_vars=['Income_Level'],
        value_vars= ['MntWines', 'MntMeatProducts','MntGoldProds', 'MntFishProducts',
       'MntSweetProducts', 'MntFruits'],
        var_name='Product',
        value_name='Sales')

sales_income_fig = px.bar(long, x="Product", y="Sales", color="Income_Level", title="Product Sales vs Income Level", color_discrete_map={'High Income':'DarkGreen', 'Middle Income':'DarkSeaGreen', 'Low Income':'wheat'})
sales_income_fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = [0, 1, 2, 3, 4, 5,6],
        ticktext = ['Wines', 'Meat', 'Gold', 'Fish Products', 'Sweets', 'Fruits']
    )
)
sales_income_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
sales_income_fig.update_layout(
    font=dict(
        size=20,
        color="goldenrod"
    )
)

# Age vs Product Breakdown Treemap (Has Dropdown)
# boomers 1946 - 1965
# gen x 1965 - 1980
# Millennials 1981 – 1996
bins = [1939, 1965, 1980, 1996]
gen_name = ['Boomers', 'Gen x', 'Millennials']
data['Gen'] = pd.cut(data['Year_Birth'], bins, labels=gen_name)
data['Total_purchase'] = data['MntWines']+data['MntMeatProducts']+data['MntGoldProds']+data['MntFishProducts']+data['MntSweetProducts']+data['MntFruits']
product_dropdown = [
            {'label': 'Wine', 'value': 'MntWines'},
            {'label': 'Meat', 'value': 'MntMeatProducts'},
            {'label': 'Gold', 'value': 'MntGoldProds'},
            {'label': 'Fish', 'value': 'MntFishProducts'},
            {'label': 'Sweets', 'value': 'MntSweetProducts'},
            {'label': 'Fruits', 'value': 'MntFruits'},
            {'label': 'Total Purchase', 'value' : 'Total_purchase'}
        ]
age_product_fig = px.treemap(data, path=['Gen'], values='Total_purchase',color=data['Gen'],
                            title='Product Purchases by Age',color_discrete_map={'Boomers':'DarkGreen', 'Gen x':'wheat', 'Millennials':'DarkSeaGreen'})
age_product_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
age_product_fig.update_layout(
    font=dict(
        size=20,
        color="DarkGreen"
    )
)
# Sales by Channel Divided by Age
#Generation
tidydf_gen = data.melt( 
            id_vars = 'Gen',
            value_vars = ['NumWebPurchases','NumCatalogPurchases', 'NumStorePurchases'],
            var_name = 'channel', 
            value_name = '# of Sales')
tidydf_gen2= pd.DataFrame(tidydf_gen.groupby(['Gen','channel'])['# of Sales'].sum()).reset_index()
sales_by_channel_gen_fig = px.bar(tidydf_gen2, x="channel", y="# of Sales",
             color='Gen',
             pattern_shape="Gen",
             color_discrete_map={'Boomers':'goldenrod', 'Gen x':'wheat', 'Millennials':'khaki'},
             title='Sales by Channel and Generation',
             labels=dict(channel="# of Purchases per Channel"),
             category_orders={'channel': ["Catalog ", "In Store", "Web/Online"]})
#Age
age_bins = [18, 30, 45, 85]
age_name = ['18-30', '30-45','45-85']
data['agebracket'] = pd.cut(data['Age'], age_bins, labels=age_name)
tidydf_age = data.melt( 
            id_vars = 'agebracket',
            value_vars = ['NumWebPurchases','NumCatalogPurchases', 'NumStorePurchases'],
            var_name = 'channel', 
            value_name = '# of Sales')
tidydf_age2= pd.DataFrame(tidydf_age.groupby(['agebracket','channel'])['# of Sales'].sum()).reset_index()
sales_by_channel_age_fig = px.bar(tidydf_age2, x="channel", y="# of Sales",
             color='agebracket',
             pattern_shape="agebracket",
             color_discrete_map={'18-30':'goldenrod', '30-45':'wheat', '45-85':'khaki'},
             title='Sales by Channel and Age',
             labels=dict(channel="# of Purchases per Channel"))

sales_by_channel_gen_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
sales_by_channel_age_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
sales_by_channel_gen_fig.update_layout(
    font=dict(
        size=20,
        color="DarkGreen"
    )
)
sales_by_channel_age_fig.update_layout(
    font=dict(
        size=20,
        color="DarkGreen"
    )
)
# Bubble Chart Fig
bubble_chart_fig = go.Figure(data=[go.Scatter(
    x=data['Country'], y=data['Total_purchase'],
    mode='markers')
])
bubble_chart_fig = px.scatter_geo(data, locations="Country", color="Country",
                     hover_name="Country", size="Total_purchase",
                     projection="natural earth", title='Bubble Chart of Product Sales by Country',
                     color_discrete_map={'Spain':'DarkGreen', 'USA':'DarkSeaGreen', 'India':'wheat', 'Saudi Arabia':'crimson', 'Canada':'goldenrod', 'Germany':'Tomato', 'Australia':'lightslategray', 'Mexico':'saddlebrown'})
bubble_chart_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
bubble_chart_fig.update_layout(
    font=dict(
        size=20,
        color="DarkGreen"
    )
)
# **************************************************************************************************************

# HTML Styles: https://www.w3schools.com/html/html_styles.asp
# Source: https://github.com/PacktPublishing/Interactive-Dashboards-and-Data-Apps-with-Plotly-and-Dash 


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[  
    # HEADER DIV 
    html.Div(
            children=[
                html.H1(children="Maven Marketing Analytics Campaign",
                        style={'textAlign': 'center','color': 'DarkGreen', 'fontSize': '44px'}, 
                        className="header-title"), 
                html.H2(
                    children="Analysis of Campaign Impact on Product Sales",
                    className="header-description", style={'textAlign': 'center','color': 'DarkSeaGreen', 'fontSize': '30px'},
                ),
            ],
            className="header",style={'background':'whitesmoke'},
        ),
    # SALES SUMMARY
    html.Div(children=[

        # NUMBER SUMMARY
        html.Div(children=[

        #TOP ROW
        html.Div(children=[
            #CARD #1
            html.Div(children=[
                html.H3("Wine Sales", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                html.P(wines_sales, style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '100%'})
            ],style={'width':'23%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                    'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                    'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'}),
            #CARD #2
            html.Div(children=[
                html.H3("Fruit Sales", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                html.P(fruits_sales, style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '100%','display': 'block'})
            ],style={'width':'23%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                    'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                    'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'}),
            #CARD #3
            html.Div(children=[
                html.H3("Meat Sales", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                html.P(meat_sales, style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '100%'})
            ],style={'width':'23%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                    'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                    'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'}),
            #CARD #4 (Total Purchase Count)
            html.Div(children=[
                html.H3("Purchase Count", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                html.P(total_purchases, style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkgreen", 'fontSize': '45px', 'width': '100%'})
            ],style={'width':'23%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                    'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                    'margin-right':'15px','margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'})
            ],style={'width':'100%','display': 'inline-block','background': 'whitesmoke', 'height':'200px'}),
        
        #BOTTOM ROW
        html.Div(children=[
            #CARD #5
            html.Div(children=[
                html.H3("Fish Sales", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                html.P(fish_sales, style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '100%'})
            ],style={'width':'23%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                    'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                    'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%', 'height':'70%'}),
            #CARD #6
            html.Div(children=[
                html.H3("Sweets Sales", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                html.P(sweets_sales, style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '100%'})
            ],style={'width':'23%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                    'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                    'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'}),
            #CARD #7
            html.Div(children=[
                html.H3("Gold Sales", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                html.P(gold_sales, style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '100%'})
            ],style={'width':'23%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                    'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                    'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'}),
            #CARD #8 (Total Sales)
            html.Div(children=[
                html.H3("Total Sales", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                html.P(total_sales, style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkgreen", 'fontSize': '45px', 'width': '100%'})
            ],style={'width':'23%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                    'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                    'margin-right':'15px','margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'})
            ],style={'width':'100%','display': 'inline-block','background': 'whitesmoke', 'height':'200px'}),
        ],style={'width':'66%','display': 'inline-block','vertical-align': 'top'}),
        # # Total Right Side
        html.Div(children=[
            dcc.Graph(figure=number_fig,style={'width': '100%', 'display': 'inline-block','vertical-align': 'top'})
            ],style={'width':'33%','display': 'inline-block'}
            )],style={'width':'100%','display': 'inline-block','background': 'whitesmoke','vertical-align': 'top'}),

    # CHART DIV - LEFT
    html.Div(children=[
        dcc.Graph(figure=sales_income_fig,style={'width': '66%', 'display': 'inline-block'}),
        dcc.Graph(figure=bubble_chart_fig,style={'width': '33%', 'display': 'inline-block'})
    ]),

    # html.Div(
    #         children=[
    #             html.Div(
    #             children = dcc.Graph(figure=sales_by_channel_age_fig,style={'width': '33%', 'display': 'inline-block'}),
    #             style={'width': '50%', 'display': 'inline-block'},
    #             ),
    #             html.Div(
    #             children = dcc.Graph(figure=sales_by_channel_age_fig,style={'width': '33%', 'display': 'inline-block'}),
    #             style={'width': '50%', 'display': 'inline-block'},
    #             ),
    #             html.Div(
    #             children = dcc.Graph(figure=sales_by_channel_age_fig,style={'width': '33%', 'display': 'inline-block'}),
    #             style={'width': '50%', 'display': 'inline-block'},
    #             ),
    #             html.Div(
    #             children = dcc.Graph(figure=sales_by_channel_age_fig,style={'width': '33%', 'display': 'inline-block'}),
    #             style={'width': '50%', 'display': 'inline-block'},
    #             ),
    #      ],
    #     className = 'double-graph',
    # ),
# CHART DIV - LEFT
    # html.Div(children=[
    html.Div(children=[
        dcc.Dropdown(id='my_dropdown',options=product_dropdown, value='',
                    style={'width': '40%', 'display': 'inline-block', 'margin-left':'980px'}, placeholder='Please select a product type')
        # ,
        #     html.Div(id='dd-output-container',style={'width': '33%', 'margin-left':'2000px'}),
    ]),
    html.Div(children=[
        dcc.Graph(figure=sales_by_channel_age_fig,style={'width': '33%', 'display': 'inline-block'}),
        dcc.Graph(figure=sales_by_channel_gen_fig,style={'width': '33%', 'display': 'inline-block'}),
        dcc.Graph(figure=age_product_fig, id= 'the_graph',style={'width': '33%', 'display': 'inline-block'})
    ])
    # ])

], style={'background':'whitesmoke'})

@app.callback(
    Output('the_graph', 'figure'),
    Input('my_dropdown', 'value')
)
def update_output(my_dropdown):
    chart_df = data
    bins = [1939, 1965, 1980, 1996]
    name = ['Boomers', 'Gen x', 'Millennials']
    chart_df['Gen'] = pd.cut(chart_df['Year_Birth'], bins, labels=name)
    chart_df['Total_purchase'] = chart_df['MntWines']+chart_df['MntMeatProducts']+chart_df['MntGoldProds']+chart_df['MntFishProducts']+chart_df['MntSweetProducts']+chart_df['MntFruits']
    product_dropdown = [
            {'label': 'Wine', 'value': 'MntWines'},
            {'label': 'Meat', 'value': 'MntMeatProducts'},
            {'label': 'Gold', 'value': 'MntGoldProds'},
            {'label': 'Fish', 'value': 'MntFishProducts'},
            {'label': 'Sweets', 'value': 'MntSweetProducts'},
            {'label': 'Fruits', 'value': 'MntFruits'},
            {'label': 'Total Purchase', 'value' : 'Total_purchase'}
        ]
    age_product_fig = px.treemap(chart_df, path=['Gen'], values=my_dropdown,color=chart_df['Gen'], title='Product Purchases by Age',color_discrete_map={'Boomers':'DarkGreen', 'Gen x':'wheat', 'Millennials':'DarkSeaGreen'})
    age_product_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    return age_product_fig


if __name__ == '__main__':
    app.run_server(debug=True)

# Uncomment the following two lines if using Jupyter Notebook
# if __name__ == '__main__':
#     app.run_server(mode='inline', height= 300, width = '80%')

# modes: external, inline, or jupyterlab

# Commnet the following two lines if using Jupyter Notebook
# if __name__ == '__main__':
#     app.run_server(debug=True)

# #############################################################################