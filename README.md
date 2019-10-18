# MultiAgentSystems
This project is done as part of the Design of Multi-Agent System course at the University of Groningen. The problem of crowd evacuation from a given building is addressed by taking several variables into account: the knowledge of the emergency exits, the age and weight of the agents and the presence of stewards that can guide agents toward the emergency exits. Agents have different strategies to escape the building such as taking the shortest path to an exit or a random one. Our goal is to study which combinations of agent types are more likely to escape the building and save themselves and how the amount of casualties varies with respect to the different variables.

## How to run it

```bash
#!/bin/bash
cd <path_to_base_dir>
python3 -m venv venv
source venv/bin/activate
export PYTHONPATH="$PYTHONPATH:<path_to_base_dir>"
cd crowd_evacuation
pip install -r requirements.txt
python run.py
```

where <path_to_base_dir> is the path to the directory where the repository was downloaded.

## Frameworks

For this project we will use the Mesa framework. It is a modular framework for building, analyzing and visualizing agent-based models.

Its goal is to be the Python 3-based alternative to NetLogo, Repast, or MASON

[Mesa - github](https://github.com/projectmesa/mesa)
[Mesa - docs](https://mesa.readthedocs.io/en/master/overview.html)

## Useful Links and Papers

[Fire evacuation articles](https://drive.google.com/open?id=1HMzqJxqz3AQLu_tjEEDJ6bSJO-sjNtLn)


