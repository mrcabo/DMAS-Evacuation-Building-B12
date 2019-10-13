# Crowd Evacuation Model

## Summary

**TODO:** Description of our model

## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```bash
pip install -r requirements.txt
```

## How to Run

To run the model, run:

```bash
python run.py
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press Reset, then Run.

## Files

* ``run.py``: Launches a model visualization server.
* ``model.py``: Contains the overall model class.
* ``<agent_name>_agent.py``: Contains the agents classes.
* ``server.py``: Defines classes for visualizing the model in the browser via Mesa's modular server, and instantiates a visualization server.
* ``path_finding.py``: Uses a graph that represents the grid, and finds the optimal path between 2 points using 
A* algorithm.

## Further Reading

Papers that inspire this model:

[Almeida, J. E., Rosseti, R. J., & Coelho, A. L. (2013). Crowd simulation modeling applied to emergency and evacuation simulations using multi-agent systems. arXiv preprint arXiv:1303.4692.
](https://arxiv.org/abs/1303.4692)