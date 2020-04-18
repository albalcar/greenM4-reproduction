from helper import *
import csv


def sAPE(value_1, value_2):
    """
    Calculate the sAPE between two single values.
    :param value_1: Float
    :param value_2: Float
    :return: Float
    """
    try:
        result = 200.0 * abs((value_2 - value_1)) / (abs(value_2) + abs(value_1))
    except ZeroDivisionError:
        # The values are both zero and the sAPE is not defined
        result = "NA"
    return result


def get_mean_absolute_scaled_error(training_values, m):
    """
    Gives the mean absolute scaled error of a time series as needed when calculating ASE.
    :param training_values: List of floats.
    :param m: Integer. Gives the frequency of the series.
    :return: Float.
    """
    n = len(training_values)
    total_seasonal_naive_error = 0
    for t in range(m, n):
        seasonal_error = abs(training_values[t] - training_values[t - m])
        total_seasonal_naive_error += seasonal_error
    mean_seasonal_naive_error = total_seasonal_naive_error / (n - m)
    return mean_seasonal_naive_error


def ASE(value_1, value_2, mean_absolute_scaled_error):
    """
    Calculate ASE where the denominator (mean_absolute_scaled_error) is already given.
    :param value_1: Float
    :param value_2: Float
    :param mean_absolute_scaled_error: Float
    :return:
    """
    absolute_error = abs(value_1 - value_2)
    try:
        result = absolute_error / mean_absolute_scaled_error
    except ZeroDivisionError:
        # ASE is not defined is this case
        result = "NA"
    return result


def compare_results_sAPE(file_1, file_2, output_path):
    """
    Takes in two files. Each file has a forecast for all the time series in the M4 competition. Writes a new file that
    contains the error between all the forecasted values. The files are expected to have a header line.
    :param file_1: String. Path to file 1
    :param file_2: String. Path to file 2
    :return: Nothing. Writes a new file with errors
    """

    file_1 = open(file_1).read().split("\n")
    file_2 = open(file_2).read().split("\n")

    # Create folders if they don't already exists and create an output file
    folders_path = remove_file_from_path(output_path)
    create_path_if_not_exists(folders_path)
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    writer.writerow(["id"] + ["F" + str(i) for i in range(1, 49)])

    for series_number in range(1, len(file_1) - 1):
        series_1 = file_1[series_number].split(",")
        series_2 = file_2[series_number].split(",")
        id_1 = remove_quotes_if_any(series_1[0])
        id_2 = remove_quotes_if_any(series_2[0])
        if id_1 != id_2:
            raise Exception("Series ids not matching")
        series_forecast_1 = series_1[1:]
        series_forecast_2 = series_2[1:]

        # Store error between the two forecasts for this series
        errors = [id_1]

        horizon = get_horizon(id_1)
        for j in range(horizon):
            # A model might not have been able to predict a value
            if series_forecast_1[j] == "NA" or series_forecast_2[j] == "NA":
                error = "NA"
            else:
                value_1 = float(series_forecast_1[j])
                value_2 = float(series_forecast_2[j])
                error = sAPE(value_1, value_2)
            errors.append(error)

        writer.writerow(errors)


def compare_results_ASE(file_1, file_2, output_path):
    """
    Takes in two files. Each file has a forecast for all the time series in the M4 competition. Writes a new file that
    contains the error between all the forecasted values. The files are expected to have a header line.
    :param file_1: String. Path to file 1
    :param file_2: String. Path to file 2
    :return: Nothing. Writes a new file with errors
    """

    file_1 = open(file_1).read().split("\n")
    file_2 = open(file_2).read().split("\n")

    # Create folders if they don't already exists and create an output file
    folders_path = remove_file_from_path(output_path)
    create_path_if_not_exists(folders_path)
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    writer.writerow(["id"] + ["F" + str(i) for i in range(1, 49)])

    for series_number in range(1, len(file_1) - 1):
        series_1 = file_1[series_number].split(",")
        series_2 = file_2[series_number].split(",")
        id_1 = remove_quotes_if_any(series_1[0])
        id_2 = remove_quotes_if_any(series_2[0])
        if id_1 != id_2:
            raise Exception("Series ids not matching")
        series_forecast_1 = series_1[1:]
        series_forecast_2 = series_2[1:]

        # Calculate the denominator in the formula. This is the mean absolute error the seasonal naive method would
        # have made on the training data.
        training_values = get_training_values(id_1)
        m = get_frequency(id_1)
        mean_seasonal_naive_error = get_mean_absolute_scaled_error(training_values, m)

        # Store error between the two forecasts for this series
        errors = [id_1]

        horizon = get_horizon(id_1)
        for j in range(horizon):
            # A model might not have been able to predict a value
            if series_forecast_1[j] == "NA" or series_forecast_2[j] == "NA":
                error = "NA"
            else:
                value_1 = float(series_forecast_1[j])
                value_2 = float(series_forecast_2[j])
                error = ASE(value_1, value_2, mean_seasonal_naive_error)
            errors.append(error)

        writer.writerow(errors)


