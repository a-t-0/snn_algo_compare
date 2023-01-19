"""Method used to perform checks on whether the input is loaded correctly."""
from pathlib import Path
from typing import Dict, List, Optional

from snnbackends.verify_nx_graphs import verify_completed_stages_list
from typeguard import typechecked

from snncompare.exp_config.run_config.Run_config import Run_config
from snncompare.graph_generation.stage_1_get_input_graphs import (
    get_input_graph,
)

from ..export_results.helper import (
    get_expected_image_paths_stage_3,
    run_config_to_filename,
)
from ..export_results.load_json_to_nx_graph import (
    load_json_to_nx_graph_from_file,
    load_pre_existing_graph_dict,
)
from ..export_results.verify_stage_1_graphs import (
    get_expected_stage_1_graph_names,
)
from ..helper import get_expected_stages, get_extensions_list


@typechecked
def get_stage_2_nx_graphs(
    run_config: Run_config,
    to_run: Dict,
) -> Dict:
    """Loads the json graphs for stage 2 from file.

    Then converts them to nx graphs and returns them.
    """
    # Load results from file.
    nx_graphs_dict = load_json_to_nx_graph_from_file(run_config, 2, to_run)
    return nx_graphs_dict


# pylint: disable=R0911
# pylint: disable=R0912
@typechecked
def has_outputted_stage(
    run_config: Run_config,
    stage_index: int,
    to_run: Dict,
    verbose: bool = False,
    results_nx_graphs: Optional[Dict] = None,
) -> bool:
    """Checks whether the the required output files exist, for a given
    simulation and whether their content is valid. Returns True if the file
    exists, and its content is valid, False otherwise.

    :param run_config: param stage_index:
    :param stage_index:
    """
    expected_filepaths = []

    filename = run_config_to_filename(run_config)

    relative_output_dir = "results/"
    extensions = get_extensions_list(run_config, stage_index)
    for extension in extensions:
        if stage_index in [1, 2, 4]:

            expected_filepaths.append(
                relative_output_dir + filename + extension
            )
            # TODO: append expected_filepath to run_config per stage.

        if stage_index == 3:
            if run_config.export_images or run_config.show_snns:
                if has_outputted_stage(run_config, 2, to_run):
                    if results_nx_graphs is None:
                        nx_graphs_dict = get_stage_2_nx_graphs(
                            run_config, to_run
                        )

                    stage_3_img_filepaths = get_expected_image_paths_stage_3(
                        nx_graphs_dict=nx_graphs_dict,
                        input_graph=get_input_graph(run_config),
                        run_config=run_config,
                        extensions=extensions,
                    )
                    expected_filepaths.extend(stage_3_img_filepaths)
                else:
                    return False  # If stage 2 is not completed, neither is 3.

    # Check if the expected output files already exist.
    for filepath in expected_filepaths:
        if not Path(filepath).is_file():
            if verbose:
                print(f"File={filepath} missing.")
            return False
        if filepath[-5:] == ".json":
            # Load the json graphs from json file to see if they exist.
            # TODO: separate loading and checking if it can be loaded.
            try:
                json_graphs = load_pre_existing_graph_dict(
                    run_config, stage_index, to_run
                )
            # pylint: disable=R0801
            except KeyError:
                if verbose:
                    print(f"KeyError for: {filepath}")
                return False
            except ValueError:
                if verbose:
                    print(f"ValueError for: {filepath}")
                return False
            except TypeError:
                if verbose:
                    print(f"TypeError for: {filepath}")
                return False
            if stage_index == 4:
                return has_valid_json_results(json_graphs, run_config, to_run)
    return True


@typechecked
def nx_graphs_have_completed_stage(
    run_config: Run_config,
    results_nx_graphs: Dict,
    stage_index: int,
) -> bool:
    """Checks whether all expected graphs have been completed for the stages:

    <stage_index>. This check is performed by loading the graph dict
    from the graph Dict, and checking whether the graph dict contains a
    list with the completed stages, and checking this list whether it
    contains the required stage number.
    """

    # Loop through expected graph names for this run_config.
    for graph_name in get_expected_stage_1_graph_names(run_config):
        graph = results_nx_graphs["graphs_dict"][graph_name]
        if graph_name not in results_nx_graphs["graphs_dict"]:
            return False
        if ("completed_stages") not in graph.graph:
            return False
        if not isinstance(
            graph.graph["completed_stages"],
            List,
        ):
            raise Exception(
                "Error, completed stages parameter type is not a list."
            )
        if stage_index not in graph.graph["completed_stages"]:
            return False
        verify_completed_stages_list(graph.graph["completed_stages"])
    return True


# pylint: disable=R1702
@typechecked
def has_valid_json_results(
    json_graphs: Dict,
    run_config: Run_config,
    to_run: Dict,
) -> bool:
    """Checks if the json_graphs contain the expected results.

    TODO: support different algorithms.
    """
    for algo_name, algo_settings in run_config.algorithm.items():
        if algo_name == "MDSA":
            if isinstance(algo_settings["m_val"], int):
                graphnames_with_results = get_expected_stage_1_graph_names(
                    run_config
                )
                graphnames_with_results.remove("input_graph")
                if not set(graphnames_with_results).issubset(
                    json_graphs.keys()
                ):
                    return False

                expected_stages = get_expected_stages(
                    export_images=run_config.export_images,
                    overwrite_images_only=run_config.overwrite_images_only,
                    show_snns=run_config.show_snns,
                    stage_index=4,
                    to_run=to_run,
                )

                for graph_name, json_graph in json_graphs.items():
                    if graph_name in graphnames_with_results:

                        if expected_stages[-1] == 1:
                            graph_properties = json_graph["graph"]

                        elif expected_stages[-1] in [2, 4]:
                            # TODO: determine why this is a list of graphs,
                            # instead of a graph with list of nodes.
                            # Completed stages are only stored in the last
                            # timestep of the graph.
                            graph_properties = json_graph["graph"]
                        else:
                            raise Exception(
                                "Error, stage:{expected_stages[-1]} is "
                                "not yet supported in this check."
                            )
                        if "results" not in graph_properties.keys():
                            return False
                return True
            raise Exception(
                "Error, m_val setting is not of type int:"
                f'{type(algo_settings["m_val"])}'
                f'm_val={algo_settings["m_val"]}'
            )

        raise Exception(
            f"Error, algo_name:{algo_name} is not (yet) supported."
        )
    return True
