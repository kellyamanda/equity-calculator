import streamlit as st

st.set_page_config(page_title=None, page_icon=None, layout="wide")

st.title('Evaluate your equity package')
st.write('''
It can be hard to understand the equity being offered to you, because it all depends on what you believe about where the company will exit. 
Use this to evaluate different outcomes. Start by entering your offered package on the left 👈. Then specify 3 different outcomes for the company. Suggest setting Outcome 1 either 0 or your company's current valuation.
Outcome 2 is your middle scenario, maybe 2-3x your company's current valuation. And Outcome 3 should be what
what the company could be worth if everything goes right. Consider recent IPOs and acquisitions of similar types of companies. Play around with the values
and see how your package value changes!
''')


# st.sidebar.write('**Salary**')
# salary = st.sidebar.number_input('Gross yearly salary in USD')

st.sidebar.write('**Equity**')
equity = st.sidebar.number_input('Stock options granted, vested over 4 years',value=1000)

st.sidebar.write('**Strike price**')
strike = st.sidebar.number_input('Price at which you can purchase options ($)',value=.01)

st.sidebar.write('**Number of fully diluted shares**')
totshares = st.sidebar.number_input('Existing shares at the time of the offer',value=100000)

st.sidebar.write('**Your percentage ownership**')
perc = equity/totshares
st.sidebar.write(round(perc*100,6
),"%")

def share_value(dilution,valuation):
    share_value = equity/totshares*(1-(dilution/100))*valuation*1000000
    return share_value

def format_curr(share_value):
    formatted_share_value = "${:,.0f}".format(share_value)
    return formatted_share_value

def spread(outcome):
    spread = outcome - (strike*equity)
    return spread

a, a1, b, b1, c = st.columns([5,1,5,1,5])

with a:
    st.subheader('Outcome 1 (Low)')
    st.write('##### Expected company valuation')

    valuation1 = st.select_slider("The value at which the company will exit ($M)", options=[0,10,25,50,75,100,125,150,175,200,250,300,350,400,500,600,750,1000,1500,2000,3000,5000,7000,10000,25000],key='valuation1')
    if valuation1 <1000:
        st.write(format_curr(valuation1),"M")
    else:
        st.write(format_curr((valuation1/1000)),"B")

    st.write('')
    st.write('##### Expected additional dilution')
    dilution1 = st.slider('Share owned by future investors (%)',0,100,20,5, format="%g", key='dilution1')

    outcome1 = share_value(dilution1,valuation1)

    st.write('##### Final value of your options')
    st.write(format_curr(outcome1))

    st.write('##### Spread of your options')
    st.write(format_curr(spread(outcome1))) 

with b:
    st.subheader('Outcome 2 (Med)')
    st.write('##### Expected company valuation')
    valuation2 = st.select_slider("The value at which the company will exit ($M)", options=[0,10,25,50,75,100,125,150,175,200,250,300,350,400,500,600,750,1000,1500,2000,3000,5000,7000,10000,25000],key='valuation2')
    if valuation2 <1000:
        st.write(format_curr(valuation2),"M")
    else:
        st.write(format_curr((valuation2/1000)),"B")

    st.write('')
    st.write('##### Expected additional dilution')
    dilution2 = st.slider('Share owned by future investors (%)',0,100,20,5, format="%g",key='dilution2')

    outcome2 = share_value(dilution2,valuation2)

    st.write('##### Final value of your options')
    st.write(format_curr(outcome2))

    st.write('##### Spread of your options')
    st.write(format_curr(spread(outcome2)))

with c:
    st.subheader('Outcome 3 (High)')
    st.write('##### Expected company valuation')
    valuation3 = st.select_slider("The value at which the company will exit ($M)", options=[0,10,25,50,75,100,125,150,175,200,250,300,350,400,500,600,750,1000,1500,2000,3000,5000,7000,10000,25000],key='valuation3')
    if valuation3 <1000:
        st.write(format_curr(valuation3),"M")
    else:
        st.write(format_curr((valuation3/1000)),"B")

    st.write('')

    st.write('##### Expected additional dilution')
    dilution3 = st.slider('Share owned by future investors (%)',0,100,20,5, format="%g",key='dilution3')

    outcome3 = share_value(dilution3,valuation3)

    st.write('##### Final value of your options')
    st.write(format_curr(outcome3))

    st.write('##### Spread of your options')
    st.write(format_curr(spread(outcome3)))
    

st.write("")
st.header("Weighted value analysis")

st.write('''
Given the uncertainty of outcomes, we can apply an expected value calculation to weigh the different scenarios.
Here is the expected value of your options, giving equal weighting to outcomes 1, 2, and 3:
''')
weighted_outcome = outcome1*(1/3)+outcome2*(1/3)+outcome3*(1/3)
formatted_outcome = "${:,.0f}".format(weighted_outcome)
st.write(formatted_outcome) 






  
