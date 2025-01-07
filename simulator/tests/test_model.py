import os
import sys
import pytest

# Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from simulator.model import SpringMassDamperModel


def test_spring_mass_damper_model_integration():
    test_mass_kg = 1
    test_force_N = 2
    model = SpringMassDamperModel(test_mass_kg, 0, 0, 0)

    assert pytest.approx(model.get_position()) == 0

    dt = 0.5

    # x_dot_dot = F/m, therefore x = F/m * t^2/2
    expected_position = test_force_N / test_mass_kg * dt**2 / 2
    assert (
        pytest.approx(model.compute_new_position(test_force_N, dt), abs=0.005)
        == expected_position
    )


def test_spring_mass_damper_model_spring():
    test_mass_kg = 1
    test_force_N = 3
    test_spring_k = 3
    model = SpringMassDamperModel(test_mass_kg, test_spring_k, 0, 0)
    # set the initial position to 1 m - this is the equilibrium position
    model.x[0][0] = 1

    assert pytest.approx(model.get_position()) == 1

    dt = 0.5

    position = model.compute_new_position(test_force_N, dt)
    assert pytest.approx(position, abs=0.005) == 1
