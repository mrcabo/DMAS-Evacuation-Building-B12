# MultiAgentSystems
This project is done as part of the Design of Multi-Agent System course at the University of Groningen. The problem of crowd evacuation from a given building is addressed by taking several variables into account: the knowledge of the emergency exits, the age and weight of the agents and the presence of stewards that can guide agents toward the emergency exits. Agents have different strategies to escape the building such as taking the shortest path to an exit or a random one. Our goal is to study which combinations of agent types are more likely to escape the building and save themselves and how the amount of casualties varies with respect to the different variables.

## How to run it

This project was designed as a python package, so it could be uploaded to a python package repository in the future,
such as PyPi for example. All the import paths that are used in the code are declared with this in mind, which is 
why we need to indicate the python interpreter where to find our python package. That is done with the PYTHONPATH 
environment variable.

A simple example on how to run this code
```bash
#!/bin/bash
cd /home/<username>/Downloads
git clone https://github.com/mrcabo/DMAS-Evacuation-Building-B12.git
cd DMAS-Evacuation-Building-B12
python3 -m venv venv
source venv/bin/activate
export PYTHONPATH="$PYTHONPATH:/home/<username>/Downloads/DMAS-Evacuation-Building-B12"
cd crowd_evacuation
pip install -r requirements.txt
python run.py
```

Creating a virtual environment is not necessary but recommended. If you don't have it installed, try:

```bash
sudo apt update && apt install -y python3-venv
```
## Files

* ``run.py``: Launches a model visualization server.
* ``model.py``: Contains the overall model class.
* ``<agent_name>_agent.py``: Contains the agents classes.
* ``server.py``: Defines classes for visualizing the model in the browser via Mesa's modular server, and instantiates a visualization server.
* ``path_finding.py``: Uses a graph that represents the grid, and finds the optimal path between 2 points using 
A* algorithm.

## Frameworks

For this project we will use the Mesa framework. It is a modular framework for building, analyzing and visualizing agent-based models.

Its goal is to be the Python 3-based alternative to NetLogo, Repast, or MASON

[Mesa - github](https://github.com/projectmesa/mesa)
[Mesa - docs](https://mesa.readthedocs.io/en/master/overview.html)

## Useful Links and Papers

Papers that inspire this model:

[Almeida, J. E., Rosseti, R. J., & Coelho, A. L. (2013). Crowd simulation modeling applied to emergency and evacuation simulations using multi-agent systems. arXiv preprint arXiv:1303.4692.
](https://arxiv.org/abs/1303.4692)

[Fire evacuation articles](https://drive.google.com/open?id=1HMzqJxqz3AQLu_tjEEDJ6bSJO-sjNtLn)