def calculate_OWA(sAPE_file, ASE_file, naive2_sAPE_file, naive2_ASE_file, output_path):
    """
    Calculate OWI between all values.
    :return: Nothing. Writes a file to output_path.
    """
    sAPE_file = open(sAPE_file).read().split("\n")
    ASE_file = open(ASE_file).read().split("\n")
    naive2_sAPE_file = open(naive2_sAPE_file).read().split("\n")
    naive2_ASE_file = open(naive2_ASE_file).read().split("\n")

    # Create folders if they don't already exists and create an output file
    folders_path = remove_file_from_path(output_path)
    create_path_if_not_exists(folders_path)
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    writer.writerow(["id"] + ["F" + str(i) for i in range(1, 49)])

    for series_number in range(1, len(sAPE_file) - 1):
        series_1 = sAPE_file[series_number].split(",")
        series_2 = ASE_file[series_number].split(",")
        series_3 = naive2_sAPE_file[series_number].split(",")
        series_4 = naive2_ASE_file[series_number].split(",")
        id_1 = remove_quotes_if_any(series_1[0])
        id_2 = remove_quotes_if_any(series_2[0])
        id_3 = remove_quotes_if_any(series_3[0])
        id_4 = remove_quotes_if_any(series_4[0])
        if id_1 != id_2 or id_1 != id_3 or id_1 != id_4:
            raise Exception("Series ids not matching. Series ids was %s %s %s and %s" % (id_1, id_2, id_3, id_4))
        sAPE_values = series_1[1:]
        ASE_values = series_2[1:]
        naive2_sAPE_values = series_3[1:]
        naive2_ASE_values = series_4[1:]

        OWA_values = [id_1]

        horizon = get_horizon(id_1)
        
        for j in range(horizon):
            try:
                # All values have to be available for the OWA to be calculated
                sAPE_value = float(sAPE_values[j])
                ASE_value = float(ASE_values[j])
                naive2_sAPE_value = float(naive2_sAPE_values[j])
                naive2_ASE_value = float(naive2_ASE_values[j])

                relative_sAPE = sAPE_value / naive2_sAPE_value
                relative_ASE = ASE_value / naive2_ASE_value

            except (ValueError, ZeroDivisionError):
                # ValueError: Some value is not available
                # ZeroDivisionError: Naive2 sAPE and ASE is zero (naive2 predicts the correct test value)
                OWA = "NA"
            else:
                OWA = (relative_sAPE + relative_ASE) / 2
            OWA_values.append(OWA)

        writer.writerow(OWA_values)


def get_average_values_for_all_reruns(output_path, *input_files):
    """
    Given a set of files containing values (for instance sAPE values), creates a new file giving the average values of
    every entry in those files.
    :param output_path: String. Path to write the output file.
    :param input_files: Each argument is a string with a path to a csv file containing values (for instance sAPE values)
    for all timesteps and all series between two forecasts (or a forecast and a test set). This kind of file cat be
    generated by compare_results()
    :return: Writes a file to output_path of the same format like the *input_files. In every field in the new file is
    the average of the corresponding fields in the input_files.
    """

    # Creates an output file for the final result
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    writer.writerow(["id"] + ["F" + str(i) for i in range(1, 49)])

    reruns = []
    for file in input_files:
        reruns.append(open(file).read().split("\n"))

    # For each time series
    for series_number in range(1, len(reruns[0])):

        # Sometimes there might be an empty newline in the end of the file
        if not reruns[0][series_number]:
            break

        # Get the id of this series for the first rerun to later check that the id is equal for all reruns
        series_id = reruns[0][series_number].split(",")[0]

        horizon = get_horizon(series_id)

        averages = []

        # For each step in the horizon
        for h in range(1, horizon + 1):

            sum = 0

            # For each rerun
            for rerun in reruns:
                series_id_this_rerun = rerun[series_number].split(",")[0]

                # Check that all the ids are equal
                if series_id_this_rerun != series_id:
                    raise Exception("Series ids are not equal.")

                value = rerun[series_number].split(",")[h]

                if value == "NA":
                    sum = "NA"
                    break
                else:
                    sum += float(value)

            try:
                average = sum / len(input_files)
            except TypeError:
                average = "NA"
            averages.append(average)

        writer.writerow([series_id] + averages)
