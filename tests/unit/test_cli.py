from unittest.mock import patch


from dxf_generator.interface import cli


def test_get_input_retries_until_valid():
    with patch("builtins.input", side_effect=["x", "2.5"]):
        value = cli.get_input("n: ")
    assert value == 2.5


def test_generate_single_ibeam_calls_service_save():
    with patch("builtins.input", side_effect=["300", "150", "8", "12"]), patch(
        "dxf_generator.interface.cli.DXFService.save"
    ) as mock_save:
        cli.generate_single_ibeam()

    assert mock_save.call_count == 1


def test_generate_column_invalid_mode_prints_message(capsys):
    with patch("builtins.input", side_effect=["2", "1", "200", "200"]), patch(
        "dxf_generator.interface.cli.DXFService.save"
    ) as mock_save:
        cli.generate_column()

    assert mock_save.call_count == 1
