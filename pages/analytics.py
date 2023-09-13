# Third party imports
import dash
from dash import html, dcc, Input, Output, callback
# import dash_latex as dl
import plotly.express as px
import dash_bootstrap_components as dbc

# Local package imports
from .tools import log_return_chart, rolling_volatility_chart, log_return_histogram, log_log_return_histogram, price_chart, log_price_chart
from .data import BTCprice as data

dash.register_page(__name__)


def latex_gbm():
    title = html.H2('Geometric Brownian Motion')
    intro = dcc.Markdown(r'''
            The "standard model" for the price dinamics of a primary financial asset (as a stock or, in this case, a 
            cryptocurrency) is the Geometric Brownian Motion (GMB). This is a stochastic process that, relying on 
            Samuelson's efficient market hypothesis, satisfies the stochastic differential equation (SDE):
            $$
            d S_t = \mu S_t dt + \sigma S_t dW_t,
            $$
            where $S_t$ is the asset price and $dW_t$ is an increment of a Wiener process (also called Simple Brownian 
            Motion). The first term derives from the compounding interest model $S_t=S_0e^{\mu t}$, while the second 
            introduces stochasticity in the form of Market Risk.       
        ''', dangerously_allow_html=False, mathjax=True)
    wiener_card = dbc.Card([
        dbc.CardHeader("Wiener process"),
        dbc.CardBody([
            dcc.Markdown(
                r'''
    The Wiener process is a fundamental building block upon which all Ito processes are built. Its probability 
    density function (pdf) evolves according to the simplest version of a Fokker-Planck equation:
    $$
    \frac{\partial}{\partial t} p(x,t|x_0, t_0) = \frac{1}{2} \frac{\partial^2}{\partial x^2} p(x,t|x_0, t_0),
    $$
    with boundary condition $p(x, t_0| x_0, t_0) = \delta(x-x_0)$, implying that the variable $x$ (the asset price in 
    our case) is known almost surely (with a Dirac's $\delta$ function) at time $t_0$. The solution is:
    $$
    p(x,t|x_0, t_0) = \frac{1}{\sqrt{2 \pi (t - t_0)}} \exp{-\frac{(x-x_0)^2}{2(t-t_0)}},
    $$
    which is a Gaussian with fixed mean $\mathbb{E}[x(t)]=x_0$, but linearly increasing variance $\mathrm{Var}[x(t)]=t-t_0$. 
    It is in this sense that, physically, the Wiener process is a Diffusion process and it can be used to model 
    the so-called Brownian motion.

    Interestingly, shifting the focus from the absolute value $x(t_i)$ to non-overlapping increments 
    $\Delta x_i = x_i-x_{i-1}$ creates Normal i.i.d. variables: $\Delta x_i \sim 
    \mathcal{N}(0,\sqrt{\Delta t_i})$. If the increments overlap, however, they get correlated: $\mathbb{E}[{x(s)x(t)}]=\min(s,t)$,
    given $x(0)=0$. A consequence, useful for numerical simulation, is that:
    $$
    x(t_2) = x(t_1) + \sqrt{t_2-t_1}\cdot Z,
    $$
    where $Z$ is an independent standard normal variable.
    Finally, the trajectory $x(t)$ is almost surely continuous, but not differentiable.
                ''', mathjax=True),
        ], id="wiener-process-card"),
    ])
    gmb_solve = dcc.Markdown(r'''
In general, the solution of an SDE requires the introduction of a stochastic calculus framework, and the choice of which
one to use is not unique. Therefore, also the analytic expression of the solution will vary along with the framework. 
What remains invariant, instead, are the pdfs (solution to the corresponding Fokker-Plack equation). 

For the GBM, a
convenient choice is Ito's set of rules: in fact, a simple application of Ito's variable change formula leads to:
$$
d \ln(S_t) = \left( \mu - \frac{\sigma^2}{2}\right)dt + \sigma dW_t.
$$
This result implies that the logarithm of the prices is a Simple Brownian Motion: a Wiener process with a drift term, 
which is much easier to analyze. 
Integrating the new SDE, the dynamic of the Log-Returns is obtained:
$$
\Delta \ln S_t = \ln\left(\frac{S(t+\Delta t)}{S(t)}\right) \sim \mathcal{N}\left( \left(\mu - \frac{\sigma^2}{2}\right)
\Delta t, \sigma \sqrt{\Delta t} \right).
$$
Given that our data are sampled daily, it is easy compute Log-Returns, with $\Delta t = 1\, \mathrm{day}$, and put them 
in a histogram, in order to check their normality and extract estimates for the parameters $\mu$ and $\sigma$.

The analytical solution (under Ito's interpretation) of the GBM SDE is:
$$
S_t = S_0 \exp\{\left(\mu - \sigma^2/2\right)t + \sigma W_t\}.
$$
Its mean and variance are obtained from the properties of random variable which are the exponential of Normal ones, and
they both diverge exponentially, as $t\rightarrow + \infty$:
$$
\begin{align}
\mathbb{E}[S_t] &= e^{\mathbb{E}[\ln S_t]}e^{1/2\mathrm{Var}[\ln S_t]} = S_0 e^{\mu(t-t_0)},\\
\mathrm{Var}[S_t] &= ... = S_0 e^{2\mu(t-t_0)}(e^{\sigma^2(t-t_0)}-1).
\end{align}
$$
Finally, the price pdf at time $t$ of a GBM, is given by a LogNormal distribution:
$$
p_\mathcal{N}({\ln S}) d\ln S = \frac{p_\mathcal{N}({\ln S})}{S}dS = p_{LN}(S)dS.
$$
        ''', dangerously_allow_html=False, mathjax=True)
    return [html.Br(), intro, wiener_card, html.Br(), gmb_solve]


layout = dbc.Container([
    html.Br(),
    html.H2('Geometric Brownian Motion'),
    dbc.Row([
        dbc.Col(latex_gbm(), width=5),
        dbc.Col([
            dcc.Graph(
                id='price-chart',
                figure=price_chart(data)),
            dcc.Graph(
                id='log-price-chart',
                figure=log_price_chart(data)),
            dcc.Graph(
                id='log-returns',
                figure=log_return_chart(data)),
            html.H4("Historical Volatility"),
            dbc.Row([
                dbc.Col("Select rolling window size [days]:", width="auto"),
                dbc.Col(dcc.Input(
                    id='window-input',
                    type='number',
                    min=2,
                    value=200), )
            ]),
            dcc.Graph(
                id='rolling-volatility',
                config={'staticPlot': False},
                figure=rolling_volatility_chart(data, window=200)
            ),
        ]),
        html.H4("Beyond GBM"),
        dbc.Row([
            dbc.Col(dcc.Graph(
                figure=log_return_histogram(data),
            )),
            dbc.Col(dcc.Graph(
                figure=log_log_return_histogram(data)
            )),
        ]),
    ]),
], fluid=True)


@callback(
    Output('rolling-volatility', 'figure'),
    Input('window-input', 'value')
)
def update_graph(window):
    return rolling_volatility_chart(data, window=int(window))
