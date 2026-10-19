"""Ensure every CLI preset is discoverable, importable and renders an image."""
import pytest
from PIL import Image
from src.examples import PRESETS, load_preset
from src.__main__ import main
from src.sketch_gif import run_sketch

@pytest.mark.parametrize("name",sorted(PRESETS))
def test_preset_import(name):
    cls=load_preset(name)
    assert callable(cls)

def test_cli_list(capsys):
    assert main(["list"])==0
    assert set(capsys.readouterr().out.splitlines())==set(PRESETS)

@pytest.mark.parametrize("name",sorted(PRESETS))
def test_preset_single_frame(name,tmp_path):
    path=tmp_path/(name+".png")
    run_sketch(load_preset(name),240,240,frame_limit=1,output=path,seed=8)
    with Image.open(path) as image:
        assert image.size==(240,240)
