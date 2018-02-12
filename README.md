## Predicting success of kickstarter projects based on their goals and presentation

[Kickstarter.com](http://kickstarter.com) provides a crowdsourcing platform for creative projects to be realized. To successfully get enough sponsor from backers, it is crucial to have a good name, blurb and realistic timeline for the crowdsourcing. This project aims at **predicting the success** of projects to have enough money pledged based on these quantities. The ultimate goal is to identify features possessed by successful projects and help future participants better tailor their project presentations.

### Files in the repo:
- Kickstarter_download_and_combine.py: Scraper that scrap html, download, clean kickstarter data from  [WebRobot](https://webrobots.io/kickstarter-datasets/) and combine them to a .csv file. It is run as a standalone python script.
- MainProgram-all-3.6.ipynb: Contains all the descriptions of the predictive model built (an ensemble of RNN, RandomForest and XGBoost) and model evaluation.
- diagnostic_plots.py: Contains modules that compares predictive values with true values, compute accuracy metrics and plot the ROC curve.
