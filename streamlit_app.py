import altair as alt
import pandas as pd
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(page_title="Equity Calculator", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Host+Grotesk:wght@300;400;500;600;700&display=swap');
    *, *::before, *::after { font-family: 'Host Grotesk', Arial, sans-serif !important; }
    h1, h2, h3, h4, h5, h6,
    [data-testid='stHeading'] { color: white !important; }
    .block-container { padding-top: 1rem; }
    [data-testid='stMetricValue'] { font-size: 1rem; color: white !important; }
    [data-testid='stMetricLabel'] { color: #bdbdbd !important; }
    [data-testid='stSidebar'] [data-testid='stMetricLabel'] { display: none; }
    [data-testid='stSidebar'] [data-testid='stMetricValue'] { font-size: 1.6rem !important; font-weight: 700; color: white !important; }
    [data-testid='stTooltipContent'] { background-color: #4f4f4f !important; color: #cbcbcb !important; border: 1px solid #1e1e1e !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

style_metric_cards(
    background_color="#292929",
    border_size_px=1,
    border_color="#1e1e1e",
    border_radius_px=6,
    border_left_color="#4f4f4f",
    box_shadow=False,
)

st.title("Evaluate your equity package")
st.write(
    """
It can be hard to understand the equity being offered to you, because it all depends on what you believe about where the company will exit.
Use this to evaluate different outcomes. Start by entering your offered package on the left 👈. Then specify 3 different outcomes for the company. Suggest setting Outcome 1 either 0 or your company's current valuation.
Outcome 2 is your middle scenario, maybe 2-3x your company's current valuation. And Outcome 3 should be what
the company could be worth if everything goes right. Consider recent IPOs and acquisitions of similar types of companies.
"""
)

st.sidebar.write("**Equity**")
equity = st.sidebar.number_input("Stock options granted, vested over 4 years", value=1000)

st.sidebar.write("**Strike price**")
strike = st.sidebar.number_input("Price at which you can purchase options ($)", value=0.01)

st.sidebar.write("**Number of fully diluted shares**")
totshares = st.sidebar.number_input("Existing shares at the time of the offer", value=1000000)

st.sidebar.write("**Your percentage ownership**")
perc = equity / totshares
st.sidebar.metric("Ownership", f"{round(perc * 100, 6)}%")

COLORS = {"Low": "#3B82F6", "Medium": "#F59E0B", "High": "#10B981"}


def share_value(dilution, valuation):
    return equity / totshares * (1 - (dilution / 100)) * valuation * 1_000_000


def format_curr(value):
    return "${:,.0f}".format(value)


def spread(value):
    return value - (strike * equity)


def outcome_card(key, label, color, slider_key_val, slider_key_dil, prob_key, default_prob):
    css = f"""
        {{
            border: 1px solid {color}55;
            border-left: 5px solid {color};
            border-radius: 10px;
            padding: 1.25rem 1.25rem 0.5rem 1.25rem;
            background-color: {color}18;
        }}
    """
    with stylable_container(key=key, css_styles=css):
        st.subheader(label)
        valuation = st.number_input(
            "Exit valuation ($M)",
            min_value=0,
            max_value=100_000,
            value=100,
            step=50,
            key=slider_key_val,
        )
        dilution = st.slider(
            "Future dilution (%)",
            0, 100, 20, 5,
            key=slider_key_dil,
            help=(
                "Dilution is the reduction in your ownership percentage as the company issues new shares to future investors.\n\n"
                "**How to estimate it:**\n"
                "Each funding round typically dilutes existing shareholders by 15–25%:\n"
                "- Seed → Series A: ~20–25%\n"
                "- Series A → Series B: ~15–20%\n"
                "- Series B → Series C: ~10–15%\n"
                "- Each round after that: ~10%\n\n"
                "**Example:** If you expect 2 more rounds at 20% each, your cumulative dilution is roughly 1 − (0.8 × 0.8) = 36%.\n\n"
                "Earlier-stage companies typically need more future funding, so higher dilution (40–60%) is realistic. "
                "Later-stage companies may need only 1–2 more rounds, so 15–30% is more appropriate."
            ),
        )
        prob_pct = st.slider(
            "Probability of this outcome",
            5, 100, int(default_prob * 100), 5,
            key=prob_key,
            format="%d%%",
        )
        prob = prob_pct / 100
        value = share_value(dilution, valuation)
        m1, m2 = st.columns(2)
        m1.metric("Option value", format_curr(value))
        m2.metric(
            "Spread",
            format_curr(spread(value)),
            help=(
                "Spread is your actual profit — the option value minus the cost to exercise your options "
                "(strike price × number of options).\n\n"
                "**Example:** If your options are worth $100,000 but it costs $5,000 to exercise them, "
                "your spread is $95,000.\n\n"
                "For early-stage companies with a very low strike price (e.g. $0.01), the spread is nearly "
                "identical to the option value. The difference grows when the strike price is significant."
            ),
        )
    return value, prob


a, _, b, __, c = st.columns([5, 1, 5, 1, 5])

with a:
    outcome1, prob1 = outcome_card(
        "low", "Outcome 1 — Low", COLORS["Low"], "valuation1", "dilution1", "prob1", 0.25
    )
with b:
    outcome2, prob2 = outcome_card(
        "med", "Outcome 2 — Med", COLORS["Medium"], "valuation2", "dilution2", "prob2", 0.50
    )
with c:
    outcome3, prob3 = outcome_card(
        "high", "Outcome 3 — High", COLORS["High"], "valuation3", "dilution3", "prob3", 0.25
    )

st.divider()
st.subheader("Outcome comparison")

prob_sum = round(prob1 + prob2 + prob3, 10)
probs_valid = abs(prob_sum - 1.0) <= 0.01

chart_df = pd.DataFrame({
    "Outcome": ["Low", "Medium", "High"],
    "Option value ($)": [outcome1, outcome2, outcome3],
    "Probability": [prob1, prob2, prob3],
})

color_scale = alt.Scale(
    domain=["Low", "Medium", "High"],
    range=[COLORS["Low"], COLORS["Medium"], COLORS["High"]],
)

base = alt.Chart(chart_df).encode(
    x=alt.X("Outcome", sort=["Low", "Medium", "High"], title=None)
)

bars = base.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
    y=alt.Y("Option value ($)", title="Option value ($)"),
    color=alt.Color("Outcome", scale=color_scale, legend=None),
    tooltip=["Outcome", "Option value ($)", "Probability"],
)

prob_line = base.mark_line(
    point=alt.OverlayMarkDef(filled=True, size=80, color="#7b6ff3"),
    strokeWidth=2,
    color="#7b6ff3",
    strokeDash=[4, 2],
).encode(
    y=alt.Y(
        "Probability",
        title="Probability",
        scale=alt.Scale(domain=[0, 1]),
        axis=alt.Axis(format=".0%"),
    ),
)

chart = alt.layer(bars, prob_line).resolve_scale(y="independent")

chart_col, metric_col = st.columns([3, 1])

with chart_col:
    st.altair_chart(chart, use_container_width=True)

with metric_col:
    if not probs_valid:
        st.error(
            f"Probabilities must add up to 1.0. Current sum: **{prob_sum:.2f}**. "
            "Adjust the sliders in the outcome cards above."
        )
    else:
        weighted_outcome = (
            outcome1 * prob1 + outcome2 * prob2 + outcome3 * prob3
        )
        ev_css = """
            {
                border: 2px solid #7b6ff333;
                border-left: 6px solid #7b6ff3;
                border-radius: 12px;
                padding: 2rem 1.5rem;
                background-color: #7b6ff30D;
                text-align: center;
            }
        """
        with stylable_container(key="ev_card", css_styles=ev_css):
            st.markdown("##### Expected value of your options")
            st.markdown(
                f"<div style='font-size:2rem; font-weight:700; color:#7b6ff3;'>{format_curr(weighted_outcome)}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:1rem; color:#6B7280; margin-top:0.5rem;'>{format_curr(weighted_outcome / 4)} / year over 4yr vest</div>",
                unsafe_allow_html=True,
            )
            st.caption("Weighted across all three outcomes by their probabilities.")
