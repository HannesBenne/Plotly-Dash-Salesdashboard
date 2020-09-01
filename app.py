import flask
import dash
import os
from random import randint
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go 
import pandas as pd
import calendar

# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)
app.title = 'EU Superstore'


#read an pre-aggregate data
df = pd.read_excel('Data/EU-Superstore.xls',sheet_name='Orders')
df['Order Year'] = df['Order Date'].dt.year
df['Order Month'] = df['Order Date'].dt.month.map(dict(enumerate(calendar.month_abbr)))
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
df['Order Month'] = pd.Categorical(df['Order Month'], categories=months, ordered=True)

#kpi data
agg_year = df.groupby(['Order Year']).sum()
agg_year_order = df.groupby(['Order ID', 'Order Year']).sum()
order_quantity_per_year = df.groupby(['Order Year'])['Order ID'].nunique().to_dict()
sales_per_year=agg_year.Sales.to_dict()
profit_per_year=agg_year.Profit.to_dict()
profitratio_per_year = (agg_year.Profit / agg_year.Sales).to_dict()
profitcustomer_per_year = {agg_year.index[i]:agg_year.iloc[i].Profit/df.groupby(['Order Year'])['Customer ID'].nunique().iloc[i] for i in range(len(agg_year))}
agg_year_order.reset_index(level=1, inplace=True)
biggest_order_per_year = {year: agg_year_order[agg_year_order['Order Year']==year].Sales.max() for year in agg_year_order['Order Year'].unique()}

#Country bar data
sales_per_country = df.groupby(['Order Year', 'Country']).agg({'Sales':'sum'}).sort_values(['Sales'])

#Product scatterplot data
sales_per_product = df.groupby(['Order Year', 'Country', 'Product Name']).agg({'Sales':'sum','Profit':'sum'})
spp = sales_per_product.groupby(['Order Year','Product Name']).sum()

#Sales per month data
sales_per_month = df.groupby(['Order Year','Order Month']).agg({'Sales':'sum'})
sales_per_month_country = df.groupby(['Order Year','Country','Order Month']).agg({'Sales':'sum'})

#Sales per category data
sales_per_category = df[['Order Year','Country','Category','Sub-Category','Sales','Profit']].groupby(['Order Year', 'Category','Sub-Category']).sum()
sales_per_category_country = df[['Order Year','Country','Category','Sub-Category','Sales','Profit']].groupby(['Order Year', 'Country', 'Category','Sub-Category']).sum()


#define layout
app.layout = html.Div(
    className='dashboard-wrapper',
    children = [
        html.H1(id='header', children='Superstore Sales Dashboard - 2018'),
        dcc.RadioItems(id='select-year', options=[{'label': year, 'value': year} for year in sorted(df['Order Year'].unique())], value=2018),
        html.Hr(),
        html.Div(id='kpi-wrapper', children=[
            html.Div(className='kpi', children=[
                html.Div(className='kpi-header', children=['Order Quantity']),
                html.Div(className='kpi-text', id='orders-per-year', children=f'{order_quantity_per_year[2018]}')
            ]),
            html.Div(className='kpi', children=[
                html.Div(className='kpi-header', children=['Sales']),
                html.Div(className='kpi-text', id='sales-per-year', children=f'{sales_per_year[2018]:0.2f} €')
            ]),
            html.Div(className='kpi', children=[
                html.Div(className='kpi-header', children=['Profit']),
                html.Div(className='kpi-text', id='profit-per-year', children=f'{profit_per_year[2018]:0.2f} €')
            ]),
            html.Div(className='kpi', children=[
                html.Div(className='kpi-header', children=['Profit Ratio']),
                html.Div(className='kpi-text', id='profit-ratio', children=f'{profitratio_per_year[2018]*100:0.2f} %')
            ]),
            html.Div(className='kpi', children=[
                html.Div(className='kpi-header', children=['Profit per Customer']),
                html.Div(className='kpi-text', id='profit-per-customer', children=f'{profitcustomer_per_year[2018]:0.2f} €')
            ]),
            html.Div(className='kpi', children=[
                html.Div(className='kpi-header', children=['Biggest Order']),
                html.Div(className='kpi-text', id='biggest-order', children=f'{biggest_order_per_year[2018]:0.2f} €')
            ]),
        ]),
        dcc.Graph(id='sales-per-country-bar',style={'width':'50%','float':'left'}),
        dcc.Graph(id='profit-sales-scatter', style={'width':'50%','float':'left'}),
        dcc.Graph(id='sales-per-month', style={'width':'50%','float':'left'}),
        dcc.Graph(id='data-table', style={'width':'50%','float':'left'}),
        html.H1(id='test')
    ]
)


