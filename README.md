# NTT Data AI Hackathon 2022

## AI in Healthcare

This is a candidate developed for the hackathon by **team ATR21** during
the semi-final round.  This is a web-app based on Machine Learning models trained on cardio
vascular and diabetic data, which can be used to predict the respective
conditions based on user-provided inputs. 

### Repository contents

 - Datasets
 - Jupyter Notebooks for training models (in progress)
 - Documentation
 - Web-app

### Prerequisites and Configuration

 - The app and the ML models are developed using Anaconda Data Science platform 4.11.0
   Requirements/dependencies are listed in `reqirements.yaml`.
 - No configuration is needed unless you want to update the models with new data
 or further tune the model hyperparameters
 - To tune the models, use the Jupyter Lab notebooks.
 
### Installation

 - Recreate the original development environment using:   
   `conda env create -n <new env name> -f requirements.yaml`
 - Clone or unzip this repository in your folder
 - Run `healthpred.py`. This will start a Flask web server on port 8080
 - Access this app via your browser at `localhost:8080`

### Usage

 - The webapp starting page has usage instructions
 

