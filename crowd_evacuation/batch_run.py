import argparse
from functools import partial
from pathlib import Path

from mesa.batchrunner import BatchRunner

from crowd_evacuation.model import EvacuationModel, count_agents_saved


def get_agents_saved(model):
    return len(model.agents_saved)


def get_list_saved_agents(model):
    list_of_agents = []
    for agent in model.agents_saved:
        list_of_agents.append(agent.attr_to_list())
    return list_of_agents


def get_list_dead_agents(model):
    list_of_agents = []
    for agent in model.agents_killed:
        list_of_agents.append(agent.attr_to_list())
    return list_of_agents


def parse_arguments():
    parser = argparse.ArgumentParser(description='Simulates evacuation of a building')
    parser.add_argument('--filename', type=str, required=True,
                        help='The name of the file where the results will be saved')
    parser.add_argument('--n_civilians', type=int, default=200,
                        help='Maximum number of civilians for the batch run. It will run experiments from 100 civilian '
                             'to n_civilians')
    parser.add_argument('--step_civilians', type=int, default=50,
                        help='The step size when iterating from 100 to n_civilians')
    parser.add_argument('--n_stewards', type=int, default=4,
                        help='Maximum number of stewards for the batch run. It will run experiments from 100 civilian '
                             'to n_civilians')
    parser.add_argument('--step_stewards', type=int, default=1,
                        help='The step size when iterating from 0 to n_stewards')
    parser.add_argument('--info_exchange', type=bool, default=True,
                        help='If civilians will exchange information or not')
    parser.add_argument('--fire_init', type=int, nargs='+', default=(1, 1),
                        help='Initial coordinates of the fire hazard. First x-coordinate then y-coordinate')
    args = parser.parse_args()
    return (args.filename, args.n_civilians, args.step_civilians, args.n_stewards, args.step_stewards,
            args.info_exchange, tuple(args.fire_init))


if __name__ == '__main__':
    filename, n_civilians, step_civilians, n_stewards, step_stewards, info_exchange, fire_init = parse_arguments()
    fixed_params = {
        "civil_info_exchange": info_exchange,
        "fire_x": fire_init[0],
        "fire_y": fire_init[1],
    }
    variable_params = {
        "N": range(100, n_civilians, step_civilians),
        "K": range(0, n_stewards, step_stewards),
    }

    batch_run = BatchRunner(
        EvacuationModel,
        variable_params,
        fixed_params,
        iterations=10,  # For now, then could be 100
        max_steps=500,
        model_reporters={"Agents saved": get_agents_saved,
                         "List saved agents": get_list_saved_agents,
                         "List dead agents": get_list_dead_agents}
    )

    batch_run.run_all()
    batch_dir = Path.cwd() / "batch_results"
    if not batch_dir.exists():
        Path.mkdir(batch_dir)
    run_data = batch_run.get_model_vars_dataframe()
    run_data.to_csv(path_or_buf=(batch_dir / filename))