#define callbacks
#update header
@app.callback(Output('header','children'),[Input('select-year','value')])
def update_header(year):
    return f'Superstore Sales Dashboard - {year}'

#kpi callbacks
@app.callback(Output('orders-per-year','children'),[Input('select-year','value')])
def update_order_per_year(year):
    return f'{order_quantity_per_year[int(year)]}'

@app.callback(Output('sales-per-year','children'),[Input('select-year','value')])
def update_sales_per_year(year):
    return f'{sales_per_year[int(year)]:0.2f} €'

@app.callback(Output('profit-per-year','children'),[Input('select-year','value')])
def update_profit_per_year(year):
    return f'{profit_per_year[int(year)]:0.2f} €'

@app.callback(Output('profit-ratio','children'),[Input('select-year','value')])
def update_profitratio_per_year(year):
    return f'{profitratio_per_year[int(year)]*100:0.2f} %'

@app.callback(Output('profit-per-customer','children'),[Input('select-year','value')])
def update_customer_profit_per_year(year):
    return f'{profitcustomer_per_year[int(year)]:0.2f} €'

@app.callback(Output('biggest-order','children'),[Input('select-year','value')])
def update_biggest_order_per_year(year):
    return f'{biggest_order_per_year[int(year)]:0.2f} €'

#update plots
@app.callback(Output('sales-per-country-bar','figure'),[Input('select-year','value')])
def update_country_bars(year):
    figure = go.Figure(
        data=go.Bar(
                y=sales_per_country.loc[int(year)].index,
                x=sales_per_country.loc[int(year)].Sales,
                orientation='h',
                marker_color='rgb(158, 0, 105)'
            ),
        layout=dict(
            title='Sales per Country', 
            margin=dict(l=10, r=10, t=50, b=10),
            plot_bgcolor='rgb(245, 245, 245)',
            paper_bgcolor='rgb(245, 245, 245)',
            xaxis=dict(title='Sales [€]')
            )
        )
    return figure

@app.callback(Output('profit-sales-scatter','figure'), [Input('select-year','value'),Input('sales-per-country-bar','clickData')])
def update_sales_profit_scatter(year,country_data):
    if country_data is None:
        spp = sales_per_product.groupby(['Order Year','Product Name']).sum()
        figure = go.Figure(
            data=go.Scatter(
                    x=spp.loc[year,:].Sales,
                    y=spp.loc[year,:].Profit, 
                    mode='markers', text=spp.loc[year].index,
                    marker=dict(size=8, color=spp.loc[year,:].Profit, colorscale='RdYlGn',)
                ),
            layout=dict(
                title='Product Sales vs Profit', 
                margin=dict(l=10, r=10, t=50, b=10),
                plot_bgcolor='rgb(245, 245, 245)',
                paper_bgcolor='rgb(245, 245, 245)',
                xaxis=dict(title='Sales [€]'),
                yaxis=dict(title='Profit [€]'))
            )
    else:
        country = country_data['points'][0]['label']

        figure = go.Figure(
            data=go.Scatter(
                    x=sales_per_product.loc[year,country,:].Sales,
                    y=sales_per_product.loc[year,country,:].Profit, 
                    mode='markers', text=sales_per_product.loc[year,country].index,
                    marker=dict(size=8, color=sales_per_product.loc[year,country,:].Profit, colorscale='RdYlGn')
                ),
            layout=dict(
                title=f'Product Sales vs Profit | Selected: {country} ', 
                margin=dict(l=10, r=10, t=50, b=10),
                plot_bgcolor='rgb(245, 245, 245)',
                paper_bgcolor='rgb(245, 245, 245)',
                xaxis=dict(title='Sales [€]'),
                yaxis=dict(title='Profit [€]'))
            )
    
    return figure
        
