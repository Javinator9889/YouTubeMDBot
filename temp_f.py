import mutagen
import subprocess

from pydub import effects, AudioSegment
from io import BytesIO
from tempfile import TemporaryFile

ctr = BytesIO()
# command = "ffmpeg -i Inm-N5rLUSI.m4a -filter:a loudnorm -vn -b:a 128k -c:a aac -f ipod {}".format(tf.name).split(" ")
# print(tf.name)
# proc = subprocess.Popen(command, stderr=subprocess.PIPE)
# out, err = proc.communicate()
# print(err.decode("utf-8"))
with open("Inm-N5rLUSI.m4a", "rb") as audio:
    sound = audio.read()
bf = BytesIO(sound)
s = AudioSegment(bf, format="m4a")
s2 = effects.normalize(s)
s2.export(bf, format="m4a")
c = input("Continue? [yes/no] - ")
if c == "yes":
    print(tf.closed)
    tf.seek(0)
    data = BytesIO(tf.read())
    data.seek(0)
    print(mutagen.File(data).pprint())
    with open("out.m4a", "wb") as file:
        data.seek(0)
        file.write(data.read())

