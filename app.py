from shiny import App, ui, render
import pandas as pd
import plotly.express as px
from htmltools import tags
import plotly.graph_objects as go
import gspread
from google.oauth2 import service_account
from shinywidgets import output_widget, render_widget


# Define your Google Sheets credentials JSON file (replace with your own)
credentials_path = 'playground-405817-b485d53d4c78.json'
    
# Authenticate with Google Sheets using the credentials
credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=['https://spreadsheets.google.com/feeds'])
    
# Authenticate with Google Sheets using gspread
gc = gspread.authorize(credentials)
    
# Your Google Sheets URL
url = "https://docs.google.com/spreadsheets/d/1PjUlnAnR4e0J3JwjuEsmPF4H-0xCgrGksciCSc2a1sQ/edit#gid=0"
    
# Open the Google Sheets spreadsheet
worksheet = gc.open_by_url(url).worksheet("playground")

data = worksheet.get_all_values()
    
# Prepare data for Plotly
headers = data[0]
data = data[1:]
df = pd.DataFrame(data, columns=headers) 

# Convert the "Amount Collected" column to numeric
df['Amount'] = df['Amount'].str.replace(',', '').astype(float)


newdf = df.groupby('Category')['Amount'].sum()

total = "Ksh. {:,.0f}".format(df['Amount'].sum())
average = "Ksh. {:,.0f}".format(df['Amount'].mean())



page_dependencies = ui.tags.head(ui.tags.link(rel="stylesheet", type="text/css", href="style.css"))

TITLE = 'PRODUCTION AND COLLECTION DASHBOARD'


def my_card(title, value, width=1.5, height=6, bg_color="#1e90ff", text_color="text-black"):
    
    card_ui= ui.div(
        ui.div(
            ui.div(ui.h4(title, class_="text-center"), class_="card-title"),
            ui.div(value, class_="card-text text-center",
            
            ),
            class_ = f'card{text_color}{bg_color}',
            style = f'background-color:{bg_color}; color:black; flex-grow:{height}; margin:2px; border-radius: 5px;',
            
        ),
        class_ = f'col-md-{width}d-flex card'
    )
    return card_ui

def total_expenses():
    return  my_card("TOTAL", total)
    

def mean_expenses():
    return my_card("AVERAGE", average)

app_ui = ui.page_fluid(
    ui.navset_card_tab(
        ui.nav(
            ui.tags.div(
                ui.img(src="https://sokodirectory.com/wp-content/uploads/2016/07/Corporate-Insurance-Company.jpg", height="70px", width="70px", style="margin:8px; border-radius: 70%;"),
                ui.h4("  " + TITLE),
                style="display:flex; background-color: #004080; justify-content: space-between; align-items: center;"
            )
        ),
        ui.nav(
            "Dashboard",
            output_widget("scatter_plot")
        ),
        ui.nav(
            "Records",
            tags.div(ui.output_data_frame("data"))
        ),
    ),
    ui.row(
        ui.div(total_expenses(), class_="col-md-4"),
        ui.div(mean_expenses(), class_="col-md-4"),
    ),
    ui.card(
        ui.output_data_frame("data")
    ),
)



def server(input, output, session): 
    @output
    @render.ui
    def total_expenses():        
        return total_expenses
    
    @output
    @render.ui
    def mean_expenses():        
        return mean_expenses
        
    @output
    @render_widget
    def scatter_plot():
        
        fig = px.bar(newdf,                        
                        y="Amount",
                        )

        fig.update_layout(
            xaxis=dict(title='Amount Expense'),
            yaxis=dict(title='Category', tickformat=",.0"),
            title={'text':'CATEGORICAL AMOUNTS', 'x': 0.5, 'xanchor': 'center'}
            )
        

        return go.FigureWidget(fig)    


    
    @output
    @render.data_frame
    def data():
        return render.DataGrid(df)
        

app = App(app_ui, server)  