@app.callback(Output('sales-per-month','figure'), [Input('select-year','value'),Input('sales-per-country-bar','clickData')])   
def update_sales_per_month_lines(year, country_data):
    if country_data is None:
        figure = go.Figure(
            data=go.Scatter(
                    x=sales_per_month.loc[year].index,
                    y=sales_per_month.loc[year].Sales, 
                    mode='lines+markers',
                    marker=dict(size=9),
                    line=dict(width=3),
                    marker_color='rgb(158, 0, 105)'
                ),
            layout=dict(
                title='Monthly Sales', 
                margin=dict(l=10, r=10, t=50, b=10),
                plot_bgcolor='rgb(245, 245, 245)',
                paper_bgcolor='rgb(245, 245, 245)',
                xaxis=dict(title='Sales [€]'),
                yaxis=dict(title='Profit [€]'))
            )
    else:
        country = country_data['points'][0]['label']
        figure = go.Figure(
            data=go.Scatter(
                    x=sales_per_month_country.loc[year,country].index,
                    y=sales_per_month_country.loc[year,country].Sales, 
                    mode='lines+markers',
                    marker=dict(size=9),
                    line=dict(width=3),
                    marker_color='rgb(158, 0, 105)'
                ),
            layout=dict(
                title=f'Monthly Sales | Selected: {country} ', 
                margin=dict(l=10, r=10, t=50, b=10),
                plot_bgcolor='rgb(245, 245, 245)',
                paper_bgcolor='rgb(245, 245, 245)',
                xaxis=dict(title='Sales [€]'),
                yaxis=dict(title='Profit [€]'))
            )
    return figure

@app.callback(Output('data-table','figure'), [Input('select-year','value'),Input('sales-per-country-bar','clickData')])   
def update_sales_per_category(year, country_data):
    if country_data is None:
        spc = sales_per_category.loc[year].reset_index()
        figure = go.Figure(
            data = go.Table(
                header=dict(values=['<b>' + txt + '</b>' for txt in spc.columns],fill_color='rgb(158, 0, 105)',font = dict(color = 'white')),
                cells=dict(values=[spc['Category'], spc['Sub-Category'], spc['Sales'].round(decimals=2), spc['Profit'].round(decimals=2)])
            ),
            layout=dict(
                        title='Sales per Category', 
                        margin=dict(l=10, r=10, t=50, b=10),
                        plot_bgcolor='rgb(245, 245, 245)',
                        paper_bgcolor='rgb(245, 245, 245)',
                        xaxis=dict(title='Sales [€]'),
                        yaxis=dict(title='Profit [€]')
                        )
                )
    else:
        country = country_data['points'][0]['label']
        spcc = sales_per_category_country.loc[year,country].reset_index()
        figure = go.Figure(
            data = go.Table(
                header=dict(values=['<b>' + txt + '</b>' for txt in spcc.columns],fill_color='rgb(158, 0, 105)',font = dict(color = 'white')),
                cells=dict(values=[spcc['Category'], spcc['Sub-Category'], spcc['Sales'].round(decimals=2), spcc['Profit'].round(decimals=2)])
            ),
            layout=dict(
                        title=f'Sales per Category | Selected: {country} ', 
                        margin=dict(l=10, r=10, t=50, b=10),
                        plot_bgcolor='rgb(245, 245, 245)',
                        paper_bgcolor='rgb(245, 245, 245)',
                        xaxis=dict(title='Sales [€]'),
                        yaxis=dict(title='Profit [€]')
                        )
                )
    return figure


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=False, threaded=True)
