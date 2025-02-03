import pytest
from analyticq.preprocessing import CodebaseMetricsCalculator


def test_average_size():
    sample = {"total_size": 100, "count": 4}
    result = CodebaseMetricsCalculator._average_size(sample)
    expected_average = 25
    assert result == expected_average, f"Expected {expected_average} average, got {result}"


def test_average_with_zero():
    sample_1 = {"total_size": 0, "count": 4}
    sample_2 = {"total_size": 100, "count": 0}

    expected_average = 0

    result_1 = CodebaseMetricsCalculator._average_size(sample_1)
    assert result_1 == expected_average, f"Expected {expected_average} average, got {result_1}"
    result_2 = CodebaseMetricsCalculator._average_size(sample_2)
    assert result_2 == expected_average, f"Expected {expected_average} average, got {result_2}"


def test_percentage_files():
    sample = {"count": 5}
    total_files = 10

    expected_percentage = 50.0

    result = CodebaseMetricsCalculator._percentage_files(sample, total_files)
    assert result == expected_percentage, f"Expected {expected_percentage} peercentage, got {result}"


def test_median():
    samples_1 = [100, 200, 300]
    expected_median_1 = 200

    samples_2 = [10, 20, 30, 40, 50]
    expected_median_2 = 30
    assert CodebaseMetricsCalculator._median_size([10, 20, 30, 40, 50]) == 30

    result_1 = CodebaseMetricsCalculator._median_size(samples_1)
    assert result_1 == expected_median_1, f"Expected {expected_median_1}, got {result_1}"

    result_2 = CodebaseMetricsCalculator._median_size(samples_2)
    assert result_2 == expected_median_2, f"Expected {expected_median_2}, got {result_2}"


def test_std():
    samples_1 = [100, 200, 300]
    expected_std_1 = 100.0

    result_1 = CodebaseMetricsCalculator._standard_deviation(samples_1)
    assert pytest.approx(result_1, 0.01) == expected_std_1, f"Expected {expected_std_1}, got {result_1}"

    samples_2 = [10, 20, 30, 40, 50]
    expected_std_2 = 15.81
    result_2 = CodebaseMetricsCalculator._standard_deviation(samples_2)
    assert pytest.approx(result_2, 0.01) == expected_std_2, f"Expected {expected_std_2}, got {result_2}"


def test_perecentage_files_with_zero():
    sample_1 = {"count": 0}
    sample_2 = {"count": 5}
    total_files_1 = 10
    total_files_2 = 0

    expected_percentage = 0

    result_1 = CodebaseMetricsCalculator._percentage_files(sample_1, total_files_1)
    assert result_1 == expected_percentage, f"Expected {expected_percentage} peercentage, got {result_1}"
    result_2 = CodebaseMetricsCalculator._percentage_files(sample_2, total_files_2)
    assert result_2 == expected_percentage, f"Expected {expected_percentage} percentage, got {result_2}"


def test_compute_language_metrics():
    language_stats_sample = {
        "Python": {"count": 3, "total_size": 1500, "largest_file": 1000, "smallest_file": 200},
        "JavaScript": {"count": 2, "total_size": 800, "largest_file": 500, "smallest_file": 300},
    }
    total_files = 5
    expected_output = {
        "Python": {
            "file_count": 3,
            "total_size": 1500,
            "largest_file": 1000,
            "smallest_file": 200,
            "average_size": 500.0,
            "median_size": 0,
            "std_size": 0,
            "percentage_files": 60.0
        },
        "JavaScript": {
            "file_count": 2,
            "total_size": 800,
            "largest_file": 500,
            "smallest_file": 300,
            "average_size": 400.0,
            "median_size": 0,
            "std_size": 0,
            "percentage_files": 40.0
        },
    }
    result = CodebaseMetricsCalculator.compute_language_metrics(language_stats_sample, total_files)
    print(result)
    assert result == expected_output, f"Expected {expected_output}, got {result}"


def test_compute_language_metrics_empty():
    expected_result = {}
    result = CodebaseMetricsCalculator.compute_language_metrics({}, 0)
    assert expected_result == result, f"Exepct empty dict, got {expected_result}"


def test_compute_language_metrics_zero_file():
    language_stats = {
        "Python": {"count": 0, "total_size": 0, "largest_file": 0, "smallest_file": 0},
    }

    expected_output = {
        "Python": {
            "file_count": 0,
            "total_size": 0,
            "largest_file": 0,
            "smallest_file": 0,
            "average_size": 0,
            "median_size": 0,
            "std_size": 0,
            "percentage_files": 0.0
        },
    }

    result = CodebaseMetricsCalculator.compute_language_metrics(language_stats, 0)
    assert result == expected_output, f"Expected {expected_output}, got {result}"
