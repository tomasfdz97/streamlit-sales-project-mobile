import streamlit as st 
import pandas as pd
import plotly.express as px
import numpy as np
from numerize.numerize import numerize

# ------ configuracion de página básica ------ #

st.set_page_config(
    page_title='Dashboard sales',
    page_icon='📊',
    layout='centered',
    initial_sidebar_state='expanded',
)

hide_st_style = """ 
<style> 
#MainMenu {visibility : hidden;}
footer {visibiliti: hodden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ----- Uso y configuración de los datos ------ #

df = pd.read_excel('supermarket_sales.xlsx')

meses = pd.to_datetime(df['Date'],format='%H:%M:%S').dt.month   # Convertimos la fecha a meses
df.insert(11,'Month', meses)

# Creamos las condiciones para asociar a los meses su nombre
condiciones= [
    df['Month'] == 1, df['Month'] == 2,
    df['Month'] == 3, df['Month'] == 4,
    df['Month'] == 5, df['Month'] == 6,
    df['Month'] == 7, df['Month'] == 8,
    df['Month'] == 9, df['Month'] == 10,
    df['Month'] == 11, df['Month'] == 12,
]

meses = ['1.January','2.February','3.March','4.April','5.May','6.June','7.July','8.August',
              '9.September','10.October','11.November','12.December']

lista = np.select(condiciones,meses)
df.insert(12,'Month_name',lista)

# Renombre columna por problemas

df.rename(columns={'Product line':'Product_line'},inplace=True)

# Titulo y encabezado de pagina

st.title('👨‍💻Sales dashboard')

# -------- Creación de los filtros -------- #

st.sidebar.header('Data filter options:')

month = st.sidebar.multiselect('Select month',
                               options=df['Month_name'].unique(),
                               default=df['Month_name'].unique(),
)

branch = st.sidebar.multiselect('Select the branch type:',
                                options=df['Branch'].unique(),
                                default=df['Branch'].unique(),
)
lineas_producto = st.sidebar.multiselect('Selct the product line:', 
                                         options=df['Product_line'].unique(),
                                         default=df['Product_line'].unique(),
)

payment = st.sidebar.multiselect('Select the payment type:',
                                 options=df['Payment'].unique(),
                                 default=df['Payment'].unique(),
)

# Para que los filtros afecten al dataframe 

df_selection = df.query('Month_name == @month & Branch == @branch & Product_line == @lineas_producto & Payment == @payment')

# -------- Seleccionamos los KPIs principales para mostrar en top page -------- #

#1
total_sales = round(df_selection['Total'].sum(),0)
#2
avg_rating = int(round(df_selection['Rating'].mean(),0))
star_rating = ":star:" * int(round(avg_rating,0))
#3
total_quantity = df_selection['Quantity'].sum()
#4
average_sales_by_transaction = round(df_selection['Total'].mean(),2)

st.markdown('---')
st.markdown("<h2 style='text-align: center; color: black;'>Principal KPIs</h2>", unsafe_allow_html=True)
st.markdown('  ')

# Dividimos en columnas los KPIs

col1,col2,col3 = st.columns(3)

with col1:
    st.image('Imagenes/growth.png')
    st.metric(label='Total sales',value=numerize(total_sales))
with col2:
    st.image('Imagenes/target.png')
    st.metric(label='Average sales transaction',value=numerize(average_sales_by_transaction))
with col3:
    st.image('Imagenes/startup.png')
    st.metric(label='Units sales',value=total_quantity)

st.markdown('---')

# -------- Preparamos las visualizaciones -------- #

# 1 ---> Ventas totales por mes

sales_month = round(df_selection.groupby(by=['Month_name']).sum()[['Total']],0)

fig_sales_month=px.bar(sales_month,
                       x=sales_month.index,
                       y='Total',
                       title='Sales by month',
                       template='plotly_white',
                       text_auto=True,
                       labels={'Month_name':'Month'},
                       color_discrete_sequence=['#2254D4','#D43522','#18CB2D'] *len(sales_month),
                       width=300,
                       height=400,
)

fig_sales_month.update_layout(title_x=0.4,
                              title_font_size=18,
                              font_size=14,
)

fig_sales_month.update_traces(textposition='outside',
)

fig_sales_month.update_yaxes(range=[0,130000],
                            tickfont_size=14,
                            title_font_size=16,
)

fig_sales_month.update_xaxes(title_font_size=16,
                             tickfont_size=13,
)


# 2 ---> Total por línea de producto

sales_product_line=df_selection[['Product_line','Total']].groupby(by='Product_line',as_index=False).sum().round(0).sort_values('Total',ascending=False)

fig_sales_product_line=px.bar(sales_product_line,
                            y='Product_line',
                            x='Total',
                            title='Sales by porduct line',
                            template='plotly_white',
                            text_auto=True,
                            labels={'Product_line':'Product line'},
                            orientation='h',
                            range_x=[0,65000],
                            color_discrete_sequence=['#2254D4','#D43522','#18CB2D'] *len(sales_product_line),
                            width=300,
                            height=400,
)

fig_sales_product_line.update_traces(textposition='outside')

fig_sales_product_line.update_layout(title_x=0.4,
                                     title_font_size=18,
                                     font_size=12,
)

fig_sales_product_line.update_yaxes(tickfont_size=10,
                                    title_font_size=13,
)

fig_sales_product_line.update_xaxes(title_font_size=14,
                                    tickfont_size=12,
)

# Visualizacion de los 2 primeros graficos

st.plotly_chart(fig_sales_month)
st.plotly_chart(fig_sales_product_line)


# -------- Preparamos las visualizaciones. Segundo nivel -------- #

# 3 ---> Gasto total por ciudad y género

group_city_gender =df_selection[['City','Gender','Total']].groupby(by=['City','Gender'],as_index=False).sum().round(0)

fig_group_city_gender=px.bar(group_city_gender,
                            x='City',y='Total',
                            color='Gender',
                            barmode='group',
                            text_auto=True, 
                            title='Ventas por ciudad y género',
                            template='plotly_white',
                            color_discrete_sequence=['#2254D4','#D43522','#81EA7C'] *len(group_city_gender),
                            width=380,
                            height=400,
)

fig_group_city_gender.update_traces(textposition='outside')

fig_group_city_gender.update_yaxes(range=[0,70000],
                                   tickfont_size=12,
                                   title_font_size=14,
)

fig_group_city_gender.update_xaxes(title_font_size=15,
                                   tickfont_size=12,
)

fig_group_city_gender.update_layout(title_x=0.25,
                                    title_font_size=18,
                                    legend_title_font_size=12,
                                    legend_font_size=11,
                                    font_size=12,
)

# 4 -----> Gasto total por branch y payment

total_branch_payment=df_selection[['Branch','Payment','Total']].groupby(by=['Branch','Payment'],as_index=False).sum().round(0)

fig_total_branch_payment=px.bar(total_branch_payment,
                                x='Branch',y='Total',
                                color='Payment',
                                barmode='group',
                                text_auto=True, 
                                title='Total per branch & payment', 
                                template='plotly_white',
                                color_discrete_sequence=['#2254D4','#D43522','#18CB2D']*len(total_branch_payment),
                                width=380,
                                height=400,
)

fig_total_branch_payment.update_traces(textposition='outside')

fig_total_branch_payment.update_yaxes(range=[0,50000],
                                      tickfont_size=12,
                                      title_font_size=14,
)

fig_total_branch_payment.update_xaxes(title_font_size=14,
                                      tickfont_size=12,
)

fig_total_branch_payment.update_layout(title_x=0.25,
                                       title_font_size=18,
                                       legend_title_font_size=12,
                                       legend_font_size=11,
                                       font_size=14,
)

# visualizacion de los 2 segundos gráficos

st.plotly_chart(fig_group_city_gender)
st.plotly_chart(fig_total_branch_payment)

# 5 ---> evolucion de las ventas totales por meses

evolution_branch = df_selection[['Branch','Month_name','Total']].groupby(by=['Branch','Month_name'],as_index=False).sum().round(0)

fig_evolution_branch = px.line(evolution_branch,
                               x='Month_name',
                               y='Total',
                               color='Branch',
                               title='Total branch evolution',
                               template='plotly_white',
                               labels={'Month_name':'Month'},
                               text='Total',
                               color_discrete_sequence=['#2254D4','#D43522','#18CB2D'] *len(evolution_branch),
                               width=380,
                               height=400, 
)

fig_evolution_branch.update_layout(title_x=0.3,
                                   title_font_size=18,
                                   legend_title_font_size=12,
                                   legend_font_size=11,
                                   font_size=14,
)

fig_evolution_branch.update_yaxes(tickfont_size=12,
)

fig_evolution_branch.update_xaxes(title_font_size=14,
                                  tickfont_size=12,
)

fig_evolution_branch.update_traces(marker_size=5,
)

# 6 ---> Total sales by gender

spend_gender = df_selection.groupby(by='Gender').sum()[['Total']].round(0)

fig_spend_gender = px.pie(spend_gender,
                          names=spend_gender.index,
                          values='Total',
                          hole=0.4,
                          title='Total sales by gender',
                          color_discrete_sequence=['#2254D4','#D43522','#18CB2D'] *len(spend_gender),
                          width=380,
                          height=400, 
)

fig_spend_gender.update_traces(textinfo='percent+value')

fig_spend_gender.update_layout(title_x=0.28,
                               legend=dict(orientation='h',
                                           yanchor='bottom',
                                           y=-0.2,xanchor='center',
                                           x=0.5),
                                title_font_size=18,
                                legend_title_font_size=14,
                                legend_font_size=12,
                                font_size=14,
)

# Visualización de las dos ultimas columnas

st.plotly_chart(fig_evolution_branch)
st.plotly_chart(fig_spend_gender)