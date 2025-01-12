# **User Interface**


## About the project

Our monitoring agent provides a simple and intuitive User Interface (UI) to display key system metrics. Follow these steps to explore the interface:

## Prerequisites

Before you continue, ensure you have met the following requirements:

- **Python 3.X**: Programming language for the application
- **virtualenv**: To create isolated Python environments [intall](https://virtualenv.pypa.io/en/latest/installation.html)
- **dash**: For building the interactive dashboard
- **dash-bootstrap-components**: For styling the dashboard with Bootstrap
- **plotly**: For rendering charts and graphs
- **requests**: For handling HTTP requests
- **pandas**: For data manipulation and analysis
- **psutil**: For retrieving system metrics

## How to install the project

- **Clone the project**:
```sh
  git clone git@devops.telecomste.fr:printerfaceadmin/2024-25/group8/ui-g8.git
  cd ui-g8
```

- **Activate a virtual environment**:
```sh
  python3 -m venv venv
  source venv/bin/activate
```

- **Install the dependencies**:
```sh
  pip install -r requirements.txt
```

## How to use the project
- **Start the application**:
```sh
  make environment
  make run
```
- **Click on**:
    http://0.0.0.0:8050/


Once the application is successfully launched, you will need to add a server. On the initial page, you'll see:

- **Server Health** : Indicates whether the server is reachable or not.
- **CPU usage** : Displays the current CPU usage as a percentage.
- **RAM usage** : Displays the current RAM usage as a percentage.


After clicking on 'View Details', you will access a more detailed interactive dashboard that includes:


- **Server Health** : Status of the server.
- **CPU Metrics** : - Average CPU Usage  
                    - CPU History Graph: A graphical representation of CPU usage over time  
                    - CPU Cores Graph: Details of individual core usage  
- **RAM Metrics** : - RAM Gauge: A gauge indicating current RAM usage  
                    - RAM History Graph: A timeline showing RAM usage patterns  
                    - Detailed RAM Metrics: Total RAM, Used RAM, Available RAM, and Free RAM  
- **Refresh Rate**: An adjustable control to set how often the dashboard refreshes the metrics.

- **Exit the application**:
```sh
  ctrl + C
```

## How to contribute to the project

- **Clone the project**:
```sh
  git clone git@devops.telecomste.fr:printerfaceadmin/2024-25/group8/ui-g8.git
  cd ui-g8
```

- **Create a branch**:
```sh
  git checkout -b my-awesome-feature
```

- **Make amazing changes!**:
Fix bugs, add features, or even update the README because good documentation makes everything better.

- **Submit a merge request:**:
Push your changes, describe what you did, and open a merge request with a nice description. We love descriptions.


## Contributors

We wouldn’t be here without the contributions of these brilliant minds:
-ASSERAR Aymane  
-EL-KOULFA Hassane  
-GOUHIER Matteo  
-HARGANE Chayma  
-TIDJANI MOHAMED Archou  

Want to see your name here? Check out the section above to learn how to contribute!

## Acknowledgements

Special thanks to:

Mehdi Zeghdallou, Damien Jacinto and Jules Chevalier: Our three professors who showed incredible patience and support throughout this project.

## License

No specific license has been assigned to this project.
For questions regarding usage or rights, please contact the authors.

