---
title: "Projects/Research"
showDate: false
showDateUpdated: false
slug: "projects-research"
showPagination: false
showReadingTime: false
showWordCount: false
showComments: false
---
The following provides an overview of projects and research that I have completed either as part of my graduate program or indenpendently.

### Final Project From [**FINM 33150 - Quantitative Trading Strategies**](https://finmath.uchicago.edu/curriculum/degree-concentrations/trading/finm-33150/)

The final group project consisted of developing a trading strategy incorporating the following:

* Creating criteria and evaluating potential trades
* Establishing position sizes, entry, and exit rules
* Minimum of 5 different assets (NOT asset classes)
* Use of leverage
* Produce a "paper" in [Jupyter Notebook](QTS_Project_REDACTED_REDACTED_Szajkowski.ipynb), [HTML](QTS_Project_REDACTED_REDACTED_Szajkowski.html)
* Produce a [PDF pitch book](QTS_Project_Pitch_Book_REDACTED_REDACTED_Szajkowski.pdf)
  
From the abstract:

> The final project seeks to develop a systematic trading/investment strategy that takes advantage of the time-tested market ideas that the market tends to increase in price/value over time, positive earnings growth tends to increase company valuation, companies with positive earnings growth tend to exhibit upward price momentum. When companies have lower earnings, they tend to have lower valuations which provides an opportunity for the value factor to take effect.

### Final Project From [**FINM 35900 - Macro-Finance**](https://finmath.uchicago.edu/curriculum/degree-concentrations/trading/finm-35900/)

The final group project consisted of selecting a fund or company and improving the fund with respect to macro/multi-asset ideas. The deliverables included:

* A concise [PDF write-up with appendicies](FINM35900_ProjectWriteUp_Szajkowski_REDACTED_REDACTED_Final.pdf)
* A [slide deck](FINM35900_ProjectSlides_Szajkowski_REDACTED_REDACTED_Final.pdf)
* Final [calculations in Jupyter Notebook](FINM35900_ProjectCalcs_Szajkowski_REDACTED_REDACTED_Final.ipynb), [HTML](FINM35900_ProjectCalcs_Szajkowski_REDACTED_REDACTED_Final.html)</br></br>

From the abstract:

> This proposal examines the potential benefits of incorporating Bitcoin into the asset allocation strategy of the Illinois State Board of Investment (ISBI). With over $25 billion in assets under management and a significant responsibility for managing pension plans for State of Illinois employees, ISBI's investment policy warrants periodic review and adjustment to optimize returns and manage risk. This study suggests initializing a 1% allocation of the fund's assets to Bitcoin as part of a diversified portfolio, alongside current assets.

### Final Project From [**FINM 35910 - Applied Algorithmic Trading**](https://finmath.uchicago.edu/curriculum/degree-concentrations/trading/finm-35910/)

The final group project was to "develop and present a fictional fund focusing on alternative algorithmic trading strategies." The strategy was to provide "uncorrelated return relative to the S&P 500 Index through robust strategy creation, risk management, and performance metrics."

* Final presentation [slide deck](finm_35910_final_presentation_Johnson_Holt_Szajkowski.pdf)
* Final [calculations in Jupyter Notebook](finm_35910_ML_Strat_ZJ_JRS.ipynb), [HTML](finm_35910_ML_Strat_ZJ_JRS.html)

From the fund prospectus:

> Part-Time Trading LLC is an investment firm focusing on developing machine-learning models to actively predict prices within cryptocurrency markets. Our fundʼs objective is to extract predictive features from crypto market data and utilize these features to develop best in class predictive machine learning models. Currently, we are focusing our trading efforts on trading Bitcoin and Ethereum on the crypto exchange Kraken. As we continue to advance our proprietary research and models, we plan to expand into other cryptocurrencies and exchanges.</br></br>Our trading system is designed to deliver consistent alpha by exploiting inefficiencies and opportunities in the highly volatile and liquid crypto markets. Our objective is to maximize returns while minimizing risk through data-driven decision making and robust predictive analytics.

### Final Project From [**FINM 33200 - Generative and Agentic AI for Finance**](https://finmath.uchicago.edu/curriculum/degree-concentrations/financial-computing/finm-33200/)

From the course description:

> The final project is your opportunity to apply the tools and concepts from this course to a real problem in finance. You will either:
>
> 1. **Conduct original research** related to generative or agentic AI in finance, or
> 2. **Build a tool** — a generative or agentic AI application that is useful in finance.
>
> This is not a traditional research paper. Think of your deliverable as something closer to a **blog post**, a **tool demo**, or a **startup pitch with a working prototype**. The goal is to showcase something concrete and practical — a new benchmark, a model comparison, a useful tool, or a compelling product idea backed by a working demo.

