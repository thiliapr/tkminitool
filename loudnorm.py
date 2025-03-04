import pathlib
import os

toConvPath = pathlib.Path("input")
outputPath = pathlib.Path("output")


for originalAudioPath in toConvPath.glob("**/*"):
    if not originalAudioPath.is_file():
        continue
    outputAudioPath = outputPath / originalAudioPath.relative_to(toConvPath)
    outputAudioPath = outputAudioPath.parent / ".".join(outputAudioPath.name.split(".")[:-1] + ["mp3"])

    if not outputAudioPath.parent.exists():
        os.makedirs(outputAudioPath.parent)

    os.system(f'ffmpeg -i "{originalAudioPath}" -vn -af loudnorm=i=-10:tp=0,volume=-45dB -y "{outputAudioPath}"')
