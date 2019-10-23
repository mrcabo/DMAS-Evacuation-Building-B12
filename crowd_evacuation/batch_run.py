import argparse
from functools import partial

from mesa.batchrunner import BatchRunner

from crowd_evacuation.model import EvacuationModel, count_agents_saved


def get_agents_saved(model):
    return len(model.agents_saved)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Simulates evacuation of a building')
    parser.add_argument('--n_civilians', type=int, default=200,
                        help='Maximum number of civilians for the batch run. It will run experiments from 100 civilian '
                             'to n_civilians')
    parser.add_argument('--step_civilians', type=int, default=50,
                        help='The step size when iterating from 100 to n_civilians')
    parser.add_argument('--n_stewards', type=int, default=4,
                        help='Maximum number of stewards for the batch run. It will run experiments from 100 civilian '
                             'to n_civilians')
    parser.add_argument('--info_exchange', type=bool, default=True,
                        help='If civilians will exchange information or not')
    parser.add_argument('--fire_init', type=int, nargs='+', default=(1, 1),
                        help='Initial coordinates of the fire hazard. First x-coordinate then y-coordinate')
    args = parser.parse_args()
    return args.n_civilians, args.step_civilians, args.n_stewards, args.info_exchange, tuple(args.fire_init)


if __name__ == '__main__':
    n_civilians, step_civilians, n_stewards, info_exchange, fire_init = parse_arguments()
    fixed_params = {
        "civil_info_exchange": info_exchange,
        "fire_x": fire_init[0],
        "fire_y": fire_init[1],
    }
    variable_params = {
        "N": range(100, n_civilians, step_civilians),
        "K": range(0, n_stewards, 1),
    }

    # Create dictionary where the diagnosis probabilities will be tracked
    # dict_batch_collector = {}
    # dict_batch_collector = {"Final_decision": get_final_decision}
    # for i, disease in enumerate(MedicalModel.LIST_OF_DISEASES.values()):
    #     disease_prob = partial(get_diagnosis_probabilities, i)
    #     dict_batch_collector[disease] = disease_prob

    # pos_exits = [(0, 5), (0, 25), (0, 45)]
    # for i in range(3):
    #     pos_exits.append((50 - 1, 14 + i))
    # for exit_pos in pos_exits:
    #     title = "Exit {}".format(exit_pos)
    #     dict_batch_collector[title] = partial(count_agents_saved, exit_pos)

    batch_run = BatchRunner(
        EvacuationModel,
        variable_params,
        fixed_params,
        iterations=10,  # For now, then could be 100
        max_steps=500,
        model_reporters={"Agents saved": get_agents_saved}
    )

    batch_run.run_all()

    run_data = batch_run.get_model_vars_dataframe()
    print("Bye")