We elected to extend research done by Chen, Kelly, and Xiu (2022) on the paper entitled "Expected Returns and Large Language Models". From our [final project repository README](https://github.com/jaredszajkowski/finm33200_final_project):

> #### Description
>
> In HW2, we produced a modified replication of the Chen, Kelly, and Xiu (2022) paper entitled "Expected Returns and Large Language Models" using independently scraped news headlines instead of Thomson Reuters full articles. The [README for HW2](README_HW2.md) provides detailed context on the original paper's methodology and our replication approach.
>
> In this final project (referred to as "Sector Sentiment", going forward), we build on that foundation with completion of a similar set of data cleaning, headline embedding, and training tasks, but extend the investigation with a focus on *sector-level* sentiment signals.
>
> #### Thesis
>
> Our thesis is based on the following ideas:
>
> 1. News headlines are a rich source of information about market sentiment and can be effectively embedded using LLMs.
> 2. Aggregating daily headline embeddings up to the sector level can capture broader sentiment trends that may not be visible at the individual stock level, and these sector-level sentiment signals can have predictive power for future sector returns.
> 3. Implementing a trading/investing strategy based on daily stock-level sentiment signals is often impractical due to the magnitude of trades required to capture the signal, but sector-level signals can be actionable due to the instruments available (e.g., sector ETFs).
> 4. Given the results from Chen et al. showing that smaller LLMs can perform nearly as well as larger ones for embedding tasks, we can process data locally and avoid the need to send headline text to external APIs. Processing data locally results in a much larger sample size of headlines.
>
> #### Sector Sentiment
>
> As with HW2, we do not have access to Thomson Reuters full-text articles. However, instead of using **independently scraped news headlines** mreged with **RavenPack** metadata (entity IDs, sentiment scores, relevance, timestamps, etc.), as was required in HW2 due to the RavenPack licensing, our approach with sector sentiment is to use the RavenPack data in its entirety. We run local models for the embedding, and are therefore not sending any of the headline text to OpenAI or any other external API.
>
> For sector sentiment, the process is as follows:
>
> 1. **Pull Data:** FRED, CRSP (Daily Stock & Index), S&P 500 constituents, RavenPack headlines, and sector ETF data.
> 2. **Link Data:** Map RavenPack company IDs to CRSP PERMNOs and merge with stock return data.
> 3. **Clean Data:** Apply the single_entity, has_return, length_filter, and deduplication cleaning filters to the RavenPack headline data.
> 4. **Compute Return Labels:** Calculate 3-day returns around each headline timestamp (r_t-1, r_t, r_t+1) and assign a label for the sign of the return (positive = 1, negative = 0). This is the target variable for the headline-level sentiment model.
> 5. **Compute Forward Returns:** Calculate forward returns for the sector ETFs over various horizons (e.g., 1-day, 3-day, 5-day).
> 6. **Merge Data:** Merge the return over 3-day window, returns from the forward return windows, labels, date, market cap, sector, permno.
> 7. **Compute Headline Embeddings:** Pass each headline through BERT and [Gemma](https://deepmind.google/models/gemma/embeddinggemma/) embedding models to obtain a single vector per headline.
> 8. **Train Sentiment Model:** Follow the same rolling-window supervised learning framework as Chen et al., using headline embeddings as features. This step produces a model that predicts the return sign of the headline.
> 9. **Aggregate Daily Return Sign Predictions To Sector Level:** Using the probabilities from the headline embedding return sign predictions, compute a daily sector-level return score by aggregating stock-level predictions using market-cap weights. This is done for both the probabilities from the and the binary predictions from those probabilities.
>
> From a bottom-up approach, the sum across all stocks in the sector gives us the sector-level return score for that day.
>
> 10. **Test Long-Short Strategy Based On Daily Sector Sentiment Score:** Each day, rank sectors by their daily sector-level return score and go long the top `L` sectors and short the bottom `S` sectors (equal-weighted within each leg) the following day. Compute the daily strategy return based on the returns of the sector ETFs.
> 11. **Forward Return Regression:** Regress forward 1-day returns on the daily headline embeddings to evaluate predictive power for future returns. Report the R-squared and correlation values.
> 12. **Aggregate Daily Predicted Stock Returns To Sector Level:** From the forward return regression, compute daily predicted sector-level future returns by aggregating the stock-level predicted returns using market-cap weights.
>
> Again, from a bottom-up approach, the sum across all stocks in the sector gives us the predicted sector-level future returns for that day.
>
> 13. **Test Long-Short Strategy Based On Daily Predicted Returns:** Each day, rank sectors by their t+1 predicted returns. Go long the top `L` sectors and short the bottom `S` sectors (equal-weighted within each leg) the following day. Compute the daily strategy return based on the returns of the sector ETFs.
