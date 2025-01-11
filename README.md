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
  python src/main.py
```
- **Click on**:
    http://127.0.0.1:8090

Once you successfully launch the application, you will be greeted with an interactive dashboard displaying detailed metrics about your system's performance. Here's what you will see:

RAM Usage Monitoring:

A gauge indicating the current percentage of RAM usage.
A real-time line graph showing the history of RAM usage over time.
Key statistics including:
Total RAM: The total memory available on the system.
Used RAM: The memory currently in use.
Available RAM: The memory that is free and can be allocated.
Free RAM: The exact amount of memory not in use.
Refresh Rate Control:

At the bottom of the dashboard, you can adjust the refresh rate slider to control how often the metrics update. Options range from 1 second to 30 seconds.

- **Debug the application**:
```sh
  python src/main.py --debug
```

### Utilisation

Une fois l'application lancée, ouvrez votre navigateur et accédez à l'adresse suivante : http://127.0.0.1:8050

Vous verrez une interface avec plusieurs graphiques dynamiques affichant les métriques du système en temps réel. Les graphiques incluent :

- **Utilisation du CPU** : Affiche l'utilisation de chaque cœur du CPU.
- **Utilisation de la RAM** : Affiche la RAM totale, utilisée et libre.
- **Utilisation du Disque** : Affiche l'espace disque total, utilisé et libre.
- **Utilisation du Réseau** : Affiche les octets reçus et envoyés par le réseau.

## How to contribute to the project

- **Clone the project**:
```sh
  git@devops.telecomste.fr:printerfaceadmin/2024-25/group8/ui-g8.git
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
