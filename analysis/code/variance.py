from helper import *
import csv
from statistics import mean, stdev


def get_coefficient_of_variation(output_path, *files):
    """
    Given a set of forecasts for a number of time series several steps ahead in time, calculate the coefficient of
    variation between all the predicted values for each step in the forecasting horizon for each time series.
    :param output_path: String. The path to the destination where a new file will be created with all the coefficients
    of variation.
    :param files: A number of strings. The strings are paths to different forecasts.
    :return: Nothing. A new file is created in output_path with the result.
    """

    # Create folders if they don't already exists and create an output file
    folders_path = remove_file_from_path(output_path)
    create_path_if_not_exists(folders_path)
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    writer.writerow(["id"] + ["F" + str(i) for i in range(1, 49)])

    reruns = []
    for file in files:
        reruns.append(open(file).read().split("\n"))

    # For each time series
    for series in range(1, len(reruns[0])):

        # Sometimes there's a newline in the end of the file
        if len(reruns[0][series].split(",")) == 1:
            break

        # Get the id of this series for the first rerun to later check that the id is equal for all reruns
        series_id = reruns[0][series].split(",")[0]

        horizon = get_horizon(series_id)

        # Creating a list for saving the coefficients of variation for this series
        coefficients_of_variation = []

        # For each step in the forecasting horizon
        for step in range(1, horizon + 1):

            # Save the different forecasts in a list to later find the coefficient of variation between them
            predicted_values = []

            # For each rerun
            for rerun in reruns:
                series_id_this_rerun = rerun[series].split(",")[0]

                # Check that all the ids are equal
                if series_id_this_rerun != series_id:
                    raise Exception("Series ids are not equal.")

                # Add the forecast
                try:
                    predicted_value = float(rerun[series].split(",")[step])
                except ValueError:
                    predicted_value = "NA"
                predicted_values.append(predicted_value)
            try:
                coefficient_of_variation = stdev(predicted_values) / mean(predicted_values)
            except (ZeroDivisionError, TypeError):
                # ZeroDivisionError: The mean is zero and the coefficient of variation is not defined
                # TypeError: Some or all values are not available
                coefficient_of_variation = "NA"
            coefficients_of_variation.append(coefficient_of_variation)

        # Write the coefficients of variation for the given series to file
        writer.writerow([series_id] + coefficients_of_variation)


def DRMSD(values_a, values_b):
    """
    Takes in two groups of values. Calculates the percentage difference between the means of the two groups.
    :param values_a: List of floats.
    :param values_b: List of floats.
    :return: Float
    """
    mean_a = mean(values_a)
    mean_b = mean(values_b)
    sd_a = stdev(values_a)
    sd_b = stdev(values_b)
    diff = abs(mean_a - mean_b)
    mean_mean = mean([mean_a, mean_b])
    mean_sd = mean([sd_a, sd_b])
    if mean_mean == 0 or mean_sd == 0:
        DRMSD_value = "NA"
    else:
        DRMSD_value = diff**2 / (mean_mean * mean_sd)
    DRMSD_value = float("%.5f" % DRMSD_value)
    return DRMSD_value


def compare_computers(input_files_a, input_files_b, output_path):
    """"
    Given two sets of files containing values (for instance forecasts), creates a new file giving the DRMSD error of those sets.
    :param input_files_a: List of strings. Each element in the list is a string with a path to a csv file containing values (for instance sAPE values) for all timesteps and all series between two
    forecasts (or a forecast and a test set). This kind of file can be generated by get_average_resolution_origin()
    :param input_files_b:
    :param output_path: String. Path to write the output file.
    :return: Writes a file to output_path of the same format like the input files. In every field in the new file is
    the DRMSD error of the corresponding fields in the input files.
    """

    # Write the different files to dataframes
    reruns_a = []
    reruns_b = []
    for file in input_files_a:
        reruns_a.append(pd.read_csv(file, index_col=0))
    for file in input_files_b:
        reruns_b.append(pd.read_csv(file, index_col=0))

    index = reruns_a[0].index.values
    columns = reruns_b[0].columns.values

    # Creates an output file for the final result
    result_df = pd.DataFrame(index=index, columns=columns)

    # Calculate the DRMSD of the reruns for each entry
    for i in index:
        for c in columns:
            values_a = []
            values_b = []
            for rerun in reruns_a:
                values_a.append(rerun.loc[i, c])
            for rerun in reruns_b:
                values_b.append(rerun.loc[i, c])
            DRMSD_value = DRMSD(values_a, values_b)
            result_df.at[i, c] = DRMSD_value

    # Write to csv
    result_df.to_csv(output_path)
