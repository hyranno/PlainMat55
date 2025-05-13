import os
import tempfile
import zipfile
import shutil
import subprocess
import re
from pathlib import Path


def changeSuffix(dir, src_suffix, dest_suffix):
  files = list(Path(dir).glob(f"*{src_suffix}"))
  for filepath in files:
    new_filepath = filepath.with_suffix(dest_suffix)
    os.rename(filepath, new_filepath)

def genGerber(path, outdir):
  command = re.sub(r"\s+", " ", """
    kicad-cli pcb export gerbers
      --output {output}
      --layers "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
      {input}.kicad_pcb
  """).strip().format(output=outdir, input=path)
  subprocess.run(command, shell=True)
  changeSuffix(outdir, ".gm1", ".gml")

def genDrill(path, outdir):
  command = re.sub(r"\s+", " ", """
    kicad-cli pcb export drill
      --output {output}
      --excellon-separate-th
      {input}.kicad_pcb
  """).strip().format(output=outdir, input=path)
  subprocess.run(command, shell=True)
  changeSuffix(outdir, ".drl", ".drl.txt")

def genGerberArchive(path, outdir):
  with tempfile.TemporaryDirectory() as tmpdir:
    genGerber(path, tmpdir)
    genDrill(path, tmpdir)
    #shutil.move(tmpdir, outdir)
    zip_filename = os.path.basename(path) + ".zip"
    output = os.path.join(outdir, zip_filename)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
      for filepath in Path(tmpdir).iterdir():
        zipf.write(filepath, arcname=os.path.basename(filepath))

def genPosition(path, outdir):
  filename = os.path.basename(path) + ".pos"
  output = os.path.join(outdir, filename)
  command = re.sub(r"\s+", " ", """
    kicad-cli pcb export pos
      --output {output}
      --exclude-dnp
      {input}.kicad_pcb
  """).strip().format(output=output, input=path)
  subprocess.run(command, shell=True)

def copyBom(path, outdir):
  filename = os.path.basename(path) + "_bom.csv"
  input = path + "_bom.csv"
  output = os.path.join(outdir, filename)
  shutil.copy(input, output)

def genBom(path, outdir):
  filename = os.path.join(outdir, os.path.basename(path) + "_bom.csv")
  command = re.sub(r"\s+", " ", """
    kicad-cli sch export bom
      --output {output}
      --fields "Reference,Manufacturer Part number,\\${{QUANTITY}},Original,Description,Purchase Link"
      --labels "Reference,Manufacturer Part number,QTY,Original,Description,Purchase Link"
      --group-by "Manufacturer Part number"
      --exclude-dnp
      {input}.kicad_sch
    """).strip().format(output=filename, input=path)
  subprocess.run(command, shell=True)



path = "./PlainMat55/PlainMat55"
outdir = "./output/elecrow"
os.makedirs(outdir, exist_ok=True)

genGerberArchive(path, outdir)
genPosition(path, outdir)
genBom(path, outdir)
