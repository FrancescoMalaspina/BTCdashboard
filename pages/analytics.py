# Third party imports
import dash
from dash import html, dcc, Input, Output, callback
# import dash_latex as dl
import plotly.express as px
import dash_bootstrap_components as dbc

# Local package imports
from .tools import log_return_plot, rolling_volatility_plot, log_return_histogram, log_log_return_histogram, \
    price_plot, log_price_plot, instaneous_volatility_plot, lognormal_evolution_plot
from .data import BTCprice as data

dash.register_page(__name__)


def latex_gbm():
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


def latex_volatility():
    volatility = dcc.Markdown(r'''
            The volatility $\sigma$ is a key property of any stochastic process, but unfortunately, unlike the spot price, it doesn't 
            assume a unique value at every time; it can only be inferred.   
            Depending on the available data, different estimates can be extracted. The most straightforward one is the 
            historical volatility, which is simply given by the empirical standard deviation of previous Log-Returns:
            $$
            \sigma_{hist}^2 = \mathrm{Var}[\Delta \ln S_t]/ \Delta t.
            $$
            Depending on the use case, it may be better not to consider the entire history of the asset price, but focus
            only on a fixed timespan window, obtaining a "rolling" volatility. When the sampling frequency gets high
            enough, it may be useful to estimate the instantaneous volatility, which outputs one value for each Log-Return:
            $$
            \sigma_{inst}^2 = \sqrt{\Delta \ln S_t/\Delta t} \quad \implies \quad \sigma_{inst}=|\Delta \ln S_t/\Delta t|.
            $$
            A final interesting volatility estimate comes from the prices of derivative assets, such as Put/Call Options.
            These prices can be modeled from first principles, using mathematical model such as the Black&Scholes option
            pricing one; but, since these derivatives can be bought in liquid exchanges (just as the underlying asset itself),
            the real price is drove by Offer/Demand balance.
            Those mathematical models involve the volatility as a parameter, and therefore, fixing all other parameters and the option price,
            an estimate for an implicit volatility $\sigma_{impl}$ can be obtained. Since this value is driven not by the 
            asset history, but by the market itself, it is often viewed as an estimate of the future volatility that the 
            asset will go through. 

            From all these considerations, it is evident that the GMB assumption that volatility remains constant is not 
            found in the real behaviour of any financial asset.
            More advanced models involve a description of the volatility as a stochastic process itself!
        ''', dangerously_allow_html=False, mathjax=True)
    return [html.H3("Volatility"), volatility]


def latex_beyond_GBM():
    beyond_GBM = dcc.Markdown(r'''
            The Geometric Brownian model is a really powerful tool for the modelling of financial assets prices in a first appriximation.
            The strong hypotheses that it must satisfy, however, do not match the dynamics of empirical data, once we begin
            to study them in detail.

            The distribution of the Log-Returns is not Gaussian, while it is still symmetrical (with low skewness, the third moment) it 
            displays a pronounced Leptokurtic nature (narrow central body with heavy tails) and it is better modeled by 
            Levy $\alpha$-stable distributions (that however have infinite variance and must be truncated), or Student's $t$-distributions.
            If we focus on the tails, a Power Law is usually pretty accurate.

            The parameters $\mu$ and, in particular, $\sigma$ are not constant as the GBM states. It is evident in the Log-Returns line plot that 
            they are not i.i.d., and they seem to cluster in "bursts"; the same happens to the estimated instantaneous volatility.
            In this aspect, GMB can be improved using Stochastic Volatility Models.
        ''', dangerously_allow_html=False, mathjax=True)
    stochastic_volatility = dbc.Card([
        dbc.CardHeader("Stochastic Volatility Models (SVM)"),
        dbc.CardBody(dcc.Markdown(
            r'''
            A model involving volatility as a stochastic process itself is based on two coupled SDEs:
            $$
            \begin{align}
            (a) \quad d S_t &= \mu S_t dt + f(Y_t)S_r dW_1(t) \\
            (b) \quad d Y_t &= \alpha(m-Y_t)dt + g(Y_t) dW_2(t)
            \end{align}
            $$
            where $(a)$ is a GBM with a stochastic noise coefficient $f(Y_t) \equiv \sigma$, while $(b)$ is a mean-reverting
            Ornstein-Uhlenbeck process for the auxiliary variable $Y$. These two equations are coupled by their Wigner terms,
            which are correlated by a coefficient $\rho$:
            $$
            dW_2(t) = \rho dW_1(t) + \sqrt{1 - \rho^2}dZ(t).
            $$ 
            This structure is common to every SVM, what separates one from the other is the choice of the functions $f(Y_t)$ and $g(Y_t)$ 
            which leads to different volatility pdfs. Some typycal choice are $f(Y)=Y$, $g(Y)=k$ (Stein-Stein model) 
            with a Normal volatility pdf, $f(Y)=\sqrt{Y},$ $g(Y)=k\sqrt{Y}$ (Heston model) 
            with a $\chi^2$ volatility pdf, and $f(Y)=e^{Y}$, $g(Y)=k$ (exp-OU model) 
            with a Log-Normal volatility pdf.
    
            All these models can be used in finance for the Monte Carlo pricing not only of plain vanilla (European) but also other exotic options (American, ...).
            ''', dangerously_allow_html=False, mathjax=True))
    ])
    beyond_GBM_2 = dcc.Markdown(r'''
        In the end, the efficient market hypothesis result, instead, verified in extremely high frequency (usually minutes), and 
        will continue to improve its efficiency with automated trading.
        This could be shown by computing autocorrelations in high frequency Log-Returns, but I have yet to obtain a 
        reliable dataset with this kind of data.

            ''', dangerously_allow_html=False, mathjax=True)
    return [html.H3("Beyond GBM"), beyond_GBM, stochastic_volatility, html.Br(), beyond_GBM_2]


layout = dbc.Container([
    html.Br(),
    html.H2('Geometric Brownian Motion'),
    dbc.Row([
        dbc.Col(latex_gbm(), width=5),
        dbc.Col([
            dcc.Graph(
                id='price-chart',
                figure=price_plot(data)),
            dcc.Graph(
                id='log-price-chart',
                figure=log_price_plot(data)),
            dcc.Graph(
                id='log-returns',
                figure=log_return_plot(data)),
            dbc.Col(dcc.Graph(
                figure=lognormal_evolution_plot(data)
            )),
        ], align="stretch"),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(latex_volatility(), width=5),
        dbc.Col([
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
                figure=rolling_volatility_plot(data, window=200)
            ),
            dcc.Graph(
                figure=instaneous_volatility_plot(data)
            ),
        ]),
    ]),
    dbc.Row([
        dbc.Col(latex_beyond_GBM(), width=5),
        dbc.Col([
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
    return rolling_volatility_plot(data, window=int(window))
